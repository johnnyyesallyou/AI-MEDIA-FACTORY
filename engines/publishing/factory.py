"""Publisher Factory - Sprint 28.

Единая точка создания publisher по каналу:
  channel.platform -> Telegram / VK

Research/Knowledge Layer НЕ знает о платформах —
платформу определяет канал.
"""
import logging

from engines.channel_profiles import resolve_channel_profile

from .base_publisher import BasePublisher
from .telegram_publisher_adapter import TelegramPlatformPublisher
from .vk_publisher import VKPlatformPublisher

logger = logging.getLogger(__name__)


def get_publisher_for_channel(channel) -> BasePublisher:
    """Возвращает publisher для канала по его платформе."""
    platform = (getattr(channel, "platform", "telegram") or "telegram").lower()

    if platform == "vk" and channel.vk_access_token and channel.vk_group_id:
        logger.info(f"Using VK publisher for channel: {channel.name}")
        return VKPlatformPublisher(channel.vk_access_token, channel.vk_group_id)

    if platform == "telegram" and channel.bot_token and channel.chat_id:
        return TelegramPlatformPublisher(channel.bot_token, channel.chat_id)

    # Fallback: telegram если есть токен, иначе ошибка
    if channel.bot_token and channel.chat_id:
        return TelegramPlatformPublisher(channel.bot_token, channel.chat_id)

    raise ValueError(f"No valid publisher config for channel: {channel.name}")