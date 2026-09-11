"""
Sprint 74.5: Telegram Alerts — уведомления о критических событиях reliability.

Отправляет сообщения в Telegram chat при:
- Circuit breaker OPEN (платформа недоступна)
- Channel auto-disabled (CONFIGURATION error)
- DLQ exhausted (self-healing исчерпал попытки)

Конфигурация через env:
- ALERT_TELEGRAM_BOT_TOKEN — токен бота для алертов
- ALERT_TELEGRAM_CHAT_ID — chat ID для отправки
- ALERT_ENABLED — включить отправку (по умолчанию false)
"""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def _is_alerts_enabled() -> bool:
    return os.getenv("ALERT_ENABLED", "false").lower() == "true"


def _get_alert_credentials() -> Optional[dict]:
    """Получить креденшелы для алертов из env. Возвращает None если не настроено."""
    token = os.getenv("ALERT_TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("ALERT_TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return None
    return {"bot_token": token, "chat_id": chat_id}


async def _send_telegram_message(bot_token: str, chat_id: str, text: str) -> bool:
    """Отправить сообщение в Telegram. Возвращает True если успешно."""
    try:
        import httpx

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            )
        return resp.status_code == 200 and resp.json().get("ok", False)
    except Exception as e:
        logger.error(f"Alert send failed: {e}")
        return False


async def send_alert(message: str) -> bool:
    """
    Отправить алерт в Telegram (если включено и настроено).
    Безопасно: при ошибке просто логирует, не ломает основной поток.
    """
    if not _is_alerts_enabled():
        return False

    creds = _get_alert_credentials()
    if not creds:
        logger.debug("Alerts disabled: no credentials configured")
        return False

    return await _send_telegram_message(creds["bot_token"], creds["chat_id"], message)


# --- Конкретные события ---

async def alert_breaker_opened(platform: str, failure_count: int, last_error: Optional[str] = None):
    """Circuit breaker открылся для платформы."""
    msg = (
        f"🔴 <b>Circuit Breaker OPEN</b>\n"
        f"Platform: <code>{platform}</code>\n"
        f"Consecutive failures: {failure_count}\n"
    )
    if last_error:
        msg += f"Last error: <code>{last_error[:200]}</code>"
    return await send_alert(msg)


async def alert_channel_disabled(channel_id: str, channel_name: str, error_msg: str):
    """Канал автоматически отключён при CONFIGURATION error."""
    msg = (
        f"⚠️ <b>Channel Auto-Disabled</b>\n"
        f"Channel: <code>{channel_name}</code> ({channel_id})\n"
        f"Reason: <code>{error_msg[:200]}</code>\n"
        f"Action required: fix credentials / check platform settings"
    )
    return await send_alert(msg)


async def alert_dlq_exhausted(failure_id: str, channel_id: str, attempts: int):
    """Self-healing исчерпал попытки — запись DLQ требует ручного вмешательства."""
    msg = (
        f"🟠 <b>DLQ Exhausted</b>\n"
        f"Failure ID: <code>{failure_id}</code>\n"
        f"Channel: <code>{channel_id}</code>\n"
        f"Self-healing attempts: {attempts}\n"
        f"Action required: manual fix or resolve via API"
    )
    return await send_alert(msg)
