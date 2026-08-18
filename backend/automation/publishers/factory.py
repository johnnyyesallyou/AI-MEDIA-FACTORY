"""Publisher Factory."""
from .base import PublisherInterface
from .telegram import TelegramPublisher
from .vk import VkPublisher
from .youtube import YouTubePublisher
from .dzen import DzenPublisher
import logging

logger = logging.getLogger(__name__)


class PublisherFactory:
    """Фабрика для создания publishers."""
    
    _publishers = {
        "telegram": TelegramPublisher,
        "vk": VkPublisher,
        "youtube": YouTubePublisher,
        "dzen": DzenPublisher,
    }
    
    @classmethod
    def get(cls, platform: str) -> PublisherInterface:
        platform_lower = (platform or "telegram").lower()
        
        if platform_lower not in cls._publishers:
            logger.warning(f"Unknown platform '{platform}', falling back to telegram")
            platform_lower = "telegram"
        
        publisher_class = cls._publishers[platform_lower]
        return publisher_class()
    
    @classmethod
    def supported_platforms(cls) -> list:
        return list(cls._publishers.keys())