"""Posts API - Sprint 57.

API для работы с историей постов и метриками.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from core.database import get_db
from core.models.post_history_orm import PostHistoryORM, PostMetricsORM, ChannelLearningsORM

router = APIRouter(prefix="/posts", tags=["posts"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class PostHistoryResponse(BaseModel):
    id: str
    channel_id: str
    platform: Optional[str]
    text: Optional[str]
    image_url: Optional[str]
    video_url: Optional[str]
    media_type: Optional[str]
    message_id: Optional[str]
    posted_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class PostMetricsResponse(BaseModel):
    views: int
    likes: int
    shares: int
    reposts: int
    comments: int
    engagement_rate: float
    collected_at: datetime


class ChannelMetricsResponse(BaseModel):
    channel_id: str
    period_days: int
    total_posts: int
    total_views: int
    total_likes: int
    avg_views_per_post: float
    avg_likes_per_post: float
    top_patterns: List[str]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/history/{channel_id}", response_model=List[PostHistoryResponse])
async def get_channel_post_history(
    channel_id: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Получить историю постов канала"""
    posts = db.query(PostHistoryORM)\
        .filter_by(channel_id=channel_id)\
        .order_by(PostHistoryORM.posted_at.desc())\
        .limit(limit)\
        .all()
    
    return posts


@router.get("/metrics/{channel_id}", response_model=ChannelMetricsResponse)
async def get_channel_metrics(
    channel_id: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Получить метрики канала"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    posts = db.query(PostHistoryORM)\
        .filter_by(channel_id=channel_id)\
        .filter(PostHistoryORM.posted_at > start_date)\
        .all()
    
    total_views = 0
    total_likes = 0
    post_count = 0
    
    for post in posts:
        latest_metric = db.query(PostMetricsORM)\
            .filter_by(post_id=post.id)\
            .order_by(PostMetricsORM.collected_at.desc())\
            .first()
        
        if latest_metric:
            total_views += latest_metric.views
            total_likes += latest_metric.likes
            post_count += 1
    
    # Получить топ паттерны
    learnings = db.query(ChannelLearningsORM)\
        .filter_by(channel_id=channel_id)\
        .order_by(ChannelLearningsORM.score.desc())\
        .limit(5)\
        .all()
    
    top_patterns = [l.pattern for l in learnings if l.score > 0.6]
    
    return ChannelMetricsResponse(
        channel_id=channel_id,
        period_days=days,
        total_posts=post_count,
        total_views=total_views,
        total_likes=total_likes,
        avg_views_per_post=total_views / post_count if post_count else 0,
        avg_likes_per_post=total_likes / post_count if post_count else 0,
        top_patterns=top_patterns
    )


@router.get("/learnings/{channel_id}")
async def get_channel_learnings(
    channel_id: str,
    min_score: float = 0.5,
    db: Session = Depends(get_db)
):
    """Получить learnings канала (что работает)"""
    learnings = db.query(ChannelLearningsORM)\
        .filter_by(channel_id=channel_id)\
        .filter(ChannelLearningsORM.score >= min_score)\
        .order_by(ChannelLearningsORM.score.desc())\
        .all()
    
    return [
        {
            "pattern": l.pattern,
            "score": l.score,
            "evidence_count": l.evidence_count,
            "last_updated": l.last_updated.isoformat() if l.last_updated else None
        }
        for l in learnings
    ]