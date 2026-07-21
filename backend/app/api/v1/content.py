from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from uuid import uuid4
from datetime import datetime

router = APIRouter(prefix="/content", tags=["content"])

# === МОДЕЛИ ===

ContentStatus = Literal["research", "brief", "draft", "review", "scheduled", "published", "rejected"]

class ContentItem(BaseModel):
    id: str
    source_url: str
    headline: str
    status: ContentStatus
    prompt_version: Optional[str] = None
    draft_text: Optional[str] = None
    image_url: Optional[str] = None
    fact_score: Optional[int] = None
    quality_score: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ContentListResponse(BaseModel):
    total: int
    items: List[ContentItem]

# === IN-MEMORY БД ДЛЯ ДЕМО ===
_content_db = {}

# === ENDPOINTS ===

@router.get("/", response_model=ContentListResponse)
async def list_content(
    status: Optional[ContentStatus] = Query(None, description="Фильтр по статусу"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    '''Получить список контента с фильтрацией по статусу (Review Queue, Drafts и т.д.).'''
    items = list(_content_db.values())
    
    if status:
        items = [item for item in items if item.status == status]
        
    # Сортировка по дате (новые сверху)
    items.sort(key=lambda x: x.created_at, reverse=True)
    
    return ContentListResponse(
        total=len(items),
        items=items[offset:offset+limit]
    )

@router.get("/{content_id}", response_model=ContentItem)
async def get_content(content_id: str):
    '''Получить полную информацию о посте (включая факты, промпт, историю).'''
    if content_id not in _content_db:
        raise HTTPException(status_code=404, detail="Content not found")
    return _content_db[content_id]

@router.put("/{content_id}/status", response_model=ContentItem)
async def update_content_status(content_id: str, new_status: ContentStatus):
    '''Перевести пост на следующий этап (например, одобрить черновик).'''
    if content_id not in _content_db:
        raise HTTPException(status_code=404, detail="Content not found")
    
    item = _content_db[content_id]
    item.status = new_status
    item.updated_at = datetime.utcnow()
    
    return item

# === ДЕМО-ДАННЫЕ ===
# Создадим пару тестовых постов, чтобы API не был пустым
_demo_1 = ContentItem(
    id=str(uuid4()),
    source_url="https://openai.com/index/gpt-red/",
    headline="OpenAI представила GPT-Red для автоматического тестирования безопасности",
    status="review",
    prompt_version="telegram_news_v2",
    draft_text=" OpenAI запустила GPT-Red. Система использует self-play для улучшения AI Safety. Анонсировано 16.07.2026.",
    fact_score=95,
    quality_score=92
)
_demo_2 = ContentItem(
    id=str(uuid4()),
    source_url="https://techcrunch.com/ai-update",
    headline="Новый прорыв в LLM: эффективность выросла на 40%",
    status="draft",
    prompt_version="telegram_news_v1",
    draft_text="Черновик поста...",
    fact_score=88,
    quality_score=85
)
_content_db[_demo_1.id] = _demo_1
_content_db[_demo_2.id] = _demo_2
