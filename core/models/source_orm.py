"""Source Registry ORM - Sprint 76.4.

Хранит информацию об источниках (RSS фидах) с метриками качества,
успешности и историей использования.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Index

from core.database import Base, PortableJSONB


class SourceORM(Base):
    """Registered RSS source with quality metrics."""

    __tablename__ = "sources"

    # Identity
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    canonical_url = Column(String(500), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    source_type = Column(String(50), default="rss")  # rss, atom, subscribe_ru, known_sources

    # Metadata
    language = Column(String(10), default="ru", index=True)
    category = Column(String(100), nullable=True, index=True)
    description = Column(String, nullable=True)

    # Capabilities (stored as JSON for flexibility)
    capabilities = Column(PortableJSONB, default=list)  # ["articles", "covers", "summaries"]
    topics = Column(PortableJSONB, default=list)

    # Quality and reliability
    quality_score = Column(Float, default=50.0)  # 0..100
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    success_rate = Column(Float, nullable=True)  # success_count / (success_count + failure_count)

    # Usage tracking
    selection_count = Column(Integer, default=0)  # How many times selected
    last_selected_at = Column(DateTime, nullable=True)
    last_successful_fetch_at = Column(DateTime, nullable=True)
    last_failed_fetch_at = Column(DateTime, nullable=True)

    # Status
    is_active = Column(Boolean, default=True, index=True)
    validation_status = Column(String(50), default="unknown")  # unknown, valid, invalid, error
    disabled_reason = Column(String, nullable=True)

    # Source origin tracking
    discovered_from = Column(String(50), nullable=True)  # "subscribe_ru", "manual", "known_sources"
    discovered_at = Column(DateTime, default=datetime.utcnow)

    # Metadata for platform-specific information
    platform_metadata = Column(PortableJSONB, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    health_checked_at = Column(DateTime, nullable=True)

    # Indices for common queries
    __table_args__ = (
        Index('ix_sources_language_category', 'language', 'category'),
        Index('ix_sources_quality_score_active', 'quality_score', 'is_active'),
        Index('ix_sources_last_selected', 'last_selected_at'),
    )

    def __repr__(self):
        return f"<SourceORM(id={self.id[:8]}..., name={self.name}, quality={self.quality_score})>"

    def update_quality_metrics(self, outcome: str, items_count: int = 0):
        """Update quality metrics based on fetch outcome.

        Args:
            outcome: "success" or "failure"
            items_count: Number of items fetched (for "success")
        """
        if outcome == "success":
            self.success_count += 1
            self.last_successful_fetch_at = datetime.utcnow()
        elif outcome == "failure":
            self.failure_count += 1
            self.last_failed_fetch_at = datetime.utcnow()

        # Update success rate
        total = self.success_count + self.failure_count
        if total > 0:
            self.success_rate = self.success_count / total

        # Update quality score (simple formula, can be improved)
        # Base 50 + success_rate * 50 - penalty for failures
        base_quality = 50.0
        success_bonus = (self.success_rate or 0.0) * 50.0 if self.success_rate else 0.0
        failure_penalty = min(50.0, self.failure_count * 2.0)  # Max penalty 50
        self.quality_score = max(0.0, min(100.0, base_quality + success_bonus - failure_penalty))

        self.updated_at = datetime.utcnow()

    def record_selection(self):
        """Record that this source was selected for use."""
        self.selection_count += 1
        self.last_selected_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def mark_validation_status(self, status: str, error: str = None):
        """Mark validation status of this source.

        Args:
            status: "valid", "invalid", "error", "unknown"
            error: Optional error message
        """
        self.validation_status = status
        if error:
            self.disabled_reason = error
        self.updated_at = datetime.utcnow()

    def disable(self, reason: str):
        """Disable this source."""
        self.is_active = False
        self.disabled_reason = reason
        self.updated_at = datetime.utcnow()

    def enable(self):
        """Enable this source."""
        self.is_active = True
        self.disabled_reason = None
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'canonical_url': self.canonical_url,
            'name': self.name,
            'source_type': self.source_type,
            'language': self.language,
            'category': self.category,
            'quality_score': self.quality_score,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'success_rate': self.success_rate,
            'selection_count': self.selection_count,
            'is_active': self.is_active,
            'validation_status': self.validation_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
