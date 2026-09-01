"""
Sprint 66.5.5: Error Handling Wrapper for Jobs

Декоратор и контекстный менеджер для автоматического логирования ошибок
в pipeline_failures таблицу.
"""

import logging
import asyncio
import uuid
from functools import wraps
from typing import Callable, Optional, Any, Dict
from datetime import datetime, timedelta
import traceback

from backend.core.error_logger import get_error_logger, ErrorType

logger = logging.getLogger(__name__)


class JobExecutionContext:
    """Контекст выполнения job для отслеживания ошибок"""
    
    def __init__(
        self,
        channel_id: str,
        pipeline: str,  # research, generation, media, publishing, learning
        job: str,  # Название конкретной работы
        execution_id: Optional[str] = None,
        max_attempts: int = 3,
    ):
        self.channel_id = channel_id
        self.pipeline = pipeline
        self.job = job
        self.execution_id = execution_id or str(uuid.uuid4())
        self.max_attempts = max_attempts
        self.attempt = 1
        self.start_time = datetime.utcnow()
        self.error_logger = get_error_logger()
        self.logger = logging.getLogger(f"job.{job}")
    
    def log_error(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Логирует ошибку в pipeline_failures"""
        try:
            self.error_logger.log_exception(
                channel_id=self.channel_id,
                pipeline=self.pipeline,
                job=self.job,
                exception=exception,
                execution_id=self.execution_id,
                context=context or {},
                attempt=self.attempt,
                max_attempts=self.max_attempts,
            )
        except Exception as e:
            self.logger.error(f"Failed to log error: {e}", exc_info=True)
    
    def log_timeout(self, timeout_seconds: float) -> None:
        """Логирует timeout"""
        try:
            self.error_logger.log_timeout(
                channel_id=self.channel_id,
                pipeline=self.pipeline,
                job=self.job,
                timeout_seconds=timeout_seconds,
                execution_id=self.execution_id,
                attempt=self.attempt,
                max_attempts=self.max_attempts,
            )
        except Exception as e:
            self.logger.error(f"Failed to log timeout: {e}", exc_info=True)
    
    def log_rate_limit(
        self,
        service: str,
        retry_after: Optional[int] = None,
    ) -> None:
        """Логирует rate limit"""
        try:
            self.error_logger.log_rate_limit(
                channel_id=self.channel_id,
                pipeline=self.pipeline,
                job=self.job,
                service=service,
                retry_after=retry_after,
                execution_id=self.execution_id,
            )
        except Exception as e:
            self.logger.error(f"Failed to log rate limit: {e}", exc_info=True)
    
    def get_duration(self) -> float:
        """Получить длительность выполнения в секундах"""
        return (datetime.utcnow() - self.start_time).total_seconds()


def handle_job_errors(
    pipeline: str,
    job: str,
    max_attempts: int = 3,
    timeout_seconds: Optional[float] = None,
):
    """
    Декоратор для автоматического логирования ошибок job функций
    
    Args:
        pipeline: Этап pipeline (research, generation, media, publishing, learning)
        job: Название работы
        max_attempts: Максимум попыток
        timeout_seconds: Timeout для async функций
    
    Example:
        @handle_job_errors(pipeline="research", job="fetch_sources", max_attempts=3)
        async def fetch_manga_sources(channel_id: str) -> Dict:
            # ... код работы ...
            pass
    """
    def decorator(func: Callable) -> Callable:
        is_async = asyncio.iscoroutinefunction(func)
        
        if is_async:
            @wraps(func)
            async def async_wrapper(channel_id: str, *args, **kwargs) -> Any:
                execution_id = kwargs.pop("execution_id", None)
                context = JobExecutionContext(
                    channel_id=channel_id,
                    pipeline=pipeline,
                    job=job,
                    execution_id=execution_id,
                    max_attempts=max_attempts,
                )
                
                try:
                    if timeout_seconds:
                        result = await asyncio.wait_for(
                            func(channel_id, *args, **kwargs),
                            timeout=timeout_seconds
                        )
                    else:
                        result = await func(channel_id, *args, **kwargs)
                    
                    duration = context.get_duration()
                    logger.info(
                        f"{job} completed successfully in {duration:.1f}s",
                        extra={
                            "channel_id": channel_id,
                            "pipeline": pipeline,
                            "job": job,
                            "execution_id": context.execution_id,
                            "duration_seconds": duration,
                        }
                    )
                    return result
                
                except asyncio.TimeoutError:
                    context.log_timeout(timeout_seconds or -1)
                    logger.error(
                        f"{job} timed out after {timeout_seconds}s",
                        extra={
                            "channel_id": channel_id,
                            "pipeline": pipeline,
                            "job": job,
                            "execution_id": context.execution_id,
                        }
                    )
                    raise
                
                except Exception as e:
                    context.log_error(
                        e,
                        context={
                            "duration_seconds": context.get_duration(),
                            "exception_type": type(e).__name__,
                        }
                    )
                    logger.error(
                        f"{job} failed with {type(e).__name__}: {str(e)}",
                        extra={
                            "channel_id": channel_id,
                            "pipeline": pipeline,
                            "job": job,
                            "execution_id": context.execution_id,
                            "error_type": type(e).__name__,
                        }
                    )
                    raise
            
            return async_wrapper
        
        else:
            @wraps(func)
            def sync_wrapper(channel_id: str, *args, **kwargs) -> Any:
                execution_id = kwargs.pop("execution_id", None)
                context = JobExecutionContext(
                    channel_id=channel_id,
                    pipeline=pipeline,
                    job=job,
                    execution_id=execution_id,
                    max_attempts=max_attempts,
                )
                
                try:
                    result = func(channel_id, *args, **kwargs)
                    
                    duration = context.get_duration()
                    logger.info(
                        f"{job} completed successfully in {duration:.1f}s",
                        extra={
                            "channel_id": channel_id,
                            "pipeline": pipeline,
                            "job": job,
                            "execution_id": context.execution_id,
                            "duration_seconds": duration,
                        }
                    )
                    return result
                
                except Exception as e:
                    context.log_error(
                        e,
                        context={
                            "duration_seconds": context.get_duration(),
                            "exception_type": type(e).__name__,
                        }
                    )
                    logger.error(
                        f"{job} failed with {type(e).__name__}: {str(e)}",
                        extra={
                            "channel_id": channel_id,
                            "pipeline": pipeline,
                            "job": job,
                            "execution_id": context.execution_id,
                            "error_type": type(e).__name__,
                        }
                    )
                    raise
            
            return sync_wrapper
    
    return decorator


class JobErrorHandler:
    """
    Контекстный менеджер для логирования ошибок в blocks of code
    
    Example:
        with JobErrorHandler(channel_id, "research", "fetch_sources") as ctx:
            result = await fetch_sources()
            # Если исключение - автоматически логируется
    """
    
    def __init__(
        self,
        channel_id: str,
        pipeline: str,
        job: str,
        execution_id: Optional[str] = None,
        max_attempts: int = 3,
    ):
        self.context = JobExecutionContext(
            channel_id=channel_id,
            pipeline=pipeline,
            job=job,
            execution_id=execution_id,
            max_attempts=max_attempts,
        )
    
    def __enter__(self):
        return self.context
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            if exc_type.__name__ == "TimeoutError":
                self.context.log_timeout(300.0)
            else:
                self.context.log_error(exc_val or Exception(str(exc_type)))
        
        return False  # Re-raise exception


# Примеры использования:
"""
# Вариант 1: Использование декоратора

@handle_job_errors(pipeline="research", job="fetch_sources", timeout_seconds=30)
async def fetch_manga_sources(channel_id: str) -> Dict:
    sources = await MangaRegistry.fetch_all()
    return {"sources": sources}

# Вызов:
result = await fetch_manga_sources("ch-123", execution_id="exec-456")


# Вариант 2: Использование контекстного менеджера

async def research_job(channel_id: str) -> Dict:
    with JobErrorHandler(channel_id, "research", "fetch_sources") as ctx:
        sources = await fetch_sources()
        return {"sources": sources}
    # Если исключение - логируется в pipeline_failures


# Вариант 3: Ручное логирование (если нужен контроль)

async def custom_job(channel_id: str) -> Dict:
    ctx = JobExecutionContext(channel_id, "research", "custom_job")
    try:
        result = await do_something()
        return result
    except RateLimitError as e:
        ctx.log_rate_limit("pixabay", retry_after=60)
        raise
    except TimeoutError as e:
        ctx.log_timeout(30.0)
        raise
    except Exception as e:
        ctx.log_error(e)
        raise
"""
