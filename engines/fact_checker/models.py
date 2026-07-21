from pydantic import BaseModel, Field
from typing import List, Literal

class FactCheckResult(BaseModel):
    """
    Результат проверки фактов.
    Используется для строгого контроля галлюцинаций LLM.
    """
    
    # Итоговый вердикт
    status: Literal["Approved", "Rejected"] = Field(
        description="Итоговый статус: Approved (принято) или Rejected (отклонено)"
    )
    
    # Общая оценка от 0 до 100
    score: int = Field(
        ge=0, le=100, 
        description="Общий скор проверки от 0 до 100. Если < 80, статус должен быть Rejected"
    )
    
    # 5 обязательных проверок
    entities_valid: bool = Field(description="Все сущности из источника присутствуют, новых выдуманных сущностей нет")
    numbers_valid: bool = Field(description="Все цифры, даты и числа точно совпадают с источником")
    facts_valid: bool = Field(description="Нет выдуманных фактов, все утверждения есть в исходных фактах")
    headline_valid: bool = Field(description="Тема и заголовок поста соответствуют исходной статье")
    style_valid: bool = Field(description="Стиль соответствует заданному профилю (опционально)")
    
    # Детализация ошибок (если есть)
    missing_entities: List[str] = Field(default_factory=list, description="Сущности из источника, которые забыли упомянуть")
    hallucinated_entities: List[str] = Field(default_factory=list, description="Сущности, которых НЕ БЫЛО в источнике")
    hallucinated_facts: List[str] = Field(default_factory=list, description="Выдуманные факты, события или причинно-следственные связи")
    
    # Объяснение
    reasoning: str = Field(description="Краткое объяснение вердикта и причин снижения оценки")
