"""Channel Manager - Sprint 35.

Управление каналами: создание, удаление, pause/resume, health monitoring.
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime

from core.database import SessionLocal
from core.models.channel_orm import ChannelORM
from core.channel_scheduler import ChannelScheduler


logger = logging.getLogger(__name__)


class ChannelManager:
    """Управляет каналами и их автоматизацией."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.scheduler = ChannelScheduler()
    
    def list_channels(self) -> List[Dict]:
        """Возвращает список всех каналов с их статусом."""
        db = SessionLocal()
        try:
            channels = db.query(ChannelORM).all()
            
            result = []
            for ch in channels:
                schedule_info = self.scheduler.schedules.get(ch.id)
                
                result.append({
                    "id": ch.id,
                    "name": ch.name,
                    "platform": ch.platform,
                    "is_connected": ch.is_connected,
                    "scheduler": {
                        "enabled": schedule_info.enabled if schedule_info else False,
                        "interval_minutes": schedule_info.interval_minutes if schedule_info else None,
                        "last_run": schedule_info.last_run.isoformat() if schedule_info and schedule_info.last_run else None,
                        "error_count": schedule_info.error_count if schedule_info else 0,
                    } if schedule_info else None,
                })
            
            return result
        finally:
            db.close()
    
    def enable_automation(self, channel_id: str, interval_minutes: int = 30):
        """Включает автоматизацию для канала."""
        db = SessionLocal()
        try:
            channel = db.query(ChannelORM).filter(ChannelORM.id == channel_id).first()
            if not channel:
                raise ValueError(f"Channel {channel_id} not found")
            
            if not channel.is_connected:
                raise ValueError(f"Channel {channel_id} not connected")
            
            self.scheduler.add_channel(channel_id, interval_minutes)
            self.logger.info(f"Automation enabled for {channel.name} (every {interval_minutes}m)")
            
        finally:
            db.close()
    
    def disable_automation(self, channel_id: str):
        """Выключает автоматизацию для канала."""
        self.scheduler.remove_channel(channel_id)
        self.logger.info(f"Automation disabled for {channel_id}")
    
    def start_scheduler(self):
        """Запускает scheduler."""
        self.scheduler.start()
    
    def stop_scheduler(self):
        """Останавливает scheduler."""
        self.scheduler.stop()
    
    def get_status(self) -> Dict:
        """Возвращает статус manager."""
        return {
            "scheduler": self.scheduler.get_status(),
            "channels": self.list_channels(),
        }