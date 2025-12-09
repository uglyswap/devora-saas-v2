"""
Security Middleware for Devora API
Implements comprehensive security measures including:
- Security headers (HSTS, CSP, X-Frame-Options, etc.)
- Request validation
- Constant-time comparisons for tokens
- Input sanitization utilities
"""
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Optional
import secrets
import re
import logging
import os

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds security headers to all responses.
    Implements OWASP recommended security headers.
    """

    def __init__(self, app, allowed_origins: Optional[list] = None):
        super().__init__(app)
        self.allowed_origins = allowed_origins or []
        self.is_production = os.environ.get('ENV', '').lower() in ('prod', 'production')

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Strict Transport Security (HSTS)
        # Only enable in production with HTTPS
        if self.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # XSS Protection (legacy but still useful)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy (formerly Feature-Policy)
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
            "magnetometer=(), microphone=(), payment=(), usb=()"
        )

        # Content Security Policy (basic, adjust based on needs)
        # Don't apply to API responses, only HTML if any
        if response.headers.get("content-type", "").startswith("text/html"):
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' https://api.openrouter.ai https://api.stripe.com;"
            )

        return response


def constant_time_compare(val1: str, val2: str) -> bool:
    """
    Perform constant-time comparison of two strings.
    Prevents timing attacks on token validation.

    Args:
        val1: First string to compare
        val2: Second string to compare

    Returns:
        True if strings are equal, False otherwise
    """
    return secrets.compare_digest(val1.encode('utf-8'), val2.encode('utf-8'))


def validate_id_format(id_value: str, max_length: int = 255) -> bool:
    """
    Validate that an ID follows expected format.
    Prevents injection attacks and DoS via oversized inputs.

    Args:
        id_value: The ID string to validate
        max_length: Maximum allowed length

    Returns:
        True if ID is valid, False otherwise
    """
    if not id_value or not isinstance(id_value, str):
        return False

    if len(id_value) > max_length:
        return False

    # Allow alphanumeric, hyphens, and underscores only
    pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, id_value))


def sanitize_error_message(error: Exception, include_details: bool = False) -> str:
    """
    Sanitize error messages to prevent information leakage.

    Args:
        error: The exception to sanitize
        include_details: Whether to include safe details (for logging)

    Returns:
        Safe error message for client response
    """
    # Map of error types to safe messages
    safe_messages = {
        'ConnectionError': "Service temporarily unavailable",
        'TimeoutError': "Request timed out, please try again",
        'AuthenticationError': "Authentication failed",
        'PermissionError': "Access denied",
        'ValueError': "Invalid input provided",
        'KeyError': "Required field missing",
        'FileNotFoundError': "Resource not found",
    }

    error_type = type(error).__name__
    safe_message = safe_messages.get(error_type, "An error occurred. Please try again later.")

    if include_details:
        # For server-side logging only
        return f"{safe_message} (Internal: {error_type})"

    return safe_message


def log_security_event(
    event_type: str,
    request: Request,
    details: Optional[dict] = None,
    severity: str = "warning"
):
    """
    Log security-relevant events for audit trail.

    Args:
        event_type: Type of security event (e.g., 'auth_failure', 'rate_limit')
        request: FastAPI request object
        details: Additional details to log
        severity: Log level (info, warning, error)
    """
    client_ip = request.client.host if request.client else "unknown"
    endpoint = request.url.path
    method = request.method
    user_agent = request.headers.get("user-agent", "unknown")

    log_data = {
        "event_type": event_type,
        "client_ip": client_ip,
        "endpoint": endpoint,
        "method": method,
        "user_agent": user_agent[:200],  # Truncate to prevent log injection
        "details": details or {}
    }

    log_message = f"SECURITY_EVENT: {event_type} | IP={client_ip} | {method} {endpoint}"

    if severity == "error":
        logger.error(log_message, extra=log_data)
    elif severity == "warning":
        logger.warning(log_message, extra=log_data)
    else:
        logger.info(log_message, extra=log_data)


def validate_email_domain(email: str, blocked_domains: Optional[list] = None) -> bool:
    """
    Validate email domain against blocklist of disposable email providers.

    Args:
        email: Email address to validate
        blocked_domains: List of blocked domains (optional)

    Returns:
        True if email domain is allowed, False otherwise
    """
    default_blocked = [
        'tempmail.com', 'throwaway.email', 'guerrillamail.com',
        'mailinator.com', '10minutemail.com', 'temp-mail.org',
        'fakeinbox.com', 'trashmail.com', 'yopmail.com'
    ]

    blocked = blocked_domains or default_blocked

    try:
        domain = email.split('@')[1].lower()
        return domain not in blocked
    except (IndexError, AttributeError):
        return False


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for validating incoming requests.
    Checks for suspicious patterns and oversized payloads.
    """

    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.MAX_CONTENT_LENGTH:
            log_security_event("oversized_request", request, {"size": content_length})
            return JSONResponse(
                status_code=413,
                content={"error": "Request entity too large"}
            )

        # Check for suspicious user agents (basic bot detection)
        user_agent = request.headers.get("user-agent", "").lower()
        suspicious_patterns = ['sqlmap', 'nikto', 'nmap', 'masscan', 'zgrab']
        if any(pattern in user_agent for pattern in suspicious_patterns):
            log_security_event("suspicious_user_agent", request, {"user_agent": user_agent})
            # Don't block, just log - could be legitimate security testing

        return await call_next(request)


# Export all security utilities
__all__ = [
    'SecurityHeadersMiddleware',
    'RequestValidationMiddleware',
    'constant_time_compare',
    'validate_id_format',
    'sanitize_error_message',
    'log_security_event',
    'validate_email_domain',
]
