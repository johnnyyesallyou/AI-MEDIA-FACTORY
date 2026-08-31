"""Analytics models - Sprint 36.

Таблицы для хранения метрик engagement и A/B тестов.
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, ForeignKey, DateTime, Text,
    UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base, PortableJSONB


class PostMetric(Base):
    """Метрики поста (engagement, CTR, etc.)."""
    
    __tablename__ = "post_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    content_id = Column(String, ForeignKey("content.id"), nullable=False, index=True)
    channel_id = Column(String, nullable=False, index=True)
    platform = Column(String(50), nullable=False)
    
    # Engagement metrics
    views_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    
    # CTR metrics
    link_clicks = Column(Integer, default=0)
    button_clicks = Column(PortableJSONB, default=dict)
    
    # Timestamps
    measured_at = Column(DateTime, default=datetime.utcnow, index=True)
    period_hours = Column(Integer, default=24)
    
    # Extra metadata (не 'metadata' - зарезервировано!)
    extra_metadata = Column(PortableJSONB, default=dict)
    
    __table_args__ = (
        UniqueConstraint('content_id', 'measured_at', name='uq_post_metric_time'),
    )
    
    def __repr__(self):
        return f"<PostMetric {self.content_id} views={self.views_count}>"


class ABTest(Base):
    """A/B тест для сравнения форматов постов."""
    
    __tablename__ = "ab_tests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Test configuration
    variants = Column(PortableJSONB, nullable=False)  # [{id, name, config}]
    traffic_split = Column(PortableJSONB, nullable=False)  # {variant_id: percentage}
    scope = Column(PortableJSONB, default=dict)  # {channel_ids: [...], content_type: 'news'}
    
    # Status
    status = Column(String(50), default="draft")  # draft, running, completed
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    
    # Results
    winner_variant_id = Column(UUID(as_uuid=True))
    winner_metric = Column(String(100))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    results = relationship("ABTestResult", back_populates="test")
    
    def __repr__(self):
        return f"<ABTest {self.name} status={self.status}>"


class ABTestResult(Base):
    """Результаты A/B теста для конкретного поста."""
    
    __tablename__ = "ab_test_results"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(UUID(as_uuid=True), ForeignKey("ab_tests.id"), nullable=False, index=True)
    content_id = Column(String, ForeignKey("content.id"), nullable=False)
    variant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Metrics for this variant
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    test = relationship("ABTest", back_populates="results")
    
    def __repr__(self):
        return f"<ABTestResult test={self.test_id} variant={self.variant_id}>"