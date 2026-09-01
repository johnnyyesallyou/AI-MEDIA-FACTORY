"""Posts API - Sprint 60.

API для работы с историей постов и генерацией.
"""
from backend.core.rate_limiter import rate_limit_call
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, ConfigDict

from core.database import get_db
from core.models.post_history_orm import PostHistoryORM, ChannelLearningsORM
from core.models.content_orm import ContentORM
from core.models.analytics import PostMetric
from engines.post_generation_service import PostGenerationService

router = APIRouter(prefix="/posts", tags=["posts"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class PostGenerateRequest(BaseModel):
    topic: str
    content: Optional[dict] = None
    content_type: str = "news"


class PostGenerateResponse(BaseModel):
    id: str
    text: str
    media_type: str
    image_url: Optional[str]
    video_url: Optional[str]
    ready_to_publish: bool


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

    model_config = ConfigDict(from_attributes=True)


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

@rate_limit_call("post_generate", timeout=120.0)
@router.post("/generate/{channel_id}", response_model=PostGenerateResponse)
async def generate_post_for_channel(
    channel_id: str,
    req: PostGenerateRequest,
    db: Session = Depends(get_db),
):
    """
    Генерировать пост для канала.

    Возвращает ContentORM в виде PostGenerateResponse.
    media_type вычисляется из video_url/image_url.
    """
    service = PostGenerationService(db)

    content = req.content or {
        "title": req.topic,
        "source_name": "Generated",
        "summary": req.topic,
    }

    try:
        post = await service.generate_post(
            channel_id=channel_id,
            content=content,
            content_type=req.content_type,
        )

        if not post:
            raise HTTPException(status_code=500, detail="Failed to generate post")

        # Безопасно достаём поля (ContentORM может не иметь всех атрибутов)
        text = getattr(post, "draft_text", None) or getattr(post, "text", "") or ""
        video_url = getattr(post, "video_url", None)
        image_url = getattr(post, "image_url", None)

        # Вычисляем media_type
        if video_url:
            media_type = "video"
        elif image_url:
            media_type = "image"
        else:
            media_type = "none"

        ready_to_publish = bool(text)

        return {
            "id": post.id,
            "text": text,
            "media_type": media_type,
            "image_url": image_url,
            "video_url": video_url,
            "ready_to_publish": ready_to_publish,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{channel_id}", response_model=List[PostHistoryResponse])
async def get_channel_post_history(
    channel_id: str,
    limit: int = 20,
    db: Session = Depends(get_db),
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
    db: Session = Depends(get_db),
):
    """Получить агрегированные метрики канала за N дней"""
    from datetime import datetime, timedelta
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # 1. Получаем все PostHistory для канала за период
    posts = db.query(PostHistoryORM)\
        .filter(PostHistoryORM.channel_id == channel_id)\
        .filter(PostHistoryORM.posted_at > start_date)\
        .all()
    
    post_count = len(posts)
    total_views = 0
    total_likes = 0
    
    # 2. Для каждого поста ищем последнюю метрику по content_id или message_id
    for post in posts:
        # Ищем метрику по content_id
        if post.content_id:
            metric = db.query(PostMetric)\
                .filter(PostMetric.content_id == post.content_id)\
                .order_by(PostMetric.measured_at.desc())\
                .first()
            
            if metric:
                total_views += metric.views_count or 0
                total_likes += metric.likes_count or 0
    
    # 3. Получаем топ-паттерны
    learnings = db.query(ChannelLearningsORM)\
        .filter(ChannelLearningsORM.channel_id == channel_id)\
        .order_by(ChannelLearningsORM.score.desc())\
        .limit(5)\
        .all()
    
    top_patterns = [l.pattern for l in learnings if (l.score or 0) > 0.3]
    
    return {
        "channel_id": channel_id,
        "period_days": days,
        "total_posts": post_count,
        "total_views": total_views,
        "total_likes": total_likes,
        "avg_views_per_post": total_views / post_count if post_count > 0 else 0.0,
        "avg_likes_per_post": total_likes / post_count if post_count > 0 else 0.0,
        "top_patterns": top_patterns,
    }


@router.get("/learnings/{channel_id}")
async def get_channel_learnings(
    channel_id: str,
    min_score: float = 0.5,
    db: Session = Depends(get_db),
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
            "last_updated": l.last_updated.isoformat() if l.last_updated else None,
        }
        for l in learnings
    ]

@rate_limit_call("post_publish", timeout=30.0)
@router.post("/publish/{content_id}")
async def publish_generated_post(content_id: str, db: Session = Depends(get_db)):
    """
    Опубликовать сгенерированный пост (ContentORM status='generated').
    Sprint 61: ручной publish из UI.
    """
    from engines.publish_service import PublishService

    service = PublishService(db)
    published = await service.publish_generated_post(content_id)

    if not published:
        raise HTTPException(
            status_code=400,
            detail="Failed to publish (post not found, wrong status, or platform error)",
        )

    return {
        "id": published.id,
        "status": published.status,
        "message_id": published.telegram_message_id,
        "published_at": published.published_at.isoformat() if published.published_at else None,
    }


@router.get("/drafts/{channel_id}")
async def list_drafts(channel_id: str, limit: int = 10, db: Session = Depends(get_db)):
    """Список сгенерированных, но не опубликованных постов."""
    drafts = (
        db.query(ContentORM)
        .filter(
            ContentORM.channel_id == channel_id,
            ContentORM.status.in_(["draft", "generated", "review", "needs_revision", "approved", "failed"]),
        )
        .order_by(ContentORM.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": d.id,
            "headline": d.headline,
            "text": d.draft_text,
            "image_url": d.image_url,
            "video_url": getattr(d, "video_url", None),
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in drafts
    ]


@router.post("/{content_id}/approve")
async def approve_post(content_id: str, db: Session = Depends(get_db)):
    """Approve draft: переводит в status='approved'."""
    content = db.query(ContentORM).filter(ContentORM.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    if content.status not in ["draft", "generated", "review", "needs_revision", "approved", "failed"]:
        raise HTTPException(
            status_code=400,
            detail=f"Content must be in 'draft/generated/review/needs_revision' status, current: '{content.status}'"
        )
    
    content.status = "approved"
    content.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(content)
    
    return {
        "id": content.id,
        "status": content.status,
        "approved_at": content.updated_at.isoformat(),
    }


@router.post("/{content_id}/reject")
async def reject_post(content_id: str, reason: str = None, db: Session = Depends(get_db)):
    """Reject draft: переводит в status='rejected'."""
    content = db.query(ContentORM).filter(ContentORM.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    if content.status not in ["draft", "generated", "review", "needs_revision", "approved", "failed"]:
        raise HTTPException(
            status_code=400,
            detail=f"Content must be in 'draft/generated/review/needs_revision' status, current: '{content.status}'"
        )
    
    content.status = "rejected"
    content.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(content)
    
    return {
        "id": content.id,
        "status": content.status,
        "reason": reason,
        "rejected_at": content.updated_at.isoformat(),
    }


@router.patch("/{content_id}")
async def edit_post(content_id: str, data: dict, db: Session = Depends(get_db)):
    """Edit draft: обновить text/image_url/video_url."""
    content = db.query(ContentORM).filter(ContentORM.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    if content.status not in ["draft", "generated", "review", "needs_revision", "approved", "failed"]:
        raise HTTPException(
            status_code=400,
            detail=f"Can only edit draft/generated/review/needs_revision, current: '{content.status}'"
        )
    
    # Обновляем разрешённые поля
    if "text" in data:
        content.draft_text = data["text"]
    if "image_url" in data:
        content.image_url = data["image_url"]
    if "video_url" in data and hasattr(content, "video_url"):
        content.video_url = data["video_url"]
    
    content.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(content)
    
    return {
        "id": content.id,
        "status": content.status,
        "text": content.draft_text,
        "image_url": content.image_url,
        "video_url": getattr(content, "video_url", None),
        "updated_at": content.updated_at.isoformat(),
    }


@router.get("/drafts")
async def list_all_drafts(limit: int = 50, db: Session = Depends(get_db)):
    """Список ВСЕХ draft posts (для Review Queue)."""
    drafts = (
        db.query(ContentORM)
        .filter(
            ContentORM.status.in_(["draft", "generated", "review", "needs_revision", "approved", "failed"])
        )
        .order_by(ContentORM.created_at.desc())
        .limit(limit)
        .all()
    )
    
    return [
        {
            "id": d.id,
            "channel_id": d.channel_id,
            "headline": d.headline,
            "text": d.draft_text,
            "image_url": d.image_url,
            "video_url": getattr(d, "video_url", None),
            "status": d.status,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in drafts
    ]

