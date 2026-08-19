"""Unsplash Adapter - Sprint 38.

Stock photos через Unsplash Search API.
Требует: UNSPLASH_ACCESS_KEY (https://unsplash.com/developers)
Без ключа — gracefully деградирует (available=False).
"""
import logging
import os
from typing import Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class UnsplashAdapter:
    """Поиск stock photos по запросу."""

    BASE_URL = "https://api.unsplash.com"
    TIMEOUT = 10

    def __init__(self, access_key: Optional[str] = None):
        self.access_key = access_key or os.getenv("UNSPLASH_ACCESS_KEY", "")
        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    def available(self) -> bool:
        return bool(self.access_key)

    def search(
        self,
        query: str,
        orientation: str = "landscape",
        limit: int = 5,
    ) -> List[Dict]:
        """Ищет фото. Возвращает [{url, width, height, alt}]."""
        if not self.available:
            return []

        try:
            r = requests.get(
                f"{self.BASE_URL}/search/photos",
                params={
                    "query": query,
                    "orientation": orientation,
                    "per_page": limit,
                },
                headers={"Authorization": f"Client-ID {self.access_key}"},
                timeout=self.TIMEOUT,
            )

            if r.status_code != 200:
                self.logger.warning(f"Unsplash search failed: {r.status_code}")
                return []

            results = []
            for photo in r.json().get("results", []):
                urls = photo.get("urls", {})
                results.append({
                    "url": urls.get("regular") or urls.get("raw"),
                    "thumb": urls.get("small"),
                    "width": photo.get("width"),
                    "height": photo.get("height"),
                    "alt": photo.get("alt_description") or "",
                })
            return results

        except Exception as e:
            self.logger.warning(f"Unsplash search error: {e}")
            return []

    def get_best_image(self, query: str) -> Optional[str]:
        """Возвращает URL лучшего фото или None."""
        results = self.search(query, limit=1)
        if results and results[0].get("url"):
            self.logger.info(f"Unsplash hit: {query[:40]}")
            return results[0]["url"]
        return None