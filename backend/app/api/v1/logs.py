from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/logs", tags=["logs"])

# === МОДЕЛИ ===

class PipelineStep(BaseModel):
    step_name: str # research, writing, fact_check, publishing
    status: str # success, failed, skipped
    duration_ms: int
    details: str = ""

class LogEntry(BaseModel):
    id: str
    timestamp: datetime
    content_id: str
    headline: str
    pipeline_steps: List[PipelineStep]
    total_duration_ms: int

class LogListResponse(BaseModel):
    total: int
    items: List[LogEntry]

# === ЗАГЛУШКИ ДАННЫХ ===
_logs_db = [
    LogEntry(
        id="log_1",
        timestamp=datetime.utcnow(),
        content_id="content_123",
        headline="OpenAI представила GPT-Red",
        total_duration_ms=14500,
        pipeline_steps=[
            PipelineStep(step_name="research", status="success", duration_ms=2000, details="Found 5 articles"),
            PipelineStep(step_name="writing", status="success", duration_ms=5000, details="Generated with Qwen3"),
            PipelineStep(step_name="fact_check", status="success", duration_ms=3000, details="Score: 95/100"),
            PipelineStep(step_name="publishing", status="success", duration_ms=4500, details="Published to Telegram")
        ]
    )
]

# === ENDPOINTS ===

@router.get("/", response_model=LogListResponse)
async def list_logs(limit: int = Query(50, ge=1, le=100)):
    '''Получить журнал последних операций.'''
    return LogListResponse(total=len(_logs_db), items=_logs_db[:limit])

@router.get("/{log_id}", response_model=LogEntry)
async def get_log_details(log_id: str):
    '''Получить полную трассировку конкретной операции (полный путь обработки).'''
    for log in _logs_db:
        if log.id == log_id:
            return log
    return {"message": "Log not found"}
