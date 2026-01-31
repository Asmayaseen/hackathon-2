"""
Structured JSON Logging Configuration.

Phase 4: Kubernetes Deployment
Provides production-ready logging for container environments.

Features:
- JSON formatted logs (container-friendly)
- Configurable log levels
- Request correlation IDs
- Performance timing
"""
import logging
import sys
import os
from datetime import datetime
from typing import Optional

try:
    from pythonjsonlogger import jsonlogger
    JSON_LOGGING_AVAILABLE = True
except ImportError:
    JSON_LOGGING_AVAILABLE = False


class CustomJsonFormatter(jsonlogger.JsonFormatter if JSON_LOGGING_AVAILABLE else logging.Formatter):
    """
    Custom JSON formatter for structured logging.

    Adds standard fields for Kubernetes/container environments:
    - timestamp (ISO format)
    - level (log level name)
    - service (application name)
    - version (application version)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service_name = os.getenv("SERVICE_NAME", "evolution-todo-api")
        self.service_version = os.getenv("SERVICE_VERSION", "1.0.0")

    def add_fields(self, log_record, record, message_dict):
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)

        # Add standard fields
        log_record["timestamp"] = datetime.utcnow().isoformat() + "Z"
        log_record["level"] = record.levelname
        log_record["service"] = self.service_name
        log_record["version"] = self.service_version
        log_record["logger"] = record.name

        # Add location info for debugging
        if record.levelno >= logging.WARNING:
            log_record["location"] = {
                "file": record.filename,
                "line": record.lineno,
                "function": record.funcName,
            }


def setup_logging(
    level: Optional[str] = None,
    json_format: bool = True,
) -> logging.Logger:
    """
    Configure application logging.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
               Defaults to LOG_LEVEL env var or INFO
        json_format: Use JSON formatting (recommended for containers)

    Returns:
        Root logger instance
    """
    # Get log level from environment or parameter
    log_level = level or os.getenv("LOG_LEVEL", "INFO")
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)

    # Set formatter
    if json_format and JSON_LOGGING_AVAILABLE:
        formatter = CustomJsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
