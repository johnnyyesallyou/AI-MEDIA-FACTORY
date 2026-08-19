"""Manga Source State - tracks last seen chapters per title per source."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB

from core.database import Base


class MangaSourceStateORM(Base):
    """
    Tracks the last seen chapter for each manga title from each source.
    
    Used by ChapterDetector to identify NEW chapters (deduplication).
    
    Unique constraint: (source, title_id) - one state per title per source.
    
    Sprint 15: Manga Chapter Release
    """
    __tablename__ = "manga_source_states"
    __table_args__ = (
        UniqueConstraint("source", "title_id", name="uq_manga_source_state_source_title"),
        Index("ix_manga_source_states_source", "source"),
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Source identifier (e.g., "remanga", "zazaza")
    source = Column(String, nullable=False, index=True)
    
    # Title identifier within the source
    title_id = Column(String, nullable=False, index=True)
    
    # Title metadata
    title_name = Column(String(255), nullable=False)
    title_name_en = Column(String(255), nullable=True)
    title_slug = Column(String(255), nullable=True)
    title_url = Column(String(500), nullable=True)
    cover_url = Column(String(500), nullable=True)
    
    # Last seen chapter
    last_chapter_number = Column(String(50), nullable=True)
    last_chapter_id = Column(String(100), nullable=True)
    last_chapter_url = Column(String(500), nullable=True)
    
    # Timestamps
    last_seen_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    first_seen_at = Column(DateTime, default=datetime.utcnow)
    
    # Statistics
    total_chapters_seen = Column(Integer, default=1)
    
    # Extra metadata (JSONB)
    extra_data = Column(JSONB, nullable=True, default=dict)
    
    def __repr__(self):
        return f"<MangaSourceState(source={self.source}, title={self.title_name}, chapter={self.last_chapter_number})>"
