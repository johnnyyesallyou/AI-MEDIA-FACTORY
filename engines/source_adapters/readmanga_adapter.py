"""ReadManga.me adapter - Sprint 30.5 (correct selectors).

HTML структура:
- Description: <meta name="description">
- Genres: <a href="/list/genre/...">
- Cover: img с разумным размером (130x180+)
"""
import logging
import re
from datetime import datetime
from typing import List, Optional

import requests
from core.retry import retry_external_api
from bs4 import BeautifulSoup

from .base_manga_adapter import BaseMangaAdapter, MangaItem


class ReadMangaAdapter(BaseMangaAdapter):
    """Адаптер для readmanga.me (HTML парсинг)."""

    BASE_URL = "https://readmanga.me"
    HOME_URL = f"{BASE_URL}/"
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru,en;q=0.9",
    }
    
    # Паттерн URL: /slug/vol1/23 или /slug/vol14/68.3
    URL_PATTERN = re.compile(r"^/([^/]+)/vol(\d+)/(.+?)/?$")

    def __init__(self, timeout: int = 20):
        super().__init__()
        self.timeout = timeout

    @retry_external_api
    def fetch_latest_chapters(self, limit: int = 20) -> List[MangaItem]:
        """Загружает последние главы с главной страницы."""
        try:
            r = requests.get(self.HOME_URL, headers=self.HEADERS, timeout=self.timeout)
            r.raise_for_status()
            
            soup = BeautifulSoup(r.text, "html.parser")
            updates_div = soup.find("div", class_="feed-latest-updates")
            if not updates_div:
                self.logger.warning("feed-latest-updates container not found")
                return []
            
            chapter_links = updates_div.find_all("a", class_="chapter-link")
            self.logger.info(f"Found {len(chapter_links)} chapter links")
            
            items: List[MangaItem] = []
            for link in chapter_links[:limit]:
                item = self._parse_chapter_link(link)
                if item:
                    items.append(item)
            
            return items
        
        except Exception as e:
            self.logger.exception(f"ReadManga fetch failed: {e}")
            return []

    def _parse_chapter_link(self, link) -> Optional[MangaItem]:
        """Парсит ссылку на главу."""
        href = link.get("href", "")
        if not href:
            return None
        
        match = self.URL_PATTERN.match(href)
        if not match:
            self.logger.debug(f"URL pattern not matched: {href}")
            return None
        
        slug, volume, chapter_num = match.groups()
        parent_card = self._find_parent_item(link)
        
        title = "Unknown"
        cover_url = None
        
        if parent_card:
            title_elem = parent_card.find("h4") or parent_card.find(class_=lambda c: c and "inline-tile__content" in " ".join(c))
            if title_elem:
                h4 = title_elem.find("h4") if title_elem.name != "h4" else title_elem
                if h4:
                    title = h4.get_text(strip=True)
            
            img = parent_card.find("img")
            if img:
                cover_url = img.get("data-src") or img.get("src")
            
            if not cover_url:
                bg = parent_card.find(attrs={"data-background-image": True})
                if bg:
                    cover_url = bg.get("data-background-image")
        
        full_url = f"{self.BASE_URL}{href}" if href.startswith("/") else href
        
        return MangaItem(
            external_id=f"{slug}_v{volume}_c{chapter_num}",
            title=title,
            chapter=chapter_num,
            url=full_url,
            language="ru",
            source="readmanga",
            cover_url=cover_url,
            title_slug=slug,
            title_url=f"{self.BASE_URL}/{slug}",
            upload_date=None,
        )

    def _find_parent_item(self, element):
        """Находит родительский div.feed-latest-updates-item."""
        parent = element.parent
        for _ in range(15):
            if parent is None:
                return None
            classes = parent.get("class", []) if hasattr(parent, "get") else []
            if "feed-latest-updates-item" in classes and "feed-latest-updates-item__footer" not in classes:
                return parent
            parent = parent.parent
        return None

    @retry_external_api
    def get_title_info(self, slug: str) -> Optional[dict]:
        """
        Загружает информацию о тайтле из ReadManga.
        
        Args:
            slug: ReadManga slug (числовой ID или транслит)
        
        Returns:
            dict с title, description, genres, cover_url
        """
        try:
            url = f"{self.BASE_URL}/{slug}"
            r = requests.get(url, headers=self.HEADERS, timeout=self.timeout)
            r.raise_for_status()
            
            soup = BeautifulSoup(r.text, "html.parser")
            
            # 1. Title — из <title> тега (убираем " — RM.me" суффикс)
            title_tag = soup.find("title")
            title = "Unknown"
            if title_tag:
                title_text = title_tag.get_text(strip=True)
                # Убираем " — RM.me" и "Манхва" префикс
                title = re.sub(r'\s*—\s*RM\.me.*$', '', title_text, flags=re.DOTALL)
                # Убираем префиксы типов контента
                title = re.sub(r'^(Манга|Манхва|Маньхуа|Комикс)\s+', '', title, flags=re.IGNORECASE)
                title = re.sub(r'\s*онлайн.*$', '', title, flags=re.IGNORECASE | re.DOTALL)
                # Убираем скобки с оригинальным названием если есть
                title = re.sub(r'\s*\([^)]*\)\s*', '', title)
                title = title.strip()
            
            # 2. Description — из meta[name="description"]
            description = ""
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc and meta_desc.get("content"):
                desc_raw = meta_desc["content"]
                # Убираем префикс "Описание манги X:"
                desc_raw = re.sub(r'^Описание\s*(?:манги|манхвы|маньхуа|комикса)?\s*[^:]*:\s*', '', desc_raw, flags=re.IGNORECASE)
                description = desc_raw.strip()
            
            # 3. Genres — из ссылок /list/genre/
            genres = []
            genre_links = soup.find_all("a", href=lambda h: h and "/list/genre/" in str(h))
            seen_genres = set()
            for a in genre_links:
                genre_text = a.get_text(strip=True)
                if genre_text and genre_text not in seen_genres:
                    genres.append(genre_text)
                    seen_genres.add(genre_text)
            
            # 4. Cover — ищем картинку разумного размера на странице тайтла
            cover_url = None
            
            # Стратегия 1: img внутри контейнера с cover в class
            cover_container = soup.find(class_=lambda c: c and "cover" in " ".join(c).lower())
            if cover_container:
                img = cover_container.find("img")
                if img:
                    cover_url = img.get("data-src") or img.get("src")
            
            # Стратегия 2: первая большая картинка (width >= 100, height >= 100)
            if not cover_url:
                for img in soup.find_all("img"):
                    src = img.get("data-src") or img.get("src")
                    if not src:
                        continue
                    # Пропускаем маленькие иконки и логотипы
                    if any(x in src for x in ["logo", "icon", "static/"]):
                        continue
                    width = img.get("width")
                    height = img.get("height")
                    try:
                        if width and height and int(width) >= 100 and int(height) >= 100:
                            cover_url = src
                            break
                    except (ValueError, TypeError):
                        pass
            
            # Стратегия 3: паттерн URL с pics/
            if not cover_url:
                for img in soup.find_all("img"):
                    src = img.get("data-src") or img.get("src")
                    if src and "/pics/" in src and "uploads" in src:
                        cover_url = src
                        break
            
            return {
                "title": title,
                "description": description,
                "genres": genres,
                "cover_url": cover_url,
            }
        except Exception as e:
            self.logger.warning(f"ReadManga get_title_info failed for {slug}: {e}")
            return None