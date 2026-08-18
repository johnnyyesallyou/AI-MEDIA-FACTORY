import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer, JSON, ForeignKey

from core.database import Base


class ChannelTemplateORM(Base):
    """
    Шаблон канала — ЧТО делает канал.
    
    Содержит функциональные настройки: тематику, источники, workflow,
    модель, расписание, правила качества.
    
    Один шаблон может использоваться множеством каналов.
    """
    __tablename__ = "channel_templates"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String, nullable=True)
    category = Column(String, nullable=True)  # technology/ai, business, gaming, etc.

    # Языки и таймзона
    language_search = Column(String, default="en")
    language_publish = Column(String, default="ru")
    timezone = Column(String, default="Europe/Moscow")

    # Источники (JSON-массив KnowledgeSource)
    sources = Column(JSON, default=list)

    # Workflow (FK → workflows)
    workflow_id = Column(String, ForeignKey("workflows.id"), nullable=True, index=True)

    # Writing
    model = Column(String, default="llama3.1:8b")
    temperature = Column(String, default="0.7")  # хранится как строка для простоты

    # Automation
    cron_expression = Column(String, default="0 */2 * * *")
    max_posts_per_day = Column(Integer, default=10)

    # Quality
    minimum_quality_score = Column(Integer, default=70)
    auto_publish = Column(Boolean, default=True)
    human_review = Column(Boolean, default=False)

    # Retry policy (JSON)
    retry_policy = Column(JSON, default=dict)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)