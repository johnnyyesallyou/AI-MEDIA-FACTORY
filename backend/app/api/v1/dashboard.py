from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# === МОДЕЛИ ОТВЕТА ===

class ServiceStatus(BaseModel):
    name: str
    status: str # "OK", "ERROR", "UNKNOWN"
    latency_ms: Optional[float] = None

class SystemHealthResponse(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: Dict[str, ServiceStatus]

class DailyStatsResponse(BaseModel):
    date: str
    news_found: int = 0
    news_selected: int = 0
    posts_created: int = 0
    posts_published: int = 0
    drafts_pending: int = 0
    errors_count: int = 0
    avg_quality_score: Optional[float] = None
    avg_fact_score: Optional[float] = None
    total_views: int = 0
    total_er: float = 0.0

# === ЗАГЛУШКИ ДАННЫХ (В реальности - запросы к БД и сервисам) ===

@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health():
    '''Проверяет статус всех ключевых компонентов системы.'''
    # Здесь будут реальные health-check запросы к БД, Redis, Ollama и т.д.
    return SystemHealthResponse(
        services={
            "Research": ServiceStatus(name="Research", status="OK", latency_ms=12),
            "Ollama": ServiceStatus(name="Ollama", status="OK", latency_ms=45),
            "ComfyUI": ServiceStatus(name="ComfyUI", status="OK", latency_ms=120),
            "Telegram": ServiceStatus(name="Telegram", status="OK", latency_ms=80),
            "Postgres": ServiceStatus(name="Postgres", status="OK", latency_ms=5),
            "Redis": ServiceStatus(name="Redis", status="OK", latency_ms=2),
            "Qdrant": ServiceStatus(name="Qdrant", status="OK", latency_ms=15),
            "MinIO": ServiceStatus(name="MinIO", status="OK", latency_ms=10)
        }
    )

@router.get("/stats", response_model=DailyStatsResponse)
async def get_daily_stats():
    '''Возвращает сводную статистику за сегодня для карточек на главной.'''
    # Здесь будет агрегация из БД
    return DailyStatsResponse(
        date=datetime.utcnow().strftime("%Y-%m-%d"),
        news_found=214,
        news_selected=18,
        posts_created=18,
        posts_published=15,
        drafts_pending=3,
        errors_count=1,
        avg_quality_score=91.5,
        avg_fact_score=94.2,
        total_views=132500,
        total_er=12.4
    )
