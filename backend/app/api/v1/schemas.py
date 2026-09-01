from pydantic import BaseModel, Field, ConfigDict
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
    workflow_id: Optional[str] = Field(default=None, description="Идентификатор workflow шаблона для канала")
    description: Optional[str] = None

    # Sprint 69: Telegram credentials (для публикации)
    bot_token: Optional[str] = None
    chat_id: Optional[str] = None

class TelegramConnectionRequest(BaseModel):
    '''Схема для подключения Telegram бота.'''
    bot_token: str = Field(description="Bot Token от @BotFather")
    chat_id: Optional[str] = None  # Можно не указывать, система определит сама



class VkConnectionRequest(BaseModel):
    '''Схема для подключения VK группы.'''
    group_id: str = Field(description="ID группы VK (например: -123456789 или my_group)")
    access_token: str = Field(description="Access token с правами wall, groups")


class YoutubeConnectionRequest(BaseModel):
    '''Схема для подключения YouTube канала.'''
    channel_id: str = Field(description="ID YouTube канала")
    api_key: str = Field(description="YouTube Data API v3 key")


class DzenConnectionRequest(BaseModel):
    '''Схема для подключения Дзен канала.'''
    channel_id: str = Field(description="ID Дзен канала")
    api_key: str = Field(description="Дзен API key")


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
    workflow_id: Optional[str] = None
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
    workflow_id: Optional[str] = None
    description: Optional[str]
    is_connected: bool
    is_active: bool
    bot_token: Optional[str] = None
    bot_token: Optional[str] = None
    chat_id: Optional[str] = None
    # Sprint 11: VK credentials
    vk_group_id: Optional[str] = None
    vk_access_token: Optional[str] = None
    # Sprint 11: YouTube credentials
    youtube_channel_id: Optional[str] = None
    youtube_api_key: Optional[str] = None
    # Sprint 11: Dzen credentials
    dzen_channel_id: Optional[str] = None
    dzen_api_key: Optional[str] = None
    sources: List[KnowledgeSource]
    created_at: datetime
    updated_at: datetime
    content_profile: Optional[dict] = None

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

class WorkflowCreateRequest(BaseModel):
    '''Схема для создания workflow шаблона.'''
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    definition: dict = Field(default_factory=dict, description="JSON-описание workflow graph")
    is_active: bool
    bot_token: Optional[str] = None
    bot_token: Optional[str] = None
    chat_id: Optional[str] = None


class WorkflowResponse(BaseModel):
    '''Ответ с workflow шаблоном.'''
    id: str
    name: str
    description: Optional[str]
    definition: dict
    is_active: bool
    bot_token: Optional[str] = None
    bot_token: Optional[str] = None
    chat_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class WorkflowListResponse(BaseModel):
    '''Список workflow шаблонов для Dashboard.'''
    total: int
    items: List[WorkflowResponse]


class KnowledgeSourceResponse(BaseModel):
    '''Ответ с информацией об источнике.'''
    id: str
    name: str
    source_type: SourceType
    url: str
    priority: int
    is_active: bool
    bot_token: Optional[str] = None
    bot_token: Optional[str] = None
    chat_id: Optional[str] = None




# === SCHEDULE SCHEMAS ===

class ChannelScheduleRequest(BaseModel):
    cron_expression: str = Field(default="0 */3 * * *")
    timezone: str = Field(default="Europe/Moscow")
    max_posts_per_day: int = Field(default=3, ge=1, le=50)
    auto_publish: bool = True
    is_active: bool = True

class ChannelScheduleResponse(BaseModel):
    id: str
    channel_id: str
    cron_expression: str
    timezone: str
    max_posts_per_day: int
    auto_publish: bool
    is_active: bool
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None


# ============ SPRINT 8.2: CHANNEL PROFILES ============

class ChannelProfileBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    platform: str = Field(default="telegram")
    audience: Optional[str] = None
    tone: Optional[str] = None
    format: Optional[str] = None
    emoji_usage: Optional[str] = None
    length_chars: int = Field(default=900, ge=100, le=10000)
    call_to_action: Optional[str] = None
    forbidden_words: List[str] = Field(default_factory=list)
    example: Optional[str] = None


class ChannelProfileCreate(ChannelProfileBase):
    pass


class ChannelProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    platform: Optional[str] = None
    audience: Optional[str] = None
    tone: Optional[str] = None
    format: Optional[str] = None
    emoji_usage: Optional[str] = None
    length_chars: Optional[int] = Field(None, ge=100, le=10000)
    call_to_action: Optional[str] = None
    forbidden_words: Optional[List[str]] = None
    example: Optional[str] = None
    is_active: Optional[bool] = None


class ChannelProfileResponse(ChannelProfileBase):
    id: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============ SPRINT 8.2: CHANNEL TEMPLATES ============

class KnowledgeSourceModel(BaseModel):
    id: str
    name: str
    source_type: str
    url: str
    priority: int = Field(ge=1, le=5)


class RetryPolicyModel(BaseModel):
    max_retries: int = Field(default=3, ge=0, le=10)
    backoff_factor: float = Field(default=2.0, ge=1.0, le=10.0)
    base_delay: float = Field(default=5.0, ge=0.1)


class ChannelTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = None
    language_search: str = Field(default="en")
    language_publish: str = Field(default="ru")
    timezone: str = Field(default="Europe/Moscow")
    sources: List[KnowledgeSourceModel] = Field(default_factory=list)
    workflow_id: Optional[str] = None
    model: str = Field(default="llama3.1:8b")
    temperature: str = Field(default="0.7")
    cron_expression: str = Field(default="0 */2 * * *")
    max_posts_per_day: int = Field(default=10, ge=1, le=100)
    minimum_quality_score: int = Field(default=70, ge=0, le=100)
    auto_publish: bool = Field(default=True)
    human_review: bool = Field(default=False)
    retry_policy: RetryPolicyModel = Field(default_factory=RetryPolicyModel)


class ChannelTemplateCreate(ChannelTemplateBase):
    pass


class ChannelTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = None
    language_search: Optional[str] = None
    language_publish: Optional[str] = None
    timezone: Optional[str] = None
    sources: Optional[List[KnowledgeSourceModel]] = None
    workflow_id: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[str] = None
    cron_expression: Optional[str] = None
    max_posts_per_day: Optional[int] = Field(None, ge=1, le=100)
    minimum_quality_score: Optional[int] = Field(None, ge=0, le=100)
    auto_publish: Optional[bool] = None
    human_review: Optional[bool] = None
    retry_policy: Optional[RetryPolicyModel] = None
    is_active: Optional[bool] = None


class ChannelTemplateResponse(ChannelTemplateBase):
    id: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplyTemplateRequest(BaseModel):
    template_id: str
    profile_id: str


class ApplyTemplateResponse(BaseModel):
    status: str
    channel_id: str
    channel_name: str
    template_name: str
    profile_name: str
    message: Optional[str] = None
