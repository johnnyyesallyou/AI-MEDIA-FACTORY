import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey

from core.database import Base, PortableJSONB


class ChannelORM(Base):
    __tablename__ = "channels"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    platform = Column(String, default="telegram")
    language_search = Column(String, default="en")
    language_publish = Column(String, default="ru")
    style_profile = Column(String, default="minimal")
    timezone = Column(String, default="UTC")
    description = Column(String, nullable=True)

    bot_token = Column(String, nullable=True)
    chat_id = Column(String, nullable=True)
    vk_group_id = Column(String(50), nullable=True)
    vk_access_token = Column(String(255), nullable=True)

    youtube_channel_id = Column(String(100), nullable=True)
    youtube_api_key = Column(String(255), nullable=True)
    youtube_access_token = Column(String, nullable=True)
    youtube_refresh_token = Column(String, nullable=True)

    dzen_channel_id = Column(String(100), nullable=True)
    dzen_api_key = Column(String(255), nullable=True)

    is_connected = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    workflow_id = Column(String, nullable=True, index=True)

    template_id = Column(String, ForeignKey("channel_templates.id"), nullable=True, index=True)
    profile_id = Column(String, ForeignKey("channel_profiles.id"), nullable=True, index=True)

    # Sprint 66.4: Use PortableJSONB for SQLite and PostgreSQL compatibility
    sources = Column(PortableJSONB, default=list)
    content_profile = Column(PortableJSONB, nullable=True)
    image_profile = Column(PortableJSONB, nullable=True, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
