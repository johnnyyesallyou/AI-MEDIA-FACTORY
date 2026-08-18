"""Base Source Adapter for manga chapter tracking."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class SourceItem:
    """
    Unified representation of a manga chapter from any source.
    """
    source: str
    title_id: str
    title_name: str
    title_name_en: Optional[str] = None
    title_slug: Optional[str] = None
    chapter_number: Optional[str] = None
    chapter_id: Optional[str] = None
    chapter_url: Optional[str] = None
    title_url: Optional[str] = None
    cover_url: Optional[str] = None
    upload_date: Optional[datetime] = None
    is_new: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "title_id": self.title_id,
            "title_name": self.title_name,
            "title_name_en": self.title_name_en,
            "title_slug": self.title_slug,
            "chapter_number": self.chapter_number,
            "chapter_id": self.chapter_id,
            "chapter_url": self.chapter_url,
            "title_url": self.title_url,
            "cover_url": self.cover_url,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "is_new": self.is_new,
        }


class BaseSourceAdapter(ABC):
    """
    Abstract base class for all manga source adapters.
    Adapters are stateless (no DB access).
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def fetch_latest_chapters(self, limit: int = 20) -> List[SourceItem]:
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        pass

    def test_connection(self) -> bool:
        try:
            items = self.fetch_latest_chapters(limit=1)
            return len(items) > 0
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
