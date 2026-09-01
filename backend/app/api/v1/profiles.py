"""Sprint 67.2: ChannelProfile CRUD API."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from core.models.channel_profile_orm import ChannelProfileORM
from backend.app.api.v1.channel_profile_schemas import (
    ChannelProfileCreate,
    ChannelProfileResponse,
    ChannelProfileListResponse,
)

router = APIRouter(prefix="/profiles", tags=["profiles"])


def _to_response(p: ChannelProfileORM) -> ChannelProfileResponse:
    return ChannelProfileResponse(
        id=p.id,
        name=p.name,
        description=p.description,
        archetype=p.archetype,
        theme=p.theme,
        niche=p.niche,
        audience=p.audience,
        language=p.language,
        tone=p.tone,
        content=p.content,
        research=p.research,
        media=p.media,
        publishing=p.publishing,
        learning=p.learning,
        is_active=p.is_active,
        created_at=p.created_at,
        updated_at=p.updated_at,
    )


@router.get("/", response_model=ChannelProfileListResponse)
async def list_profiles(
    archetype: Optional[str] = None,
    theme: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """List all channel profiles with optional filters."""
    q = db.query(ChannelProfileORM).filter(ChannelProfileORM.is_active == True)
    if archetype:
        q = q.filter(ChannelProfileORM.archetype == archetype)
    if theme:
        q = q.filter(ChannelProfileORM.theme == theme)
    profiles = q.order_by(ChannelProfileORM.created_at.desc()).limit(limit).all()
    return ChannelProfileListResponse(
        total=q.count(),
        profiles=[_to_response(p) for p in profiles],
    )


@router.get("/{profile_id}", response_model=ChannelProfileResponse)
async def get_profile(profile_id: str, db: Session = Depends(get_db)):
    """Get a single profile by ID."""
    p = db.query(ChannelProfileORM).filter(ChannelProfileORM.id == profile_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Profile not found")
    return _to_response(p)


@router.post("/", response_model=ChannelProfileResponse, status_code=201)
async def create_profile(request: ChannelProfileCreate, db: Session = Depends(get_db)):
    """Create a new channel profile."""
    # Check uniqueness
    existing = db.query(ChannelProfileORM).filter(ChannelProfileORM.name == request.name).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Profile with name '{request.name}' already exists")
    
    p = ChannelProfileORM(
        name=request.name,
        description=request.description,
        archetype=request.archetype,
        theme=request.theme,
        niche=request.niche,
        audience=request.audience.model_dump() if request.audience else None,
        language=request.language,
        tone=request.tone,
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


@router.delete("/{profile_id}", status_code=204)
async def delete_profile(profile_id: str, db: Session = Depends(get_db)):
    """Soft-delete a profile (set is_active=False)."""
    p = db.query(ChannelProfileORM).filter(ChannelProfileORM.id == profile_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Profile not found")
    p.is_active = False
    db.commit()