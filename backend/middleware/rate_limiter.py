"""
Rate Limiting Middleware using slowapi
Prevents API abuse and ensures fair usage across different endpoint types.

Configuration:
- AUTH endpoints: 5/minute (login, register) - strict to prevent brute force
- GENERATE endpoints: 10/minute - based on computational cost
- DEFAULT: 100/minute - general API usage

Usage:
    from middleware import limiter, RateLimits, rate_limit

    @router.post('/login')
    @limiter.limit(RateLimits.AUTH_LOGIN)
    async def login(request: Request, ...):
        ...
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, status
from fastapi.responses import JSONResponse
from typing import Callable, Optional
import logging
import os

logger = logging.getLogger(__name__)

# Get Redis URL from environment for production, fallback to in-memory for dev
REDIS_URL = os.environ.get('REDIS_URL', None)
STORAGE_URI = f"redis://{REDIS_URL}" if REDIS_URL else "memory://"

# Initialize rate limiter with intelligent key extraction
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],  # Global default
    storage_uri=STORAGE_URI,
    strategy="fixed-window"
)


class RateLimits:
    """
    Predefined rate limits for different operation types.
    Adjust these values based on your application's needs and server capacity.
    """

    # ===========================
    # Authentication endpoints (strictest limits - prevent brute force)
    # ===========================
    AUTH_LOGIN = "5/minute"
    AUTH_REGISTER = "3/minute"
    AUTH_PASSWORD_RESET = "3/hour"
    AUTH_VERIFY_EMAIL = "10/minute"
    AUTH_REFRESH_TOKEN = "30/minute"

    # ===========================
    # Generation endpoints (based on computational cost)
    # ===========================
    GENERATE_SIMPLE = "20/minute"
    GENERATE_STANDARD = "10/minute"  # Default for most generation
    GENERATE_AGENTIC = "10/minute"
    GENERATE_FULLSTACK = "5/minute"  # Most expensive operations
    GENERATE_COMPLEX = "3/minute"    # Very heavy operations

    # ===========================
    # Project operations
    # ===========================
    PROJECT_CREATE = "30/minute"
    PROJECT_UPDATE = "60/minute"
    PROJECT_DELETE = "10/minute"
    PROJECT_LIST = "100/minute"
    PROJECT_EXPORT = "5/minute"

    # ===========================
    # Billing operations
    # ===========================
    BILLING_CHECKOUT = "5/minute"
    BILLING_PORTAL = "10/minute"
    BILLING_WEBHOOK = "1000/minute"  # Webhooks need higher limits (Stripe retries)

    # ===========================
    # Admin operations
    # ===========================
    ADMIN_STATS = "20/minute"
    ADMIN_CONFIG = "10/minute"
    ADMIN_USER_MANAGEMENT = "30/minute"

    # ===========================
    # Default limits
    # ===========================
    DEFAULT = "100/minute"
    DEFAULT_STRICT = "30/minute"
    DEFAULT_RELAXED = "200/minute"


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Custom handler for rate limit exceeded errors.
    Returns a user-friendly JSON response with retry information.

    Args:
        request: FastAPI request object
        exc: RateLimitExceeded exception from slowapi

    Returns:
        JSONResponse with 429 status and rate limit details
    """
    client_ip = get_remote_address(request)
    endpoint = request.url.path

    logger.warning(
        f"Rate limit exceeded: IP={client_ip}, endpoint={endpoint}, "
        f"limit={exc.detail if hasattr(exc, 'detail') else 'unknown'}"
    )

    # Parse retry-after from exception if available
    retry_after = 60  # Default to 60 seconds
    if hasattr(exc, 'detail') and exc.detail:
        detail_str = str(exc.detail)
        # Try to extract the time from the limit (e.g., "5 per 1 minute")
        if 'minute' in detail_str.lower():
            retry_after = 60
        elif 'hour' in detail_str.lower():
            retry_after = 3600
        elif 'second' in detail_str.lower():
            retry_after = 1

    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "rate_limit_exceeded",
            "message": "Trop de requetes. Veuillez patienter avant de reessayer.",
            "message_en": "Too many requests. Please wait before retrying.",
            "detail": str(exc.detail) if hasattr(exc, 'detail') else None,
            "retry_after_seconds": retry_after
        },
        headers={
            "Retry-After": str(retry_after),
            "X-RateLimit-Reset": str(retry_after)
        }
    )


def get_user_rate_limit_key(request: Request) -> str:
    """
    Get rate limit key based on authenticated user or IP address.

    For authenticated requests, uses user ID for more accurate per-user limiting.
    For anonymous requests, falls back to IP address.
    This ensures that authenticated users get their own rate limit bucket,
    preventing IP-based limits from affecting legitimate users behind NAT.

    Args:
        request: FastAPI request object

    Returns:
        Unique identifier string for rate limiting (e.g., "user:abc123" or "ip:192.168.1.1")
    """
    # Try to get user from JWT token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            # Import here to avoid circular imports
            from auth import decode_token
            token = auth_header.split(" ")[1]
            payload = decode_token(token)
            user_id = payload.get("sub")
            if user_id:
                return f"user:{user_id}"
        except Exception as e:
            # Token invalid or expired - fall back to IP
            logger.debug(f"Could not extract user from token for rate limiting: {e}")

    # Fall back to IP address
    ip = get_remote_address(request)
    return f"ip:{ip}"


def rate_limit(limit: str) -> Callable:
    """
    Decorator for applying rate limits to endpoints.

    Usage:
        @router.get("/example")
        @rate_limit(RateLimits.PROJECT_LIST)
        async def example_endpoint(request: Request):
            return {"message": "success"}

    Note: The endpoint must accept a 'request: Request' parameter for rate limiting to work.

    Args:
        limit: Rate limit string (e.g., "5/minute", "100/hour")

    Returns:
        Decorated function with rate limiting applied
    """
    def decorator(func: Callable) -> Callable:
        return limiter.limit(limit)(func)
    return decorator


def get_endpoint_limit(endpoint_type: str) -> str:
    """
    Get the appropriate rate limit for an endpoint type.

    Args:
        endpoint_type: Type of endpoint (auth, generate, project, billing, admin)

    Returns:
        Rate limit string
    """
    limits_map = {
        'auth': RateLimits.AUTH_LOGIN,
        'auth_login': RateLimits.AUTH_LOGIN,
        'auth_register': RateLimits.AUTH_REGISTER,
        'generate': RateLimits.GENERATE_STANDARD,
        'generate_simple': RateLimits.GENERATE_SIMPLE,
        'generate_complex': RateLimits.GENERATE_COMPLEX,
        'project': RateLimits.PROJECT_LIST,
        'project_create': RateLimits.PROJECT_CREATE,
        'billing': RateLimits.BILLING_CHECKOUT,
        'admin': RateLimits.ADMIN_STATS,
        'default': RateLimits.DEFAULT,
    }
    return limits_map.get(endpoint_type.lower(), RateLimits.DEFAULT)


# Export for convenience
__all__ = [
    'limiter',
    'RateLimits',
    'rate_limit_exceeded_handler',
    'get_user_rate_limit_key',
    'rate_limit',
    'get_endpoint_limit',
]
