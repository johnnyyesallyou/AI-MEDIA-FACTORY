"""News Knowledge Layer - Sprint 32.

NewsArticle модель для хранения уникальных статей.
Дедупликация по URL (canonical_url).
"""
from sqlalchemy import Column, String, Text, DateTime, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from datetime import datetime

from core.database import Base


class NewsArticle(Base):
    __tablename__ = "news_articles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Уникальный идентификатор статьи (URL)
    canonical_url = Column(String(512), unique=True, nullable=False, index=True)
    
    # Метаданные статьи
    title = Column(String(512), nullable=False)
    source_name = Column(String(128), nullable=False)  # "habr", "vc", "techcrunch"
    author = Column(String(256), nullable=True)
    
    # Изображения
    og_image_url = Column(String(1024), nullable=True)  # og:image из HTML
    cover_image_url = Column(String(1024), nullable=True)  # финальное изображение (может быть AI)
    
    # Контент
    summary = Column(Text, nullable=True)
    full_text = Column(Text, nullable=True)
    
    # Метаданные источника
    source_metadata = Column(JSON, nullable=True)  # произвольные данные от RSS/HTML
    tags = Column(JSON, nullable=True)  # теги/категории
    
    # Timestamps
    published_at = Column(DateTime, nullable=True)  # когда опубликовано на источнике
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<NewsArticle {self.source_name}: {self.title[:50]}>"