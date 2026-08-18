from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime

class SourceType(str, Enum):
    RSS = "rss"
    REDDIT = "reddit"
    HACKER_NEWS = "hacker_news"
    ARXIV = "arxiv"
    GITHUB = "github"
    YOUTUBE = "youtube"
    GOOGLE_NEWS = "google_news"
    CUSTOM_BLOG = "custom_blog"
    RAG_DOCUMENT = "rag_document"

class KnowledgeSource(BaseModel):
    """
    Источник знаний с приоритетом доверия.
    """
    id: str
    name: str
    source_type: SourceType
    url: str
    priority: int = Field(ge=1, le=5, description="Приоритет источника от 1 (низкий) до 5 (высший)")
    is_active: bool = True

class ChannelConfig(BaseModel):
    """
    Полная конфигурация медиа-канала.
    """
    id: str
    name: str
    platform: str = Field(default="telegram", description="telegram, vk, youtube, etc.")
    language_search: str = Field(default="en", description="Язык поиска источников")
    language_publish: str = Field(default="ru", description="Язык публикации")
    style_profile: str = Field(default="minimal", description="Стиль: openai, techcrunch, vc, minimal, expert")
    timezone: str = Field(default="UTC", description="Часовой пояс канала")
    description: Optional[str] = None
    
    # Интеграции (заглушки для API ключей, в реальности хранить в Secrets Manager)
    bot_token: Optional[str] = None
    chat_id: Optional[str] = None
    is_connected: bool = False
    
    # Источники для этого канала
    sources: List[KnowledgeSource] = []
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
