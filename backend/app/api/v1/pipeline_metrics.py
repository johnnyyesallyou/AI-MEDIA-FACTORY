"""Sprint 73.1: Pipeline Run Metrics API.

История прогонов Universal Pipeline, агрегаты по стадиям и
поиск самых медленных каналов (кандидаты на оптимизацию).
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from core.database import get_db
from core.models.pipeline_run_metrics_orm import PipelineRunMetrics

router = APIRouter(prefix="/metrics/pipeline", tags=["pipeline-metrics"])


def _to_dict(m: PipelineRunMetrics) -> dict:
    return {
        "id": m.id,
        "channel_id": m.channel_id,
        "channel_name": m.channel_name,
        "execution_id": m.execution_id,
        "stage_timings_ms": {
            "research": m.research_ms,
            "writing": m.writing_ms,
            "media": m.media_ms,
            "publishing": m.publishing_ms,
        },
        "total_ms": m.total_ms,
        "topics": {
            "found": m.topics_found,
            "generated": m.topics_generated,
            "published": m.topics_published,
        },
        "errors_count": m.errors_count,
        "success": m.success == "true",
        "created_at": m.created_at.isoformat() if m.created_at else None,
    }


@router.get("/{channel_id}")
async def get_pipeline_metrics(channel_id: str, limit: int = Query(10, le=100), db: Session = Depends(get_db)):
    """История последних N прогонов пайплайна для канала."""
    rows = (
        db.query(PipelineRunMetrics)
        .filter(PipelineRunMetrics.channel_id == channel_id)
        .order_by(PipelineRunMetrics.created_at.desc())
        .limit(limit)
        .all()
    )
    return {"channel_id": channel_id, "runs": [_to_dict(m) for m in rows], "count": len(rows)}


@router.get("/summary/all")
async def get_pipeline_summary(limit: int = Query(50, le=500), db: Session = Depends(get_db)):
    """Сводка по всем каналам: средние тайминги по стадиям (по последним прогонам)."""
    rows = (
        db.query(
            PipelineRunMetrics.channel_id,
            func.count(PipelineRunMetrics.id).label("runs"),
            func.avg(PipelineRunMetrics.research_ms).label("avg_research"),
            func.avg(PipelineRunMetrics.writing_ms).label("avg_writing"),
            func.avg(PipelineRunMetrics.media_ms).label("avg_media"),
            func.avg(PipelineRunMetrics.publishing_ms).label("avg_publishing"),
            func.avg(PipelineRunMetrics.total_ms).label("avg_total"),
            func.sum(PipelineRunMetrics.topics_published).label("published"),
        )
        .group_by(PipelineRunMetrics.channel_id)
        .all()
    )
    # limit применяем к средним по убыванию avg_total — самые медленные сверху
    summary = [
        {
            "channel_id": r.channel_id,
            "runs": int(r.runs or 0),
            "avg_ms": {
                "research": round(float(r.avg_research or 0)),
                "writing": round(float(r.avg_writing or 0)),
                "media": round(float(r.avg_media or 0)),
                "publishing": round(float(r.avg_publishing or 0)),
                "total": round(float(r.avg_total or 0)),
            },
            "topics_published": int(r.published or 0),
        }
        for r in rows
    ]
    summary.sort(key=lambda x: x["avg_ms"]["total"], reverse=True)
    return {"channels": summary[:limit], "count": len(summary)}


@router.get("/slowest/top")
async def get_slowest_channels(limit: int = Query(5, le=50), db: Session = Depends(get_db)):
    """Самые медленные каналы (по среднему total_ms) — кандидаты на оптимизацию."""
    rows = (
        db.query(
            PipelineRunMetrics.channel_id,
            PipelineRunMetrics.channel_name,
            func.avg(PipelineRunMetrics.total_ms).label("avg_total"),
            func.avg(PipelineRunMetrics.writing_ms).label("avg_writing"),
            func.count(PipelineRunMetrics.id).label("runs"),
        )
        .group_by(PipelineRunMetrics.channel_id, PipelineRunMetrics.channel_name)
        .order_by(func.avg(PipelineRunMetrics.total_ms).desc())
        .limit(limit)
        .all()
    )
    return {
        "slowest": [
            {
                "channel_id": r.channel_id,
                "channel_name": r.channel_name,
                "runs": int(r.runs or 0),
                "avg_total_ms": round(float(r.avg_total or 0)),
                "avg_writing_ms": round(float(r.avg_writing or 0)),
            }
            for r in rows
        ]
    }
