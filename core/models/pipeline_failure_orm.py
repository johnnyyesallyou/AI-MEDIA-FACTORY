"""
Sprint 66.5: Pipeline Failure Tracking ORM Model

Таблица для отслеживания всех ошибок в pipeline:
- timeout
- exception
- rate_limit
- network
- validation
- llm_error
- media_error
- publish_error
- unknown
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, Index, Boolean
from sqlalchemy.dialects.postgresql import JSONB

from core.database import Base, PortableJSONB


class PipelineFailure(Base):
    """Журнал ошибок pipeline - для отслеживания failures во время работы каналов"""
    
    __tablename__ = "pipeline_failures"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Идентификаторы
    channel_id = Column(String, nullable=False, index=True)
    execution_id = Column(String, nullable=True, index=True)  # Трассировка через систему
    job_id = Column(String, nullable=True, index=True)
    
    # Описание ошибки
    pipeline = Column(String, nullable=False)  # research, generation, media, publishing, learning
    job = Column(String, nullable=False)  # fetch_sources, generate_post, format_media, publish_telegram, record_metrics
    
    error_type = Column(String, nullable=False, index=True)  # timeout, exception, rate_limit, network, validation, llm_error, media_error, publish_error, unknown
    error_message = Column(Text, nullable=False)  # Полное сообщение об ошибке
    error_code = Column(String, nullable=True)  # HTTP status или custom code
    
    # Попытки
    attempt = Column(Integer, default=1)  # Номер попытки
    max_attempts = Column(Integer, default=3)
    retry_at = Column(DateTime, nullable=True)  # Когда будет следующая попытка
    
    # Дополнительный контекст
    context = Column(PortableJSONB, nullable=True, default=dict)  # {request_data, response, headers, etc}
    
    # Статус
    resolved = Column(Boolean, default=False)  # Была ли ошибка разрешена
    resolved_at = Column(DateTime, nullable=True)
    resolution = Column(Text, nullable=True)  # Как была разрешена (retry_success, manual_fix, etc)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Индексы для быстрого поиска
    __table_args__ = (
        Index("idx_channel_error_type", "channel_id", "error_type"),
        Index("idx_execution_id", "execution_id"),
        Index("idx_pipeline_job", "pipeline", "job"),
        Index("idx_created_at", "created_at"),
        Index("idx_unresolved", "resolved", "created_at"),  # Для dashboard неразрешённых ошибок
    )
    
    def __repr__(self):
        return f"<PipelineFailure {self.id} ch={self.channel_id} err={self.error_type}>"
    
    def is_retryable(self) -> bool:
        """Можно ли повторить эту ошибку?"""
        retryable_types = {
            "timeout",
            "rate_limit",
            "network",
            "llm_error",  # Если LLM временно недоступен
        }
        return self.error_type in retryable_types and self.attempt < self.max_attempts
    
    def mark_resolved(self, resolution: str = "success") -> None:
        """Отметить ошибку как разрешённую"""
        self.resolved = True
        self.resolved_at = datetime.utcnow()
        self.resolution = resolution
