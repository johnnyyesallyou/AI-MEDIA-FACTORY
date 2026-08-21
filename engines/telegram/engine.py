import logging
from datetime import datetime

from .publisher import TelegramPublisher
from .models import TelegramPublishResult
from .exceptions import TelegramPublishError


logger = logging.getLogger(__name__)


class TelegramEngine:
    """
    Engine layer for Telegram publishing.
    Hides Telegram API implementation from automation layer.
    """

    def publish(self, text: str, bot_token: str, chat_id: str) -> TelegramPublishResult:
        try:
            publisher = TelegramPublisher(bot_token=bot_token, chat_id=chat_id)
            result = publisher.publish(text)
            return TelegramPublishResult(
                status=result["status"],
                message_id=result["message_id"],
                chat_id=result["chat_id"],
                published_at=datetime.utcnow(),
                text_length=result.get("text_length", len(text))
            )
        except Exception as e:
            logger.exception("Telegram publish failed")
            raise TelegramPublishError(str(e))

    def publish_photo(self, text: str, image_url: str, bot_token: str, chat_id: str) -> TelegramPublishResult:
        try:
            publisher = TelegramPublisher(bot_token=bot_token, chat_id=chat_id)
            result = publisher.publish_photo(text=text, image_url=image_url)
            return TelegramPublishResult(
                status=result["status"],
                message_id=result["message_id"],
                chat_id=result["chat_id"],
                published_at=datetime.utcnow(),
                text_length=result.get("text_length", len(text))
            )
        except Exception as e:
            logger.exception("Telegram publish_photo failed")
            raise TelegramPublishError(str(e))