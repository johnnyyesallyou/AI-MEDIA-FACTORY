"""Error Taxonomy - Sprint 41.

Классификация ошибок для автономной обработки:
- TRANSIENT: временные ошибки (429, timeout) → retry с backoff
- PERMANENT: постоянные ошибки (404, invalid URL) → fail + alert
- CONFIGURATION: ошибки конфигурации (401, missing token) → alert + disable
- NETWORK: сетевые ошибки (DNS, connection refused) → retry
- CONTENT: ошибки контента (invalid format) → skip + log

Каждая ошибка классифицируется и получает рекомендацию по обработке.
"""
import logging
from enum import Enum
from typing import Optional, Dict, Any
import requests


logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Типы ошибок для автономной обработки."""
    TRANSIENT = "transient"        # Временные: retry
    PERMANENT = "permanent"        # Постоянные: fail + alert
    CONFIGURATION = "configuration" # Конфигурация: alert + disable
    NETWORK = "network"            # Сеть: retry
    CONTENT = "content"            # Контент: skip + log
    UNKNOWN = "unknown"            # Неизвестные: log + alert


class ErrorSeverity(Enum):
    """Критичность ошибки."""
    LOW = "low"           # Можно игнорировать (skip)
    MEDIUM = "medium"     # Retry или alert
    HIGH = "high"         # Alert + возможно disable
    CRITICAL = "critical" # Alert + disable + notify


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
        self.retry_after = retry_after  # seconds
        self.action = action  # log, retry, alert, disable
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
    
    # HTTP статусы → тип ошибки
    HTTP_ERROR_MAP = {
        # TRANSIENT (retry)
        408: ErrorType.TRANSIENT,      # Request Timeout
        429: ErrorType.TRANSIENT,      # Too Many Requests (rate limit)
        500: ErrorType.TRANSIENT,      # Internal Server Error
        502: ErrorType.TRANSIENT,      # Bad Gateway
        503: ErrorType.TRANSIENT,      # Service Unavailable
        504: ErrorType.TRANSIENT,      # Gateway Timeout
        
        # PERMANENT (fail)
        400: ErrorType.PERMANENT,      # Bad Request
        404: ErrorType.PERMANENT,      # Not Found
        405: ErrorType.PERMANENT,
        409: ErrorType.PERMANENT,
        410: ErrorType.PERMANENT,      # Gone
        422: ErrorType.PERMANENT,
        451: ErrorType.PERMANENT,
        402: ErrorType.PERMANENT,      # Payment Required (anti-bot)
        
        # CONFIGURATION (alert + disable)
        401: ErrorType.CONFIGURATION,  # Unauthorized
        403: ErrorType.CONFIGURATION,  # Forbidden
        
        # NETWORK (retry)
        # Обработка отдельно (не HTTP)
    }
    
    def classify(self, error: Exception, context: Optional[str] = None) -> ClassifiedError:
        """Классифицирует ошибку и возвращает рекомендацию."""
        
        # HTTP ошибки
        if isinstance(error, requests.HTTPError):
            return self._classify_http_error(error, context)
        
        # Timeout ошибки
        if isinstance(error, requests.Timeout):
            return self._classify_timeout(error, context)
        
        # Connection ошибки
        if isinstance(error, requests.ConnectionError):
            return self._classify_connection_error(error, context)
        
        # RequestException (общая)
        if isinstance(error, requests.RequestException):
            return self._classify_request_exception(error, context)
        
        # Fallback: любое исключение с .response (HTTP статус) классифицируем по статусу
        response = getattr(error, "response", None)
        if response is not None:
            status_code = getattr(response, "status_code", 0) or 0
            error_type = self.HTTP_ERROR_MAP.get(status_code, ErrorType.UNKNOWN)
            return ClassifiedError(
                error_type=error_type,
                severity=ErrorSeverity.HIGH if error_type == ErrorType.CONFIGURATION else ErrorSeverity.MEDIUM,
                message=f"HTTP {status_code}: {error}",
                original_error=error,
                action={"transient": "retry", "network": "retry", "permanent": "fail",
                        "configuration": "alert_disable"}.get(error_type.value, "log"),
                metadata={"status_code": status_code, "context": context},
            )

        # Неизвестные ошибки
        return ClassifiedError(
            error_type=ErrorType.UNKNOWN,
            severity=ErrorSeverity.MEDIUM,
            message=f"Unknown error: {type(error).__name__}",
            original_error=error,
            action="log",
        )
    
    def _classify_http_error(self, error: requests.HTTPError, context: Optional[str]) -> ClassifiedError:
        """Классификация HTTP ошибок."""
        response = error.response
        status_code = response.status_code if response else 0
        
        error_type = self.HTTP_ERROR_MAP.get(status_code, ErrorType.UNKNOWN)
        
        # Определяем severity
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
        
        # Извлекаем Retry-After header если есть
        retry_after = None
        if response and status_code == 429:
            retry_after_header = response.headers.get("Retry-After")
            if retry_after_header:
                try:
                    retry_after = int(retry_after_header)
                except ValueError:
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
                "url": response.url if response else None,
            },
        )
    
    def _classify_timeout(self, error: requests.Timeout, context: Optional[str]) -> ClassifiedError:
        """Классификация timeout ошибок."""
        return ClassifiedError(
            error_type=ErrorType.NETWORK,
            severity=ErrorSeverity.LOW,
            message=f"Timeout: {error}",
            original_error=error,
            action="retry",
            metadata={"context": context},
        )
    
    def _classify_connection_error(self, error: requests.ConnectionError, context: Optional[str]) -> ClassifiedError:
        """Классификация connection ошибок."""
        error_str = str(error)
        
        # DNS resolution errors
        if "Name or service not known" in error_str or "DNS" in error_str:
            return ClassifiedError(
                error_type=ErrorType.NETWORK,
                severity=ErrorSeverity.MEDIUM,
                message=f"DNS resolution failed: {error}",
                original_error=error,
                action="retry",
                metadata={"context": context, "error_detail": "dns"},
            )
        
        # Connection refused
        if "Connection refused" in error_str:
            return ClassifiedError(
                error_type=ErrorType.NETWORK,
                severity=ErrorSeverity.MEDIUM,
                message=f"Connection refused: {error}",
                original_error=error,
                action="retry",
                metadata={"context": context, "error_detail": "refused"},
            )
        
        # Generic connection error
        return ClassifiedError(
            error_type=ErrorType.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            message=f"Connection error: {error}",
            original_error=error,
            action="retry",
            metadata={"context": context},
        )
    
    def _classify_request_exception(self, error: requests.RequestException, context: Optional[str]) -> ClassifiedError:
        """Классификация общих RequestException."""
        return ClassifiedError(
            error_type=ErrorType.NETWORK,
            severity=ErrorSeverity.LOW,
            message=f"Request failed: {error}",
            original_error=error,
            action="retry",
            metadata={"context": context},
        )


# Глобальный instance
taxonomy = ErrorTaxonomy()


def classify_error(error: Exception, context: Optional[str] = None) -> ClassifiedError:
    """Удобная функция для классификации ошибок."""
    return taxonomy.classify(error, context)