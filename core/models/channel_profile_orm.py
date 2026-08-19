import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer, JSON

from core.database import Base


class ChannelProfileORM(Base):
    """
    Профиль канала — КАК канал "звучит".
    
    Содержит стилистические настройки: тон, аудиторию, формат,
    использование эмодзи, длину постов, CTA, запрещённые слова.
    
    Один профиль может использоваться множеством шаблонов/каналов.
    """
    __tablename__ = "channel_profiles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String, nullable=True)

    # Платформа (telegram, vk, dzen, youtube)
    platform = Column(String, default="telegram")

    # Стиль
    audience = Column(String, nullable=True)
    tone = Column(String, nullable=True)
    format = Column(String, nullable=True)
    emoji_usage = Column(String, nullable=True)
    length_chars = Column(Integer, default=900)
    call_to_action = Column(String, nullable=True)

    # Запрещённые слова (JSON-массив)
    forbidden_words = Column(JSON, default=list)

    # Пример поста
    example = Column(String, nullable=True)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)