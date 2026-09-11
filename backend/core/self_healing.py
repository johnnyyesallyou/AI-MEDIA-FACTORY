"""
Sprint 74.2: Self-Healing Worker — автоматическая переотправка постов из DLQ.

Периодически берёт due_for_retry() записи из DeadLetterQueue и повторяет
публикацию без регенерации контента (content payload из DLQ):
- telegram: content {"platform": "telegram", "chat_id": ..., "text": ...,
                     optional "photo_url"} — TelegramPublisher
- vk:       content {"platform": "vk", ...} — publish_to_vk

Respect'ит reliability-механизмы Sprint 74.2:
- circuit breaker платформы открыт → запись остаётся в DLQ
- канал на паузе (429) → запись остаётся в DLQ

Успех → mark_resolved("self_healing"); неудача → retry_at = now + backoff.
"""
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from backend.core.dead_letter import DeadLetterQueue, get_dlq
from backend.core.reliability import (
    get_breaker,
    channel_paused,
    CircuitOpenError,
    ChannelPausedError,
)

logger = logging.getLogger(__name__)

# Backoff между self-healing попытками одной записи (секунды)
SELF_HEALING_BACKOFF_SECONDS = 900.0
# Максимальное число self-healing попыток на запись
SELF_HEALING_MAX_ATTEMPTS = 5


class SelfHealingWorker:
    """Self-healing: периодический re-publish постов из DLQ."""

    def __init__(self, db=None, interval: float = 300.0):
        self._db = db
        self.interval = interval
        self.last_run_summary: Optional[Dict[str, Any]] = None
        self._running = False

    # ------------------------------------------------------------------
    # Publish helpers
    # ------------------------------------------------------------------
    async def _republish_telegram(self, content: Dict[str, Any], bot_token: str) -> bool:
        from backend.engines.telegram_publisher import TelegramPublisher

        chat_id = content.get("chat_id")
        if not chat_id or not bot_token:
            logger.warning("Self-healing telegram: missing chat_id/bot_token — skip")
            return False
        publisher = TelegramPublisher(bot_token, chat_id)
        photo_url = content.get("photo_url")
        if photo_url:
            result = await publisher.send_photo(
                photo_url, caption=content.get("text", ""),
                parse_mode=content.get("parse_mode", "HTML"),
            )
        else:
            result = await publisher.send_message(
                content.get("text", ""),
                parse_mode=content.get("parse_mode", "HTML"),
            )
        return bool(result.get("success"))

    async def _republish_vk(self, content: Dict[str, Any]) -> bool:
        from backend.engines.vk_publisher import publish_to_vk

        group_id = content.get("vk_group_id") or content.get("group_id")
        token = content.get("vk_access_token")
        if not group_id or not token:
            logger.warning("Self-healing vk: missing group_id/token — skip")
            return False
        post = {
            "title": content.get("title", ""),
            "content": content.get("text", ""),
            "url": content.get("url", ""),
        }
        post_id = await publish_to_vk(post, group_id, token)
        return post_id is not None

    def _resolve_bot_token(self, failure) -> Optional[str]:
        """Токен бота: из content payload или из ChannelORM по chat_id/id."""
        content = (failure.context or {}).get("content", {}) \
            if isinstance(failure.context, dict) else {}
        if content.get("bot_token"):
            return content["bot_token"]
        try:
            from core.models.channel_orm import ChannelORM
            from core.database import SessionLocal

            db = SessionLocal()
            try:
                ch = db.query(ChannelORM).filter(
                    ChannelORM.id == failure.channel_id
                ).first()
                if ch is None:
                    ch = db.query(ChannelORM).filter(
                        ChannelORM.chat_id == content.get("chat_id")
                    ).first()
                return ch.bot_token if ch else None
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Self-healing: bot_token lookup failed: {e}")
            return None

    async def _process_one(self, dlq: DeadLetterQueue, failure) -> str:
        """Переотправка одной записи. Возвращает 'success'|'retry'|'skip'."""
        content = (failure.context or {}).get("content", {}) \
            if isinstance(failure.context, dict) else {}
        platform = content.get("platform") or (
            "vk" if "vk" in (failure.job or "").lower() else "telegram"
        )

        # Reliability guards: не долбим API, если breaker открыт или канал на паузе
        breaker = get_breaker(platform)
        if not breaker.is_available():
            logger.info(
                f"Self-healing skip {failure.id}: circuit breaker {platform} "
                f"is {breaker.state}"
            )
            return "skip"
        if channel_paused(failure.channel_id) > 0:
            logger.info(f"Self-healing skip {failure.id}: channel on rate-limit pause")
            return "skip"

        # Лимит self-healing попыток
        if (failure.attempt or 0) >= SELF_HEALING_MAX_ATTEMPTS:
            logger.warning(
                f"Self-healing: {failure.id} reached max attempts — resolve as exhausted"
            )
            dlq.mark_resolved(failure.id, resolution="self_healing_exhausted")
            # Sprint 74.5: Telegram alert при исчерпании (fire-and-forget)
            try:
                from backend.core.alerts import send_alert
                import threading
                msg = (
                    f"🟠 <b>DLQ Exhausted</b>\n"
                    f"Failure ID: <code>{failure.id}</code>\n"
                    f"Channel: <code>{failure.channel_id}</code>\n"
                    f"Self-healing attempts: {failure.attempt or 0}"
                )
                threading.Thread(
                    target=lambda: __import__("asyncio").run(send_alert(msg)),
                    daemon=True,
                ).start()
            except Exception:  # pragma: no cover
                pass
            return "success"

        try:
            if platform == "vk":
                ok = await self._republish_vk(content)
            else:
                bot_token = self._resolve_bot_token(failure)
                ok = await self._republish_telegram(content, bot_token or "")
        except (CircuitOpenError, ChannelPausedError) as e:
            logger.info(f"Self-healing skip {failure.id}: {e}")
            return "skip"
        except Exception as e:
            logger.error(f"Self-healing republish failed for {failure.id}: {e}")
            ok = False

        if ok:
            dlq.mark_resolved(failure.id, resolution="self_healing")
            logger.info(f"Self-healing: {failure.id} republished successfully")
            return "success"

        # Неудача: отложить (backoff), increment attempt
        failure.attempt = (failure.attempt or 0) + 1
        failure.retry_at = datetime.utcnow() + timedelta(
            seconds=SELF_HEALING_BACKOFF_SECONDS
        )
        dlq.db.commit()
        return "retry"

    async def run_once(self, limit: int = 10) -> Dict[str, Any]:
        """Один проход self-healing: обработать все due записи."""
        dlq = DeadLetterQueue(self._db) if self._db is not None else get_dlq()
        summary: Dict[str, Any] = {
            "ran_at": datetime.utcnow().isoformat(),
            "processed": 0, "success": 0, "retry": 0, "skip": 0,
        }
        try:
            due = dlq.due_for_retry(limit=limit)
            for failure in due:
                outcome = await self._process_one(dlq, failure)
                summary[outcome] = summary.get(outcome, 0) + 1
            summary["processed"] = len(due)
        finally:
            dlq.close()
        self.last_run_summary = summary
        logger.info(f"Self-healing run: {summary}")
        return summary

    async def run_forever(self) -> None:
        """Периодический self-healing loop (фоновая задача)."""
        self._running = True
        logger.info(f"Self-healing worker started (interval={self.interval}s)")
        while self._running:
            try:
                await self.run_once()
            except Exception as e:
                logger.error(f"Self-healing run failed: {e}")
            await asyncio.sleep(self.interval)

    def stop(self) -> None:
        self._running = False


# Глобальный worker (для API и фоновой задачи)
_worker: Optional[SelfHealingWorker] = None


def get_self_healing_worker(interval: float = 300.0) -> SelfHealingWorker:
    global _worker
    if _worker is None:
        _worker = SelfHealingWorker(interval=interval)
    return _worker
