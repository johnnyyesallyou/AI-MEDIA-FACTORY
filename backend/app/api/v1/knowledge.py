from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import uuid4
from datetime import datetime

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

# === МОДЕЛИ ===

class KnowledgeInsight(BaseModel):
    '''
    Единица "опыта" платформы. 
    Хранит лучшие темы, заголовки, изображения, модели и промпты.
    '''
    id: str
    category: str # best_topic, best_headline, best_image, best_model, best_prompt
    title: str
    description: str
    confidence_score: float = Field(ge=0.0, le=1.0, description="Уверенность системы в этом инсайте")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class InsightCreateRequest(BaseModel):
    category: str
    title: str
    description: str
    confidence_score: float = 0.9

# === IN-MEMORY БД ===
_insights_db = {
    "1": KnowledgeInsight(id="1", category="best_topic", title="AI Safety", description="Темы по безопасности AI показывают CTR на 40% выше среднего.", confidence_score=0.95),
    "2": KnowledgeInsight(id="2", category="best_headline", title="Вопрос в заголовке", description="Заголовки, заканчивающиеся вопросом, дают +15% к ER.", confidence_score=0.88)
}

# === ENDPOINTS ===

@router.get("/insights", response_model=List[KnowledgeInsight])
async def list_insights(category: Optional[str] = None):
    '''Получить список накопленных инсайтов (опыта) платформы.'''
    insights = list(_insights_db.values())
    if category:
        insights = [i for i in insights if i.category == category]
    return insights

@router.post("/insights", response_model=KnowledgeInsight, status_code=201)
async def create_insight(request: InsightCreateRequest):
    '''Добавить новый инсайт (вручную или автоматически от Experience Engine).'''
    insight_id = str(uuid4())
    insight = KnowledgeInsight(
        id=insight_id,
        category=request.category,
        title=request.title,
        description=request.description,
        confidence_score=request.confidence_score
    )
    _insights_db[insight_id] = insight
    return insight

@router.delete("/insights/{insight_id}", status_code=204)
async def delete_insight(insight_id: str):
    '''Удалить инсайт, если он устарел.'''
    if insight_id not in _insights_db:
        raise HTTPException(status_code=404, detail="Insight not found")
    del _insights_db[insight_id]
