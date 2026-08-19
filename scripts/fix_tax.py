import pathlib

p = pathlib.Path("/app/core/error_taxonomy.py")
c = p.read_text(encoding="utf-8")

# Расширяем карту статусов
old_map = """        # PERMANENT (fail)
        400: ErrorType.PERMANENT,      # Bad Request
        404: ErrorType.PERMANENT,      # Not Found
        410: ErrorType.PERMANENT,      # Gone"""
new_map = """        # PERMANENT (fail)
        400: ErrorType.PERMANENT,      # Bad Request
        404: ErrorType.PERMANENT,      # Not Found
        405: ErrorType.PERMANENT,
        409: ErrorType.PERMANENT,
        410: ErrorType.PERMANENT,      # Gone
        422: ErrorType.PERMANENT,
        451: ErrorType.PERMANENT,
        402: ErrorType.PERMANENT,      # Payment Required (anti-bot)"""
c = c.replace(old_map, new_map, 1)

# Добавляем fallback: любое исключение с .response классифицируем по статусу
old_classify = """        # Неизвестные ошибки
        return ClassifiedError(
            error_type=ErrorType.UNKNOWN,"""
new_classify = """        # Fallback: любое исключение с .response (HTTP статус) классифицируем по статусу
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
            error_type=ErrorType.UNKNOWN,"""
c = c.replace(old_classify, new_classify, 1)

p.write_text(c, encoding="utf-8")
print("taxonomy hardened")