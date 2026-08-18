"""Monitoring & Logging - Sprint 34.

Structured logging для production observability.
"""
import logging
import json
import time
from datetime import datetime
from typing import Dict, Any
from functools import wraps


class StructuredFormatter(logging.Formatter):
    """JSON formatter для structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Добавляем extra fields если есть
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        return json.dumps(log_data, ensure_ascii=False)


def setup_structured_logging(level: str = "INFO"):
    """Настраивает structured logging для production."""
    handler = logging.StreamHandler()
    handler.setFormatter(StructuredFormatter())
    
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    root_logger.addHandler(handler)
    
    # Подавляем noisy loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


class JobMetrics:
    """Собирает метрики для jobs."""
    
    def __init__(self, job_name: str):
        self.job_name = job_name
        self.logger = logging.getLogger(f"metrics.{job_name}")
        self.start_time = None
    
    def start(self):
        """Начинает измерение."""
        self.start_time = time.time()
        self.logger.info(
            "job_started",
            extra={"extra": {"job": self.job_name, "event": "start"}}
        )
    
    def finish(self, result: Dict[str, Any]):
        """Завершает измерение и логирует результат."""
        if self.start_time:
            duration = time.time() - self.start_time
            self.logger.info(
                "job_finished",
                extra={"extra": {
                    "job": self.job_name,
                    "event": "finish",
                    "duration_seconds": round(duration, 2),
                    "result": result,
                }}
            )
    
    def error(self, error: Exception):
        """Логирует ошибку."""
        self.logger.error(
            "job_error",
            extra={"extra": {
                "job": self.job_name,
                "event": "error",
                "error_type": type(error).__name__,
                "error_message": str(error),
            }}
        )


def monitor_job(job_name: str):
    """Декоратор для мониторинга jobs."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            metrics = JobMetrics(job_name)
            metrics.start()
            
            try:
                result = func(*args, **kwargs)
                metrics.finish(result)
                return result
            except Exception as e:
                metrics.error(e)
                raise
        
        return wrapper
    return decorator