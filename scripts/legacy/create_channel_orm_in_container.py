import pathlib

content = '''import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey

from core.database import Base


class ChannelORM(Base):
    """
    ORM-модель канала в PostgreSQL.
    Pydantic-модель ChannelConfig (core/models/channel.py) остаётся
    доменным/API контрактом и не меняется.
    """
    __tablename__ = "channels"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    platform = Column(String, default="telegram")
    language_search = Column(String, default="en")
    language_publish = Column(String, default="ru")
    style_profile = Column(String, default="minimal")
    timezone = Column(String, default="UTC")
    description = Column(String, nullable=True)

    # Sprint 14: Image profile configuration
    # mode: source_first / ai_only
    # source_image: use og:image from source_url
    # search_image: search by entity
    # ai_generation: fallback / off / always
    # require_relevance: validate image matches content
    # prefer_official: prefer official sources
    # style: news / anime / realistic
    image_profile = Column(JSON, nullable=True, default=dict)

    bot_token = Column(String, nullable=True)
    chat_id = Column(String, nullable=True)
    # Sprint 11: VK credentials
    vk_group_id = Column(String(50), nullable=True)
    vk_access_token = Column(String(255), nullable=True)

    # Sprint 11: YouTube credentials
    youtube_channel_id = Column(String(100), nullable=True)
    youtube_api_key = Column(String(255), nullable=True)
    youtube_access_token = Column(String, nullable=True)
    youtube_refresh_token = Column(String, nullable=True)

    # Sprint 11: Dzen credentials
    dzen_channel_id = Column(String(100), nullable=True)
    dzen_api_key = Column(String(255), nullable=True)

    is_connected = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    workflow_id = Column(String, nullable=True, index=True)

    # Sprint 8.2: ссылки на шаблон и профиль
    template_id = Column(String, ForeignKey("channel_templates.id"), nullable=True, index=True)
    profile_id = Column(String, ForeignKey("channel_profiles.id"), nullable=True, index=True)

    # Источники храним как JSON-массив
    sources = Column(JSON, default=list)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
'''

f = pathlib.Path('/app/core/models/channel_orm.py')
f.write_text(content, encoding='utf-8', newline='\n')
print('✅ channel_orm.py создан с правильной индентацией (LF, пробелы)')

# Проверяем синтаксис
import ast
ast.parse(content)
print('✅ Python syntax OK')
