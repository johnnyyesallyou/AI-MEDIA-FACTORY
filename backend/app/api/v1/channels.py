import uuid
from datetime import datetime
import logging
from fastapi import APIRouter, Body, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session
import requests

from .schemas import (
    ChannelCreateRequest,
    ChannelUpdateRequest,
    ChannelResponse,
    ChannelListResponse,
    TelegramConnectionRequest, VkConnectionRequest, YoutubeConnectionRequest, DzenConnectionRequest,
    TelegramConnectionResponse,
    KnowledgeSourceCreateRequest,
    KnowledgeSourceResponse,
    ChannelScheduleRequest,
    ChannelScheduleResponse
)
from core.database import get_db, engine, Base, ensure_sqlite_schema
from core.models.channel_orm import ChannelORM
from core.models.channel_schedule_orm import ChannelScheduleORM
from core.repositories.channel_repository import ChannelRepository
from backend.automation.scheduler import automation_scheduler

Base.metadata.create_all(bind=engine)
ensure_sqlite_schema()

router = APIRouter(prefix="/channels", tags=["channels"])

logger = logging.getLogger(__name__)


def _to_response(c: ChannelORM) -> ChannelResponse:
    return ChannelResponse(
        id=c.id,
        name=c.name,
        platform=c.platform,
        language_search=c.language_search,
        language_publish=c.language_publish,
        style_profile=c.style_profile,
        timezone=c.timezone,
        workflow_id=c.workflow_id,
        description=c.description,
        # Sprint 11: Multi-platform credentials
        vk_group_id=getattr(c, "vk_group_id", None),
        vk_access_token=getattr(c, "vk_access_token", None),
        youtube_channel_id=getattr(c, "youtube_channel_id", None),
        youtube_api_key=getattr(c, "youtube_api_key", None),
        dzen_channel_id=getattr(c, "dzen_channel_id", None),
        dzen_api_key=getattr(c, "dzen_api_key", None),
        is_connected=c.is_connected,
        is_active=c.is_active,
        sources=c.sources or [],
        created_at=c.created_at,
        updated_at=c.updated_at
    )


@router.post("/", response_model=ChannelResponse, status_code=201)
async def create_channel(request: ChannelCreateRequest, db: Session = Depends(get_db)):
    repo = ChannelRepository(db)
    channel = repo.create(
        name=request.name,
        platform=request.platform,
        language_search=request.language_search,
        language_publish=request.language_publish,
        style_profile=request.style_profile,
        timezone=request.timezone,
        workflow_id=request.workflow_id,
        description=request.description,
    )
    return _to_response(channel)


@router.get("/", response_model=ChannelListResponse)
async def list_channels(db: Session = Depends(get_db)):
    repo = ChannelRepository(db)
    channels = repo.list_all()
    return ChannelListResponse(total=len(channels), channels=[_to_response(c) for c in channels])


@router.get("/{channel_id}", response_model=ChannelResponse)
async def get_channel(channel_id: str, db: Session = Depends(get_db)):
    repo = ChannelRepository(db)
    channel = repo.get(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    return _to_response(channel)


@router.put("/{channel_id}", response_model=ChannelResponse)
async def update_channel(channel_id: str, request: ChannelUpdateRequest, db: Session = Depends(get_db)):
    repo = ChannelRepository(db)
    channel = repo.update(
        channel_id,
        name=request.name,
        description=request.description,
        language_search=request.language_search,
        language_publish=request.language_publish,
        style_profile=request.style_profile,
        timezone=request.timezone,
        workflow_id=request.workflow_id,
        is_active=request.is_active,
    )
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    return _to_response(channel)


@router.delete("/{channel_id}", status_code=204)
async def delete_channel(channel_id: str, db: Session = Depends(get_db)):
    repo = ChannelRepository(db)
    if not repo.delete_cascade(channel_id):
        raise HTTPException(status_code=404, detail="Channel not found")


@router.post("/{channel_id}/connect-telegram", response_model=TelegramConnectionResponse)
async def connect_telegram(channel_id: str, request: TelegramConnectionRequest, db: Session = Depends(get_db)):
    '''Подключить Telegram бота к каналу с реальной проверкой через Telegram Bot API.'''
    repo = ChannelRepository(db)
    channel = repo.get(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    chat_id = request.chat_id or ""
    if not chat_id:
        raise HTTPException(status_code=400, detail="chat_id обязателен (например, @username канала)")

    try:
        me_resp = requests.get(f"https://api.telegram.org/bot{request.bot_token}/getMe", timeout=10)
        me_data = me_resp.json()
    except requests.exceptions.RequestException as e:
        return TelegramConnectionResponse(success=False, error=f"Не удалось связаться с Telegram API: {e}")

    if not me_data.get("ok"):
        return TelegramConnectionResponse(success=False, error=f"Неверный bot_token: {me_data.get('description')}")

    try:
        chat_resp = requests.get(
            f"https://api.telegram.org/bot{request.bot_token}/getChat",
            params={"chat_id": chat_id},
            timeout=10,
        )
        chat_data = chat_resp.json()
    except requests.exceptions.RequestException as e:
        return TelegramConnectionResponse(success=False, error=f"Не удалось связаться с Telegram API: {e}")

    if not chat_data.get("ok"):
        return TelegramConnectionResponse(
            success=False,
            error=f"Бот не имеет доступа к каналу {chat_id}: {chat_data.get('description')}"
        )

    real_chat_id = str(chat_data["result"]["id"])
    chat_title = chat_data["result"].get("title", channel.name)
    bot_username = me_data["result"].get("username", "")

        # Прямое сохранение токенов в БД (в обход репозитория)
    channel.bot_token = request.bot_token
    channel.chat_id = real_chat_id
    channel.is_connected = True
    db.commit()
    db.refresh(channel)
    
    channel = repo.connect_telegram(channel_id, bot_token=request.bot_token, chat_id=real_chat_id)

    return TelegramConnectionResponse(
        success=True,
        chat_id=channel.chat_id,
        chat_title=chat_title,
        bot_username=bot_username,
        error=None
    )




@router.post("/{channel_id}/connect-vk", response_model=ChannelResponse)
async def connect_vk(channel_id: str, request: VkConnectionRequest, db: Session = Depends(get_db)):
    """
    Sprint 11: Подключает VK группу к каналу.
    
    Сохраняет group_id и access_token в БД.
    Валидация токена будет добавлена в VkPublisher.
    """
    repo = ChannelRepository(db)
    channel = repo.get(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    channel.vk_group_id = request.group_id
    channel.vk_access_token = request.access_token
    channel.is_connected = True
    db.commit()
    db.refresh(channel)
    
    logger.info("VK connected for channel %s: group_id=%s", channel_id, request.group_id)
    return _to_response(channel)


@router.post("/{channel_id}/connect-youtube", response_model=ChannelResponse)
async def connect_youtube(channel_id: str, request: YoutubeConnectionRequest, db: Session = Depends(get_db)):
    """Sprint 11: Подключает YouTube канал."""
    repo = ChannelRepository(db)
    channel = repo.get(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    channel.youtube_channel_id = request.channel_id
    channel.youtube_api_key = request.api_key
    channel.is_connected = True
    db.commit()
    db.refresh(channel)
    
    logger.info("YouTube connected for channel %s", channel_id)
    return _to_response(channel)


@router.post("/{channel_id}/connect-dzen", response_model=ChannelResponse)
async def connect_dzen(channel_id: str, request: DzenConnectionRequest, db: Session = Depends(get_db)):
    """Sprint 11: Подключает Дзен канал."""
    repo = ChannelRepository(db)
    channel = repo.get(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    channel.dzen_channel_id = request.channel_id
    channel.dzen_api_key = request.api_key
    channel.is_connected = True
    db.commit()
    db.refresh(channel)
    
    logger.info("Dzen connected for channel %s", channel_id)
    return _to_response(channel)

@router.post("/{channel_id}/sources", response_model=KnowledgeSourceResponse)
async def add_knowledge_source(channel_id: str, request: KnowledgeSourceCreateRequest, db: Session = Depends(get_db)):
    repo = ChannelRepository(db)
    source_id = str(uuid.uuid4())
    source = {
        "id": source_id,
        "name": request.name,
        "source_type": request.source_type.value,
        "url": request.url,
        "priority": request.priority,
        "is_active": True,
    }
    channel = repo.add_source(channel_id, source)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    return KnowledgeSourceResponse(
        id=source["id"], name=source["name"], source_type=request.source_type,
        url=source["url"], priority=source["priority"], is_active=source["is_active"],
    )


@router.get("/{channel_id}/sources", response_model=List[KnowledgeSourceResponse])
async def list_knowledge_sources(channel_id: str, db: Session = Depends(get_db)):
    repo = ChannelRepository(db)
    channel = repo.get(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    return [
        KnowledgeSourceResponse(
            id=s["id"], name=s["name"], source_type=s["source_type"],
            url=s["url"], priority=s["priority"], is_active=s.get("is_active", True),
        )
        for s in (channel.sources or [])
    ]



# === SCHEDULE ENDPOINTS ===

def _schedule_to_response(s: ChannelScheduleORM) -> ChannelScheduleResponse:
    # Берём next_run из живого APScheduler, а не из БД
    next_run = automation_scheduler.get_next_run(s.channel_id)
    return ChannelScheduleResponse(
        id=s.id,
        channel_id=s.channel_id,
        cron_expression=s.cron_expression,
        timezone=s.timezone,
        max_posts_per_day=s.max_posts_per_day,
        auto_publish=s.auto_publish,
        is_active=s.is_active,
        last_run=s.last_run,
        next_run=next_run,
    )


@router.get("/{channel_id}/schedule", response_model=ChannelScheduleResponse)
async def get_channel_schedule(channel_id: str, db: Session = Depends(get_db)):
    schedule = (
        db.query(ChannelScheduleORM)
        .filter(ChannelScheduleORM.channel_id == channel_id)
        .first()
    )
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return _schedule_to_response(schedule)


@router.put("/{channel_id}/schedule", response_model=ChannelScheduleResponse)
async def upsert_channel_schedule(channel_id: str, request: ChannelScheduleRequest, db: Session = Depends(get_db)):
    channel = db.query(ChannelORM).filter(ChannelORM.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    # Валидация cron ДО сохранения в БД
    try:
        from apscheduler.triggers.cron import CronTrigger
        from pytz import timezone as pytz_timezone
        CronTrigger.from_crontab(request.cron_expression, timezone=pytz_timezone(request.timezone))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid cron: {e}")

    schedule = (
        db.query(ChannelScheduleORM)
        .filter(ChannelScheduleORM.channel_id == channel_id)
        .first()
    )
    if not schedule:
        schedule = ChannelScheduleORM(channel_id=channel_id)
        db.add(schedule)

    schedule.cron_expression = request.cron_expression
    schedule.timezone = request.timezone
    schedule.max_posts_per_day = request.max_posts_per_day
    schedule.auto_publish = request.auto_publish
    schedule.is_active = request.is_active
    db.commit()
    db.refresh(schedule)

    # Планировщик подхватывает изменения БЕЗ перезапуска backend
    await automation_scheduler.refresh_schedule(channel_id)

    return _schedule_to_response(schedule)


@router.delete("/{channel_id}/sources/{source_id}", status_code=204)
async def delete_source(channel_id: str, source_id: str, db: Session = Depends(get_db)):
    """Удалить источник знаний из канала."""
    repo = ChannelRepository(db)
    channel = repo.remove_source(channel_id, source_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel or source not found")
    return None


# === AUTOMATION ENDPOINT ===

@router.post("/{channel_id}/automation/enable")
async def enable_channel_automation(
    channel_id: str,
    request: dict = Body(...),
    db: Session = Depends(get_db)
):
    """Включить автоматизацию для канала"""
    from core.channel_manager import ChannelManager
    
    repo = ChannelRepository(db)
    channel = repo.get(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    interval_minutes = request.get("interval_minutes", 120)
    
    # Создаём ChannelManager и включаем automation
    try:
        manager = ChannelManager()
        manager.enable_automation(channel_id, interval_minutes)
        return {
            "status": "enabled",
            "channel_id": channel_id,
            "interval_minutes": interval_minutes
        }
    except ValueError as e:
        # Channel not connected
        return {
            "status": "pending_connection",
            "channel_id": channel_id,
            "interval_minutes": interval_minutes,
            "reason": str(e),
            "next_step": "Connect Telegram first via /channels/{id}/connect-telegram"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Automation error: {e}")

@router.post("/{channel_id}/automation/disable")
async def disable_channel_automation(
    channel_id: str,
    db: Session = Depends(get_db)
):
    """Отключить автоматизацию для канала"""
    from core.channel_manager import ChannelManager
    
    repo = ChannelRepository(db)
    channel = repo.get(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    manager = ChannelManager()
    manager.disable_automation(channel_id)
    
    return {
        "status": "disabled",
        "channel_id": channel_id
    }

