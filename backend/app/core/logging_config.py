"""
Sprint 66.4: Structured JSON Logging Configuration for AI Media Factory

This module provides centralized JSON logging setup with:
- JSON-formatted logs for machine parsing
- Request/Response tracking
- Performance metrics
- Error tracing with execution IDs
- Separate log files for different severity levels
"""

import logging
import json
import sys
import os
from pathlib import Path
from datetime import datetime
from pythonjsonlogger import jsonlogger
from typing import Dict, Any
import traceback


class StructuredFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter that adds context and structured fields"""

    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        super().add_fields(log_record, record, message_dict)

        # Add standard fields
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno

        # Add execution context if available
        if hasattr(record, 'execution_id'):
            log_record['execution_id'] = record.execution_id
        if hasattr(record, 'channel_id'):
            log_record['channel_id'] = record.channel_id
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id

        # Add exception details if present
        if record.exc_info and not log_record.get('exc_info'):
            log_record['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else 'Unknown',
                'message': str(record.exc_info[1]) if record.exc_info[1] else '',
                'traceback': traceback.format_exception(*record.exc_info)
            }

        # Add custom fields
        if hasattr(record, 'duration_ms'):
            log_record['duration_ms'] = record.duration_ms
        if hasattr(record, 'status_code'):
            log_record['status_code'] = record.status_code
        if hasattr(record, 'endpoint'):
            log_record['endpoint'] = record.endpoint


def setup_logging(
    log_dir: str = "logs",
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
    enable_json: bool = True
) -> None:
    """
    Setup structured JSON logging for the application.

    Args:
        log_dir: Directory to store log files
        console_level: Logging level for console output
        file_level: Logging level for file output
        enable_json: Whether to use JSON formatting (True) or standard format (False)
    """
    # Create logs directory if it doesn't exist
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Define formatters
    if enable_json:
        console_formatter = StructuredFormatter()
        file_formatter = StructuredFormatter()
    else:
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
        )

    # Console handler (INFO and above)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler for all logs
    all_logs_file = os.path.join(log_dir, "app.log")
    file_handler = logging.FileHandler(all_logs_file)
    file_handler.setLevel(file_level)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # File handler for errors and warnings
    error_logs_file = os.path.join(log_dir, "errors.log")
    error_handler = logging.FileHandler(error_logs_file)
    error_handler.setLevel(logging.WARNING)
    error_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_handler)

    # File handler for debug info
    debug_logs_file = os.path.join(log_dir, "debug.log")
    debug_handler = logging.FileHandler(debug_logs_file)
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(file_formatter)
    root_logger.addHandler(debug_handler)

    # Suppress overly verbose loggers
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    root_logger.info("Logging system initialized", extra={
        'log_dir': log_dir,
        'console_level': logging.getLevelName(console_level),
        'file_level': logging.getLevelName(file_level),
        'json_enabled': enable_json
    })


def get_logger(name: str) -> logging.LoggerAdapter:
    """
    Get a named logger with context support.

    Args:
        name: Logger name (typically __name__)

    Returns:
        LoggerAdapter with context support
    """
    base_logger = logging.getLogger(name)
    return logging.LoggerAdapter(base_logger, {})


class ExecutionContextFilter(logging.Filter):
    """Filter that injects execution context into log records"""

    def filter(self, record: logging.LogRecord) -> bool:
        # This can be extended to pull execution context from thread-local storage
        # or async context variables
        return True


# Initialize logging on module import
if os.getenv("APP_ENV") != "test":
    setup_logging(
        log_dir=os.getenv("LOG_DIR", "logs"),
        console_level=logging.getLevelName(os.getenv("LOG_LEVEL", "INFO")),
        file_level=logging.DEBUG,
        enable_json=os.getenv("JSON_LOGGING", "true").lower() == "true"
    )
