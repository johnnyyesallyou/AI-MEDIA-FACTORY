"""Manga Adapter Registry - единая точка доступа ко всем manga источникам.

Sprint 22: Manga Sources Expansion

Usage:
    from engines.source_adapters.manga_registry import MangaRegistry
    
    # Все источники сразу
    all_items = MangaRegistry.fetch_all(limit=20)
    
    # Только конкретный источник
    remanga_items = MangaRegistry.fetch_from("remanga", limit=20)
    
    # Все доступные источники
    sources = MangaRegistry.available_sources()
"""
import logging
from typing import List, Optional, Dict

from .base_manga_adapter import BaseMangaAdapter, MangaItem
from .remanga_adapter import ReMangaAdapter
from .mangadex_adapter import MangaDexAdapter
from .readmanga_adapter import ReadMangaAdapter

logger = logging.getLogger(__name__)


class MangaRegistry:
    """Реестр manga адаптеров."""
    
    _adapters: Dict[str, BaseMangaAdapter] = {
        "remanga": ReMangaAdapter(),
        "mangadex": MangaDexAdapter(),
        "readmanga": ReadMangaAdapter(),
    }
    
    @classmethod
    def available_sources(cls) -> List[str]:
        """Список доступных источников."""
        return list(cls._adapters.keys())
    
    @classmethod
    def get_adapter(cls, source: str) -> Optional[BaseMangaAdapter]:
        """Получить адаптер по имени источника."""
        return cls._adapters.get(source)
    
    @classmethod
    def register(cls, source: str, adapter: BaseMangaAdapter):
        """Зарегистрировать новый адаптер."""
        cls._adapters[source] = adapter
        logger.info(f"Registered new manga adapter: {source}")
    
    @classmethod
    def fetch_from(cls, source: str, limit: int = 20) -> List[MangaItem]:
        """Загружает главы из конкретного источника."""
        adapter = cls._adapters.get(source)
        if not adapter:
            logger.warning(f"Unknown source: {source}")
            return []
        
        try:
            items = adapter.fetch_latest_chapters_manga(limit=limit)
            logger.info(f"Fetched {len(items)} items from {source}")
            return items
        except Exception as e:
            logger.error(f"Failed to fetch from {source}: {e}")
            return []
    
    @classmethod
    def fetch_all(
        cls,
        limit: int = 20,
        sources: Optional[List[str]] = None,
    ) -> List[MangaItem]:
        """
        Загружает главы со всех (или указанных) источников.
        
        Args:
            limit: лимит на каждый источник
            sources: список источников (None = все)
        
        Returns:
            Общий список MangaItem со всех источников
        """
        sources = sources or cls.available_sources()
        all_items: List[MangaItem] = []
        
        for source in sources:
            items = cls.fetch_from(source, limit=limit)
            all_items.extend(items)
        
        logger.info(f"Total fetched: {len(all_items)} items from {len(sources)} sources")
        return all_items
    
    @classmethod
    def fetch_with_dedup(
        cls,
        limit: int = 20,
        sources: Optional[List[str]] = None,
    ) -> List[MangaItem]:
        """
        Загружает главы с дедупликацией по external_id.
        
        Если одна глава пришла из нескольких источников, берёт первую.
        """
        items = cls.fetch_all(limit=limit, sources=sources)
        
        seen_ids = set()
        unique_items = []
        for item in items:
            key = (item.source, item.external_id)
            if key not in seen_ids:
                seen_ids.add(key)
                unique_items.append(item)
        
        logger.info(f"Dedup: {len(items)} -> {len(unique_items)} unique items")
        return unique_items