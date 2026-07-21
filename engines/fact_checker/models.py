from pydantic import BaseModel, Field
from typing import List

class FactCheckResult(BaseModel):
    is_valid: bool = Field(description="True, если пост не содержит галлюцинаций и соответствует фактам")
    accuracy_score: float = Field(description="Оценка точности от 0.0 до 1.0")
    missing_facts: List[str] = Field(description="Список важных фактов из источника, которые забыли упомянуть")
    hallucinations: List[str] = Field(description="Список утверждений в посте, которых НЕ БЫЛО в исходных фактах")
    reasoning: str = Field(description="Краткое объяснение вердикта")
