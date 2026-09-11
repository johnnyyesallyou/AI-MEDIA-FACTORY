"""Sprint 69.20: TelegramPublisher — реальная отправка сообщений в Telegram с санитизацией.
Sprint 74.1: retry с exponential backoff для transient-ошибок (429/5xx/network)."""
import logging
import asyncio
import requests
from typing import Dict, Any, Optional
from backend.engines.html_sanitizer import sanitize_for_telegram, sanitize_keep_links
from backend.core.reliability import with_retry, get_policy

logger = logging.getLogger(__name__)


class TelegramPublisher:
    """Отправляет сообщения в Telegram через Bot API."""

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    def _post_sync(self, method: str, payload: dict) -> Dict[str, Any]:
        """Синхронный вызов Telegram Bot API. Raise при ошибке (для retry)."""
        response = requests.post(
            f"{self.base_url}/{method}",
            json=payload,
            timeout=30,
        )
        # 429/5xx → HTTPError с response → taxonomy: TRANSIENT (retry)
        # 400/401/403 → PERMANENT/CONFIGURATION (fail fast)
        response.raise_for_status()
        result = response.json()
        if not result.get("ok"):
            # Telegram возвращает HTTP 200 с ok=false
            error = result.get("description", "Unknown error")
            parameters = result.get("parameters") or {}
            retry_after = parameters.get("retry_after")
            if retry_after is not None:
                response.headers["Retry-After"] = str(retry_after)
            exc = requests.HTTPError(f"Telegram API error: {error}")
            exc.response = response
            raise exc
        return result

    async def _post(self, method: str, payload: dict) -> Dict[str, Any]:
        """
        Асинхронная обёртка с retry (telegram policy: 4 attempts, backoff 1-2-4-8s).
        Sprint 74.2: circuit breaker + channel-wide pause при 429 (Retry-After).
        """
        return await with_retry(
            self._post_sync, method, payload,
            policy=get_policy("telegram"),
            context=f"telegram.{method}",
            channel_id=self.chat_id,
            platform="telegram",
        )

    async def send_message(self, text: str, parse_mode: str = "HTML", reply_markup: dict = None, disable_web_page_preview: bool = False) -> Dict[str, Any]:
        """
        Отправляет текстовое сообщение в канал.

        Sprint 69.20: автоматически санитизирует текст от неподдерживаемого HTML.
        Sprint 74.4: при исчерпании retry → автозапись в DLQ (self-healing).

        Args:
            text: текст сообщения
            parse_mode: "HTML" | "Markdown" | None

        Returns:
            {"success": bool, "message_id": int, "error": str}
        """
        # Sprint 69.6: rate limit — минимум 1 секунда между сообщениями
        await asyncio.sleep(1.0)

        # Sprint 69.20: санитизация HTML перед отправкой
        if parse_mode == "HTML":
            original_len = len(text)
            text = sanitize_for_telegram(text)
            if len(text) != original_len:
                logger.debug(f"Text sanitized: {original_len} → {len(text)} chars")

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        if disable_web_page_preview:
            payload["disable_web_page_preview"] = True

        try:
            result = await self._post("sendMessage", payload)
            message_id = result.get("result", {}).get("message_id")
            logger.info(f"Message sent to {self.chat_id}: message_id={message_id}")
            return {"success": True, "message_id": message_id}

        except requests.exceptions.RequestException as e:
            logger.error(f"Telegram request failed after retries: {e}")
            self._enqueue_dlq(text, None, str(e))
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            self._enqueue_dlq(text, None, str(e))
            return {"success": False, "error": str(e)}

    def _enqueue_dlq(self, text: str, photo_url: Optional[str], error_message: str):
        """
        Sprint 74.4: автозапись в DLQ при исчерпании retry.
        Сохраняет content payload для self-healing (переотправка без регенерации).
        """
        try:
            from backend.core.dead_letter import get_dlq

            content: Dict[str, Any] = {
                "platform": "telegram",
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "HTML",
            }
            if photo_url:
                content["photo_url"] = photo_url

            dlq = get_dlq()
            try:
                failure = dlq.enqueue(
                    channel_id=self.chat_id,
                    pipeline="publishing",
                    job="publish_telegram",
                    error_message=error_message,
                    content_payload=content,
                    error_type="publish_error",
                    retry_delay_seconds=900.0,
                )
                logger.warning(
                    f"DLQ auto-enqueue (telegram): {failure.id} "
                    f"channel={self.chat_id} retry_at={failure.retry_at}"
                )
            finally:
                dlq.close()
        except Exception as e:  # pragma: no cover — защита основного потока
            logger.error(f"DLQ auto-enqueue failed (telegram): {e}")

    async def send_photo(self, photo_url: str, caption: str = "", parse_mode: str = "HTML") -> Dict[str, Any]:
        """Отправляет фото с подписью. Sprint 74.4: при исчерпании retry → DLQ."""
        # Sprint 69.20: санитизация caption
        if parse_mode == "HTML" and caption:
            caption = sanitize_for_telegram(caption)

        try:
            payload = {
                "chat_id": self.chat_id,
                "photo": photo_url,
                "caption": caption,
                "parse_mode": parse_mode,
            }

            result = await self._post("sendPhoto", payload)
            message_id = result.get("result", {}).get("message_id")
            logger.info(f"Photo sent to {self.chat_id}: message_id={message_id}")
            return {"success": True, "message_id": message_id}

        except Exception as e:
            logger.error(f"Send photo failed after retries: {e}")
            self._enqueue_dlq(caption, photo_url, str(e))
            return {"success": False, "error": str(e)}