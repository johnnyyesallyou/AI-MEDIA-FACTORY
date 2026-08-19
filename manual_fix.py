import pathlib

p = pathlib.Path("/app/core/error_taxonomy.py")
c = p.read_text(encoding="utf-8")

# Полная замена classify метода
old_method_start = '''    def classify(self, error: Exception, context: Optional[str] = None) -> ClassifiedError:
        """Классифицирует ошибку и возвращает рекомендацию."""

        # HTTP ошибки
        if isinstance(error, requests.HTTPError):
            return self._classify_http_error(error, context)'''

new_method_start = '''    def classify(self, error: Exception, context: Optional[str] = None) -> ClassifiedError:
        """Классифицирует ошибку и возвращает рекомендацию."""

        # Приоритет 1: Timeout (Network)
        if isinstance(error, requests.Timeout):
            return self._classify_timeout(error, context)

        # Приоритет 2: Connection (Network)
        if isinstance(error, requests.ConnectionError):
            return self._classify_connection_error(error, context)

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
            return self._classify_request_exception(error, context)'''

c = c.replace(old_method_start, new_method_start, 1)

# Удаляем старые вызовы _classify_http_error (они больше не нужны)
# Оставляем только _classify_timeout, _classify_connection_error, _classify_request_exception

p.write_text(c, encoding="utf-8")
print("[OK] classify method rewritten with priority-based classification")