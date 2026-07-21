from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/analytics", tags=["analytics"])

# === МОДЕЛИ ===

class AnalyticsOverview(BaseModel):
    '''Сводная BI-статистика для главной страницы аналитики.'''
    total_views: int = 0
    avg_ctr: float = 0.0
    avg_er: float = 0.0
    subscribers_growth: int = 0
    retention_rate: float = 0.0

class BestPerformer(BaseModel):
    '''Лучший показатель в конкретной категории.'''
    category: str # prompt, llm, topic, image_style, hour
    name: str
    score: float
    metric_name: str # e.g., "CTR", "Views"

class TimeSeriesPoint(BaseModel):
    date: str
    views: int
    ctr: float
    er: float

# === ЗАГЛУШКИ ДАННЫХ ===

@router.get("/overview", response_model=AnalyticsOverview)
async def get_analytics_overview():
    '''Получить общие метрики (CTR, ER, Retention, Просмотры, Подписчики).'''
    return AnalyticsOverview(
        total_views=132500,
        avg_ctr=6.4,
        avg_er=9.3,
        subscribers_growth=1240,
        retention_rate=88.5
    )

@router.get("/best-performers", response_model=List[BestPerformer])
async def get_best_performers():
    '''
    Узнать, что работает лучше всего.
    Отвечает на вопросы: Лучший Prompt, Лучший LLM, Лучшие часы, Лучшие темы.
    '''
    return [
        BestPerformer(category="prompt", name="telegram_news_v7", score=9.3, metric_name="ER"),
        BestPerformer(category="llm", name="Qwen3 32B", score=8.9, metric_name="Quality Score"),
        BestPerformer(category="hour", name="18:30", score=12.5, metric_name="CTR"),
        BestPerformer(category="topic", name="AI Safety", score=11.2, metric_name="Views"),
        BestPerformer(category="image_style", name="Illustration", score=10.5, metric_name="ER")
    ]

@router.get("/time-series", response_model=List[TimeSeriesPoint])
async def get_time_series(days: int = Query(7, ge=1, le=30)):
    '''Получить данные по дням для построения графиков.'''
    # В реальности здесь будет запрос к БД
    return [
        TimeSeriesPoint(date="2026-07-14", views=15000, ctr=5.1, er=7.9),
        TimeSeriesPoint(date="2026-07-15", views=18200, ctr=5.8, er=8.5),
        TimeSeriesPoint(date="2026-07-16", views=21000, ctr=6.4, er=9.3)
    ]
