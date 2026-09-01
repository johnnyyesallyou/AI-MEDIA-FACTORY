"""
Sprint 66.5: Failures API Endpoint

GET /api/v1/failures - получить список ошибок
GET /api/v1/failures/:failure_id - получить деталь ошибки
GET /api/v1/channels/:channel_id/failures - ошибки канала
POST /api/v1/failures/:failure_id/resolve - отметить как разрешённую
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from core.database import get_db
from core.models.pipeline_failure_orm import PipelineFailure
from backend.core.error_logger import get_error_logger
from pydantic import BaseModel

router = APIRouter(prefix="/failures", tags=["failures"])


# === SCHEMAS ===

class PipelineFailureResponse(BaseModel):
    """Ответ с информацией об ошибке"""
    id: str
    channel_id: str
    pipeline: str
    job: str
    error_type: str
    error_message: str
    error_code: Optional[str]
    execution_id: Optional[str]
    attempt: int
    max_attempts: int
    resolved: bool
    resolved_at: Optional[datetime]
    resolution: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FailureListResponse(BaseModel):
    """Список ошибок с фильтрацией"""
    total: int
    failures: List[PipelineFailureResponse]


class FailureStatsResponse(BaseModel):
    """Статистика ошибок"""
    channel_id: str
    total_errors: int
    by_type: dict  # {error_type: count}
    by_pipeline: dict  # {pipeline: count}
    by_job: dict  # {job: count}
    unresolved: int


class MarkResolvedRequest(BaseModel):
    """Запрос на отметку как разрешённой"""
    resolution: str = "success"  # success, manual_fix, ignored, etc


# === ENDPOINTS ===

@router.get("/", response_model=FailureListResponse)
async def get_failures(
    channel_id: Optional[str] = Query(None, description="Filter by channel ID"),
    pipeline: Optional[str] = Query(None, description="Filter by pipeline (research, generation, media, publishing)"),
    error_type: Optional[str] = Query(None, description="Filter by error type (timeout, exception, rate_limit, etc)"),
    unresolved_only: bool = Query(True, description="Show only unresolved failures"),
    limit: int = Query(100, ge=1, le=1000, description="Limit results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db),
):
    """Получить список failures с фильтрацией"""
    query = db.query(PipelineFailure)
    
    if channel_id:
        query = query.filter(PipelineFailure.channel_id == channel_id)
    
    if pipeline:
        query = query.filter(PipelineFailure.pipeline == pipeline)
    
    if error_type:
        query = query.filter(PipelineFailure.error_type == error_type)
    
    if unresolved_only:
        query = query.filter(PipelineFailure.resolved == False)
    
    total = query.count()
    
    failures = query.order_by(PipelineFailure.created_at.desc()).offset(offset).limit(limit).all()
    
    return FailureListResponse(
        total=total,
        failures=[PipelineFailureResponse.from_orm(f) for f in failures]
    )


@router.get("/{failure_id}", response_model=PipelineFailureResponse)
async def get_failure(
    failure_id: str,
    db: Session = Depends(get_db),
):
    """Получить детальную информацию об ошибке"""
    failure = db.query(PipelineFailure).filter(
        PipelineFailure.id == failure_id
    ).first()
    
    if not failure:
        raise HTTPException(status_code=404, detail="Failure not found")
    
    return PipelineFailureResponse.from_orm(failure)


@router.get("/channels/{channel_id}/failures", response_model=FailureListResponse)
async def get_channel_failures(
    channel_id: str,
    limit: int = Query(50, ge=1, le=1000),
    unresolved_only: bool = Query(True),
    db: Session = Depends(get_db),
):
    """Получить failures конкретного канала"""
    query = db.query(PipelineFailure).filter(
        PipelineFailure.channel_id == channel_id
    )
    
    if unresolved_only:
        query = query.filter(PipelineFailure.resolved == False)
    
    total = query.count()
    failures = query.order_by(PipelineFailure.created_at.desc()).limit(limit).all()
    
    return FailureListResponse(
        total=total,
        failures=[PipelineFailureResponse.from_orm(f) for f in failures]
    )


@router.get("/channels/{channel_id}/stats", response_model=FailureStatsResponse)
async def get_channel_failure_stats(
    channel_id: str,
    db: Session = Depends(get_db),
):
    """Получить статистику ошибок канала за последние 7 дней"""
    from datetime import timedelta
    
    error_logger = get_error_logger(db)
    stats = error_logger.get_error_stats(channel_id)
    
    stats["channel_id"] = channel_id
    
    return FailureStatsResponse(**stats)


@router.post("/{failure_id}/resolve", response_model=PipelineFailureResponse)
async def resolve_failure(
    failure_id: str,
    request: MarkResolvedRequest,
    db: Session = Depends(get_db),
):
    """Отметить failure как разрешённую"""
    failure = db.query(PipelineFailure).filter(
        PipelineFailure.id == failure_id
    ).first()
    
    if not failure:
        raise HTTPException(status_code=404, detail="Failure not found")
    
    failure.mark_resolved(request.resolution)
    db.commit()
    db.refresh(failure)
    
    return PipelineFailureResponse.from_orm(failure)


@router.delete("/{failure_id}", status_code=204)
async def delete_failure(
    failure_id: str,
    db: Session = Depends(get_db),
):
    """Удалить failure (архивирование)"""
    failure = db.query(PipelineFailure).filter(
        PipelineFailure.id == failure_id
    ).first()
    
    if not failure:
        raise HTTPException(status_code=404, detail="Failure not found")
    
    db.delete(failure)
    db.commit()


# === BATCH OPERATIONS ===

@router.post("/batch/resolve")
async def resolve_multiple_failures(
    channel_id: str = Query(..., description="Channel ID to resolve failures for"),
    error_type: Optional[str] = Query(None, description="Filter by error type"),
    resolution: str = Query("success", description="Resolution type"),
    db: Session = Depends(get_db),
):
    """Отметить несколько failures как разрешённые"""
    query = db.query(PipelineFailure).filter(
        PipelineFailure.channel_id == channel_id,
        PipelineFailure.resolved == False
    )
    
    if error_type:
        query = query.filter(PipelineFailure.error_type == error_type)
    
    failures = query.all()
    
    for failure in failures:
        failure.mark_resolved(resolution)
    
    db.commit()
    
    return {
        "resolved_count": len(failures),
        "message": f"Resolved {len(failures)} failures"
    }


# === DASHBOARD SUMMARY ===

@router.get("/dashboard/summary")
async def get_dashboard_summary(db: Session = Depends(get_db)):
    """Краткая сводка failures для dashboard"""
    from datetime import timedelta
    from sqlalchemy import func
    
    now = datetime.utcnow()
    
    # Общая статистика
    total_unresolved = db.query(func.count(PipelineFailure.id)).filter(
        PipelineFailure.resolved == False
    ).scalar() or 0
    
    # За последний день
    day_ago = now - timedelta(days=1)
    errors_24h = db.query(func.count(PipelineFailure.id)).filter(
        PipelineFailure.created_at > day_ago
    ).scalar() or 0
    
    # Топ ошибок
    top_errors = db.query(
        PipelineFailure.error_type,
        func.count(PipelineFailure.id).label("count")
    ).filter(
        PipelineFailure.created_at > day_ago
    ).group_by(PipelineFailure.error_type).order_by(
        func.count(PipelineFailure.id).desc()
    ).limit(5).all()
    
    # Топ каналов с ошибками
    top_channels = db.query(
        PipelineFailure.channel_id,
        func.count(PipelineFailure.id).label("count")
    ).filter(
        PipelineFailure.created_at > day_ago,
        PipelineFailure.resolved == False
    ).group_by(PipelineFailure.channel_id).order_by(
        func.count(PipelineFailure.id).desc()
    ).limit(10).all()
    
    return {
        "total_unresolved": total_unresolved,
        "errors_24h": errors_24h,
        "top_error_types": [{"error_type": t, "count": c} for t, c in top_errors],
        "top_channels_by_errors": [{"channel_id": ch, "count": c} for ch, c in top_channels],
    }
