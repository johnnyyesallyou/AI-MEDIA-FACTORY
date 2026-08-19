"""Error Handlers - Sprint 41.

Обработчики ошибок с правильной реакцией на основе Error Taxonomy:
- TRANSIENT → retry с exponential backoff
- PERMANENT → fail + alert
- CONFIGURATION → alert + disable channel
- NETWORK → retry
- CONTENT → skip + log
"""
import logging
import time
from typing import Callable, Any, Optional
from functools import wraps

from core.error_taxonomy import classify_error, ErrorType, ErrorSeverity


logger = logging.getLogger(__name__)


class ErrorHandler:
    """Обработчик ошибок с автономной реакцией."""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        alert_callback: Optional[Callable] = None,
        disable_callback: Optional[Callable] = None,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.alert_callback = alert_callback
        self.disable_callback = disable_callback
    
    def handle(self, func: Callable, *args, **kwargs) -> Any:
        """Выполняет функцию с обработкой ошибок."""
        attempt = 0
        
        while attempt < self.max_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                classified = classify_error(e, context=func.__name__)
                
                logger.warning(
                    f"Error in {func.__name__}: {classified.error_type.value} "
                    f"(attempt {attempt + 1}/{self.max_retries}): {classified.message}"
                )
                
                # Определяем действие
                if classified.error_type == ErrorType.TRANSIENT:
                    # Retry с exponential backoff
                    if attempt < self.max_retries - 1:
                        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                        logger.info(f"Retrying in {delay}s...")
                        time.sleep(delay)
                        attempt += 1
                        continue
                    else:
                        logger.error(f"Max retries exceeded for {func.__name__}")
                        self._send_alert(classified)
                        raise
                
                elif classified.error_type == ErrorType.NETWORK:
                    # Retry
                    if attempt < self.max_retries - 1:
                        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                        logger.info(f"Network error, retrying in {delay}s...")
                        time.sleep(delay)
                        attempt += 1
                        continue
                    else:
                        logger.error(f"Max retries exceeded for {func.__name__}")
                        self._send_alert(classified)
                        raise
                
                elif classified.error_type == ErrorType.PERMANENT:
                    # Fail + alert
                    logger.error(f"Permanent error in {func.__name__}: {classified.message}")
                    self._send_alert(classified)
                    raise
                
                elif classified.error_type == ErrorType.CONFIGURATION:
                    # Alert + disable
                    logger.error(f"Configuration error in {func.__name__}: {classified.message}")
                    self._send_alert(classified)
                    self._disable_component(classified)
                    raise
                
                elif classified.error_type == ErrorType.CONTENT:
                    # Skip + log
                    logger.warning(f"Content error, skipping: {classified.message}")
                    return None
                
                else:
                    # Unknown
                    logger.error(f"Unknown error in {func.__name__}: {classified.message}")
                    self._send_alert(classified)
                    raise
        
        raise RuntimeError(f"Unexpected exit from retry loop in {func.__name__}")
    
    def _send_alert(self, classified):
        """Отправляет alert если severity >= MEDIUM."""
        if classified.severity in (ErrorSeverity.MEDIUM, ErrorSeverity.HIGH, ErrorSeverity.CRITICAL):
            if self.alert_callback:
                try:
                    self.alert_callback(classified)
                except Exception as e:
                    logger.error(f"Failed to send alert: {e}")
    
    def _disable_component(self, classified):
        """Отключает компонент при configuration error."""
        if self.disable_callback:
            try:
                self.disable_callback(classified)
            except Exception as e:
                logger.error(f"Failed to disable component: {e}")


def handle_errors(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
):
    """Декоратор для обработки ошибок."""
    
    def decorator(func: Callable) -> Callable:
        handler = ErrorHandler(max_retries, base_delay, max_delay)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return handler.handle(func, *args, **kwargs)
        
        return wrapper
    
    return decorator