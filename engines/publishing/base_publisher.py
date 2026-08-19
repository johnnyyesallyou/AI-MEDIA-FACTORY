"""Base Publisher - Sprint 25.2.

Контракт платформы: publish(Publication) -> result.
Publisher НЕ решает, какую картинку/текст поставить — только доставка.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict

from .publication import Publication


class BasePublisher(ABC):
    platform: str = "base"

    @abstractmethod
    def publish(self, publication: Publication) -> Dict[str, Any]:
        """Доставляет публикацию на платформу."""
        pass