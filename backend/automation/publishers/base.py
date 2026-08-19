"""
Publisher Abstraction Layer.
Универсальный интерфейс для публикации контента на разных платформах.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any
import logging


logger = logging.getLogger(__name__)


@dataclass
class PublishResult:
    """Результат публикации."""
    success: bool
    message_id: Optional[str] = None
    published_at: Optional[datetime] = None
    error: Optional[str] = None
    platform_data: Optional[dict] = None


class PublisherInterface(ABC):
    """Абстрактный базовый класс для publishers."""
    
    @abstractmethod
    def publish(
        self,
        text: str,
        credentials: dict,
        channel: Any = None,
        **kwargs
    ) -> PublishResult:
        pass
    
    @abstractmethod
    def validate_credentials(self, credentials: dict) -> bool:
        pass
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        pass