"""Telegram Rate Limiter - защита от flood-бана."""
import time
import logging

logger = logging.getLogger(__name__)


class TelegramRateLimiter:
    """
    Ограничивает частоту сообщений Telegram.
    
    Telegram limits: ~20-30 msg/min per channel.
    Default: 1 msg per 2.5 sec = 24/min (safe).
    
    Sprint 19: Telegram improvements
    """
    
    def __init__(self, min_interval: float = 2.5, max_per_minute: int = 25):
        self.min_interval = min_interval
        self.max_per_minute = max_per_minute
        self.last_call = 0.0
        self.calls_this_minute = []
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def wait(self):
        """Блокирует до момента, когда можно отправить следующее сообщение."""
        now = time.time()
        
        # Чистим старые вызовы (> 60 сек)
        self.calls_this_minute = [t for t in self.calls_this_minute if now - t < 60]
        
        # Если достигли лимита в минуту - ждём
        if len(self.calls_this_minute) >= self.max_per_minute:
            oldest = min(self.calls_this_minute)
            wait_time = 60 - (now - oldest) + 0.5
            if wait_time > 0:
                self.logger.info(f"Rate limit: waiting {wait_time:.1f}s (minute cap)")
                time.sleep(wait_time)
                now = time.time()
                self.calls_this_minute = [t for t in self.calls_this_minute if now - t < 60]
        
        # Минимальный интервал между сообщениями
        elapsed = now - self.last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        
        self.last_call = time.time()
        self.calls_this_minute.append(self.last_call)
    
    def handle_429(self, retry_after: int):
        """Обработка flood-лимита Telegram (429)."""
        wait = retry_after + 1
        self.logger.warning(f"429 FloodWait: sleeping {wait}s")
        time.sleep(wait)