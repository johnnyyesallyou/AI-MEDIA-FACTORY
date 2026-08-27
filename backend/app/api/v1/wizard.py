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
# 1. SUGGEST
# ---------------------------------------------------------------------------

@router.post("/suggest", response_model=WizardSuggestResponse)
async def suggest_channel_config(req: WizardSuggestRequest):
    """Предложить конфигурацию канала на основе названия (детерминированно)."""
    name_lower = req.name.lower()
    desc_lower = (req.description or "").lower()
    combined = f"{name_lower} {desc_lower}"

    config = _analyze_name(combined)
    if not config:
        raise HTTPException(
            status_code=400,
            detail="Не удалось определить тип канала. Укажите 'манга', 'аниме' или 'новости' в названии.",
        )

    sources = SourceRegistry.get_sources_for(
        content_type=config["content_type"],
        topic=config["topic"],
        language=config["language"],
    )
    source_ids = [s.id for s in sources]

    if not source_ids:
        sources = SourceRegistry.get_sources_for(content_type=config["content_type"])
        source_ids = [s.id for s in sources]

    return WizardSuggestResponse(
        content_type=config["content_type"],
        topic=config["topic"],
        language=config["language"],
        profile_key=config["profile_key"],
        sources=source_ids,
        confidence=config["confidence"],
        reasoning=config["reasoning"],
    )


def _analyze_name(text: str) -> Optional[dict]:
    """Анализирует текст и возвращает конфигурацию."""
    # Manga
    if any(kw in text for kw in ["манга", "manga", "главы", "chapters", "тайтл"]):
        return {
            "content_type": "manga",
            "topic": "new_chapters",
            "language": "ru",
            "profile_key": "manga_releases",
            "confidence": 0.9,
            "reasoning": "Обнаружены ключевые слова: манга/главы",
        }
    # Anime
    if any(kw in text for kw in ["аниме", "anime", "сериал", "series", "эпизод"]):
        return {
            "content_type": "anime",
            "topic": "news",
            "language": "ru",
            "profile_key": "anime_news",
            "confidence": 0.9,
            "reasoning": "Обнаружены ключевые слова: аниме/сериал",
        }
    # News
    if any(kw in text for kw in ["новости", "news", "технологии", "tech", "ai", "ии"]):
        topic = "technology"
        if any(kw in text for kw in ["бизнес", "business", "стартап"]):
            topic = "business"
        elif any(kw in text for kw in ["игры", "games", "gaming"]):
            topic = "gaming"
        return {
            "content_type": "news",
            "topic": topic,
            "language": "ru",
            "profile_key": "ai_news",
            "confidence": 0.85,
            "reasoning": f"Обнаружены ключевые слова: новости/tech, тема: {topic}",
        }
    return None


# ---------------------------------------------------------------------------
# 2. VALIDATE
# ---------------------------------------------------------------------------

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
    db.add(channel)
    db.flush()

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