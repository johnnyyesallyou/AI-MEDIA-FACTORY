"""MangaDex Source Adapter - fetches latest RU chapters."""
import requests
from core.retry import retry_external_api
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import logging

from .base import BaseSourceAdapter, SourceItem
from .base_manga_adapter import BaseMangaAdapter, MangaItem

logger = logging.getLogger(__name__)


class MangaDexAdapter(BaseSourceAdapter, BaseMangaAdapter):
    """
    Adapter for MangaDex.org API.
    
    API: https://api.mangadex.org (no auth required)
    - /chapter: latest RU chapters (order[readableAt]=desc)
    - /manga?ids[]: batch fetch titles + covers (up to 100)
    
    Content filter: safe + suggestive only (no erotica/pornographic)
    
    Sprint 16: MangaDex backup source
    """
    
    BASE_URL = "https://api.mangadex.org"
    COVER_BASE = "https://uploads.mangadex.org/covers"
    TITLE_BASE = "https://mangadex.org/title"
    
    HEADERS = {"User-Agent": "Mozilla/5.0 (AI-Media-Factory/1.0)"}
    
    def __init__(self, timeout: int = 30):
        super().__init__()
        self.timeout = timeout
    
    def get_source_name(self) -> str:
        return "mangadex"
    
    def _safe_get(self, d, *keys, default=None):
        """Безопасное извлечение вложенных значений."""
        for k in keys:
            if d is None:
                return default
            d = d.get(k) if isinstance(d, dict) else None
        return d if d is not None else default
    
    def fetch_latest_chapters(self, limit: int = 20, offset: int = 0) -> List[SourceItem]:
        """
        Fetch latest RU chapters from MangaDex.
        
        Strategy:
        1. GET /chapter (RU, readableAt desc, safe+suggestive)
        2. Collect unique manga_ids
        3. Batch GET /manga?ids[] for titles + covers
        4. Merge into SourceItem list
        """
        now = datetime.now(timezone.utc)
        
        # Step 1: Fetch latest chapters
        self.logger.info(f"Fetching latest RU chapters from MangaDex (limit={limit})")
        
        response = requests.get(
            f"{self.BASE_URL}/chapter",
            params=[
                ("limit", min(limit * 2, 100)),
                ("offset", offset),  # берём больше для фильтрации
                ("order[readableAt]", "desc"),
                ("translatedLanguage[]", "ru"),
                ("contentRating[]", "safe"),
                ("contentRating[]", "suggestive"),
                ("includes[]", "manga"),
            ],
            headers=self.HEADERS,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        chapters = response.json().get("data", [])
        self.logger.info(f"Fetched {len(chapters)} chapters")
        
        # Step 2: Filter valid chapters + collect manga_ids
        valid_chapters = []
        manga_ids = set()
        
        for ch in chapters:
            a = ch.get("attributes", {}) or {}
            
            # Фильтруем будущее (readableAt <= NOW)
            readable_str = a.get("readableAt") or ""
            try:
                readable_dt = datetime.fromisoformat(readable_str.replace("Z", "+00:00"))
                if readable_dt > now:
                    continue
            except Exception:
                continue
            
            # Находим manga_id
            manga_id = None
            for rel in ch.get("relationships", []) or []:
                if rel.get("type") == "manga":
                    manga_id = rel.get("id")
                    break
            
            if not manga_id:
                continue
            
            valid_chapters.append({
                "chapter_id": ch.get("id"),
                "chapter_num": a.get("chapter") or "?",
                "chapter_title": a.get("title") or "",
                "readable_at": readable_str,
                "pages": a.get("pages") or 0,
                "manga_id": manga_id,
            })
            manga_ids.add(manga_id)
            
            if len(valid_chapters) >= limit:
                break
        
        self.logger.info(f"Valid chapters: {len(valid_chapters)}, unique manga: {len(manga_ids)}")
        
        # Step 3: Batch fetch manga info
        manga_info = self._fetch_manga_batch(list(manga_ids))
        
        # Step 4: Merge into SourceItem
        items = []
        for ch in valid_chapters:
            info = manga_info.get(ch["manga_id"], {})
            
            title_name = info.get("title_ru") or info.get("title_en") or "Unknown"
            title_name_en = info.get("title_en") or ""
            cover_url = info.get("cover_url")
            
            # Chapter URL (MangaDex chapter page)
            chapter_url = f"https://mangadex.org/chapter/{ch['chapter_id']}"
            title_url = f"{self.TITLE_BASE}/{ch['manga_id']}"
            
            # Parse readable_at
            upload_date = None
            try:
                upload_date = datetime.fromisoformat(ch["readable_at"].replace("Z", "+00:00"))
            except Exception:
                pass
            
            items.append(SourceItem(
                source=self.get_source_name(),
                title_id=ch["manga_id"],
                title_name=title_name,
                title_name_en=title_name_en,
                title_slug=ch["manga_id"],
                chapter_number=ch["chapter_num"],
                chapter_id=ch["chapter_id"],
                chapter_url=chapter_url,
                title_url=title_url,
                cover_url=cover_url,
                upload_date=upload_date,
                is_new=False,
            ))
        
        self.logger.info(f"Created {len(items)} SourceItems from MangaDex")
        return items
    
    def _fetch_manga_batch(self, manga_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Batch fetch manga info (titles + covers).
        
        MangaDex supports up to 100 ids per request.
        """
        if not manga_ids:
            return {}
        
        result = {}
        
        # Batch in chunks of 100
        for i in range(0, len(manga_ids), 100):
            chunk = manga_ids[i:i+100]
            
            try:
                response = requests.get(
                    f"{self.BASE_URL}/manga",
                    params=[("ids[]", mid) for mid in chunk] + [("includes[]", "cover_art")],
                    headers=self.HEADERS,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                for manga in response.json().get("data", []):
                    manga_id = manga.get("id")
                    attrs = manga.get("attributes", {}) or {}
                    
                    # Titles
                    titles = attrs.get("title", {}) or {}
                    title_ru = titles.get("ru")
                    title_en = titles.get("en")
                    
                    # Fallback to altTitles
                    if not (title_ru or title_en):
                        for alt in attrs.get("altTitles", []) or []:
                            if isinstance(alt, dict):
                                title_ru = title_ru or alt.get("ru")
                                title_en = title_en or alt.get("en")
                    
                    # Cover
                    cover_file = None
                    for rel in manga.get("relationships", []) or []:
                        if rel.get("type") == "cover_art":
                            cover_file = self._safe_get(rel, "attributes", "fileName")
                            break
                    
                    cover_url = f"{self.COVER_BASE}/{manga_id}/{cover_file}.512.jpg" if cover_file else None
                    
                    result[manga_id] = {
                        "title_ru": title_ru,
                        "title_en": title_en,
                        "cover_url": cover_url,
                    }
            
            except Exception as e:
                self.logger.error(f"Failed to fetch manga batch: {e}")
                continue
        
        return result

    # ========== Sprint 22: New manga adapter interface ==========

    def _to_manga_item(self, item) -> "MangaItem":
        """Конвертирует SourceItem в MangaItem."""
        return MangaItem(
            external_id=item.chapter_id or item.title_id,
            title_external_id=item.title_id,
            title=item.title_name or "Unknown",
            chapter=item.chapter_number or "?",
            url=item.chapter_url or item.title_url,
            language="ru",
            source="mangadex",
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
