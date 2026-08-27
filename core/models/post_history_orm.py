"""Post History ORM - Sprint 57.

Отслеживание истории постов + метрики + learnings.
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from core.database import Base


class PostHistoryORM(Base):
    __tablename__ = "post_history"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    channel_id = Column(String, ForeignKey("channels.id"), nullable=False, index=True)
    content_id = Column(String, ForeignKey("content.id"), nullable=True)
    platform = Column(String(50))
    
    text = Column(Text)
    image_url = Column(String(2000))
    video_url = Column(String(2000))
    media_type = Column(String(50))  # 'image', 'video', 'none'
    
    message_id = Column(String(200))  # ID поста на платформе
    posted_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    metrics = relationship("PostMetricsORM", back_populates="post", cascade="all, delete-orphan")


class PostMetricsORM(Base):
    __tablename__ = "post_metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = Column(String, ForeignKey("post_history.id"), nullable=False, index=True)
    platform = Column(String(50))
    
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    reposts = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    
    engagement_rate = Column(Float, default=0.0)
    collected_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    post = relationship("PostHistoryORM", back_populates="metrics")


class ChannelLearningsORM(Base):
    __tablename__ = "channel_learnings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    channel_id = Column(String, ForeignKey("channels.id"), nullable=False, index=True)
    
    pattern = Column(String(500))  # e.g., "video_increases_views_by_50%"
    score = Column(Float)  # 0.0 - 1.0
    evidence_count = Column(Integer, default=1)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    metadata_json = Column(Text)  # JSON string с деталями