from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import uuid4
from datetime import datetime

from .schemas import (
    ChannelCreateRequest,
    ChannelUpdateRequest,
    ChannelResponse,
    ChannelListResponse,
    TelegramConnectionRequest,
    TelegramConnectionResponse,
    KnowledgeSourceCreateRequest,
    KnowledgeSourceResponse
)
from core.models.channel import ChannelConfig, KnowledgeSource

router = APIRouter(prefix="/channels", tags=["channels"])

# In-memory хранилище для демонстрации (в реальности - PostgreSQL)
_channels_db = {}

@router.post("/", response_model=ChannelResponse, status_code=201)
async def create_channel(request: ChannelCreateRequest):
    '''Создать новый канал.'''
    channel_id = str(uuid4())
    
    channel = ChannelConfig(
        id=channel_id,
        name=request.name,
        platform=request.platform,
        language_search=request.language_search,
        language_publish=request.language_publish,
        style_profile=request.style_profile,
        timezone=request.timezone,
        description=request.description,
        sources=[]
    )
    
    _channels_db[channel_id] = channel
    
    return ChannelResponse(
        id=channel.id,
        name=channel.name,
        platform=channel.platform,
        language_search=channel.language_search,
        language_publish=channel.language_publish,
        style_profile=channel.style_profile,
        timezone=channel.timezone,
        description=channel.description,
        is_connected=channel.is_connected,
        is_active=True,
        sources=channel.sources,
        created_at=channel.created_at,
        updated_at=channel.updated_at
    )

@router.get("/", response_model=ChannelListResponse)
async def list_channels():
    '''Получить список всех каналов.'''
    channels = list(_channels_db.values())
    
    return ChannelListResponse(
        total=len(channels),
        channels=[
            ChannelResponse(
                id=c.id,
                name=c.name,
                platform=c.platform,
                language_search=c.language_search,
                language_publish=c.language_publish,
                style_profile=c.style_profile,
                timezone=c.timezone,
                description=c.description,
                is_connected=c.is_connected,
                is_active=True,
                sources=c.sources,
                created_at=c.created_at,
                updated_at=c.updated_at
            )
            for c in channels
        ]
    )

@router.get("/{channel_id}", response_model=ChannelResponse)
async def get_channel(channel_id: str):
    '''Получить информацию о канале.'''
    if channel_id not in _channels_db:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    channel = _channels_db[channel_id]
    
    return ChannelResponse(
        id=channel.id,
        name=channel.name,
        platform=channel.platform,
        language_search=channel.language_search,
        language_publish=channel.language_publish,
        style_profile=channel.style_profile,
        timezone=channel.timezone,
        description=channel.description,
        is_connected=channel.is_connected,
        is_active=True,
        sources=channel.sources,
        created_at=channel.created_at,
        updated_at=channel.updated_at
    )

@router.put("/{channel_id}", response_model=ChannelResponse)
async def update_channel(channel_id: str, request: ChannelUpdateRequest):
    '''Обновить настройки канала.'''
    if channel_id not in _channels_db:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    channel = _channels_db[channel_id]
    
    if request.name is not None:
        channel.name = request.name
    if request.description is not None:
        channel.description = request.description
    if request.language_search is not None:
        channel.language_search = request.language_search
    if request.language_publish is not None:
        channel.language_publish = request.language_publish
    if request.style_profile is not None:
        channel.style_profile = request.style_profile
    if request.timezone is not None:
        channel.timezone = request.timezone
    
    channel.updated_at = datetime.utcnow()
    
    return ChannelResponse(
        id=channel.id,
        name=channel.name,
        platform=channel.platform,
        language_search=channel.language_search,
        language_publish=channel.language_publish,
        style_profile=channel.style_profile,
        timezone=channel.timezone,
        description=channel.description,
        is_connected=channel.is_connected,
        is_active=True,
        sources=channel.sources,
        created_at=channel.created_at,
        updated_at=channel.updated_at
    )

@router.delete("/{channel_id}", status_code=204)
async def delete_channel(channel_id: str):
    '''Удалить канал.'''
    if channel_id not in _channels_db:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    del _channels_db[channel_id]

@router.post("/{channel_id}/connect-telegram", response_model=TelegramConnectionResponse)
async def connect_telegram(channel_id: str, request: TelegramConnectionRequest):
    '''
    Подключить Telegram бота к каналу.
    В реальности здесь будет вызов Telegram Bot API для проверки токена и получения Chat ID.
    '''
    if channel_id not in _channels_db:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    channel = _channels_db[channel_id]
    
    # ЗАГЛУШКА: В реальности здесь будет:
    # 1. Вызов getMe() для проверки токена
    # 2. Вызов getUpdates() или getChat() для получения chat_id
    # 3. Проверка, что бот является администратором канала
    
    # Имитация успешного подключения
    channel.bot_token = request.bot_token
    channel.chat_id = request.chat_id or "auto_detected_chat_id"
    channel.is_connected = True
    channel.updated_at = datetime.utcnow()
    
    return TelegramConnectionResponse(
        success=True,
        chat_id=channel.chat_id,
        chat_title=channel.name,
        bot_username="ai_media_factory_bot",
        error=None
    )

@router.post("/{channel_id}/sources", response_model=KnowledgeSourceResponse)
async def add_knowledge_source(channel_id: str, request: KnowledgeSourceCreateRequest):
    '''Добавить источник знаний к каналу.'''
    if channel_id not in _channels_db:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    channel = _channels_db[channel_id]
    
    source = KnowledgeSource(
        id=str(uuid4()),
        name=request.name,
        source_type=request.source_type,
        url=request.url,
        priority=request.priority,
        is_active=True
    )
    
    channel.sources.append(source)
    channel.updated_at = datetime.utcnow()
    
    return KnowledgeSourceResponse(
        id=source.id,
        name=source.name,
        source_type=source.source_type,
        url=source.url,
        priority=source.priority,
        is_active=source.is_active
    )

@router.get("/{channel_id}/sources", response_model=List[KnowledgeSourceResponse])
async def list_knowledge_sources(channel_id: str):
    '''Получить список источников знаний канала.'''
    if channel_id not in _channels_db:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    channel = _channels_db[channel_id]
    
    return [
        KnowledgeSourceResponse(
            id=s.id,
            name=s.name,
            source_type=s.source_type,
            url=s.url,
            priority=s.priority,
            is_active=s.is_active
        )
        for s in channel.sources
    ]

