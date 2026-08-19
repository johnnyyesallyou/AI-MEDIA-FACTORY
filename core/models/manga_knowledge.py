"""Manga Knowledge Layer - Sprint 23.

Таблицы для хранения знаний о манге:
- manga_titles: уникальные произведения (canonical + aliases)
- manga_chapters: главы, привязанные к произведению
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, JSON, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from core.database import Base


class MangaTitle(Base):
    """Уникальное произведение манги."""
    __tablename__ = "manga_titles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    canonical_title = Column(String(500), nullable=False, index=True)
    title_slug = Column(String(500), index=True)
    
    # Все варианты названия: {"ru": "Ван Пис", "en": "One Piece", "ja": "ワンピース"}
    aliases = Column(JSONB, default=dict)
    
    # Связь с внешними источниками: {"remanga": "12345", "mangadex": "abc-123"}
    external_ids = Column(JSONB, default=dict)
    # Сырые данные из каждого источника (Sprint 26)
    sources_data = Column(JSONB, default=dict)
    
    description = Column(String, nullable=True)
    genres = Column(JSONB, default=list)
    cover_url = Column(String, nullable=True)
    cover_asset_id = Column(String, nullable=True)
    
    # Языки доступных глав
    available_languages = Column(JSONB, default=list)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    chapters = relationship("MangaChapter", back_populates="manga_title")


class MangaChapter(Base):
    """Конкретная глава произведения."""
    __tablename__ = "manga_chapters"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    manga_title_id = Column(String, ForeignKey("manga_titles.id"), nullable=False, index=True)
    
    chapter_number = Column(String(50), nullable=False)
    volume = Column(String(50), nullable=True)
    
    source = Column(String(100), nullable=False)  # remanga, mangadex
    external_id = Column(String(255), nullable=False)
    language = Column(String(10), default="ru")
    
    url = Column(String, nullable=True)
    
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    manga_title = relationship("MangaTitle", back_populates="chapters")
    
    __table_args__ = (
        Index("idx_chapter_unique", "manga_title_id", "chapter_number", "source", "language", unique=True),
    )