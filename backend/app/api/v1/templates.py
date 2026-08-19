"""
API endpoints для Channel Templates и Profiles (Sprint 8.2).
"""
import logging
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from core.database import SessionLocal
from core.repositories.templates_repository import ChannelProfileRepository, ChannelTemplateRepository
from core.repositories.channel_repository import ChannelRepository
from core.models.channel_orm import ChannelORM
from core.models.channel_schedule_orm import ChannelScheduleORM

from .schemas import (
    ChannelProfileCreate, ChannelProfileUpdate, ChannelProfileResponse,
    ChannelTemplateCreate, ChannelTemplateUpdate, ChannelTemplateResponse,
    ApplyTemplateRequest, ApplyTemplateResponse
)

logger = logging.getLogger(__name__)


# ============ PROFILES ============
profiles_router = APIRouter(prefix="/profiles", tags=["profiles"])


@profiles_router.get("/", response_model=List[ChannelProfileResponse])
async def list_profiles(
    platform: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None)
):
    """Список всех профилей (опционально по платформе и статусу)."""
    db = SessionLocal()
    try:
        repo = ChannelProfileRepository(db)
        return repo.list_all(platform=platform, is_active=is_active)
    finally:
        db.close()


@profiles_router.get("/{profile_id}", response_model=ChannelProfileResponse)
async def get_profile(profile_id: str):
    """Получить профиль по ID."""
    db = SessionLocal()
    try:
        repo = ChannelProfileRepository(db)
        profile = repo.get_by_id(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        return profile
    finally:
        db.close()


@profiles_router.post("/", response_model=ChannelProfileResponse, status_code=201)
async def create_profile(data: ChannelProfileCreate):
    """Создать новый профиль."""
    db = SessionLocal()
    try:
        repo = ChannelProfileRepository(db)
        if repo.get_by_name(data.name):
            raise HTTPException(status_code=409, detail=f"Profile with name '{data.name}' already exists")
        return repo.create(**data.dict())
    finally:
        db.close()


@profiles_router.patch("/{profile_id}", response_model=ChannelProfileResponse)
async def update_profile(profile_id: str, data: ChannelProfileUpdate):
    """Обновить профиль (только переданные поля)."""
    db = SessionLocal()
    try:
        repo = ChannelProfileRepository(db)
        profile = repo.update(profile_id, **data.dict(exclude_unset=True))
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        return profile
    finally:
        db.close()


@profiles_router.delete("/{profile_id}")
async def delete_profile(profile_id: str):
    """Удалить профиль."""
    db = SessionLocal()
    try:
        repo = ChannelProfileRepository(db)
        if not repo.delete(profile_id):
            raise HTTPException(status_code=404, detail="Profile not found")
        return {"status": "deleted", "id": profile_id}
    finally:
        db.close()


# ============ TEMPLATES ============
templates_router = APIRouter(prefix="/templates", tags=["templates"])


@templates_router.get("/", response_model=List[ChannelTemplateResponse])
async def list_templates(
    category: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None)
):
    """Список всех шаблонов."""
    db = SessionLocal()
    try:
        repo = ChannelTemplateRepository(db)
        return repo.list_all(category=category, is_active=is_active)
    finally:
        db.close()


@templates_router.get("/{template_id}", response_model=ChannelTemplateResponse)
async def get_template(template_id: str):
    """Получить шаблон по ID."""
    db = SessionLocal()
    try:
        repo = ChannelTemplateRepository(db)
        template = repo.get_by_id(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return template
    finally:
        db.close()


@templates_router.post("/", response_model=ChannelTemplateResponse, status_code=201)
async def create_template(data: ChannelTemplateCreate):
    """Создать новый шаблон."""
    db = SessionLocal()
    try:
        repo = ChannelTemplateRepository(db)
        if repo.get_by_name(data.name):
            raise HTTPException(status_code=409, detail=f"Template with name '{data.name}' already exists")
        return repo.create(**data.dict())
    finally:
        db.close()


@templates_router.patch("/{template_id}", response_model=ChannelTemplateResponse)
async def update_template(template_id: str, data: ChannelTemplateUpdate):
    """Обновить шаблон (только переданные поля)."""
    db = SessionLocal()
    try:
        repo = ChannelTemplateRepository(db)
        template = repo.update(template_id, **data.dict(exclude_unset=True))
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return template
    finally:
        db.close()


@templates_router.delete("/{template_id}")
async def delete_template(template_id: str):
    """Удалить шаблон (только если он не используется каналами)."""
    db = SessionLocal()
    try:
        repo = ChannelTemplateRepository(db)
        if not repo.delete(template_id):
            raise HTTPException(status_code=400, detail="Template is in use or not found")
        return {"status": "deleted", "id": template_id}
    finally:
        db.close()


# ============ APPLY TEMPLATE ============
@templates_router.post("/{template_id}/apply-to/{channel_id}", response_model=ApplyTemplateResponse)
async def apply_template_to_channel(template_id: str, channel_id: str, data: ApplyTemplateRequest):
    """
    Применяет шаблон и профиль к существующему каналу.
    
    Копирует настройки из template и profile в channel и channel_schedule.
    """
    db = SessionLocal()
    try:
        template_repo = ChannelTemplateRepository(db)
        profile_repo = ChannelProfileRepository(db)
        channel_repo = ChannelRepository(db)
        
        template = template_repo.get_by_id(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        profile = profile_repo.get_by_id(data.profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        channel = channel_repo.get(channel_id)
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")
        
        # Применяем template → channel
        channel.template_id = template.id
        channel.profile_id = profile.id
        channel.language_search = template.language_search
        channel.language_publish = template.language_publish
        channel.timezone = template.timezone
        channel.sources = template.sources or []
        channel.workflow_id = template.workflow_id
        channel.platform = profile.platform
        
        # Применяем profile → channel
        channel.style_profile = profile.name
        
        # Обновляем или создаём schedule из template
        from sqlalchemy.orm import Session
        schedule = db.query(ChannelScheduleORM).filter(
            ChannelScheduleORM.channel_id == channel.id
        ).first()
        
        if schedule:
            schedule.cron_expression = template.cron_expression
            schedule.timezone = template.timezone
            schedule.max_posts_per_day = template.max_posts_per_day
            schedule.auto_publish = template.auto_publish
        else:
            import uuid
            schedule = ChannelScheduleORM(
                id=str(uuid.uuid4()),
                channel_id=channel.id,
                cron_expression=template.cron_expression,
                timezone=template.timezone,
                max_posts_per_day=template.max_posts_per_day,
                auto_publish=template.auto_publish,
                is_active=True
            )
            db.add(schedule)
        
        db.commit()
        
        logger.info(f"Applied template '{template.name}' + profile '{profile.name}' to channel '{channel.name}'")
        
        return ApplyTemplateResponse(
            status="ok",
            channel_id=channel.id,
            channel_name=channel.name,
            template_name=template.name,
            profile_name=profile.name,
            message=f"Template '{template.name}' and profile '{profile.name}' applied successfully"
        )
    finally:
        db.close()