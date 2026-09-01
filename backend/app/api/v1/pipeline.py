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
import backend.engines.register_news  # Автоматическая регистрация News strategies

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