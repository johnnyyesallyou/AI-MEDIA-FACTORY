import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text
from core.database import Base

class ExecutionLogORM(Base):
    """ORM-модель для трассировки выполнения пайплайна."""
    __tablename__ = "execution_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String, nullable=False, index=True)
    channel_id = Column(String, nullable=True)
    content_id = Column(String, nullable=True)
    headline = Column(String, nullable=True)
    
    # Этап пайплайна: research, writing, evaluation, publish
    stage = Column(String, nullable=False)
    
    # Статус: started, success, failed, skipped
    status = Column(String, nullable=False, default="started")
    
    # Время выполнения
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    
    # Детали и ошибки
    details = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
