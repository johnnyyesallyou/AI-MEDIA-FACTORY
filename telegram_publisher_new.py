"""Telegram Publisher."""
from .base import PublisherInterface, PublishResult
from engines.telegram.engine import TelegramEngine
from datetime import datetime
from typing import Any
import logging


logger = logging.getLogger(__name__)


class TelegramPublisher(PublisherInterface):
    """Publisher для Telegram."""

    def __init__(self):
        self.engine = TelegramEngine()

    @property
    def platform_name(self) -> str:
        return "telegram"

    def validate_credentials(self, credentials: dict) -> bool:
        """Проверяет что есть bot_token и chat_id."""
        return bool(
            credentials.get("bot_token") and
            credentials.get("chat_id")
        )

    def publish(
        self,
        text: str,
        credentials: dict,
        channel: Any = None,
        **kwargs
    ) -> PublishResult:
        """Публикует текст в Telegram (с поддержкой картинок)."""

        if not self.validate_credentials(credentials):
            return PublishResult(
                success=False,
                error="Missing bot_token or chat_id"
            )

        # Sprint 11: поддержка картинок через image_url
        image_url = kwargs.get('image_url')
        
        try:
            if image_url:
                # Публикуем с картинкой через sendPhoto
                logger.info(f"Publishing with image: {image_url[:80]}...")
                result = self.engine.publish_photo(
                    text=text,
                    image_url=image_url,
                    bot_token=credentials["bot_token"],
                    chat_id=credentials["chat_id"]
                )
            else:
                # Обычная публикация текстом
                result = self.engine.publish(
                    text=text,
                    bot_token=credentials["bot_token"],
                    chat_id=credentials["chat_id"]
                )

            return PublishResult(
                success=True,
                message_id=str(result.message_id),
                published_at=result.published_at,
                platform_data={
                    "telegram_message_id": result.message_id,
                    "has_image": bool(image_url)
                }
            )

        except Exception as e:
            logger.error(f"Telegram publish failed: {e}")
            return PublishResult(
                success=False,
                error=str(e)
            )