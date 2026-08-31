"""Channel Wizard - Sprint 55 (полная версия).

POST /wizard/suggest            — предлагает конфигурацию по названию
POST /wizard/validate           — валидирует конфиг
POST /wizard/create-from-wizard — создаёт канал с этим конфигом
"""
import uuid
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from core.database import get_db
from core.models.channel_orm import ChannelORM
from core.models.channel_schedule_orm import ChannelScheduleORM
from engines.source_registry import SourceRegistry
from engines.channel_profiles import PROFILES
from engines.capability_matcher import suggest_strategy
from core.models.wizard_intelligence import ChannelIntent, ChannelStrategy

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/wizard", tags=["wizard"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class WizardSuggestRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class WizardSuggestResponse(BaseModel):
    content_type: str
    topic: str
    language: str
    profile_key: str
    sources: List[str]
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    # Sprint 65.2: Smart Wizard fields
    domain: Optional[str] = None
    subtopics: List[str] = Field(default_factory=list)
    audience: Optional[str] = None
    publishing_frequency: Optional[str] = None
    publishing_mode: Optional[str] = None


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

    publishing_mode: Optional[str] = None
    publishing_frequency: Optional[str] = None

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
# 1. SUGGEST
# ---------------------------------------------------------------------------

@router.post("/suggest", response_model=WizardSuggestResponse)
async def suggest_config(request: WizardSuggestRequest):
    """Sprint 65.2: Smart Wizard — ChannelIntent -> ChannelStrategy.

    Работает для ЛЮБЫХ тематик (fallback: general_news),
    legacy-семейства (manga/anime) используют существующие профили.
    """
    intent, strategy = suggest_strategy(request.description or "", request.name)

    if intent.domain in ("manga", "anime"):
        # Legacy families: существующие профили + источники
        candidates = (
            ["manga", "manga_releases"] if intent.domain == "manga"
            else ["anime", "anime_news"]
        )
        profile_key = next((k for k in candidates if k in PROFILES), strategy.profile_key)
        sources = [s.id for s in SourceRegistry.get_sources_for(content_type=intent.domain)] or strategy.sources
        content_type = intent.domain
    else:
        profile_key = strategy.profile_key
        sources = strategy.sources
        content_type = "news"

    if not sources:
        raise HTTPException(status_code=400, detail="No sources available for this channel type")

    reasoning = f"{intent.reasoning}. Strategy: {'; '.join(strategy.reasoning[:2])}"

    return WizardSuggestResponse(
        content_type=content_type,
        topic=intent.topic,
        language=intent.language,
        profile_key=profile_key,
        sources=sources,
        confidence=intent.confidence,
        reasoning=reasoning,
        domain=intent.domain,
        subtopics=intent.subtopics,
        audience=intent.audience,
        publishing_frequency=strategy.publishing_frequency,
        publishing_mode=strategy.publishing_mode,
    )


@router.post("/validate", response_model=WizardValidateResponse)
async def validate_wizard_config(req: WizardConfigRequest):
    """Валидирует конфиг: profile_key в PROFILES + sources в SourceRegistry."""
    errors = []
    warnings = []

    if req.profile_key not in PROFILES:
        errors.append(f"Profile '{req.profile_key}' not found in PROFILES")

    valid_ids, invalid_ids = SourceRegistry.validate_sources(req.sources)
    if invalid_ids:
        errors.append(f"Unknown sources: {invalid_ids}")

    for src_id in valid_ids:
        src = SourceRegistry.get_source(src_id)
        if src and req.content_type not in src.content_types:
            errors.append(f"Source '{src_id}' does not support content_type '{req.content_type}'")

    if not req.sources:
        warnings.append("No sources selected")

    return WizardValidateResponse(valid=len(errors) == 0, errors=errors, warnings=warnings)


# ---------------------------------------------------------------------------
# 3. CREATE
# ---------------------------------------------------------------------------

@router.post("/create-from-wizard", response_model=CreateFromWizardResponse, status_code=201)
async def create_channel_from_wizard(
    req: CreateFromWizardRequest,
    db: Session = Depends(get_db),
):
    """Создаёт канал по Wizard конфигу (content_profile JSONB + schedule)."""
    validation = await validate_wizard_config(req.config)
    if not validation.valid:
        raise HTTPException(status_code=400, detail=f"Invalid config: {'; '.join(validation.errors)}")

    job_type = req.config.job_type or _infer_job_type(req.config.content_type)

    content_profile = {
        "profile_key": req.config.profile_key,
        "content_type": req.config.content_type,
        "topic": req.config.topic,
        "language": req.config.language,
        "sources": req.config.sources,
        "job_type": job_type,
        "schedule": req.config.schedule_cron,
    }

    # Sprint 65.4: persist publishing settings in content_profile
    if req.config.publishing_mode:
        content_profile["publishing_mode"] = req.config.publishing_mode
    if req.config.publishing_frequency:
        content_profile["publishing_frequency"] = req.config.publishing_frequency

    channel = ChannelORM(
        id=str(uuid.uuid4()),
        name=req.name,
        platform=req.config.platform,
        content_profile=content_profile,
        sources=[],
        is_active=True,
        is_connected=False,
        language_search=req.config.language,
        language_publish=req.config.language,
        chat_id=req.chat_id,
        bot_token=req.bot_token,
        vk_group_id=req.vk_group_id,
        vk_access_token=req.vk_access_token,
    )

    logger.info(f"BEFORE db.add: content_profile={content_profile}")
    db.add(channel)
    logger.info(f"AFTER db.add: channel.content_profile={channel.content_profile}")
    db.flush()
    logger.info(f"AFTER flush: channel.content_profile={channel.content_profile}")

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

    logger.info(f"Created channel from wizard: {req.name} (type={req.config.content_type})")

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
    mapping = {"manga": "manga_pipeline", "anime": "anime_pipeline", "news": "news_pipeline"}
    return mapping.get(content_type, "generic_pipeline")