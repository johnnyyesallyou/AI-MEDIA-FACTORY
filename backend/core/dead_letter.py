"""
Sprint 74.1: Dead-Letter Queue для постов, у которых исчерпаны retry.

Реализован поверх таблицы pipeline_failures:
- enqueue(): публикация не удалась после всех попыток → запись в DLQ
            (resolved=False, retry_at=now + backoff, контент в context.content)
- list():    просмотр DLQ (для dashboard)
- requeue(): ручной/автоматический возврат в обработку (retry_at=now)
- due_for_retry(): записи, готовые к повторной публикации (self-healing)
- stats():   агрегаты для /reliability/stats
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from sqlalchemy.orm import Session

from core.models.pipeline_failure_orm import PipelineFailure
from core.database import SessionLocal

logger = logging.getLogger(__name__)

# Типы ошибок, которые имеет смысл переотправлять из DLQ
RETRYABLE_DLQ_TYPES = {"timeout", "rate_limit", "network", "llm_error", "publish_error"}


class DeadLetterQueue:
    """DLQ для failed posts на основе pipeline_failures."""

    def __init__(self, db: Optional[Session] = None):
        self.db = db or SessionLocal()
        self.own_session = db is None

    def close(self) -> None:
        if self.own_session:
            self.db.close()

    def enqueue(
        self,
        channel_id: str,
        pipeline: str,
        job: str,
        error_message: str,
        content_payload: Optional[Dict[str, Any]] = None,
        execution_id: Optional[str] = None,
        error_type: str = "publish_error",
        error_code: Optional[str] = None,
        attempts: int = 3,
        retry_delay_seconds: float = 300.0,
    ) -> PipelineFailure:
        """
        Помещает неудавшийся пост в DLQ.

        Args:
            content_payload: контент поста (text, media, platform-метаданные)
                            для повторной публикации без регенерации.
            retry_delay_seconds: через сколько вернуться к посту (backoff).
        """
        failure = PipelineFailure(
            channel_id=channel_id,
            pipeline=pipeline,
            job=job,
            error_type=error_type,
            error_message=error_message[:4000],
            error_code=error_code,
            execution_id=execution_id,
            attempt=attempts,
            max_attempts=attempts,
            retry_at=datetime.utcnow() + timedelta(seconds=retry_delay_seconds),
            context={
                "dlq": True,
                "content": content_payload or {},
            },
        )
        self.db.add(failure)
        self.db.commit()
        self.db.refresh(failure)
        logger.warning(
            f"DLQ enqueue: channel={channel_id} pipeline={pipeline} job={job} "
            f"id={failure.id} retry_at={failure.retry_at}"
        )
        return failure

    def list(
        self,
        channel_id: Optional[str] = None,
        unresolved_only: bool = True,
        limit: int = 50,
    ) -> List[PipelineFailure]:
        """Список записей DLQ (dlq-флаг фильтруется в Python — SQLite-совместимо)."""
        q = self.db.query(PipelineFailure)
        if unresolved_only:
            q = q.filter(PipelineFailure.resolved == False)  # noqa: E712
        if channel_id:
            q = q.filter(PipelineFailure.channel_id == channel_id)
        rows = q.order_by(PipelineFailure.created_at.desc()).limit(limit * 3).all()
        return [f for f in rows if isinstance(f.context, dict) and f.context.get("dlq")][:limit]

    def requeue(self, failure_id: str, reset_attempts: bool = True) -> Optional[PipelineFailure]:
        """Возвращает запись DLQ в обработку (retry_at=now)."""
        failure = self.db.query(PipelineFailure).filter(
            PipelineFailure.id == failure_id
        ).first()
        if not failure:
            return None
        if reset_attempts:
            failure.attempt = 0
            failure.max_attempts = max(failure.max_attempts, 1)
        failure.retry_at = datetime.utcnow()
        failure.resolved = False
        self.db.commit()
        self.db.refresh(failure)
        logger.info(f"DLQ requeue: {failure_id}")
        return failure

    def due_for_retry(self, limit: int = 10) -> List[PipelineFailure]:
        """Записи, готовые к повторной попытке (self-healing)."""
        now = datetime.utcnow()
        candidates = self.db.query(PipelineFailure).filter(
            PipelineFailure.resolved == False,  # noqa: E712
            PipelineFailure.retry_at != None,  # noqa: E711
            PipelineFailure.retry_at <= now,
            PipelineFailure.error_type.in_(RETRYABLE_DLQ_TYPES),
        ).order_by(PipelineFailure.retry_at.asc()).limit(limit * 3).all()
        return [f for f in candidates if isinstance(f.context, dict) and f.context.get("dlq")][:limit]

    def mark_resolved(self, failure_id: str, resolution: str = "retry_success") -> Optional[PipelineFailure]:
        """Отметить как успешно обработанную."""
        failure = self.db.query(PipelineFailure).filter(
            PipelineFailure.id == failure_id
        ).first()
        if failure:
            failure.mark_resolved(resolution)
            self.db.commit()
        return failure

    def stats(self) -> Dict[str, Any]:
        """Агрегаты DLQ для dashboard."""
        items = self.list(unresolved_only=False, limit=1000)
        by_type: Dict[str, int] = {}
        by_channel: Dict[str, int] = {}
        unresolved = 0
        for f in items:
            by_type[f.error_type] = by_type.get(f.error_type, 0) + 1
            by_channel[f.channel_id] = by_channel.get(f.channel_id, 0) + 1
            if not f.resolved:
                unresolved += 1
        return {
            "total": len(items),
            "unresolved": unresolved,
            "by_type": by_type,
            "by_channel": by_channel,
        }


def get_dlq(db: Optional[Session] = None) -> DeadLetterQueue:
    """Фабрика DLQ (совместимо с паттерном get_error_logger)."""
    return DeadLetterQueue(db)
