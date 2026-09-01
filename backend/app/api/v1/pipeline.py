"""Sprint 67.3: Universal Pipeline API."""
import asyncio
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from core.models.channel_orm import ChannelORM
from core.models.channel_profile_orm import ChannelProfileORM
from core.models.archetypes import Archetype
from backend.engines.universal_pipeline import UniversalContentPipeline
from backend.engines.strategy_registry import get_strategies
import backend.engines.register_all  # Автоматическая регистрация News strategies

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/{channel_id}/run-universal")
async def run_universal_pipeline(
    channel_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Запустить Universal Pipeline для канала."""
    channel = db.query(ChannelORM).filter(ChannelORM.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    profile = None
    if channel.profile_id:
        profile = db.query(ChannelProfileORM).filter(
            ChannelProfileORM.id == channel.profile_id
        ).first()
    
    if not profile:
        raise HTTPException(
            status_code=400,
            detail=f"Channel {channel.name} has no profile assigned"
        )
    
    try:
        archetype = Archetype(profile.archetype)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown archetype: {profile.archetype}"
        )
    
    strategies = get_strategies(archetype)
    if not strategies:
        raise HTTPException(
            status_code=501,
            detail=f"No strategies for archetype: {archetype.value}"
        )
    
    # Sprint 69.3 fix: стратегии читают RSS из channel.content_profile,
    # но получают profile (ChannelProfileORM). Пробрасываем content_profile.
    if channel.content_profile and not getattr(profile, 'content_profile', None):
        profile.content_profile = channel.content_profile
    
    # Sprint 69.5: пробрасываем bot_token + chat_id для publishing
    if channel.bot_token and not getattr(profile, 'bot_token', None):
        profile.bot_token = channel.bot_token
    if channel.chat_id and not getattr(profile, 'chat_id', None):
        profile.chat_id = channel.chat_id
    # Sprint 69.5 fix: channel_id для привязки контента к каналу
    if not getattr(profile, 'channel_id', None):
        profile.channel_id = channel.id

    pipeline = UniversalContentPipeline(channel=channel, profile=profile)
    pipeline.set_strategy("research", strategies.research(profile))
    pipeline.set_strategy("generation", strategies.generation(profile))
    pipeline.set_strategy("media", strategies.media(profile))
    pipeline.set_strategy("publishing", strategies.publishing(profile))
    
    async def run_pipeline():
        result = await pipeline.run()
        return result
    
    background_tasks.add_task(run_pipeline)
    
    return {
        "channel_id": channel_id,
        "channel_name": channel.name,
        "archetype": archetype.value,
        "profile_name": profile.name,
        "status": "started",
    }


@router.get("/archetypes")
async def list_archetypes():
    """Список поддерживаемых архетипов."""
    from backend.engines.strategy_registry import list_registered_archetypes
    registered = list_registered_archetypes()
    
    return {
        "all_archetypes": [a.value for a in Archetype],
        "registered_archetypes": [a.value for a in registered],
        "total": len(registered),
    }