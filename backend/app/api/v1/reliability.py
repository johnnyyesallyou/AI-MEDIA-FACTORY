"""
Sprint 74.1: Reliability API — Dead-Letter Queue + circuit breaker stats.

Маршруты:
- GET  /api/v1/reliability/dead-letters           — список DLQ
- GET  /api/v1/reliability/dead-letters/stats     — агрегаты DLQ
- POST /api/v1/reliability/dead-letters/{id}/requeue — вернуть пост в обработку
- POST /api/v1/reliability/dead-letters/{id}/resolve — пометить обработанным
- GET  /api/v1/reliability/circuit-breakers       — состояние circuit breakers
"""
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import get_db
from backend.core.dead_letter import DeadLetterQueue
from backend.core.rate_limiter import get_rate_limiter
from core.models.pipeline_failure_orm import PipelineFailure

router = APIRouter(prefix="/reliability", tags=["reliability"])


class DeadLetterItem(BaseModel):
    id: str
    channel_id: str
    pipeline: str
    job: str
    error_type: str
    error_message: str
    error_code: Optional[str] = None
    execution_id: Optional[str] = None
    attempt: int
    max_attempts: int
    resolved: bool
    retry_at: Optional[str] = None
    content: Dict[str, Any] = {}
    created_at: Optional[str] = None


class DeadLetterListResponse(BaseModel):
    total: int
    items: List[DeadLetterItem]


def _to_item(f: PipelineFailure) -> DeadLetterItem:
    ctx = f.context or {}
    return DeadLetterItem(
        id=f.id,
        channel_id=f.channel_id,
        pipeline=f.pipeline,
        job=f.job,
        error_type=f.error_type,
        error_message=f.error_message,
        error_code=f.error_code,
        execution_id=f.execution_id,
        attempt=f.attempt or 0,
        max_attempts=f.max_attempts or 0,
        resolved=bool(f.resolved),
        retry_at=f.retry_at.isoformat() if f.retry_at else None,
        content=ctx.get("content", {}) if isinstance(ctx, dict) else {},
        created_at=f.created_at.isoformat() if f.created_at else None,
    )


@router.get("/dead-letters", response_model=DeadLetterListResponse)
def list_dead_letters(
    channel_id: Optional[str] = None,
    unresolved_only: bool = True,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Список постов в DLQ (publish failures после исчерпания retry)."""
    dlq = DeadLetterQueue(db)
    try:
        items = dlq.list(channel_id=channel_id, unresolved_only=unresolved_only, limit=min(limit, 200))
        return DeadLetterListResponse(total=len(items), items=[_to_item(f) for f in items])
    finally:
        dlq.close()


@router.get("/dead-letters/stats")
def dead_letter_stats(db: Session = Depends(get_db)):
    """Агрегаты DLQ: total/unresolved, разбивка по типам и каналам."""
    dlq = DeadLetterQueue(db)
    try:
        return dlq.stats()
    finally:
        dlq.close()


@router.post("/dead-letters/{failure_id}/requeue")
def requeue_dead_letter(failure_id: str, db: Session = Depends(get_db)):
    """Вернуть пост из DLQ в обработку (retry_at=now → подхватит self-healing)."""
    dlq = DeadLetterQueue(db)
    try:
        failure = dlq.requeue(failure_id)
        if not failure:
            raise HTTPException(status_code=404, detail=f"DLQ item {failure_id} not found")
        return {"success": True, "id": failure.id, "retry_at": failure.retry_at.isoformat()}
    finally:
        dlq.close()


@router.post("/dead-letters/{failure_id}/resolve")
def resolve_dead_letter(failure_id: str, db: Session = Depends(get_db)):
    """Пометить запись DLQ как обработанную (вручную исправлено)."""
    dlq = DeadLetterQueue(db)
    try:
        failure = dlq.mark_resolved(failure_id, resolution="manual_fix")
        if not failure:
            raise HTTPException(status_code=404, detail=f"DLQ item {failure_id} not found")
        return {"success": True, "id": failure.id, "resolved": True}
    finally:
        dlq.close()


@router.get("/circuit-breakers")
@router.get("/status")
def circuit_breakers():
    """Состояние circuit breakers (reliability) + rate limit stats + паузы каналов."""
    from backend.core.reliability import all_breakers, channel_pauses_snapshot

    breakers = {name: b.snapshot() for name, b in all_breakers().items()}
    return {
        "breakers": breakers,
        "channel_pauses": channel_pauses_snapshot(),
        "rate_limit_stats": get_rate_limiter().get_stats(),
    }


@router.post("/self-healing/run")
async def self_healing_run(limit: int = 10):
    """Ручной запуск self-healing прохода: переотправка due-постов из DLQ."""
    from backend.core.self_healing import get_self_healing_worker

    worker = get_self_healing_worker()
    summary = await worker.run_once(limit=min(limit, 50))
    return {"success": True, "summary": summary}


@router.get("/self-healing/status")
def self_healing_status():
    """Статус self-healing worker'а (последний прогон)."""
    from backend.core.self_healing import get_self_healing_worker

    worker = get_self_healing_worker()
    return {
        "interval_seconds": worker.interval,
        "running": worker._running,
        "last_run": worker.last_run_summary,
    }


# ---------------------------------------------------------------------------
# Sprint 74.4: Health Checks
# ---------------------------------------------------------------------------
@router.get("/health")
async def health_check(platforms: Optional[str] = None):
    """
    Проверка доступности Telegram/VK API.

    platforms: JSON-строка с креденшелами, например:
    {"telegram": {"bot_token": "..."}, "vk": {"access_token": "...", "group_id": "..."}}
    Если не передан — возвращает unknown (без креденшелов проверить нельзя).
    """
    import json

    from backend.core.health import check_all

    cfg = None
    if platforms:
        try:
            cfg = json.loads(platforms)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in platforms parameter")
    return await check_all(cfg)


# ---------------------------------------------------------------------------
# Sprint 74.4: Manual pause / resume
# ---------------------------------------------------------------------------
@router.post("/channels/{channel_id}/pause")
def pause_channel_endpoint(channel_id: str, seconds: float = 300.0):
    """Вручную поставить канал на паузу (по умолчанию 5 минут)."""
    from backend.core.reliability import pause_channel, channel_paused

    pause_channel(channel_id, float(seconds))
    return {
        "success": True,
        "channel_id": channel_id,
        "paused_for_seconds": float(seconds),
        "remaining_seconds": round(channel_paused(channel_id), 1),
    }


@router.post("/channels/{channel_id}/resume")
def resume_channel_endpoint(channel_id: str):
    """Вручную снять паузу с канала (resume)."""
    from backend.core.reliability import reset_channel_pauses, channel_paused

    reset_channel_pauses(channel_id)
    return {
        "success": True,
        "channel_id": channel_id,
        "remaining_seconds": round(channel_paused(channel_id), 1),
    }


@router.get("/channels/{channel_id}/pause")
def get_channel_pause_status(channel_id: str):
    """Проверить, на паузе ли канал (в т.ч. ручная/автоматическая)."""
    from backend.core.reliability import channel_paused

    remaining = channel_paused(channel_id)
    return {
        "channel_id": channel_id,
        "paused": remaining > 0,
        "remaining_seconds": round(remaining, 1),
    }
