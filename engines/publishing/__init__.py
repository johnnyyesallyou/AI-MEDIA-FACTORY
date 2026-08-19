"""Publishing layer - normalized Publication + platform publishers."""
from .publication import Publication, PublicationButton
from .base_publisher import BasePublisher
from .telegram_publisher_adapter import TelegramPlatformPublisher
from .vk_publisher import VKPlatformPublisher
from .image_resolver import PublicationImageResolver
from .image_acquisition import ImageAcquisitionPolicy, AcquisitionResult
from .factory import get_publisher_for_channel

__all__ = [
    "Publication",
    "PublicationButton",
    "BasePublisher",
    "TelegramPlatformPublisher",
    "VKPlatformPublisher",
    "PublicationImageResolver",
    "ImageAcquisitionPolicy",
    "AcquisitionResult",
    "get_publisher_for_channel",
]