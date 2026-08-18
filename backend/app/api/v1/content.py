from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime
from sqlalchemy.orm import Session

from core.database import get_db, engine, Base
from core.models.content_orm import ContentORM
from core.repositories.content_repository import ContentRepository

Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/content", tags=["content"])

ContentStatus = Literal["research", "brief", "draft", "review", "needs_revision", "approved", "scheduled", "published", "rejected"]


class ContentItem(BaseModel):
    id: str
    channel_id: Optional[str] = None
    source_url: str
    headline: str
    status: ContentStatus
    prompt_version: Optional[str] = None
    draft_text: Optional[str] = None
    image_url: Optional[str] = None
    fact_score: Optional[int] = None
    quality_score: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ContentListResponse(BaseModel):
    total: int
    items: List[ContentItem]


class StatusUpdateRequest(BaseModel):
    status: ContentStatus


def _to_response(c: ContentORM) -> ContentItem:
    return ContentItem(
        id=c.id,
        channel_id=c.channel_id,
        source_url=c.source_url,
        headline=c.headline,
        status=c.status,
        prompt_version=c.prompt_version,
        draft_text=c.draft_text,
        image_url=c.image_url,
        fact_score=c.fact_score,
        quality_score=c.quality_score,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


def _seed_demo_data_if_empty(db: Session):
    '''Сохраняем прежнее поведение: пара демо-постов, чтобы Dashboard не был пустым при первом старте.'''
    repo = ContentRepository(db)
    if repo.count() > 0:
        return
    repo.create(
        source_url="https://openai.com/index/gpt-red/",
        headline="OpenAI представила GPT-Red для автоматического тестирования безопасности",
        status="review",
        prompt_version="telegram_news_v2",
        draft_text="OpenAI запустила GPT-Red. Система использует self-play для улучшения AI Safety.",
        fact_score=95,
        quality_score=92,
    )
    repo.create(
        source_url="https://techcrunch.com/ai-update",
        headline="Новый прорыв в LLM: эффективность выросла на 40%",
        status="draft",
        prompt_version="telegram_news_v1",
        draft_text="Черновик поста...",
        fact_score=88,
        quality_score=85,
    )


@router.get("/", response_model=ContentListResponse)
async def list_content(
    status: Optional[ContentStatus] = Query(None, description="Фильтр по статусу"),
    channel_id: Optional[str] = Query(None, description="Фильтр по каналу"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    '''Получить список контента с фильтрацией по статусу и каналу.'''
    _seed_demo_data_if_empty(db)
    repo = ContentRepository(db)
    items = repo.list_all(status=status, channel_id=channel_id, limit=limit, offset=offset)
    total = repo.count(status=status, channel_id=channel_id)
    return ContentListResponse(total=total, items=[_to_response(i) for i in items])


@router.get("/{content_id}", response_model=ContentItem)
async def get_content(content_id: str, db: Session = Depends(get_db)):
    '''Получить полную информацию о посте.'''
    repo = ContentRepository(db)
    item = repo.get(content_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content not found")
    return _to_response(item)


@router.put("/{content_id}/status", response_model=ContentItem)
async def update_content_status(content_id: str, request: StatusUpdateRequest, db: Session = Depends(get_db)):
    '''Перевести пост на следующий этап.'''
    repo = ContentRepository(db)
    item = repo.update_status(content_id, request.status)
    if not item:
        raise HTTPException(status_code=404, detail="Content not found")
    return _to_response(item)


@router.post("/{content_id}/approve", response_model=ContentItem)
async def approve_content(content_id: str, db: Session = Depends(get_db)):
    '''Approve draft: переводит content из draft/review в approved и готовит его к publish.'''
    repo = ContentRepository(db)
    item = repo.get(content_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content not found")

    if item.status not in {"draft", "review"}:
        raise HTTPException(
            status_code=400,
            detail=f"Content must be in 'draft' or 'review' status before approval, current: '{item.status}'"
        )

    approved_item = repo.update_status(content_id, "approved")
    if not approved_item:
        raise HTTPException(status_code=404, detail="Content not found")
    return _to_response(approved_item)
