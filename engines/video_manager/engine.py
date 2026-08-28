"""Video Manager - Sprint 59.

Бесплатные источники видео:
  1. Pexels API  (бесплатно, 200 req/hour) - опционально
  2. Pixabay API (бесплатно)               - основной
  3. Fallback: None -> пост с картинкой

Локальная AI-генерация НЕ используется (RTX 3050 Ti 4GB < 8GB минимум).
Runway ML НЕ используется (платный).
"""
import os
import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class VideoManager:
    """Поиск бесплатного видео по теме с fallback-цепочкой."""

    def __init__(self, pexels_key: str = None, pixabay_key: str = None):
        self.pexels_key = pexels_key or os.getenv("PEXELS_API_KEY")
        self.pixabay_key = pixabay_key or os.getenv("PIXABAY_API_KEY")

    def get_video(self, topic: str, timeout: int = 20) -> Optional[dict]:
        """Fallback chain: Pexels -> Pixabay -> None."""
        for searcher in (self.search_pexels, self.search_pixabay):
            try:
                video = searcher(topic, timeout=timeout)
                if video:
                    logger.info(f"Video found via {video['source']}: {topic}")
                    return video
            except Exception as e:
                logger.warning(f"{searcher.__name__} failed for '{topic}': {e}")
        logger.info(f"No video found for '{topic}' (will use image)")
        return None

    def search_pexels(self, topic: str, timeout: int = 20) -> Optional[dict]:
        if not self.pexels_key:
            return None
        resp = requests.get(
            "https://api.pexels.com/videos/search",
            headers={"Authorization": self.pexels_key},
            params={"query": topic, "per_page": 5, "orientation": "landscape"},
            timeout=timeout,
        )
        resp.raise_for_status()
        for video in resp.json().get("videos", []):
            files = [f for f in video.get("video_files", []) if "mp4" in (f.get("file_type") or "")]
            if not files:
                continue
            files = sorted(files, key=lambda f: f.get("width", 0))
            pick = next((f for f in reversed(files) if (f.get("width") or 0) <= 1280), files[0])
            if pick.get("link"):
                pics = video.get("video_pictures") or []
                return {
                    "url": pick["link"],
                    "type": "video",
                    "duration": video.get("duration"),
                    "source": "pexels",
                    "thumbnail": pics[0].get("picture") if pics else None,
                }
        return None

    def search_pixabay(self, topic: str, timeout: int = 20) -> Optional[dict]:
        if not self.pixabay_key:
            return None
        resp = requests.get(
            "https://pixabay.com/api/videos/",
            params={"key": self.pixabay_key, "q": topic, "per_page": 5},
            timeout=timeout,
        )
        resp.raise_for_status()
        for hit in resp.json().get("hits", []):
            videos = hit.get("videos") or {}
            medium = videos.get("medium") or videos.get("small") or videos.get("tiny")
            if medium and medium.get("url"):
                return {
                    "url": medium["url"],
                    "type": "video",
                    "duration": hit.get("duration"),
                    "source": "pixabay",
                    "thumbnail": None,
                }
        return None