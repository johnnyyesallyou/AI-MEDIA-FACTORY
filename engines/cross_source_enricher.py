"""Cross-source Enricher - Sprint 30.5 (source-aware).

Обогащает MangaTitle из всех доступных источников.
Ключевое улучшение: определяет источник по slug формату.

ReManga slug: URL-safe (one-piece, attack-on-titan)
ReadManga slug: числовой ID (34223) или транслит с underscore (v_komande_geroia_...)
MangaDex: UUID в external_ids
"""
import logging
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup

from core.models.manga_knowledge import MangaTitle
from engines.source_adapters.remanga_adapter import ReMangaAdapter
from engines.source_adapters.readmanga_adapter import ReadMangaAdapter

logger = logging.getLogger(__name__)


class CrossSourceEnricher:
    """Обогащает MangaTitle из всех доступных источников."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.remanga_adapter = ReMangaAdapter()
        self.readmanga_adapter = ReadMangaAdapter()

    def enrich(self, manga_title: MangaTitle) -> None:
        """Обогащает MangaTitle из всех доступных источников."""
        
        # Определяем, какие источники доступны для этого тайтла
        available_sources = self._get_available_sources(manga_title)
        
        if not available_sources:
            self.logger.debug(f"No sources available for {manga_title.title[:50]}")
            return
        
        # Обогащаем из каждого доступного источника
        for source in available_sources:
            try:
                self._enrich_from_source(manga_title, source)
            except Exception as e:
                self.logger.warning(f"Enrichment from {source} failed for {manga_title.title[:50]}: {e}")
        
        # Merge данных из всех источников
        self._merge_sources_data(manga_title)

    def _get_available_sources(self, manga_title: MangaTitle) -> List[str]:
        """Определяет, из каких источников можно обогащать этот тайтл."""
        available = []
        
        # Если есть title_slug
        if manga_title.title_slug:
            if self._is_readmanga_slug(manga_title.title_slug):
                available.append("readmanga")
            else:
                available.append("remanga")
        
        # Если есть external_ids для MangaDex
        if "mangadex" in (manga_title.external_ids or {}):
            available.append("mangadex")
        
        return available

    def _is_readmanga_slug(self, slug: str) -> bool:
        """
        Проверяет, является ли slug ReadManga форматом.
        
        ReadManga: числовой ID (34223) или транслит с underscore
        ReManga: URL-safe slug без underscore (one-piece)
        """
        return slug.isdigit() or "_" in slug

    def _enrich_from_source(self, manga_title: MangaTitle, source: str) -> None:
        """Обогащает из конкретного источника."""
        if source == "remanga":
            self._enrich_from_remanga(manga_title)
        elif source == "mangadex":
            self._enrich_from_mangadex(manga_title)
        elif source == "readmanga":
            self._enrich_from_readmanga(manga_title)

    def _enrich_from_remanga(self, manga_title: MangaTitle) -> None:
        """Обогащает из ReManga API."""
        if not manga_title.title_slug:
            return
        
        info = self.remanga_adapter.get_title_info(manga_title.title_slug)
        if not info:
            return
        
        # Сохраняем данные в sources_data
        if not manga_title.sources_data:
            manga_title.sources_data = {}
        
        manga_title.sources_data["remanga"] = {
            "description": info.get("description"),
            "genres": info.get("genres", []),
            "cover_url": info.get("cover_url"),
        }

    def _enrich_from_mangadex(self, manga_title: MangaTitle) -> None:
        """Обогащает из MangaDex API."""
        mangadex_id = (manga_title.external_ids or {}).get("mangadex")
        if not mangadex_id:
            return
        
        # TODO: Реализовать MangaDex API enrichment
        # Пока пропускаем
        pass

    def _enrich_from_readmanga(self, manga_title: MangaTitle) -> None:
        """Обогащает из ReadManga."""
        if not manga_title.title_slug:
            return
        
        info = self.readmanga_adapter.get_title_info(manga_title.title_slug)
        if not info:
            return
        
        # Сохраняем данные в sources_data
        if not manga_title.sources_data:
            manga_title.sources_data = {}
        
        manga_title.sources_data["readmanga"] = {
            "description": info.get("description"),
            "genres": info.get("genres", []),
            "cover_url": info.get("cover_url"),
        }


    def _build_sources_data(self, manga_title) -> dict:
        """
        Строит sources_data из уже обогащённого manga_title.
        Вызывается из manga_research_job для обратной совместимости.
        """
        sources_data = {}
        
        # Если уже есть sources_data, возвращаем его
        if manga_title.sources_data:
            return manga_title.sources_data
        
        # Иначе строим из description/genres/cover
        if manga_title.description or manga_title.genres or manga_title.cover_url:
            # Определяем источник по slug
            if manga_title.title_slug:
                if self._is_readmanga_slug(manga_title.title_slug):
                    source = "readmanga"
                else:
                    source = "remanga"
                
                sources_data[source] = {
                    "description": manga_title.description,
                    "genres": manga_title.genres or [],
                    "cover_url": manga_title.cover_url,
                }
        
        return sources_data

    def _merge_sources_data(self, manga_title: MangaTitle) -> None:
        """Объединяет данные из всех источников."""
        if not manga_title.sources_data:
            return
        
        # Приоритет источников: ReManga > MangaDex > ReadManga
        priority = ["remanga", "mangadex", "readmanga"]
        
        # Description
        if not manga_title.description:
            for source in priority:
                data = manga_title.sources_data.get(source, {})
                if data.get("description"):
                    manga_title.description = data["description"]
                    break
        
        # Genres
        if not manga_title.genres:
            for source in priority:
                data = manga_title.sources_data.get(source, {})
                if data.get("genres"):
                    manga_title.genres = data["genres"]
                    break
        
        # Cover
        if not manga_title.cover_url:
            for source in priority:
                data = manga_title.sources_data.get(source, {})
                if data.get("cover_url"):
                    manga_title.cover_url = data["cover_url"]
                    break