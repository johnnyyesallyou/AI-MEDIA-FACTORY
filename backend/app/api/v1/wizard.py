"""Channel Wizard - Sprint 55 (дополнение).

POST /wizard/validate  — валидирует предложенный конфиг
POST /channels/create-from-wizard — создаёт канал с этим конфигом
"""
import uuid
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from core.database import get_db
from core.models.channel_orm import ChannelORM
from core.models.channel_schedule_orm import ChannelScheduleORM
from engines.source_registry import SourceRegistry
from engines.channel_profiles import PROFILES

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/wizard", tags=["wizard"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class WizardConfigRequest(BaseModel):
    content_type: str
    topic: str
    language: str = "ru"
    profile_key: str
    sources: List[str]
    name: Optional[str] = None
    platform: str = "telegram"
    schedule_cron: str = "*/30 * * * *"
    job_type: Optional[str] = None


class WizardValidateResponse(BaseModel):
    valid: bool
    errors: List[str]
    warnings: List[str]


class CreateFromWizardRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    config: WizardConfigRequest
    chat_id: Optional[str] = None
    bot_token: Optional[str] = None
    vk_group_id: Optional[str] = None
    vk_access_token: Optional[str] = None


class CreateFromWizardResponse(BaseModel):
    id: str
    name: str
    platform: str
    content_type: str
    topic: str
    profile_key: str
    sources: List[str]
    schedule_cron: str
    status: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/validate", response_model=WizardValidateResponse)
async def validate_wizard_config(req: WizardConfigRequest):
    """
    Валидирует предложенную Wizard-ом конфигурацию.
    Проверяет:
    - profile_key существует в PROFILES
    - все sources есть в SourceRegistry
    - все sources поддерживают данный content_type
    """
    errors = []
    warnings = []

    # 1. Проверяем profile_key
    if req.profile_key not in PROFILES:
        errors.append(f"Profile '{req.profile_key}' not found in PROFILES")

    # 2. Проверяем sources
    valid_ids, invalid_ids = SourceRegistry.validate_sources(req.sources)
    if invalid_ids:
        errors.append(f"Unknown sources: {invalid_ids}")

    # 3. Проверяем что sources поддерживают content_type
    for src_id in valid_ids:
        src = SourceRegistry.get_source(src_id)
        if src and req.content_type not in src.content_types:
            errors.append(
                f"Source '{src_id}' does not support content_type '{req.content_type}'"
            )

    # 4. Предупреждения
    if not req.sources:
        warnings.append("No sources selected")

    return WizardValidateResponse(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


@router.post("/create-from-wizard", response_model=CreateFromWizardResponse, status_code=201)
async def create_channel_from_wizard(
    req: CreateFromWizardRequest,
    db: Session = Depends(get_db),
):
    """
    Создаёт канал по Wizard конфигу.
    
    Flow:
    1. Валидирует конфиг
    2. Создаёт ChannelORM с content_profile JSONB
    3. Создаёт ChannelScheduleORM
    4. Возвращает созданный канал
    """
    # 1. Валидация
    validation = await validate_wizard_config(req.config)
    if not validation.valid:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid config: {'; '.join(validation.errors)}",
        )

    # 2. Определяем job_type
    job_type = req.config.job_type or _infer_job_type(req.config.content_type)

    # 3. Создаём content_profile (JSONB)
    content_profile = {
        "profile_key": req.config.profile_key,
        "content_type": req.config.content_type,
        "topic": req.config.topic,
        "language": req.config.language,
        "sources": req.config.sources,
        "job_type": job_type,
        "schedule": req.config.schedule_cron,
    }

    # 4. Создаём канал
    channel = ChannelORM(
        id=str(uuid.uuid4()),
        name=req.name,
        platform=req.config.platform,
        content_profile=content_profile,
        sources=[],  # старые sources (KnowledgeSourceORM), оставим пустым
        is_active=True,
        is_connected=False,
        language_search=req.config.language,
        language_publish=req.config.language,
        chat_id=req.chat_id,
        bot_token=req.bot_token,
        vk_group_id=req.vk_group_id,
        vk_access_token=req.vk_access_token,
    )
    db.add(channel)
    db.flush()

    # 5. Создаём schedule
    schedule = ChannelScheduleORM(
        channel_id=channel.id,
        cron_expression=req.config.schedule_cron,
        timezone="Europe/Moscow",
        max_posts_per_day=48,
        auto_publish=True,
        is_active=True,
    )
    db.add(schedule)

    db.commit()
    db.refresh(channel)

    logger.info(
        f"Created channel from wizard: {req.name} "
        f"(type={req.config.content_type}, topic={req.config.topic}, "
        f"sources={req.config.sources})"
    )

    return CreateFromWizardResponse(
        id=channel.id,
        name=channel.name,
        platform=channel.platform,
        content_type=req.config.content_type,
        topic=req.config.topic,
        profile_key=req.config.profile_key,
        sources=req.config.sources,
        schedule_cron=req.config.schedule_cron,
        status="created",
    )


def _infer_job_type(content_type: str) -> str:
    """Определяет job_type по content_type."""
    mapping = {
        "manga": "manga_pipeline",
        "anime": "anime_pipeline",
        "news": "news_pipeline",
    }
    return mapping.get(content_type, "generic_pipeline")