"""
Structured Logging with JSON format for centralized log aggregation

Features:
- JSON formatted logs
- Correlation IDs for request tracing
- Contextual logging with metadata
- Log levels with filtering
- Integration with Sentry
"""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
import uuid
from contextvars import ContextVar
import traceback


# Context variable for request correlation
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)


class JSONFormatter(logging.Formatter):
    """
    Custom formatter to output logs in JSON format.

    Fields:
    - timestamp: ISO 8601 timestamp
    - level: Log level (INFO, WARNING, ERROR, etc.)
    - logger: Logger name
    - message: Log message
    - request_id: Correlation ID for request tracing
    - user_id: User ID if authenticated
    - extra: Additional context fields
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add request context
        request_id = request_id_var.get()
        if request_id:
            log_data["request_id"] = request_id

        user_id = user_id_var.get()
        if user_id:
            log_data["user_id"] = user_id

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }

        # Add extra fields
        if hasattr(record, 'extra_fields'):
            log_data["extra"] = record.extra_fields

        # Add custom attributes from record
        for key, value in record.__dict__.items():
            if key not in [
                'name', 'msg', 'args', 'created', 'filename', 'funcName',
                'levelname', 'lineno', 'module', 'msecs', 'pathname',
                'process', 'processName', 'relativeCreated', 'thread',
                'threadName', 'exc_info', 'exc_text', 'stack_info',
                'extra_fields', 'message', 'asctime'
            ]:
                if not key.startswith('_'):
                    log_data[key] = value

        return json.dumps(log_data, default=str)


class StructuredLogger:
    """
    Wrapper around Python logging with structured context.

    Usage:
        logger = StructuredLogger(__name__)
        logger.info("User logged in", user_id="123", ip="1.2.3.4")
    """

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def _log(self, level: int, message: str, **kwargs):
        """Internal logging method with structured context."""
        extra_fields = kwargs
        self.logger.log(level, message, extra={'extra_fields': extra_fields})

    def debug(self, message: str, **kwargs):
        """Log debug message with context."""
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log info message with context."""
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message with context."""
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message with context."""
        self._log(logging.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message with context."""
        self._log(logging.CRITICAL, message, **kwargs)

    def exception(self, message: str, exc_info: Exception, **kwargs):
        """Log exception with full traceback."""
        self.logger.exception(message, extra={'extra_fields': kwargs})


def configure_logging(
    log_level: str = "INFO",
    json_logs: bool = True,
    log_file: Optional[str] = None
):
    """
    Configure application logging.

    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Use JSON formatter (True for production)
        log_file: Optional log file path
    """
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))

    if json_logs:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )

    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(JSONFormatter() if json_logs else logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        root_logger.addHandler(file_handler)

    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


class RequestContextMiddleware:
    """
    FastAPI middleware to inject request context into logs.

    Adds:
    - request_id: Unique ID for each request
    - user_id: Authenticated user ID
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Generate request ID
            request_id = str(uuid.uuid4())
            request_id_var.set(request_id)

            # Extract user ID from request if available
            user_id = None  # Extract from JWT or session
            if user_id:
                user_id_var.set(user_id)

            # Add request ID to response headers
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    message["headers"].append(
                        (b"x-request-id", request_id.encode())
                    )
                await send(message)

            await self.app(scope, receive, send_wrapper)

            # Clear context
            request_id_var.set(None)
            user_id_var.set(None)
        else:
            await self.app(scope, receive, send)


# Audit logging for security events
class AuditLogger:
    """
    Specialized logger for security audit events.

    All events are logged at INFO level minimum.
    """

    def __init__(self):
        self.logger = StructuredLogger("audit")

    def log_authentication(self, success: bool, user_id: Optional[str], **kwargs):
        """Log authentication attempt."""
        self.logger.info(
            f"Authentication {'successful' if success else 'failed'}",
            event_type="authentication",
            success=success,
            user_id=user_id,
            **kwargs
        )

    def log_authorization(self, granted: bool, user_id: str, resource: str, action: str, **kwargs):
        """Log authorization decision."""
        self.logger.info(
            f"Authorization {'granted' if granted else 'denied'}",
            event_type="authorization",
            granted=granted,
            user_id=user_id,
            resource=resource,
            action=action,
            **kwargs
        )

    def log_data_access(self, user_id: str, resource_type: str, resource_id: str, action: str, **kwargs):
        """Log data access event."""
        self.logger.info(
            f"Data access: {action} on {resource_type}",
            event_type="data_access",
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            **kwargs
        )

    def log_admin_action(self, admin_id: str, action: str, target: str, **kwargs):
        """Log administrative action."""
        self.logger.warning(
            f"Admin action: {action}",
            event_type="admin_action",
            admin_id=admin_id,
            action=action,
            target=target,
            **kwargs
        )

    def log_security_event(self, event_type: str, severity: str, **kwargs):
        """Log security event."""
        log_method = getattr(self.logger, severity.lower(), self.logger.warning)
        log_method(
            f"Security event: {event_type}",
            event_type=event_type,
            severity=severity,
            **kwargs
        )
