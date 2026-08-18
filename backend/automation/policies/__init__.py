"""
Policies для AutomationManager v2.

Определяют поведение системы при:
- Retry (повторные попытки при ошибках)
- Rate limits (ограничения частоты публикаций)
- Error handling (обработка и логирование ошибок)
"""
import logging
from datetime import datetime
from typing import Optional
from dataclasses import dataclass

from core.database import SessionLocal
from core.models.channel_orm import ChannelORM
from core.models.channel_schedule_orm import ChannelScheduleORM
from core.models.content_orm import ContentORM


logger = logging.getLogger(__name__)


@dataclass
class RetryPolicy:
    """
    Политика повторных попыток при ошибках.
    
    Использует exponential backoff: каждая следующая попытка ждёт дольше.
    """
    max_retries: int = 3
    backoff_factor: float = 2.0
    base_delay: float = 5.0  # seconds
    
    def should_retry(self, current_retry: int, max_retries: Optional[int] = None) -> bool:
        """Проверяет, стоит ли делать ещё одну попытку."""
        limit = max_retries if max_retries is not None else self.max_retries
        return current_retry < limit
    
    def get_backoff_time(self, retry_count: int) -> float:
        """Возвращает время ожидания перед следующей попыткой (exponential backoff)."""
        return self.base_delay * (self.backoff_factor ** retry_count)


@dataclass
class RateLimitPolicy:
    """
    Политика ограничений частоты публикаций.
    
    Проверяет, не превышен ли дневной лимит публикаций для канала.
    Читает daily_post_limit из ChannelScheduleORM.
    """
    
    def can_run(self, channel: ChannelORM) -> bool:
        """Проверяет, можно ли запускать пайплайн для канала."""
        db = SessionLocal()
        try:
            schedule = db.query(ChannelScheduleORM).filter(
                ChannelScheduleORM.channel_id == channel.id
            ).first()
            
            if not schedule:
                logger.warning("No schedule found for channel %s, allowing run", channel.name)
                return True
            
            # Считаем сколько постов опубликовано сегодня
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            published_today = db.query(ContentORM).filter(
                ContentORM.channel_id == channel.id,
                ContentORM.status == "published",
                ContentORM.published_at >= today_start
            ).count()
            
            # Безопасный доступ: пробуем несколько вариантов имени поля
            daily_limit = (
                getattr(schedule, 'daily_post_limit', None) or
                getattr(schedule, 'daily_limit', None) or
                getattr(schedule, 'max_daily_posts', None) or
                getattr(schedule, 'posts_per_day', None) or
                50
            )
            
            if published_today >= daily_limit:
                logger.warning(
                    "Rate limit exceeded for channel %s: %d/%d posts today",
                    channel.name, published_today, daily_limit
                )
                return False
            
            logger.info(
                "Rate limit OK for channel %s: %d/%d posts today",
                channel.name, published_today, daily_limit
            )
            return True
            
        finally:
            db.close()
    
    def get_remaining_quota(self, channel: ChannelORM) -> dict:
        """Возвращает информацию о remaining quota для канала."""
        db = SessionLocal()
        try:
            schedule = db.query(ChannelScheduleORM).filter(
                ChannelScheduleORM.channel_id == channel.id
            ).first()
            
            if not schedule:
                return {
                    "daily_limit": None,
                    "published_today": 0,
                    "remaining": None
                }
            
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            published_today = db.query(ContentORM).filter(
                ContentORM.channel_id == channel.id,
                ContentORM.status == "published",
                ContentORM.published_at >= today_start
            ).count()
            
            # Безопасный доступ: пробуем несколько вариантов имени поля
            daily_limit = (
                getattr(schedule, 'daily_post_limit', None) or
                getattr(schedule, 'daily_limit', None) or
                getattr(schedule, 'max_daily_posts', None) or
                getattr(schedule, 'posts_per_day', None) or
                50
            )
            remaining = max(0, daily_limit - published_today)
            
            return {
                "daily_limit": daily_limit,
                "published_today": published_today,
                "remaining": remaining
            }
            
        finally:
            db.close()


@dataclass
class ErrorHandlingPolicy:
    """
    Политика обработки ошибок.
    
    Определяет, как система должна реагировать на ошибки:
    - Логирование
    - Уведомления (future: email, Slack, Telegram)
    - Автоматическое восстановление (future)
    """
    log_errors: bool = True
    notify_on_failure: bool = False  # Future: enable notifications
    auto_recover: bool = True
    
    def handle_error(self, task) -> None:
        """Обрабатывает ошибку задачи."""
        if self.log_errors:
            logger.error(
                "Task %s failed after %d retries. Channel: %s. Error: %s",
                task.task_id, task.retry_count, task.channel_name, task.error
            )
        
        if self.notify_on_failure:
            self._send_notification(task)
        
        if self.auto_recover:
            self._attempt_recovery(task)
    
    def _send_notification(self, task) -> None:
        """Отправляет уведомление об ошибке (placeholder)."""
        logger.info("Notification would be sent for task %s", task.task_id)
    
    def _attempt_recovery(self, task) -> None:
        """Пытается автоматически восстановить задачу (placeholder)."""
        logger.info("Auto-recovery would be attempted for task %s", task.task_id)


# Экспортируем классы для удобного импорта
__all__ = ['RetryPolicy', 'RateLimitPolicy', 'ErrorHandlingPolicy']