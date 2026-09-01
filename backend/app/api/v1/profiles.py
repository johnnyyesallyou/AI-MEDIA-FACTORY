"""Sprint 67.2 + 67.5: ChannelProfile CRUD + Templates + Assign API."""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from core.models.channel_profile_orm import ChannelProfileORM
from core.models.channel_orm import ChannelORM
from core.models.archetypes import Archetype, get_archetype_defaults
from backend.app.api.v1.channel_profile_schemas import (
    ChannelProfileCreate,
    ChannelProfileResponse,
    ChannelProfileListResponse,
)

router = APIRouter(prefix="/profiles", tags=["profiles"])


def _to_response(p: ChannelProfileORM) -> ChannelProfileResponse:
    return ChannelProfileResponse(
        id=p.id, name=p.name, description=p.description, archetype=p.archetype,
        theme=p.theme, niche=p.niche, audience=p.audience, language=p.language,
        tone=p.tone, content=p.content, research=p.research, media=p.media,
        publishing=p.publishing, learning=p.learning, is_active=p.is_active,
        created_at=p.created_at, updated_at=p.updated_at,
    )


@router.get("/", response_model=ChannelProfileListResponse)
async def list_profiles(
    archetype: Optional[str] = None,
    theme: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(ChannelProfileORM).filter(ChannelProfileORM.is_active == True)
    if archetype:
        q = q.filter(ChannelProfileORM.archetype == archetype)
    if theme:
        q = q.filter(ChannelProfileORM.theme == theme)
    total = q.count()
    profiles = q.order_by(ChannelProfileORM.created_at.desc()).limit(limit).all()
    return ChannelProfileListResponse(total=total, profiles=[_to_response(p) for p in profiles])


# ВАЖНО: /templates ДО /{profile_id} (иначе "templates" парсится как id)
@router.get("/templates")
async def list_channel_templates():
    """Sprint 67.5: список YAML-шаблонов."""
    from backend.core.channel_template_loader import list_templates
    templates = list_templates()
    return {"total": len(templates), "templates": templates}


@router.post("/from-template/{template_name}", response_model=ChannelProfileResponse, status_code=201)
async def create_profile_from_template(
    template_name: str,
    overrides: dict = Body(default={}),
    db: Session = Depends(get_db),
):
    """Sprint 67.5: создать ChannelProfile из YAML-шаблона + overrides."""
    from backend.core.channel_template_loader import get_template

    t = get_template(template_name)
    if not t:
        raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")

    try:
        archetype = Archetype(t.get("archetype", "news"))
    except ValueError:
        archetype = Archetype.NEWS
    defaults = get_archetype_defaults(archetype)

    name = overrides.get("name") or f"{t.get('display_name', template_name)} Profile"
    existing = db.query(ChannelProfileORM).filter(ChannelProfileORM.name == name).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Profile '{name}' already exists")

    def merged(section: str, fallback: dict) -> dict:
        base = dict(t.get(section) or fallback)
        base.update(overrides.get(section) or {})
        return base

    p = ChannelProfileORM(
        name=name,
        description=overrides.get("description") or t.get("description"),
        archetype=archetype.value,
        theme=overrides.get("theme") or t.get("theme"),
        niche=overrides.get("niche") or t.get("niche"),
        audience=overrides.get("audience") or t.get("audience"),
        language=overrides.get("language") or t.get("language", "ru"),
        tone=overrides.get("tone") or t.get("tone", defaults.tone),
        content=merged("content", {"formats": defaults.allowed_formats, "max_length": defaults.max_post_length}),
        research=merged("research", {"freshness_hours": 24, "sources": ["rss", "web"]}),
        media=merged("media", {"preferred": ["image"], "fallback": []}),
        publishing=merged("publishing", {"frequency_per_day": defaults.frequency_per_day, "mode": defaults.publishing_mode}),
        learning=merged("learning", {"enabled": True}),
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return _to_response(p)


@router.post("/", response_model=ChannelProfileResponse, status_code=201)
async def create_profile(request: ChannelProfileCreate, db: Session = Depends(get_db)):
    existing = db.query(ChannelProfileORM).filter(ChannelProfileORM.name == request.name).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Profile with name '{request.name}' already exists")
    p = ChannelProfileORM(
        name=request.name, description=request.description, archetype=request.archetype,
        theme=request.theme, niche=request.niche,
        audience=request.audience.model_dump() if request.audience else None,
        language=request.language, tone=request.tone,
        content=request.content.model_dump() if request.content else None,
        research=request.research.model_dump() if request.research else None,
        media=request.media.model_dump() if request.media else None,
        publishing=request.publishing.model_dump() if request.publishing else None,
        learning=request.learning.model_dump() if request.learning else None,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return _to_response(p)


@router.get("/{profile_id}", response_model=ChannelProfileResponse)
async def get_profile(profile_id: str, db: Session = Depends(get_db)):
    p = db.query(ChannelProfileORM).filter(ChannelProfileORM.id == profile_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Profile not found")
    return _to_response(p)


@router.post("/{profile_id}/assign/{channel_id}")
async def assign_profile_to_channel(profile_id: str, channel_id: str, db: Session = Depends(get_db)):
    """Sprint 67.5: привязать profile к каналу."""
    p = db.query(ChannelProfileORM).filter(ChannelProfileORM.id == profile_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Profile not found")
    ch = db.query(ChannelORM).filter(ChannelORM.id == channel_id).first()
    if not ch:
        raise HTTPException(status_code=404, detail="Channel not found")
    ch.profile_id = profile_id
    db.commit()
    return {"channel_id": channel_id, "profile_id": profile_id, "profile_name": p.name, "status": "assigned"}


@router.delete("/{profile_id}", status_code=204)
async def delete_profile(profile_id: str, db: Session = Depends(get_db)):
    p = db.query(ChannelProfileORM).filter(ChannelProfileORM.id == profile_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Profile not found")
    p.is_active = False
    db.commit()