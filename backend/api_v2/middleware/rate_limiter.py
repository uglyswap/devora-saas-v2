"""
Rate Limiting Middleware using slowapi
Prevents API abuse and ensures fair usage
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from typing import Callable
import logging

logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],  # Global default
    storage_uri="memory://",  # Use Redis in production: "redis://localhost:6379"
    strategy="fixed-window"
)


# Rate limit configurations by endpoint type
class RateLimits:
    """Predefined rate limits for different operations"""

    # Authentication endpoints (stricter limits)
    AUTH_LOGIN = "5/minute"
    AUTH_REGISTER = "3/minute"
    AUTH_PASSWORD_RESET = "3/hour"

    # Generation endpoints (based on computational cost)
    GENERATE_SIMPLE = "20/minute"
    GENERATE_AGENTIC = "10/minute"
    GENERATE_FULLSTACK = "5/minute"

    # Project operations
    PROJECT_CREATE = "30/minute"
    PROJECT_UPDATE = "60/minute"
    PROJECT_LIST = "100/minute"

    # Billing operations
    BILLING_CHECKOUT = "5/minute"
    BILLING_WEBHOOK = "1000/minute"  # Webhooks need higher limits

    # Admin operations
    ADMIN_STATS = "20/minute"
    ADMIN_CONFIG = "10/minute"


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Custom handler for rate limit exceeded errors

    Args:
        request: FastAPI request object
        exc: RateLimitExceeded exception

    Returns:
        JSON response with rate limit information
    """
    logger.warning(f"Rate limit exceeded for {request.client.host} on {request.url.path}")

    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "rate_limit_exceeded",
            "message": "Trop de requêtes. Veuillez patienter avant de réessayer.",
            "detail": str(exc),
            "retry_after": exc.detail if hasattr(exc, 'detail') else None
        },
        headers={"Retry-After": "60"}  # Suggest retry after 60 seconds
    )


def get_user_rate_limit_key(request: Request) -> str:
    """
    Get rate limit key based on authenticated user or IP

    For authenticated requests, use user ID for more accurate limiting.
    For anonymous requests, fall back to IP address.

    Args:
        request: FastAPI request object

    Returns:
        Unique identifier for rate limiting
    """
    # Try to get user from JWT token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            # Extract user ID from token (simplified - use proper JWT decode in production)
            from auth import decode_token
            token = auth_header.split(" ")[1]
            payload = decode_token(token)
            user_id = payload.get("sub")
            if user_id:
                return f"user:{user_id}"
        except Exception as e:
            logger.debug(f"Could not extract user from token: {e}")

    # Fall back to IP address
    return f"ip:{get_remote_address(request)}"


# Example usage decorators
def rate_limit(limit: str):
    """
    Decorator for applying rate limits to endpoints

    Usage:
        @router.get("/example")
        @rate_limit(RateLimits.PROJECT_LIST)
        async def example_endpoint():
            return {"message": "success"}
    """
    def decorator(func: Callable) -> Callable:
        return limiter.limit(limit)(func)
    return decorator
