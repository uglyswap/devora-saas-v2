"""
Redis Caching Middleware
Improves API performance by caching expensive operations
"""
from typing import Optional, Callable, Any
from functools import wraps
import hashlib
import json
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

# Redis client (to be initialized in main app)
redis_client: Optional[Any] = None


class CacheConfig:
    """Cache TTL configurations for different data types"""

    # User data (short TTL due to frequent updates)
    USER_PROFILE = timedelta(minutes=5)
    USER_SETTINGS = timedelta(minutes=10)

    # Project data (medium TTL)
    PROJECT_LIST = timedelta(minutes=15)
    PROJECT_DETAIL = timedelta(minutes=10)

    # Billing data (short TTL due to sync with Stripe)
    SUBSCRIPTION_STATUS = timedelta(minutes=3)
    INVOICES = timedelta(minutes=30)

    # Static/semi-static data (longer TTL)
    SUBSCRIPTION_PLANS = timedelta(hours=1)
    OPENROUTER_MODELS = timedelta(hours=6)

    # Admin stats (can be slightly stale)
    ADMIN_STATS = timedelta(minutes=5)


def init_redis_cache(redis_url: str = "redis://localhost:6379/0"):
    """
    Initialize Redis connection for caching

    Args:
        redis_url: Redis connection URL

    Note: In production, use a dedicated Redis instance
    """
    global redis_client
    try:
        import redis.asyncio as redis
        redis_client = redis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        logger.info(f"Redis cache initialized: {redis_url}")
    except ImportError:
        logger.warning("redis package not installed. Caching disabled.")
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {e}")


async def get_cached(key: str) -> Optional[str]:
    """
    Get value from cache

    Args:
        key: Cache key

    Returns:
        Cached value or None if not found/expired
    """
    if not redis_client:
        return None

    try:
        value = await redis_client.get(key)
        if value:
            logger.debug(f"Cache HIT: {key}")
            return value
        logger.debug(f"Cache MISS: {key}")
        return None
    except Exception as e:
        logger.error(f"Cache get error: {e}")
        return None


async def set_cached(key: str, value: str, ttl: timedelta):
    """
    Set value in cache with TTL

    Args:
        key: Cache key
        value: Value to cache (must be JSON-serializable)
        ttl: Time-to-live for cached value
    """
    if not redis_client:
        return

    try:
        await redis_client.setex(
            key,
            int(ttl.total_seconds()),
            value
        )
        logger.debug(f"Cache SET: {key} (TTL: {ttl})")
    except Exception as e:
        logger.error(f"Cache set error: {e}")


async def invalidate_cache(pattern: str):
    """
    Invalidate cache entries matching pattern

    Args:
        pattern: Redis key pattern (e.g., "user:123:*")
    """
    if not redis_client:
        return

    try:
        keys = await redis_client.keys(pattern)
        if keys:
            await redis_client.delete(*keys)
            logger.info(f"Invalidated {len(keys)} cache keys matching: {pattern}")
    except Exception as e:
        logger.error(f"Cache invalidation error: {e}")


def generate_cache_key(*args, **kwargs) -> str:
    """
    Generate deterministic cache key from arguments

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        MD5 hash of serialized arguments
    """
    # Sort kwargs for deterministic ordering
    sorted_kwargs = sorted(kwargs.items())

    # Serialize arguments
    key_data = json.dumps({"args": args, "kwargs": sorted_kwargs}, sort_keys=True)

    # Generate hash
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(ttl: timedelta, key_prefix: str = ""):
    """
    Decorator for caching function results

    Usage:
        @cached(ttl=CacheConfig.PROJECT_LIST, key_prefix="projects")
        async def get_projects(user_id: str):
            # Expensive database query
            return projects

    Args:
        ttl: Cache time-to-live
        key_prefix: Prefix for cache key (e.g., "projects")

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            arg_hash = generate_cache_key(*args, **kwargs)
            cache_key = f"{key_prefix}:{func.__name__}:{arg_hash}"

            # Try to get from cache
            cached_value = await get_cached(cache_key)
            if cached_value:
                try:
                    return json.loads(cached_value)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON in cache for key: {cache_key}")

            # Execute function
            result = await func(*args, **kwargs)

            # Cache the result
            try:
                await set_cached(cache_key, json.dumps(result), ttl)
            except (TypeError, ValueError) as e:
                logger.warning(f"Could not cache result for {func.__name__}: {e}")

            return result

        return wrapper
    return decorator


# Utility functions for common cache invalidation patterns
async def invalidate_user_cache(user_id: str):
    """Invalidate all cache entries for a specific user"""
    await invalidate_cache(f"user:{user_id}:*")


async def invalidate_project_cache(project_id: str):
    """Invalidate all cache entries for a specific project"""
    await invalidate_cache(f"project:{project_id}:*")
