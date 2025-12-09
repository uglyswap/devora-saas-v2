"""
Sentry Integration for Error Tracking and Performance Monitoring

Features:
- Error tracking with context
- Performance monitoring (APM)
- Custom event tracking
- Release tracking
- User feedback integration
"""

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import logging
import os
from typing import Optional, Dict, Any


class SentryConfig:
    """Sentry configuration for different environments."""

    def __init__(
        self,
        dsn: str,
        environment: str = "production",
        release: Optional[str] = None,
        sample_rate: float = 1.0,
        traces_sample_rate: float = 0.1
    ):
        self.dsn = dsn
        self.environment = environment
        self.release = release or os.getenv("GIT_COMMIT", "unknown")
        self.sample_rate = sample_rate
        self.traces_sample_rate = traces_sample_rate


def initialize_sentry(config: SentryConfig):
    """
    Initialize Sentry SDK with optimal configuration.

    Args:
        config: SentryConfig instance with environment settings
    """
    # Configure logging integration
    logging_integration = LoggingIntegration(
        level=logging.INFO,        # Capture info and above as breadcrumbs
        event_level=logging.ERROR  # Send errors as events
    )

    sentry_sdk.init(
        dsn=config.dsn,
        environment=config.environment,
        release=config.release,

        # Performance Monitoring
        traces_sample_rate=config.traces_sample_rate,
        _experiments={
            "profiles_sample_rate": 0.1,  # Profiling for 10% of transactions
        },

        # Integrations
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
            RedisIntegration(),
            logging_integration,
        ],

        # Error sampling
        sample_rate=config.sample_rate,

        # Send default PII (be careful in production)
        send_default_pii=False,

        # Before send hook for filtering
        before_send=before_send_hook,

        # Before breadcrumb hook
        before_breadcrumb=before_breadcrumb_hook,

        # Max breadcrumbs
        max_breadcrumbs=50,

        # Attach stack trace to messages
        attach_stacktrace=True,

        # Debug mode (only for development)
        debug=config.environment == "development",
    )

    logging.info(f"Sentry initialized for environment: {config.environment}")


def before_send_hook(event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Filter and modify events before sending to Sentry.

    Args:
        event: Sentry event data
        hint: Additional context

    Returns:
        Modified event or None to drop
    """
    # Don't send certain exceptions
    if 'exc_info' in hint:
        exc_type, exc_value, tb = hint['exc_info']

        # Ignore common non-critical exceptions
        ignored_exceptions = [
            'KeyboardInterrupt',
            'SystemExit',
            'BrokenPipeError',
        ]

        if exc_type.__name__ in ignored_exceptions:
            return None

    # Sanitize sensitive data
    if 'request' in event:
        # Remove sensitive headers
        if 'headers' in event['request']:
            sensitive_headers = ['Authorization', 'Cookie', 'X-API-Key']
            for header in sensitive_headers:
                if header in event['request']['headers']:
                    event['request']['headers'][header] = '[Filtered]'

    # Add custom tags
    event.setdefault('tags', {})
    event['tags']['service'] = 'devora-backend'

    return event


def before_breadcrumb_hook(crumb: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Filter breadcrumbs before adding to event.

    Args:
        crumb: Breadcrumb data
        hint: Additional context

    Returns:
        Modified breadcrumb or None to drop
    """
    # Don't log health check requests
    if crumb.get('category') == 'httplib' and '/health' in crumb.get('data', {}).get('url', ''):
        return None

    return crumb


class SentryMonitor:
    """Helper class for custom Sentry monitoring."""

    @staticmethod
    def capture_message(message: str, level: str = "info", **kwargs):
        """
        Send custom message to Sentry.

        Args:
            message: Message to log
            level: Log level (debug, info, warning, error, fatal)
            **kwargs: Additional context
        """
        with sentry_sdk.push_scope() as scope:
            for key, value in kwargs.items():
                scope.set_extra(key, value)

            sentry_sdk.capture_message(message, level)

    @staticmethod
    def capture_exception(exception: Exception, **kwargs):
        """
        Capture exception with additional context.

        Args:
            exception: Exception to capture
            **kwargs: Additional context
        """
        with sentry_sdk.push_scope() as scope:
            for key, value in kwargs.items():
                scope.set_extra(key, value)

            sentry_sdk.capture_exception(exception)

    @staticmethod
    def set_user(user_id: str, email: Optional[str] = None, username: Optional[str] = None):
        """
        Set user context for error tracking.

        Args:
            user_id: User ID
            email: User email
            username: Username
        """
        sentry_sdk.set_user({
            "id": user_id,
            "email": email,
            "username": username
        })

    @staticmethod
    def set_context(name: str, context: Dict[str, Any]):
        """
        Set custom context for events.

        Args:
            name: Context name
            context: Context data
        """
        sentry_sdk.set_context(name, context)

    @staticmethod
    def add_breadcrumb(message: str, category: str = "custom", level: str = "info", **data):
        """
        Add custom breadcrumb for debugging.

        Args:
            message: Breadcrumb message
            category: Category (e.g., "auth", "database", "api")
            level: Log level
            **data: Additional data
        """
        sentry_sdk.add_breadcrumb(
            message=message,
            category=category,
            level=level,
            data=data
        )

    @staticmethod
    def start_transaction(name: str, op: str = "task") -> Any:
        """
        Start performance monitoring transaction.

        Args:
            name: Transaction name
            op: Operation type (e.g., "http.server", "db.query", "task")

        Returns:
            Transaction context manager
        """
        return sentry_sdk.start_transaction(name=name, op=op)

    @staticmethod
    def start_span(operation: str, description: str = "") -> Any:
        """
        Start a span within a transaction for detailed performance tracking.

        Args:
            operation: Span operation (e.g., "db.query", "http.client")
            description: Detailed description

        Returns:
            Span context manager
        """
        return sentry_sdk.start_span(op=operation, description=description)


# Decorator for automatic transaction tracking
def monitor_performance(operation: str):
    """
    Decorator to automatically track function performance.

    Usage:
        @monitor_performance("api.endpoint")
        async def my_endpoint():
            ...
    """
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            with sentry_sdk.start_transaction(op=operation, name=func.__name__):
                return await func(*args, **kwargs)

        def sync_wrapper(*args, **kwargs):
            with sentry_sdk.start_transaction(op=operation, name=func.__name__):
                return func(*args, **kwargs)

        # Return appropriate wrapper
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
