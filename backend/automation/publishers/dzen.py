"""Dzen Publisher (stub)."""
from .base import PublisherInterface, PublishResult
from typing import Any
import logging

logger = logging.getLogger(__name__)


class DzenPublisher(PublisherInterface):
    """Publisher для Dzen (stub)."""
    
    @property
    def platform_name(self) -> str:
        return "dzen"
    
    def validate_credentials(self, credentials: dict) -> bool:
        logger.warning("Dzen Publisher is not implemented yet")
        return False
    
    def publish(self, text: str, credentials: dict, channel: Any = None, **kwargs) -> PublishResult:
        return PublishResult(
            success=False,
            error="Dzen Publisher is not implemented yet"
        )