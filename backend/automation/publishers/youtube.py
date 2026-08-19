"""YouTube Publisher (stub)."""
from .base import PublisherInterface, PublishResult
from typing import Any
import logging

logger = logging.getLogger(__name__)


class YouTubePublisher(PublisherInterface):
    """Publisher для YouTube (stub)."""
    
    @property
    def platform_name(self) -> str:
        return "youtube"
    
    def validate_credentials(self, credentials: dict) -> bool:
        logger.warning("YouTube Publisher is not implemented yet")
        return False
    
    def publish(self, text: str, credentials: dict, channel: Any = None, **kwargs) -> PublishResult:
        return PublishResult(
            success=False,
            error="YouTube Publisher is not implemented yet"
        )