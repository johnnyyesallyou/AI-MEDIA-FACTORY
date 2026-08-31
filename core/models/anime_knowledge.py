"""Anime Knowledge Layer - Sprint 31.

Таблицы для хранения знаний об anime:
- anime_titles: уникальные произведения
- anime_episodes: эпизоды, привязанные к произведению
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship

from core.database import Base, PortableJSONB


class AnimeTitle(Base):
    """Уникальное произведение anime."""
    __tablename__ = "anime_titles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    canonical_title = Column(String(500), nullable=False, index=True)
    title_romaji = Column(String(500), index=True)
    title_english = Column(String(500), index=True)
    title_native = Column(String(500))
    title_slug = Column(String(500), index=True)

    # Sprint 66.4: Use PortableJSONB for SQLite and PostgreSQL compatibility
    # Все варианты названия: {"ja": "ワンピース", "en": "One Piece", "romaji": "ONE PIECE"}
    aliases = Column(PortableJSONB, default=dict)

    # Связь с внешними источниками: {"anilist": "21", "mal": "21"}
    external_ids = Column(PortableJSONB, default=dict)
    
    # Данные из разных источников (для cross-source enrichment)
    sources_data = Column(PortableJSONB, default=dict)

    description = Column(String, nullable=True)
    genres = Column(PortableJSONB, default=list)
    cover_url = Column(String, nullable=True)

    # Статус и сезон
    status = Column(String(50), nullable=True)  # RELEASING, FINISHED, etc.
    season = Column(String(20), nullable=True)  # WINTER, SPRING, SUMMER, FALL
    season_year = Column(Integer, nullable=True)
    episodes = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    episodes_list = relationship("AnimeEpisode", back_populates="anime_title")


class AnimeEpisode(Base):
    """Конкретный эпизод anime."""
    __tablename__ = "anime_episodes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    anime_title_id = Column(String, ForeignKey("anime_titles.id"), nullable=False, index=True)

    episode_number = Column(String(50), nullable=False)
    season_number = Column(Integer, default=1)

    source = Column(String(100), nullable=False)  # anilist, mal, etc.
    external_id = Column(String(255), nullable=False)
    language = Column(String(10), default="ja")

    title = Column(String(500), nullable=True)
    description = Column(String, nullable=True)

    aired_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    anime_title = relationship("AnimeTitle", back_populates="episodes_list")

    __table_args__ = (
        Index("idx_anime_episode_unique", "anime_title_id", "episode_number", "season_number", "source", unique=True),
    )
