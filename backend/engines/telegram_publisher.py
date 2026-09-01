"""Sprint 69.5: TelegramPublisher — реальная отправка сообщений в Telegram."""
import logging
import asyncio
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class TelegramPublisher:
    """Отправляет сообщения в Telegram через Bot API."""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    async def send_message(self, text: str, parse_mode: str = "HTML") -> Dict[str, Any]:
        """
        Отправляет текстовое сообщение в канал.
        
        Args:
            text: текст сообщения
            parse_mode: "HTML" | "Markdown" | None
        
        Returns:
            {"success": bool, "message_id": int, "error": str}
        """
        # Sprint 69.6: rate limit — минимум 1 секунда между сообщениями
        await asyncio.sleep(1.0)
        
        try:
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": parse_mode,
            }
            
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("ok"):
                message_id = result.get("result", {}).get("message_id")
                logger.info(f"Message sent to {self.chat_id}: message_id={message_id}")
                return {"success": True, "message_id": message_id}
            else:
                error = result.get("description", "Unknown error")
                logger.error(f"Telegram API error: {error}")
                return {"success": False, "error": error}
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Telegram request failed: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_photo(self, photo_url: str, caption: str = "") -> Dict[str, Any]:
        """Отправляет фото с подписью."""
        try:
            payload = {
                "chat_id": self.chat_id,
                "photo": photo_url,
                "caption": caption,
            }
            
            response = requests.post(
                f"{self.base_url}/sendPhoto",
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("ok"):
                message_id = result.get("result", {}).get("message_id")
                logger.info(f"Photo sent to {self.chat_id}: message_id={message_id}")
                return {"success": True, "message_id": message_id}
            else:
                error = result.get("description", "Unknown error")
                logger.error(f"Telegram API error: {error}")
                return {"success": False, "error": error}
        
        except Exception as e:
            logger.error(f"Send photo failed: {e}")
            return {"success": False, "error": str(e)}