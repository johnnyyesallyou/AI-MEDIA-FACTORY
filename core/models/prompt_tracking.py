from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PromptMetadata(BaseModel):
    """
    Метаданные загруженного промпта.
    Позволяют точно знать, какая версия и с каким содержимым была использована.
    """
    category: str = Field(description="Категория промпта, например 'writing'")
    name: str = Field(description="Имя промпта, например 'telegram_news'")
    version: str = Field(description="Версия промпта, например 'v1', 'v2'")
    file_path: str = Field(description="Путь к файлу промпта")
    content_hash: str = Field(description="SHA-256 хэш содержимого файла для контроля незаметных изменений")
    loaded_at: datetime = Field(default_factory=datetime.utcnow)


class GenerationRecord(BaseModel):
    """
    Запись о генерации для аналитики и Prompt Lab.
    Позволяет связать результат с конкретной версией промпта и оценивать её эффективность.
    """
    id: str = Field(description="Уникальный идентификатор генерации (UUID)")
    task_type: str = Field(description="Тип задачи, например 'telegram_news_generation'")
    
    # Данные о промпте
    prompt_category: str
    prompt_name: str
    prompt_version: str
    prompt_hash: str
    
    # Входные и выходные данные
    source_url: str
    generated_content: str
    
    # Результаты проверок (Sprint 7.2 и 7.3)
    fact_check_status: str = Field(default="Pending", description="Approved / Rejected / Pending")
    fact_check_score: Optional[int] = Field(default=None, ge=0, le=100)
    evaluator_score: Optional[float] = Field(default=None, ge=0.0, le=10.0, description="Оценка от LLM Evaluator")
    
    # Метаданные времени
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # === ПОЛЯ ДЛЯ БУДУЩЕЙ АНАЛИТИКИ (заполняются постфактум из Telegram API) ===
    ctr: Optional[float] = Field(default=None, description="Click-Through Rate (%)")
    engagement_rate: Optional[float] = Field(default=None, description="Engagement Rate (%)")
    views: Optional[int] = Field(default=None, description="Количество просмотров")
    
    def to_analytics_row(self) -> dict:
        """
        Формирует строку для выгрузки в аналитику (CSV/БД).
        """
        return {
            "prompt_version": f"{self.prompt_name}_{self.prompt_version}",
            "prompt_hash": self.prompt_hash,
            "fact_check_status": self.fact_check_status,
            "fact_check_score": self.fact_check_score,
            "evaluator_score": self.evaluator_score,
            "ctr": self.ctr,
            "engagement_rate": self.engagement_rate,
            "views": self.views,
            "created_at": self.created_at.isoformat()
        }
