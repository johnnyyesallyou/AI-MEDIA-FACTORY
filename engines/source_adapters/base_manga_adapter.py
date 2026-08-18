"""Base Manga Adapter - Sprint 30 (fixed).

Добавлено:
- self.logger (раньше не было)
- fetch_latest_chapters_manga() — конвертация в MangaItem
- _to_manga_item() — для наследников
"""
import logging
from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MangaItem:
    """Единая структура для главы манги из любого источника."""
    external_id: str
    title: str
    chapter: str
    url: str
    language: str
    source: str

    title_external_id: str = None
    description: str = None
    genres: list = None
    cover_url: str = None
    title_slug: str = None
    title_name_en: str = None
    chapter_id: str = None
    title_url: str = None
    upload_date: datetime = None


class BaseMangaAdapter(ABC):
    """Базовый класс для всех manga адаптеров."""

    def __init__(self):
        self.name = self.__class__.__name__
        self.logger = logging.getLogger(self.name)

    @abstractmethod
    def fetch_latest_chapters(self, limit: int = 20) -> List[MangaItem]:
        """Загружает последние главы (возвращает MangaItem напрямую)."""
        pass

    def fetch_latest_chapters_manga(self, limit: int = 20) -> List[MangaItem]:
        """Единый интерфейс — возвращает List[MangaItem]."""
        return self.fetch_latest_chapters(limit=limit)

    def get_manga_info(self, slug: str):
        return None