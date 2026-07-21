from pydantic import BaseModel, Field

class EvaluationResult(BaseModel):
    """
    Результат оценки качества сгенерированного поста независимой LLM-моделью (Judge).
    """
    
    # Детальные оценки от 0 до 100
    accuracy: int = Field(ge=0, le=100, description="Точность передачи смысла исходных фактов")
    clarity: int = Field(ge=0, le=100, description="Ясность, структурированность и читаемость текста")
    clickability: int = Field(ge=0, le=100, description="Кликбейтность/привлекательность заголовка и начала")
    telegram_style: int = Field(ge=0, le=100, description="Соответствие канонам Telegram-постов (эмодзи, абзацы, тон)")
    engagement_prediction: int = Field(ge=0, le=100, description="Прогноз вовлеченности аудитории (реакции, репосты)")
    
    # Итоговая оценка
    overall: int = Field(ge=0, le=100, description="Средневзвешенная или итоговая общая оценка")
    
    # Вердикт и обратная связь
    is_approved: bool = Field(description="True, если overall >= 80, иначе False")
    feedback_for_regeneration: str = Field(description="Конкретные рекомендации по улучшению, если is_approved = False")
