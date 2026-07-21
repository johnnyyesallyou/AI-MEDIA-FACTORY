from typing import List, Dict
from uuid import uuid4
from ..models.prompt_tracking import GenerationRecord, PromptMetadata

class PromptExecutionLogger:
    """
    Логгер выполнений промптов. 
    В будущем будет заменен на реальный репозиторий (PostgreSQL).
    """
    
    def __init__(self):
        # In-memory хранилище для демонстрации
        self._records: Dict[str, GenerationRecord] = {}
    
    def log_generation(
        self,
        task_type: str,
        metadata: PromptMetadata,
        source_url: str,
        generated_content: str,
        fact_check_status: str = "Pending",
        fact_check_score: int = None
    ) -> GenerationRecord:
        """
        Создает и сохраняет запись о генерации.
        """
        record = GenerationRecord(
            id=str(uuid4()),
            task_type=task_type,
            prompt_category=metadata.category,
            prompt_name=metadata.name,
            prompt_version=metadata.version,
            prompt_hash=metadata.content_hash,
            source_url=source_url,
            generated_content=generated_content,
            fact_check_status=fact_check_status,
            fact_check_score=fact_check_score
        )
        
        self._records[record.id] = record
        return record
    
    def update_analytics(self, record_id: str, ctr: float, er: float, views: int):
        """
        Обновляет пост-фактум метрики из Telegram/аналитики.
        """
        if record_id in self._records:
            self._records[record_id].ctr = ctr
            self._records[record_id].engagement_rate = er
            self._records[record_id].views = views
    
    def get_analytics_summary(self) -> List[dict]:
        """
        Возвращает данные в формате, готовом для анализа (как в твоей таблице).
        """
        return [record.to_analytics_row() for record in self._records.values()]
