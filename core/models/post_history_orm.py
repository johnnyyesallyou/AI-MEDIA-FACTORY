"""Post History ORM - Sprint 57.

Таблицы для хранения истории постов и learnings.
ВАЖНО: метрики хранятся в существующей таблице post_metrics (core.models.analytics.PostMetric)
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from datetime import datetime
import uuid

from core.database import Base


class PostHistoryORM(Base):
    """История постов: что было опубликовано, когда, на какой платформе."""

    __tablename__ = "post_history"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    channel_id = Column(String, ForeignKey("channels.id"), nullable=False, index=True)
    content_id = Column(String, ForeignKey("content.id"), nullable=True)
    platform = Column(String(50))

    text = Column(Text)
    image_url = Column(String(2000))
    video_url = Column(String(2000))
    media_type = Column(String(50))  # 'image', 'video', 'none'

    message_id = Column(String(200))  # ID поста на платформе (для сбора метрик)
    posted_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ChannelLearningsORM(Base):
    """Learnings канала: паттерны которые работают (обучение на метриках)."""

    __tablename__ = "channel_learnings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    channel_id = Column(String, ForeignKey("channels.id"), nullable=False, index=True)

    pattern = Column(String(500))  # например "video_increases_views_by_50%"
    score = Column(Float)  # 0.0 - 1.0
    evidence_count = Column(Integer, default=1)
    last_updated = Column(DateTime, default=datetime.utcnow)

    metadata_json = Column(Text)  # JSON с деталями