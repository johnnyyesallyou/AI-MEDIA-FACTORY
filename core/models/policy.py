from pydantic import BaseModel, Field
from typing import Optional

class ChannelPolicy(BaseModel):
    """
    Правила, регулирующие поведение AI для конкретного канала.
    Позволяют менять логику без изменения кода.
    """
    channel_id: str
    
    # Временные ограничения
    max_posts_per_day: int = Field(default=5, ge=1, le=20, description="Максимум публикаций в сутки")
    publish_start_hour: int = Field(default=8, ge=0, le=23, description="Начало окна публикаций")
    publish_end_hour: int = Field(default=22, ge=0, le=23, description="Конец окна публикаций")
    max_news_age_hours: int = Field(default=24, ge=1, description="Не публиковать новости старше N часов")
    
    # Ограничения на дубликаты
    max_posts_per_topic_per_day: int = Field(default=1, ge=1, description="Максимум постов на одну тему в сутки")
    
    # Пороги качества (интеграция со Sprint 7)
    min_fact_check_score: int = Field(default=90, ge=0, le=100, description="Минимальный скор Fact Checker")
    min_quality_score: int = Field(default=85, ge=0, le=100, description="Минимальный скор LLM Evaluator")
    
    # Игнорирование низкокачественных источников
    ignore_sources_below_priority: int = Field(default=2, ge=1, le=5, description="Игнорировать источники с приоритетом ниже этого")
