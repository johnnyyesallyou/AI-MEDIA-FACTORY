import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON

from core.database import Base


class WorkflowORM(Base):
    """ORM-модель workflow, хранящего граф процесса как данные."""
    __tablename__ = "workflows"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String, nullable=True)
    definition = Column(JSON, nullable=False, default=dict)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
