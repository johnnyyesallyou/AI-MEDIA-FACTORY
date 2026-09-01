"""
Sprint 66.5: ErrorLogger Service

Централизованный сервис для логирования ошибок pipeline.
Используется всеми workers для записи failures в БД.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import traceback
from enum import Enum

from sqlalchemy.orm import Session
from core.models.pipeline_failure_orm import PipelineFailure
from core.database import SessionLocal

logger = logging.getLogger(__name__)


class ErrorType(str, Enum):
    """Типы ошибок в pipeline"""
    TIMEOUT = "timeout"
    EXCEPTION = "exception"
    RATE_LIMIT = "rate_limit"
    NETWORK = "network"
    VALIDATION = "validation"
    LLM_ERROR = "llm_error"
    MEDIA_ERROR = "media_error"
    PUBLISH_ERROR = "publish_error"
    UNKNOWN = "unknown"


class ErrorLogger:
    """Логирует ошибки pipeline в БД для отслеживания и анализа"""
    
    def __init__(self, db: Optional[Session] = None):
        """Инициализация logger"""
        self.db = db or SessionLocal()
        self.own_session = db is None
    
    def log_error(
        self,
        channel_id: str,
        pipeline: str,  # research, generation, media, publishing, learning
        job: str,  # Конкретная задача
        error_type: ErrorType,
        error_message: str,
        error_code: Optional[str] = None,
        execution_id: Optional[str] = None,
        job_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        attempt: int = 1,
        max_attempts: int = 3,
        retry_at: Optional[datetime] = None,
    ) -> PipelineFailure:
        """
        Записать ошибку в БД
        
        Args:
            channel_id: ID канала
            pipeline: Этап pipeline (research, generation, media, publishing, learning)
            job: Название работы (fetch_sources, generate_post, format_media, publish_telegram)
            error_type: Тип ошибки
            error_message: Текст ошибки
            error_code: Код ошибки (HTTP status или custom)
            execution_id: ID выполнения для трассировки
            job_id: ID работы
            context: Дополнительный контекст ({request, response, headers, etc})
            attempt: Номер попытки
            max_attempts: Максимум попыток
            retry_at: Когда повторить (если retryable)
        
        Returns:
            Созданный объект PipelineFailure
        """
        try:
            failure = PipelineFailure(
                channel_id=channel_id,
                pipeline=pipeline,
                job=job,
                error_type=error_type.value if isinstance(error_type, ErrorType) else error_type,
                error_message=error_message,
                error_code=error_code,
                execution_id=execution_id,
                job_id=job_id,
                context=context or {},
                attempt=attempt,
                max_attempts=max_attempts,
                retry_at=retry_at,
            )
            
            self.db.add(failure)
            self.db.commit()
            self.db.refresh(failure)
            
            logger.warning(
                f"Pipeline failure logged",
                extra={
                    "channel_id": channel_id,
                    "pipeline": pipeline,
                    "job": job,
                    "error_type": error_type.value if isinstance(error_type, ErrorType) else error_type,
                    "execution_id": execution_id,
                    "failure_id": failure.id,
                }
            )
            
            return failure
        
        except Exception as e:
            logger.error(f"Failed to log error: {e}", exc_info=True)
            raise
    
    def log_exception(
        self,
        channel_id: str,
        pipeline: str,
        job: str,
        exception: Exception,
        execution_id: Optional[str] = None,
        job_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        attempt: int = 1,
        max_attempts: int = 3,
    ) -> PipelineFailure:
        """
        Логирование исключения
        
        Args:
            channel_id: ID канала
            pipeline: Этап pipeline
            job: Название работы
            exception: Исключение
            execution_id: ID выполнения
            job_id: ID работы
            context: Дополнительный контекст
            attempt: Номер попытки
            max_attempts: Максимум попыток
        
        Returns:
            Созданный объект PipelineFailure
        """
        error_message = f"{exception.__class__.__name__}: {str(exception)}"
        tb = traceback.format_exc()
        
        context = context or {}
        context["traceback"] = tb
        
        # Определяем тип ошибки
        error_type = self._classify_exception(exception)
        
        # Определяем код ошибки
        error_code = None
        if hasattr(exception, "status_code"):
            error_code = str(exception.status_code)
        
        return self.log_error(
            channel_id=channel_id,
            pipeline=pipeline,
            job=job,
            error_type=error_type,
            error_message=error_message,
            error_code=error_code,
            execution_id=execution_id,
            job_id=job_id,
            context=context,
            attempt=attempt,
            max_attempts=max_attempts,
        )
    
    def log_timeout(
        self,
        channel_id: str,
        pipeline: str,
        job: str,
        timeout_seconds: float,
        execution_id: Optional[str] = None,
        job_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        attempt: int = 1,
        max_attempts: int = 3,
    ) -> PipelineFailure:
        """Логирование timeout"""
        context = context or {}
        context["timeout_seconds"] = timeout_seconds
        
        return self.log_error(
            channel_id=channel_id,
            pipeline=pipeline,
            job=job,
            error_type=ErrorType.TIMEOUT,
            error_message=f"Task timeout after {timeout_seconds}s",
            error_code="TIMEOUT",
            execution_id=execution_id,
            job_id=job_id,
            context=context,
            attempt=attempt,
            max_attempts=max_attempts,
            retry_at=datetime.utcnow() + timedelta(seconds=min(300, timeout_seconds * 1.5)),
        )
    
    def log_rate_limit(
        self,
        channel_id: str,
        pipeline: str,
        job: str,
        service: str,  # "pixabay", "ollama", "telegram", etc
        retry_after: Optional[int] = None,
        execution_id: Optional[str] = None,
        job_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> PipelineFailure:
        """Логирование rate limit error"""
        context = context or {}
        context["service"] = service
        
        retry_at = None
        if retry_after:
            retry_at = datetime.utcnow() + timedelta(seconds=retry_after)
        
        return self.log_error(
            channel_id=channel_id,
            pipeline=pipeline,
            job=job,
            error_type=ErrorType.RATE_LIMIT,
            error_message=f"Rate limited by {service}",
            error_code="429",
            execution_id=execution_id,
            job_id=job_id,
            context=context,
            retry_at=retry_at,
        )
    
    def get_channel_failures(
        self,
        channel_id: str,
        limit: int = 100,
        unresolved_only: bool = True,
    ) -> list:
        """Получить ошибки канала"""
        query = self.db.query(PipelineFailure).filter(
            PipelineFailure.channel_id == channel_id
        )
        
        if unresolved_only:
            query = query.filter(PipelineFailure.resolved == False)
        
        return query.order_by(PipelineFailure.created_at.desc()).limit(limit).all()
    
    def get_error_stats(self, channel_id: str) -> Dict[str, Any]:
        """Получить статистику ошибок канала"""
        from sqlalchemy import func
        
        failures = self.db.query(PipelineFailure).filter(
            PipelineFailure.channel_id == channel_id,
            PipelineFailure.created_at > datetime.utcnow() - timedelta(days=7),
        ).all()
        
        if not failures:
            return {
                "total_errors": 0,
                "by_type": {},
                "by_pipeline": {},
                "by_job": {},
                "unresolved": 0,
            }
        
        by_type = {}
        by_pipeline = {}
        by_job = {}
        unresolved = 0
        
        for failure in failures:
            by_type[failure.error_type] = by_type.get(failure.error_type, 0) + 1
            by_pipeline[failure.pipeline] = by_pipeline.get(failure.pipeline, 0) + 1
            by_job[failure.job] = by_job.get(failure.job, 0) + 1
            
            if not failure.resolved:
                unresolved += 1
        
        return {
            "total_errors": len(failures),
            "by_type": by_type,
            "by_pipeline": by_pipeline,
            "by_job": by_job,
            "unresolved": unresolved,
        }
    
    def mark_resolved(self, failure_id: str, resolution: str = "success") -> Optional[PipelineFailure]:
        """Отметить ошибку как разрешённую"""
        failure = self.db.query(PipelineFailure).filter(
            PipelineFailure.id == failure_id
        ).first()
        
        if failure:
            failure.mark_resolved(resolution)
            self.db.commit()
            self.db.refresh(failure)
            logger.info(f"Failure {failure_id} marked as resolved: {resolution}")
        
        return failure
    
    def cleanup(self) -> None:
        """Закрыть сессию если она была создана в __init__"""
        if self.own_session:
            self.db.close()
    
    @staticmethod
    def _classify_exception(exception: Exception) -> ErrorType:
        """Классифицировать исключение по типу"""
        exc_type = type(exception).__name__
        exc_str = str(exception).lower()
        
        if "timeout" in exc_type.lower() or "timeout" in exc_str:
            return ErrorType.TIMEOUT
        elif "rate" in exc_str or "429" in exc_str:
            return ErrorType.RATE_LIMIT
        elif "connection" in exc_str or "network" in exc_str:
            return ErrorType.NETWORK
        elif "validation" in exc_str or "invalid" in exc_str:
            return ErrorType.VALIDATION
        elif "llm" in exc_str or "generation" in exc_str:
            return ErrorType.LLM_ERROR
        elif "media" in exc_str or "image" in exc_str or "video" in exc_str:
            return ErrorType.MEDIA_ERROR
        elif "publish" in exc_str or "telegram" in exc_str or "vk" in exc_str:
            return ErrorType.PUBLISH_ERROR
        else:
            return ErrorType.EXCEPTION


# Глобальный экземпляр для удобства
_error_logger: Optional[ErrorLogger] = None


def get_error_logger(db: Optional[Session] = None) -> ErrorLogger:
    """Получить глобальный ErrorLogger"""
    global _error_logger
    
    if _error_logger is None or db is not None:
        _error_logger = ErrorLogger(db)
    
    return _error_logger


# Примеры использования:
"""
from backend.core.error_logger import get_error_logger, ErrorType

logger = get_error_logger()

# Логирование ошибки
try:
    result = await fetch_sources("remanga")
except TimeoutError as e:
    failure = logger.log_timeout(
        channel_id="ch-123",
        pipeline="research",
        job="fetch_sources",
        timeout_seconds=30.0,
        execution_id="exec-456"
    )

# Логирование исключения
try:
    await publish_telegram(post)
except Exception as e:
    failure = logger.log_exception(
        channel_id="ch-123",
        pipeline="publishing",
        job="publish_telegram",
        exception=e,
        execution_id="exec-456"
    )

# Получить статистику
stats = logger.get_error_stats("ch-123")
print(f"Errors by type: {stats['by_type']}")

# Отметить как разрешённую
logger.mark_resolved(failure.id, "retry_success")
"""
