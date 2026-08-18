"""Telegram platform publisher - адаптер над TelegramPublisher."""
import logging
from typing import Any, Dict

from engines.telegram.publisher import TelegramPublisher

from .base_publisher import BasePublisher
from .publication import Publication

logger = logging.getLogger(__name__)


class TelegramPlatformPublisher(BasePublisher):
    platform = "telegram"

    def __init__(self, bot_token: str, chat_id: str):
        self._inner = TelegramPublisher(bot_token, chat_id)

    def publish(self, publication: Publication) -> Dict[str, Any]:
        buttons = [{"text": b.text, "url": b.url} for b in publication.buttons] or None

        # Проверяем наличие image_bytes в metadata (для news с проблемными URL)
        image_bytes = publication.metadata.get("_image_bytes")
        
        if publication.image_url:
            # Если есть скачанные bytes, отправляем их напрямую через sendPhoto
            if image_bytes:
                return self._publish_photo_bytes(
                    text=publication.text,
                    image_bytes=image_bytes,
                    inline_buttons=buttons,
                )
            
            # Иначе используем URL (для manga/anime covers с расширением)
            return self._inner.publish_photo(
                text=publication.text,
                image_url=publication.image_url,
                inline_buttons=buttons,
            )

        # Fallback: текстовое сообщение
        return self._inner.publish(
            text=publication.text,
            inline_buttons=buttons,
        )
    
    def _publish_photo_bytes(
        self,
        text: str,
        image_bytes: bytes,
        inline_buttons=None,
    ) -> Dict[str, Any]:
        """Отправляет фото из bytes (для news URL без расширения)."""
        import json
        import os
        from engines.telegram.rate_limiter import TelegramRateLimiter
        
        clean_text = text[:1021] + "..." if len(text) > 1024 else text
        
        payload = {
            "chat_id": self._inner.chat_id,
            "caption": clean_text,
        }
        
        if inline_buttons:
            keyboard = {"inline_keyboard": [[{"text": b["text"], "url": b["url"]}] for b in inline_buttons]}
            payload["reply_markup"] = json.dumps(keyboard, ensure_ascii=False)
        
        files = {"photo": ("cover.jpg", image_bytes, "image/jpeg")}
        
        data = self._inner._send_with_retry("sendPhoto", payload, files=files)
        
        if data and data.get("ok"):
            return {
                "status": "success",
                "message_id": data["result"]["message_id"],
                "chat_id": self._inner.chat_id,
            }
        
        # Fallback на text
        return self._inner.publish(text=text, inline_buttons=inline_buttons)