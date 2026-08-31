import pathlib, re

analytics = pathlib.Path('./backend/app/api/v1/analytics.py')
s = '''from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from core.database import get_db
from core.models.content_orm import ContentORM

router = APIRouter(prefix="/analytics", tags=["analytics"])

# === МОДЕЛИ ===

class AnalyticsOverview(BaseModel):
    """Сводная статистика для главной страницы аналитики."""
    total_published: int = 0
    total_drafts: int = 0
    avg_quality_score: Optional[float] = None
    avg_fact_score: Optional[float] = None
    total_views: int = 0  # Нет данных из Telegram API
    avg_ctr: float = 0.0  # Нет данных из Telegram API
    avg_er: float = 0.0   # Нет данных из Telegram API
    subscribers_growth: int = 0  # Нет данных из Telegram API
    retention_rate: float = 0.0  # Нет данных из Telegram API

class BestPerformer(BaseModel):
    """Лучший показатель в конкретной категории."""
    category: str  # channel, headline, hour
    name: str
    score: float
    metric_name: str

class TimeSeriesPoint(BaseModel):
    date: str
    published_count: int
    avg_quality_score: Optional[float] = None
    views: int = 0  # Нет данных из Telegram API
    ctr: float = 0.0  # Нет данных из Telegram API
    er: float = 0.0   # Нет данных из Telegram API

# === ENDPOINTS ===

@router.get("/overview", response_model=AnalyticsOverview)
async def get_analytics_overview(db: Session = Depends(get_db)):
    """Получить реальные метрики из БД."""
    total_published = db.query(ContentORM).filter(ContentORM.status == "published").count()
    total_drafts = db.query(ContentORM).filter(ContentORM.status == "draft").count()
    
    # Среднее качество опубликованных постов
    quality_stats = db.query(
        func.avg(ContentORM.quality_score)
    ).filter(
        ContentORM.status == "published",
        ContentORM.quality_score.isnot(None)
    ).scalar()
    
    fact_stats = db.query(
        func.avg(ContentORM.fact_score)
    ).filter(
        ContentORM.status == "published",
        ContentORM.fact_score.isnot(None)
    ).scalar()
    
    return AnalyticsOverview(
        total_published=total_published,
        total_drafts=total_drafts,
        avg_quality_score=round(quality_stats, 2) if quality_stats else None,
        avg_fact_score=round(fact_stats, 2) if fact_stats else None,
    )

@router.get("/best-performers", response_model=List[BestPerformer])
async def get_best_performers(db: Session = Depends(get_db)):
    """Топ-каналы по количеству публикаций + топ-headline по качеству."""
    performers = []
    
    # Топ-каналы по количеству опубликованных постов
    top_channels = db.query(
        ContentORM.channel_id,
        func.count(ContentORM.id).label("count")
    ).filter(
        ContentORM.status == "published",
        ContentORM.channel_id.isnot(None)
    ).group_by(ContentORM.channel_id).order_by(desc("count")).limit(3).all()
    
    for ch in top_channels:
        channel_id = ch[0]
        count = ch[1]
        performers.append(BestPerformer(
            category="channel",
            name=f"Channel {channel_id[:8]}..." if channel_id else "Unknown",
            score=float(count),
            metric_name="Published Posts"
        ))
    
    # Топ-3 поста по quality_score
    top_quality = db.query(
        ContentORM.headline,
        ContentORM.quality_score
    ).filter(
        ContentORM.status == "published",
        ContentORM.quality_score.isnot(None)
    ).order_by(desc(ContentORM.quality_score)).limit(3).all()
    
    for post in top_quality:
        performers.append(BestPerformer(
            category="headline",
            name=post[0][:50] + "..." if len(post[0]) > 50 else post[0],
            score=float(post[1]),
            metric_name="Quality Score"
        ))
    
    # Топ-часы публикации (в какие часы чаще публикуют)
    top_hours = db.query(
        func.extract("hour", ContentORM.published_at).label("hour"),
        func.count(ContentORM.id).label("count")
    ).filter(
        ContentORM.status == "published",
        ContentORM.published_at.isnot(None)
    ).group_by("hour").order_by(desc("count")).limit(3).all()
    
    for h in top_hours:
        performers.append(BestPerformer(
            category="hour",
            name=f"{int(h[0]):02d}:00",
            score=float(h[1]),
            metric_name="Publications"
        ))
    
    return performers

@router.get("/time-series", response_model=List[TimeSeriesPoint])
async def get_time_series(days: int = Query(7, ge=1, le=30), db: Session = Depends(get_db)):
    """Публикации по дням за последние N дней."""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    daily_stats = db.query(
        func.date(ContentORM.published_at).label("date"),
        func.count(ContentORM.id).label("count"),
        func.avg(ContentORM.quality_score).label("avg_quality")
    ).filter(
        ContentORM.status == "published",
        ContentORM.published_at >= start_date
    ).group_by(func.date(ContentORM.published_at)).order_by("date").all()
    
    result = []
    for stat in daily_stats:
        result.append(TimeSeriesPoint(
            date=stat[0].isoformat() if stat[0] else "",
            published_count=stat[1],
            avg_quality_score=round(stat[2], 2) if stat[2] else None,
        ))
    
    return result
'''

analytics.write_text(s, encoding='utf-8')
print('OK: analytics.py rewritten with real SQL queries')