"""Anime Registry - Sprint 31.

Единая точка доступа к anime источникам (AniList).
Аналог MangaRegistry для anime.
"""
import logging
from typing import List, Optional

from engines.source_adapters.anilist_adapter import AniListAdapter, AnimeItem

logger = logging.getLogger(__name__)


class AnimeRegistry:
    """Registry для anime источников."""
    
    @classmethod
    def available_sources(cls) -> List[str]:
        """Возвращает список доступных источников."""
        return ["anilist"]
    
    @classmethod
    def fetch_trending(cls, limit: int = 20, source: str = "anilist") -> List[AnimeItem]:
        """Загружает trending anime из источника."""
        if source == "anilist":
            adapter = AniListAdapter()
            return adapter.fetch_trending_anime(limit=limit)
        else:
            logger.warning(f"Unknown source: {source}")
            return []
    
    @classmethod
    def fetch_currently_airing(cls, limit: int = 20, source: str = "anilist") -> List[AnimeItem]:
        """Загружает currently airing anime из источника."""
        if source == "anilist":
            adapter = AniListAdapter()
            return adapter.fetch_currently_airing(limit=limit)
        else:
            logger.warning(f"Unknown source: {source}")
            return []
    
    @classmethod
    def get_anime_info(cls, anime_id: str, source: str = "anilist") -> Optional[AnimeItem]:
        """Получает информацию об anime по ID."""
        if source == "anilist":
            adapter = AniListAdapter()
            return adapter.get_anime_info(anime_id)
        else:
            logger.warning(f"Unknown source: {source}")
            return None