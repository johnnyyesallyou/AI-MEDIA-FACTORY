import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Index

from core.database import Base


class PipelineRunMetrics(Base):
    """Sprint 73.1: метрики одного прогона Universal Pipeline по каналу.

    Хранит тайминги по стадиям (в мс) и счётчики тем — для истории,
    агрегатов и поиска узких мест.
    """

    __tablename__ = "pipeline_run_metrics"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    channel_id = Column(String, nullable=False, index=True)
    channel_name = Column(String, nullable=True)
    execution_id = Column(String, nullable=True, index=True)

    # Тайминги по стадиям (миллисекунды)
    research_ms = Column(Integer, default=0)
    writing_ms = Column(Integer, default=0)
    media_ms = Column(Integer, default=0)
    publishing_ms = Column(Integer, default=0)
    total_ms = Column(Integer, default=0)

    # Счётчики
    topics_found = Column(Integer, default=0)
    topics_generated = Column(Integer, default=0)
    topics_published = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    success = Column(String, default="true")  # "true"/"false" (portable bool-as-string)

    # Sprint 73.3: агрегированные LLM-метрики прогона
    llm_calls = Column(Integer, default=0)
    llm_errors = Column(Integer, default=0)
    llm_latency_ms = Column(Integer, default=0)
    tokens_in = Column(Integer, default=0)
    tokens_out = Column(Integer, default=0)
    llm_model = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("idx_prm_channel_created", "channel_id", "created_at"),
    )

    def __repr__(self):
        return f"<PipelineRunMetrics {self.id} ch={self.channel_id} total={self.total_ms}ms>"
