from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum
from core.models.channel import ChannelConfig, KnowledgeSource, SourceType

# === REQUEST SCHEMAS ===

class ChannelCreateRequest(BaseModel):
    '''Схема для создания нового канала.'''
    name: str = Field(min_length=1, max_length=100)
    platform: str = Field(default="telegram", description="telegram, vk, youtube, etc.")
    language_search: str = Field(default="en")
    language_publish: str = Field(default="ru")
    style_profile: str = Field(default="minimal")
    timezone: str = Field(default="UTC", description="Часовой пояс канала")
    description: Optional[str] = None

class TelegramConnectionRequest(BaseModel):
    '''Схема для подключения Telegram бота.'''
    bot_token: str = Field(description="Bot Token от @BotFather")
    chat_id: Optional[str] = None  # Можно не указывать, система определит сама

class KnowledgeSourceCreateRequest(BaseModel):
    '''Схема для добавления источника знаний.'''
    name: str
    source_type: SourceType
    url: str
    priority: int = Field(ge=1, le=5, default=3)

class ChannelUpdateRequest(BaseModel):
    '''Схема для обновления канала.'''
    name: Optional[str] = None
    description: Optional[str] = None
    language_search: Optional[str] = None
    language_publish: Optional[str] = None
    style_profile: Optional[str] = None
    timezone: Optional[str] = None
    is_active: Optional[bool] = None

# === RESPONSE SCHEMAS ===

class ChannelResponse(BaseModel):
    '''Полный ответ с информацией о канале.'''
    id: str
    name: str
    platform: str
    language_search: str
    language_publish: str
    style_profile: str
    timezone: str
    description: Optional[str]
    is_connected: bool
    is_active: bool
    sources: List[KnowledgeSource]
    created_at: datetime
    updated_at: datetime

class ChannelListResponse(BaseModel):
    '''Список каналов для Dashboard.'''
    total: int
    channels: List[ChannelResponse]

class TelegramConnectionResponse(BaseModel):
    '''Результат проверки подключения к Telegram.'''
    success: bool
    chat_id: Optional[str] = None
    chat_title: Optional[str] = None
    bot_username: Optional[str] = None
    error: Optional[str] = None

class KnowledgeSourceResponse(BaseModel):
    '''Ответ с информацией об источнике.'''
    id: str
    name: str
    source_type: SourceType
    url: str
    priority: int
    is_active: bool


