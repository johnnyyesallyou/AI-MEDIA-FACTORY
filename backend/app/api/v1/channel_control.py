"""Channel Control - Sprint 56.

POST /channels/{id}/start  — активировать канал (is_connected=True + cron)
POST /channels/{id}/pause  — пауза
GET  /channels/{id}/status — статус + статистика
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import get_db
from core.models.channel_orm import ChannelORM
from core.models.channel_schedule_orm import ChannelScheduleORM
from core.models.content_orm import ContentORM

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class ChannelStartResponse(BaseModel):
    id: str
    name: str
    status: str
    message: str


class ChannelStatusResponse(BaseModel):
    id: str
    name: str
    platform: str
    is_connected: bool
    is_active: bool
    content_type: Optional[str]
    topic: Optional[str]
    profile_key: Optional[str]
    sources: list
    schedule_cron: Optional[str]
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    today_published: int
    today_failed: int


class DashboardResponse(BaseModel):
    total_channels: int
    active_channels: int
    channels: list


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/{channel_id}/start", response_model=ChannelStartResponse)
async def start_channel(channel_id: str, db: Session = Depends(get_db)):
    """
    Активировать канал: установить is_connected=True.
    Cron job уже существует в scheduler.py, просто нужно is_connected.
    """
    channel = db.query(ChannelORM).filter(ChannelORM.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # Проверяем что есть schedule
    schedule = db.query(ChannelScheduleORM).filter(
        ChannelScheduleORM.channel_id == channel_id
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=400,
            detail="Channel has no schedule. Create schedule first."
        )
    
    # Активируем
    channel.is_connected = True
    channel.is_active = True
    schedule.is_active = True
    
    db.commit()
    db.refresh(channel)
    
    logger.info(f"Channel started: {channel.name} (id={channel_id})")
    
    return ChannelStartResponse(
        id=channel.id,
        name=channel.name,
        status="active",
        message=f"Channel '{channel.name}' activated. Will run on schedule: {schedule.cron_expression}"
    )


@router.post("/{channel_id}/pause", response_model=ChannelStartResponse)
async def pause_channel(channel_id: str, db: Session = Depends(get_db)):
    """Пауза канала: is_connected=False (cron не запускается)."""
    channel = db.query(ChannelORM).filter(ChannelORM.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    schedule = db.query(ChannelScheduleORM).filter(
        ChannelScheduleORM.channel_id == channel_id
    ).first()
    
    channel.is_connected = False
    if schedule:
        schedule.is_active = False
    
    db.commit()
    
    logger.info(f"Channel paused: {channel.name} (id={channel_id})")
    
    return ChannelStartResponse(
        id=channel.id,
        name=channel.name,
        status="paused",
        message=f"Channel '{channel.name}' paused"
    )


@router.get("/{channel_id}/status", response_model=ChannelStatusResponse)
async def get_channel_status(channel_id: str, db: Session = Depends(get_db)):
    """
    Получить статус канала + статистику за сегодня.
    """
    channel = db.query(ChannelORM).filter(ChannelORM.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # Schedule
    schedule = db.query(ChannelScheduleORM).filter(
        ChannelScheduleORM.channel_id == channel_id
    ).first()
    
    # Content profile
    content_profile = channel.content_profile or {}
    
    # Статистика за сегодня
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    today_published = db.query(ContentORM).filter(
        ContentORM.channel_id == channel_id,
        ContentORM.status == "published",
        ContentORM.published_at >= today_start
    ).count()
    
    today_failed = db.query(ContentORM).filter(
        ContentORM.channel_id == channel_id,
        ContentORM.status == "failed",
        ContentORM.updated_at >= today_start
    ).count()
    
    return ChannelStatusResponse(
        id=channel.id,
        name=channel.name,
        platform=channel.platform,
        is_connected=channel.is_connected or False,
        is_active=channel.is_active or False,
        content_type=content_profile.get("content_type"),
        topic=content_profile.get("topic"),
        profile_key=content_profile.get("profile_key"),
        sources=content_profile.get("sources", []),
        schedule_cron=schedule.cron_expression if schedule else None,
        last_run=schedule.last_run if schedule else None,
        next_run=schedule.next_run if schedule else None,
        today_published=today_published,
        today_failed=today_failed,
    )


@router.get("", response_model=DashboardResponse)
async def get_dashboard(db: Session = Depends(get_db)):
    """
    Dashboard: все каналы с базовой статистикой.
    """
    channels = db.query(ChannelORM).all()
    
    channel_list = []
    for ch in channels:
        content_profile = ch.content_profile or {}
        
        # Статистика за последние 24 часа
        yesterday = datetime.utcnow() - timedelta(hours=24)
        
        published_24h = db.query(ContentORM).filter(
            ContentORM.channel_id == ch.id,
            ContentORM.status == "published",
            ContentORM.published_at >= yesterday
        ).count()
        
        channel_list.append({
            "id": ch.id,
            "name": ch.name,
            "platform": ch.platform,
            "is_connected": ch.is_connected or False,
            "is_active": ch.is_active or False,
            "content_type": content_profile.get("content_type"),
            "topic": content_profile.get("topic"),
            "published_24h": published_24h,
        })
    
    active_count = sum(1 for ch in channel_list if ch["is_connected"])
    
    return DashboardResponse(
        total_channels=len(channel_list),
        active_channels=active_count,
        channels=channel_list,
    )