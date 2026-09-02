"""Sprint 69.13: Pilot Metrics API."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from core.database import get_db

router = APIRouter(prefix="/pilot", tags=["pilot"])


class PilotMetricResponse(BaseModel):
    id: str
    channel_id: str
    channel_name: str
    collected_at: datetime
    period_hours: int
    pipeline_runs: int
    pipeline_successes: int
    pipeline_failures: int
    pipeline_success_rate: float
    topics_extracted: int
    topics_new: int
    topics_duplicated: int
    posts_generated: int
    posts_published: int
    posts_failed: int
    publish_success_rate: float
    avg_pipeline_duration_seconds: float
    total_llm_calls: int
    error_count: int
    active_sources: int


class PilotSummaryResponse(BaseModel):
    period_hours: int
    total_channels: int
    total_pipeline_runs: int
    total_posts_published: int
    avg_pipeline_success_rate: float
    avg_publish_success_rate: float
    total_errors: int
    channels: List[PilotMetricResponse]


@router.get("/metrics", response_model=List[PilotMetricResponse])
async def get_pilot_metrics(
    hours: int = Query(24, description="Сколько часов назад смотреть"),
    channel_id: Optional[str] = Query(None, description="Фильтр по каналу"),
    db: Session = Depends(get_db),
):
    """Получить метрики пилота за последние N часов."""
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    query = """
        SELECT * FROM pilot_metrics 
        WHERE collected_at >= :cutoff
    """
    params = {"cutoff": cutoff}
    
    if channel_id:
        query += " AND channel_id = :channel_id"
        params["channel_id"] = channel_id
    
    query += " ORDER BY collected_at DESC"
    
    result = db.execute(text(query), params)
    rows = result.fetchall()
    
    metrics = []
    for row in rows:
        metrics.append(PilotMetricResponse(
            id=row[0],
            channel_id=row[1],
            channel_name=row[2],
            collected_at=row[3],
            period_hours=row[4],
            pipeline_runs=row[5],
            pipeline_successes=row[6],
            pipeline_failures=row[7],
            pipeline_success_rate=row[8],
            topics_extracted=row[9],
            topics_new=row[10],
            topics_duplicated=row[11],
            posts_generated=row[12],
            posts_published=row[13],
            posts_failed=row[14],
            publish_success_rate=row[15],
            avg_pipeline_duration_seconds=row[16],
            total_llm_calls=row[17],
            error_count=row[18],
            active_sources=row[20],
        ))
    
    return metrics


@router.get("/metrics/summary", response_model=PilotSummaryResponse)
async def get_pilot_summary(
    hours: int = Query(24, description="Сколько часов назад смотреть"),
    db: Session = Depends(get_db),
):
    """Получить сводку метрик пилота."""
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    # Общая статистика
    stats = db.execute(text("""
        SELECT 
            COUNT(DISTINCT channel_id) as total_channels,
            SUM(pipeline_runs) as total_runs,
            SUM(posts_published) as total_published,
            AVG(pipeline_success_rate) as avg_success_rate,
            AVG(publish_success_rate) as avg_publish_rate,
            SUM(error_count) as total_errors
        FROM pilot_metrics
        WHERE collected_at >= :cutoff
    """), {"cutoff": cutoff}).fetchone()
    
    # Детали по каналам
    channels = db.execute(text("""
        SELECT * FROM pilot_metrics
        WHERE collected_at >= :cutoff
        ORDER BY collected_at DESC
    """), {"cutoff": cutoff}).fetchall()
    
    channel_metrics = []
    for row in channels:
        channel_metrics.append(PilotMetricResponse(
            id=row[0],
            channel_id=row[1],
            channel_name=row[2],
            collected_at=row[3],
            period_hours=row[4],
            pipeline_runs=row[5],
            pipeline_successes=row[6],
            pipeline_failures=row[7],
            pipeline_success_rate=row[8],
            topics_extracted=row[9],
            topics_new=row[10],
            topics_duplicated=row[11],
            posts_generated=row[12],
            posts_published=row[13],
            posts_failed=row[14],
            publish_success_rate=row[15],
            avg_pipeline_duration_seconds=row[16],
            total_llm_calls=row[17],
            error_count=row[18],
            active_sources=row[20],
        ))
    
    return PilotSummaryResponse(
        period_hours=hours,
        total_channels=stats[0] or 0,
        total_pipeline_runs=stats[1] or 0,
        total_posts_published=stats[2] or 0,
        avg_pipeline_success_rate=stats[3] or 0,
        avg_publish_success_rate=stats[4] or 0,
        total_errors=stats[5] or 0,
        channels=channel_metrics,
    )


@router.post("/metrics/collect")
async def trigger_metrics_collection():
    """Запустить сбор метрик вручную."""
    import subprocess
    
    try:
        result = subprocess.run(
            ["python", "/app/collect_pilot_metrics.py"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        
        return {
            "success": True,
            "output": result.stdout,
            "errors": result.stderr,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))