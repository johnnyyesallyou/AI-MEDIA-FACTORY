"""Error Taxonomy - Sprint 41.

Классификация ошибок для автономной обработки:
- TRANSIENT: временные ошибки (429, timeout) → retry с backoff
- PERMANENT: постоянные ошибки (404, invalid URL) → fail + alert
- CONFIGURATION: ошибки конфигурации (401, missing token) → alert + disable
- NETWORK: сетевые ошибки (DNS, connection refused) → retry
- CONTENT: ошибки контента (invalid format) → skip + log
"""
import logging
from enum import Enum
from typing import Optional, Dict, Any
import requests


logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Типы ошибок для автономной обработки."""
    TRANSIENT = "transient"
    PERMANENT = "permanent"
    CONFIGURATION = "configuration"
    NETWORK = "network"
    CONTENT = "content"
    UNKNOWN = "unknown"


class ErrorSeverity(Enum):
    """Критичность ошибки."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ClassifiedError:
    """Классифицированная ошибка с рекомендацией."""
    
    def __init__(
        self,
        error_type: ErrorType,
        severity: ErrorSeverity,
        message: str,
        original_error: Exception,
        retry_after: Optional[int] = None,
        action: str = "log",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.error_type = error_type
        self.severity = severity
        self.message = message
        self.original_error = original_error
        self.retry_after = retry_after
        self.action = action
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_type": self.error_type.value,
            "severity": self.severity.value,
            "message": self.message,
            "retry_after": self.retry_after,
            "action": self.action,
            "metadata": self.metadata,
        }


class ErrorTaxonomy:
    """Классификатор ошибок для автономной обработки."""
    
    HTTP_ERROR_MAP = {
        408: ErrorType.TRANSIENT,
        429: ErrorType.TRANSIENT,
        500: ErrorType.TRANSIENT,
        502: ErrorType.TRANSIENT,
        503: ErrorType.TRANSIENT,
        504: ErrorType.TRANSIENT,
        400: ErrorType.PERMANENT,
        404: ErrorType.PERMANENT,
        405: ErrorType.PERMANENT,
        409: ErrorType.PERMANENT,
        410: ErrorType.PERMANENT,
        422: ErrorType.PERMANENT,
        451: ErrorType.PERMANENT,
        402: ErrorType.PERMANENT,
        401: ErrorType.CONFIGURATION,
        403: ErrorType.CONFIGURATION,
    }
    
    def classify(self, error: Exception, context: Optional[str] = None) -> ClassifiedError:
        """Классифицирует ошибку и возвращает рекомендацию."""
        
        # Приоритет 1: Timeout (Network)
        if isinstance(error, requests.Timeout):
            return ClassifiedError(
                error_type=ErrorType.NETWORK,
                severity=ErrorSeverity.LOW,
                message=f"Timeout: {error}",
                original_error=error,
                action="retry",
                metadata={"context": context},
            )
        
        # Приоритет 2: Connection (Network)
        if isinstance(error, requests.ConnectionError):
            error_str = str(error)
            if "Name or service not known" in error_str or "DNS" in error_str:
                return ClassifiedError(
                    error_type=ErrorType.NETWORK,
                    severity=ErrorSeverity.MEDIUM,
                    message=f"DNS resolution failed: {error}",
                    original_error=error,
                    action="retry",
                    metadata={"context": context, "error_detail": "dns"},
                )
            elif "Connection refused" in error_str:
                return ClassifiedError(
                    error_type=ErrorType.NETWORK,
                    severity=ErrorSeverity.MEDIUM,
                    message=f"Connection refused: {error}",
                    original_error=error,
                    action="retry",
                    metadata={"context": context, "error_detail": "refused"},
                )
            else:
                return ClassifiedError(
                    error_type=ErrorType.NETWORK,
                    severity=ErrorSeverity.MEDIUM,
                    message=f"Connection error: {error}",
                    original_error=error,
                    action="retry",
                    metadata={"context": context},
                )
        
        # Приоритет 3: HTTP ошибки (через .response атрибут)
        response = getattr(error, "response", None)
        if response is not None and hasattr(response, "status_code"):
            status_code = response.status_code
            error_type = self.HTTP_ERROR_MAP.get(status_code, ErrorType.UNKNOWN)
            
            # Определяем severity и action
            if error_type == ErrorType.CONFIGURATION:
                severity = ErrorSeverity.HIGH
                action = "alert_disable"
            elif error_type == ErrorType.PERMANENT:
                severity = ErrorSeverity.MEDIUM
                action = "fail"
            elif error_type == ErrorType.TRANSIENT:
                severity = ErrorSeverity.LOW
                action = "retry"
            else:
                severity = ErrorSeverity.MEDIUM
                action = "log"
            
            # Извлекаем Retry-After если есть
            retry_after = None
            if status_code == 429 and hasattr(response, "headers"):
                retry_after_header = response.headers.get("Retry-After")
                if retry_after_header:
                    try:
                        retry_after = int(retry_after_header)
                    except (ValueError, TypeError):
                        pass
            
            return ClassifiedError(
                error_type=error_type,
                severity=severity,
                message=f"HTTP {status_code}: {error}",
                original_error=error,
                retry_after=retry_after,
                action=action,
                metadata={
                    "status_code": status_code,
                    "context": context,
                    "url": getattr(response, "url", None),
                },
            )
        
        # Приоритет 4: Общие RequestException (Network)
        if isinstance(error, requests.RequestException):
            return ClassifiedError(
                error_type=ErrorType.NETWORK,
                severity=ErrorSeverity.LOW,
                message=f"Request failed: {error}",
                original_error=error,
                action="retry",
                metadata={"context": context},
            )
        
        # Неизвестные ошибки
        return ClassifiedError(
            error_type=ErrorType.UNKNOWN,
            severity=ErrorSeverity.MEDIUM,
            message=f"Unknown error: {type(error).__name__}",
            original_error=error,
            action="log",
        )


taxonomy = ErrorTaxonomy()


def classify_error(error: Exception, context: Optional[str] = None) -> ClassifiedError:
    """Удобная функция для классификации ошибок."""
    return taxonomy.classify(error, context)