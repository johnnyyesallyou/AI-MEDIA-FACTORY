"""Re:Manga Source Adapter."""
import logging
import re
import time
from datetime import datetime
from typing import List, Optional, Dict, Any

import requests
from core.retry import retry_external_api

from .base import BaseSourceAdapter, SourceItem
from engines.source_adapters.base_manga_adapter import BaseMangaAdapter, MangaItem

logger = logging.getLogger(__name__)


class ReMangaAdapter(BaseSourceAdapter, BaseMangaAdapter):
    """
    Адаптер для Re:Manga API.
    
    Sprint 22: наследует BaseMangaAdapter для единого MangaItem интерфейса.
    """

    BASE_URL = "https://remanga.org"
    API_BASE = "https://remanga.org/api"
    LAST_CHAPTERS_ENDPOINT = "/titles/last-chapters/"
    TITLE_INFO_ENDPOINT = "/titles/{slug}/"
    TITLE_SEARCH_ENDPOINT = "/search/"
    TITLE_BASE = "https://remanga.org/manga"
    COVER_BASE = "https://remanga.org"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Accept-Language": "ru,en;q=0.9",
    }

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_source_name(self) -> str:
        return "remanga"

    def fetch_latest_chapters(self, limit: int = 20) -> List[SourceItem]:
        url = f"{self.BASE_URL}/api{self.LAST_CHAPTERS_ENDPOINT}"
        params = {"page": 1, "count": min(limit, 100)}

        self.logger.info(f"Fetching latest chapters from ReManga (limit={limit})")

        response = requests.get(
            url, params=params, headers=self.HEADERS, timeout=self.timeout
        )
        response.raise_for_status()

        data = response.json()
        content = data.get("content", [])
        self.logger.info(f"Fetched {len(content)} chapters from ReManga")

        items = []
        for item_data in content:
            try:
                item = self._parse_item(item_data)
                if item:
                    items.append(item)
            except Exception as e:
                self.logger.warning(f"Failed to parse item: {e}")
                continue

        return items

    def get_title_info(self, slug: str) -> Optional[Dict[str, Any]]:
        url = f"{self.API_BASE}/titles/{slug}/"
        try:
            response = requests.get(url, headers=self.HEADERS, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            content = data.get("content", {})
            if not content:
                return None

            description_html = content.get("description", "")
            description = self._strip_html(description_html)

            genres = content.get("genres", [])
            if genres and isinstance(genres, list):
                if isinstance(genres[0], dict):
                    genres = [g.get("name", "") for g in genres]

            type_info = content.get("type", {})
            type_name = type_info.get("name", "") if isinstance(type_info, dict) else ""

            status_info = content.get("status", {})
            status_name = status_info.get("name", "") if isinstance(status_info, dict) else ""

            return {
                "description": description,
                "genres": genres,
                "type": type_name,
                "status": status_name,
                "count_chapters": content.get("count_chapters", 0),
            }
        except Exception as e:
            self.logger.error(f"Failed to get title info for {slug}: {e}")
            return None

    def search_title(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            url = f"{self.API_BASE}{self.TITLE_SEARCH_ENDPOINT}"
            response = requests.get(
                url, params={"query": query, "count": limit},
                headers=self.HEADERS, timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            content = data.get("content", [])
            results = []
            for item in content[:limit]:
                results.append({
                    "id": item.get("id"),
                    "title": item.get("rus_name") or item.get("en_name"),
                    "slug": item.get("dir"),
                })
            return results
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return []

    def find_title_slug(self, title_name: str, title_id: str = "") -> Optional[str]:
        results = self.search_title(title_name)
        if results:
            return results[0].get("slug")
        return None

    def _strip_html(self, html: str) -> str:
        if not html:
            return ""
        text = re.sub(r"<[^>]+>", "", html)
        text = re.sub(r"&nbsp;", " ", text)
        text = re.sub(r"&amp;", "&", text)
        text = re.sub(r"&lt;", "<", text)
        text = re.sub(r"&gt;", ">", text)
        return text.strip()

    def fetch_first_chapter_preview(self, slug: str, limit: int = 5) -> Optional[List[str]]:
        try:
            response = requests.get(
                f"{self.API_BASE}/titles/{slug}/",
                headers=self.HEADERS, timeout=self.timeout
            )
            response.raise_for_status()
            title_content = response.json().get("content", {})
            first_chapter = title_content.get("first_chapter")
            if not first_chapter:
                self.logger.warning(f"No first_chapter for {slug}")
                return None

            chapter_id = first_chapter.get("id") if isinstance(first_chapter, dict) else first_chapter
            ch_response = requests.get(
                f"{self.API_BASE}/titles/chapters/{chapter_id}/",
                headers=self.HEADERS, timeout=self.timeout
            )
            ch_response.raise_for_status()
            ch_data = ch_response.json().get("content", {})
            pages = ch_data.get("pages", [])

            page_urls = []
            for page_item in pages[:limit]:
                if isinstance(page_item, list) and page_item:
                    page_obj = page_item[0]
                    if isinstance(page_obj, dict):
                        url = page_obj.get("link")
                        if url:
                            page_urls.append(url)
                elif isinstance(page_item, dict):
                    url = page_item.get("link")
                    if url:
                        page_urls.append(url)

            self.logger.info(f"Fetched {len(page_urls)} preview pages for {slug}")
            return page_urls
        except Exception as e:
            self.logger.error(f"Failed to fetch preview for {slug}: {e}")
            return None

    def _parse_item(self, data: Dict[str, Any]) -> Optional[SourceItem]:
        if not data:
            return None

        title_id = str(data.get("id", ""))
        title_slug = data.get("dir", "")
        title_name = data.get("rus_name", "") or data.get("main_name", "") or "Unknown"
        title_name_en = data.get("en_name", "") or data.get("secondary_name", "")

        chapter_number = str(data.get("chapter", ""))
        chapter_id = str(data.get("chapter_id", ""))

        cover_data = data.get("cover", {}) or {}
        cover_path = cover_data.get("mid") or cover_data.get("high") or cover_data.get("low")
        cover_url = f"{self.COVER_BASE}{cover_path}" if cover_path else None

        title_url = f"{self.TITLE_BASE}/{title_slug}" if title_slug else None
        chapter_url = f"{title_url}/{chapter_id}" if title_url and chapter_id else None

        upload_timestamp = data.get("upload_date")
        upload_date = None
        if upload_timestamp:
            try:
                if isinstance(upload_timestamp, (int, float)):
                    upload_date = datetime.fromtimestamp(upload_timestamp)
                else:
                    upload_date = datetime.fromisoformat(upload_timestamp.replace("Z", "+00:00"))
            except Exception:
                pass

        return SourceItem(
            source=self.get_source_name(),
            title_id=title_id,
            title_name=title_name,
            title_name_en=title_name_en,
            title_slug=title_slug,
            chapter_number=chapter_number,
            chapter_id=chapter_id,
            chapter_url=chapter_url,
            title_url=title_url,
            cover_url=cover_url,
            upload_date=upload_date,
            is_new=False,
        )

    # ========== Sprint 22: New manga adapter interface ==========

    def _to_manga_item(self, item) -> MangaItem:
        """Конвертирует SourceItem в MangaItem."""
        return MangaItem(
            external_id=item.chapter_id or item.title_id,
            title_external_id=item.title_id,
            title=item.title_name or "Unknown",
            chapter=item.chapter_number or "?",
            url=item.chapter_url or item.title_url,
            language="ru",
            source="remanga",
            description=None,
            genres=None,
            cover_url=item.cover_url,
            title_slug=item.title_slug,
            title_name_en=item.title_name_en,
            chapter_id=item.chapter_id,
            title_url=item.title_url,
            upload_date=item.upload_date,
        )

    @retry_external_api
    def fetch_latest_chapters_manga(self, limit: int = 20) -> list:
        """Возвращает List[MangaItem] (новый интерфейс)."""
        source_items = self.fetch_latest_chapters(limit)
        return [self._to_manga_item(item) for item in source_items]