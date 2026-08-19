"""Notification Engine - sends alerts via Telegram.

Sprint 12. Architecture rule: engines never access the database.
Credentials are passed explicitly (from env or from MonitoringJob).
"""
import logging
from typing import Optional

from engines.telegram.publisher import TelegramPublisher

logger = logging.getLogger(__name__)


class NotificationEngine:
    """Sends alert messages to a Telegram chat."""

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send(self, text: str) -> Optional[int]:
        """Send alert. Returns message_id or None on failure."""
        try:
            publisher = TelegramPublisher(
                bot_token=self.bot_token,
                chat_id=self.chat_id,
            )
            result = publisher.publish(text)
            logger.info("Alert sent message_id=%s", result["message_id"])
            return result["message_id"]
        except Exception as e:
            logger.error("Failed to send alert: %s", e)
            return None