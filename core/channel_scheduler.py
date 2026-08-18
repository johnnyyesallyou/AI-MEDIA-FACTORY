"""Channel Scheduler - Sprint 35.

Автоматический запуск research + publish jobs для каналов по расписанию.

Каждый канал имеет:
- schedule (cron-like: every 30m, every 1h, etc.)
- enabled (bool)
- last_run (timestamp)
- error_count (int)
- max_errors (int, after which channel is paused)
"""
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from core.database import SessionLocal
from core.models.channel_orm import ChannelORM


logger = logging.getLogger(__name__)


class ChannelStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class ChannelSchedule:
    """Расписание для канала."""
    channel_id: str
    interval_minutes: int  # запуск каждые N минут
    enabled: bool = True
    last_run: Optional[datetime] = None
    error_count: int = 0
    max_errors: int = 5  # после 5 ошибок подряд → pause


class ChannelScheduler:
    """Scheduler для автоматического запуска jobs."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.schedules: Dict[str, ChannelSchedule] = {}
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        # Job runners (инжектируются извне)
        self.research_runner: Optional[Callable] = None
        self.publish_runner: Optional[Callable] = None
    
    def add_channel(self, channel_id: str, interval_minutes: int = 30):
        """Добавляет канал в scheduler."""
        self.schedules[channel_id] = ChannelSchedule(
            channel_id=channel_id,
            interval_minutes=interval_minutes,
            enabled=True,
        )
        self.logger.info(f"Channel {channel_id} added to scheduler (every {interval_minutes}m)")
    
    def remove_channel(self, channel_id: str):
        """Удаляет канал из scheduler."""
        if channel_id in self.schedules:
            del self.schedules[channel_id]
            self.logger.info(f"Channel {channel_id} removed from scheduler")
    
    def start(self):
        """Запускает scheduler в background thread."""
        if self.running:
            self.logger.warning("Scheduler already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        self.logger.info("Scheduler started")
    
    def stop(self):
        """Останавливает scheduler."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        self.logger.info("Scheduler stopped")
    
    def _run_loop(self):
        """Main loop scheduler."""
        while self.running:
            try:
                self._tick()
            except Exception as e:
                self.logger.exception(f"Scheduler tick error: {e}")
            
            time.sleep(10)  # check every 10 seconds
    
    def _tick(self):
        """Одна итерация scheduler loop."""
        now = datetime.utcnow()
        
        for channel_id, schedule in list(self.schedules.items()):
            if not schedule.enabled:
                continue
            
            # Проверяем нужно ли запускать
            if schedule.last_run:
                time_since_last = now - schedule.last_run
                if time_since_last.total_seconds() < schedule.interval_minutes * 60:
                    continue
            
            # Запускаем jobs для этого канала
            self._run_channel_jobs(channel_id, schedule)
    
    def _run_channel_jobs(self, channel_id: str, schedule: ChannelSchedule):
        """Запускает research + publish для канала."""
        self.logger.info(f"Running jobs for channel {channel_id}")
        
        try:
            # 1. Research
            if self.research_runner:
                research_result = self.research_runner(channel_id)
                self.logger.info(f"Research result: {research_result}")
            
            # 2. Publish
            if self.publish_runner:
                publish_result = self.publish_runner(channel_id)
                self.logger.info(f"Publish result: {publish_result}")
            
            # Успех — сбрасываем error_count
            schedule.last_run = datetime.utcnow()
            schedule.error_count = 0
            
        except Exception as e:
            self.logger.error(f"Channel {channel_id} jobs failed: {e}")
            schedule.error_count += 1
            schedule.last_run = datetime.utcnow()
            
            # Если слишком много ошибок — pause
            if schedule.error_count >= schedule.max_errors:
                self.logger.warning(
                    f"Channel {channel_id} paused after {schedule.error_count} errors"
                )
                schedule.enabled = False
    
    def get_status(self) -> Dict:
        """Возвращает статус всех каналов."""
        return {
            "running": self.running,
            "channels": {
                cid: {
                    "enabled": s.enabled,
                    "interval_minutes": s.interval_minutes,
                    "last_run": s.last_run.isoformat() if s.last_run else None,
                    "error_count": s.error_count,
                }
                for cid, s in self.schedules.items()
            }
        }