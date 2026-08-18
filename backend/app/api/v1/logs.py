from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from core.database import get_db
from core.models.execution_log_orm import ExecutionLogORM
from pydantic import BaseModel

router = APIRouter(prefix="/logs", tags=["logs"])

# === МОДЕЛИ PYDANTIC ===

class PipelineStep(BaseModel):
    step_name: str
    status: str
    duration_ms: int
    details: str = ""

class LogEntry(BaseModel):
    id: str
    execution_id: str
    channel_id: Optional[str] = None
    content_id: Optional[str] = None
    headline: Optional[str] = None
    pipeline_steps: List[PipelineStep]
    total_duration_ms: int
    created_at: datetime

class LogListResponse(BaseModel):
    total: int
    items: List[LogEntry]

# === ENDPOINTS ===

@router.get("/", response_model=LogListResponse)
async def list_logs(limit: int = Query(50, ge=1, le=100), db: Session = Depends(get_db)):
    """Получить журнал последних операций из БД."""
    
    # Простой и надежный запрос: берем последние записи, отсортированные по времени
    # Умножаем limit на 4, так как на 1 execution_id приходится ~4-5 шагов
    logs = db.query(ExecutionLogORM).order_by(ExecutionLogORM.created_at.desc()).limit(limit * 5).all()
    
    # Группируем логи по execution_id в Python (это быстро и надежно)
    grouped = {}
    for log in logs:
        if log.execution_id not in grouped:
            grouped[log.execution_id] = {
                "id": log.execution_id,
                "execution_id": log.execution_id,
                "channel_id": log.channel_id,
                "content_id": log.content_id,
                "headline": log.headline or "Без заголовка",
                "pipeline_steps": [],
                "total_duration_ms": 0,
                "created_at": log.created_at
            }
        
        duration = log.duration_ms or 0
        grouped[log.execution_id]["total_duration_ms"] += duration
        
        # Добавляем шаг в начало списка, чтобы они шли в хронологическом порядке
        grouped[log.execution_id]["pipeline_steps"].insert(0, PipelineStep(
            step_name=log.stage,
            status=log.status,
            duration_ms=duration,
            details=log.details or ""
        ))
    
    # Преобразуем в список (он уже отсортирован по created_at.desc() благодаря исходному запросу)
    items = list(grouped.values())
    
    return LogListResponse(total=len(items), items=items[:limit])

@router.get("/{execution_id}")
async def get_log_details(execution_id: str, db: Session = Depends(get_db)):
    """Получить полную трассировку конкретной операции."""
    logs = db.query(ExecutionLogORM).filter(
        ExecutionLogORM.execution_id == execution_id
    ).order_by(ExecutionLogORM.started_at.asc()).all()
    
    if not logs:
        return {"message": "Log not found"}
    
    first_log = logs[0]
    pipeline_steps = [
        PipelineStep(
            step_name=log.stage,
            status=log.status,
            duration_ms=log.duration_ms or 0,
            details=log.details or "",
        )
        for log in logs
    ]
    
    total_duration = sum(log.duration_ms or 0 for log in logs)
    
    return {
        "id": execution_id,
        "execution_id": execution_id,
        "channel_id": first_log.channel_id,
        "content_id": first_log.content_id,
        "headline": first_log.headline or "Без заголовка",
        "pipeline_steps": pipeline_steps,
        "total_duration_ms": total_duration,
        "created_at": first_log.created_at
    }
