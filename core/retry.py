"""Retry Decorator - Sprint 34.

Универсальный retry с exponential backoff для всех внешних вызовов.

Использование:
    @retry_on_failure(max_retries=3, backoff_factor=2.0)
    def fetch_data():
        # код который может упасть
        pass
"""
import functools
import time
import logging
from typing import Callable, Tuple, Type, Any

logger = logging.getLogger(__name__)


def retry_on_failure(
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Callable[[Exception, int], None] = None,
    on_final_failure: Callable[[Exception], None] = None,
):
    """
    Декоратор для retry с exponential backoff.
    
    Args:
        max_retries: Максимальное количество попыток
        backoff_factor: Множитель задержки (2.0 = 1s, 2s, 4s, ...)
        exceptions: Типы исключений для retry
        on_retry: Callback при каждой retry (exception, attempt)
        on_final_failure: Callback при финальной ошибке (exception)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries - 1:
                        # Финальная ошибка
                        logger.error(
                            f"{func.__name__} failed after {max_retries} attempts: {e}"
                        )
                        if on_final_failure:
                            on_final_failure(e)
                        raise
                    
                    # Retry с exponential backoff
                    wait_time = backoff_factor ** attempt
                    logger.warning(
                        f"{func.__name__} attempt {attempt + 1}/{max_retries} failed: {e}. "
                        f"Retrying in {wait_time:.1f}s..."
                    )
                    
                    if on_retry:
                        on_retry(e, attempt + 1)
                    
                    time.sleep(wait_time)
            
            raise last_exception
        
        return wrapper
    
    return decorator


# Convenience decorators для разных сценариев
def retry_network(func: Callable) -> Callable:
    """Retry для network calls (HTTP, API)."""
    import requests
    
    return retry_on_failure(
        max_retries=3,
        backoff_factor=2.0,
        exceptions=(requests.exceptions.RequestException, ConnectionError, TimeoutError),
    )(func)


def retry_database(func: Callable) -> Callable:
    """Retry для database operations."""
    from sqlalchemy.exc import OperationalError, DatabaseError
    
    return retry_on_failure(
        max_retries=3,
        backoff_factor=1.5,
        exceptions=(OperationalError, DatabaseError),
    )(func)


def retry_external_api(func: Callable) -> Callable:
    """Retry для внешних API (AniList, MangaDex, Habr)."""
    import requests
    
    return retry_on_failure(
        max_retries=5,  # Больше попыток для API
        backoff_factor=2.0,
        exceptions=(requests.exceptions.RequestException, ConnectionError, TimeoutError),
    )(func)