"""Publisher Abstraction Layer."""
from .base import PublisherInterface, PublishResult
from .factory import PublisherFactory
from .telegram import TelegramPublisher
from .vk import VkPublisher
from .youtube import YouTubePublisher
from .dzen import DzenPublisher

__all__ = [
    "PublisherInterface",
    "PublishResult",
    "PublisherFactory",
    "TelegramPublisher",
    "VkPublisher",
    "YouTubePublisher",
    "DzenPublisher",
]