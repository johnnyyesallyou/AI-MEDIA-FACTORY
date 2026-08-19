"""Telegram Publisher v2 - с inline-кнопками и rate limiter."""

import re
import os
import time
import logging
from typing import Optional, List, Dict

import requests

from engines.telegram.rate_limiter import TelegramRateLimiter

logger = logging.getLogger(__name__)


def _strip_markdown(text: str) -> str:
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    return text.strip()


class TelegramPublisher:
    """Telegram Bot API Publisher v2 с inline-кнопками и rate limiter."""

    API_URL = "https://api.telegram.org/bot{token}/{method}"

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.rate_limiter = TelegramRateLimiter(min_interval=2.5, max_per_minute=25)

    def _url(self, method: str) -> str:
        return self.API_URL.format(token=self.bot_token, method=method)

    def _build_inline_keyboard(self, buttons: List[Dict[str, str]]) -> Optional[Dict]:
        """
        Строит inline keyboard из списка кнопок.
        
        Args:
            buttons: список {"text": "...", "url": "..."}
        
        Returns:
            Dict для Telegram reply_markup
        """
        if not buttons:
            return None
        
        # Каждая кнопка - отдельный ряд
        rows = [[{"text": b["text"], "url": b["url"]}] for b in buttons if b.get("url")]
        
        if not rows:
            return None
        
        return {
            "inline_keyboard": rows
        }

    def _send_with_retry(self, method: str, payload: Dict, files=None, max_retries: int = 3):
        """Универсальная отправка с rate limiting и retry на 429."""
        for attempt in range(max_retries):
            self.rate_limiter.wait()
            
            try:
                if files:
                    response = requests.post(
                        self._url(method), 
                        data=payload, 
                        files=files, 
                        timeout=60
                    )
                else:
                    response = requests.post(
                        self._url(method),
                        json=payload,
                        timeout=30
                    )
                
                data = response.json()
                
                if data.get("ok"):
                    return data
                
                error_code = data.get("error_code")
                if error_code == 429:
                    retry_after = data.get("parameters", {}).get("retry_after", 10)
                    self.rate_limiter.handle_429(retry_after)
                    continue
                
                logger.error(f"Telegram error: code={error_code}, desc={data.get('description')}")
                return data
            
            except Exception as e:
                logger.warning(f"Attempt {attempt+1} failed: {e}")
                time.sleep(2 ** attempt)
        
        return None

    def publish_photo(
        self,
        text: str,
        image_url: str,
        inline_buttons: Optional[List[Dict[str, str]]] = None
    ) -> dict:
        """
        Публикует пост с картинкой и inline-кнопками.
        
        Sprint 19: добавлены inline-кнопки и rate limiter.
        """
        clean_text = _strip_markdown(text)
        if len(clean_text) > 1024:
            clean_text = clean_text[:1021] + "..."

        payload = {
            "chat_id": self.chat_id,
            "caption": clean_text,
        }

        # Inline keyboard
        keyboard = self._build_inline_keyboard(inline_buttons or [])
        if keyboard:
            import json
            payload["reply_markup"] = json.dumps(keyboard, ensure_ascii=False)

        try:
            if self._is_local_path(image_url):
                file_path = image_url if image_url.startswith("/app") else f"/app{image_url}"
                
                if not os.path.exists(file_path):
                    logger.error(f"File not found: {file_path}")
                    return self.publish(text, inline_buttons)
                
                with open(file_path, "rb") as f:
                    files = {"photo": (os.path.basename(file_path), f, "image/webp")}
                    data = self._send_with_retry("sendPhoto", payload, files=files)
            else:
                payload["photo"] = image_url
                data = self._send_with_retry("sendPhoto", payload)
            
            if data and data.get("ok"):
                message_id = data["result"]["message_id"]
                logger.info(f"Photo sent: message_id={message_id}")
                return {
                    "status": "success",
                    "message_id": message_id,
                    "chat_id": self.chat_id,
                    "text_length": len(clean_text)
                }
            
            logger.warning("sendPhoto failed, fallback to text")
            return self.publish(text, inline_buttons)
        
        except Exception as e:
            logger.error(f"publish_photo error: {e}")
            return self.publish(text, inline_buttons)

    def publish(self, text: str, inline_buttons: Optional[List[Dict[str, str]]] = None) -> dict:
        """Отправляет текстовое сообщение с опциональными inline-кнопками."""
        clean_text = _strip_markdown(text)
        if not clean_text:
            return {"status": "error", "error": "Empty text"}

        payload = {
            "chat_id": self.chat_id,
            "text": clean_text,
            "parse_mode": "HTML"
        }

        keyboard = self._build_inline_keyboard(inline_buttons or [])
        if keyboard:
            import json
            payload["reply_markup"] = json.dumps(keyboard, ensure_ascii=False)

        data = self._send_with_retry("sendMessage", payload)
        
        if data and data.get("ok"):
            return {
                "status": "success",
                "message_id": data["result"]["message_id"],
                "chat_id": self.chat_id
            }
        
        return {"status": "error", "error": "Failed to send"}

    def _is_local_path(self, image_url: str) -> bool:
        return image_url.startswith("/assets/") or image_url.startswith("/app/assets/")