"""
Redis Cache Implementation

A production-ready Redis caching system with:
- Async operations using redis.asyncio
- Connection pooling
- TTL management
- Pattern-based invalidation
- Decorator for automatic function caching
- Metrics and health checks
"""

import redis.asyncio as redis
import json
import hashlib
import logging
import time
from typing import Any, Optional, Callable, TypeVar, Union
from functools import wraps
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

# Type variable for generic cached function return types
T = TypeVar("T")

# Global cache instance (singleton pattern)
_cache_instance: Optional["RedisCache"] = None


class RedisCache:
    """
    Production-ready Redis cache with async support.

    Features:
    - Connection pooling for performance
    - Automatic serialization/deserialization
    - TTL-based expiration
    - Pattern-based cache invalidation
    - Metrics tracking
    - Health check support

    Example:
        cache = RedisCache("redis://localhost:6379")
        await cache.set("user:123", {"name": "John"}, ttl=3600)
        user = await cache.get("user:123")
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        default_ttl: int = 3600,
        key_prefix: str = "devora",
        max_connections: int = 10,
    ):
        """
        Initialize Redis cache.

        Args:
            redis_url: Redis connection URL
            default_ttl: Default TTL in seconds (default: 1 hour)
            key_prefix: Prefix for all cache keys
            max_connections: Maximum number of Redis connections
        """
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.key_prefix = key_prefix
        self.max_connections = max_connections

        # Connection pool (lazy initialization)
        self._pool: Optional[redis.ConnectionPool] = None
        self._redis: Optional[redis.Redis] = None

        # Metrics
        self._metrics = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0,
        }

    async def _get_client(self) -> redis.Redis:
        """Get or create Redis client with connection pooling."""
        if self._redis is None:
            try:
                self._pool = redis.ConnectionPool.from_url(
                    self.redis_url,
                    max_connections=self.max_connections,
                    decode_responses=True,
                )
                self._redis = redis.Redis(connection_pool=self._pool)
                logger.info(f"[RedisCache] Connected to Redis at {self.redis_url}")
            except Exception as e:
                logger.error(f"[RedisCache] Connection failed: {e}")
                self._metrics["errors"] += 1
                raise
        return self._redis

    def _make_key(self, key: str) -> str:
        """Create a namespaced cache key."""
        return f"{self.key_prefix}:{key}"

    def _serialize(self, value: Any) -> str:
        """Serialize value to JSON string."""
        return json.dumps(value, default=str, ensure_ascii=False)

    def _deserialize(self, value: Optional[str]) -> Optional[Any]:
        """Deserialize JSON string to Python object."""
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.

        Args:
            key: Cache key (will be prefixed automatically)

        Returns:
            Cached value or None if not found
        """
        try:
            client = await self._get_client()
            full_key = self._make_key(key)
            value = await client.get(full_key)

            if value is not None:
                self._metrics["hits"] += 1
                logger.debug(f"[RedisCache] HIT: {key}")
                return self._deserialize(value)
            else:
                self._metrics["misses"] += 1
                logger.debug(f"[RedisCache] MISS: {key}")
                return None

        except Exception as e:
            logger.error(f"[RedisCache] GET error for {key}: {e}")
            self._metrics["errors"] += 1
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Set a value in cache.

        Args:
            key: Cache key (will be prefixed automatically)
            value: Value to cache (must be JSON serializable)
            ttl: Time-to-live in seconds (uses default if None)

        Returns:
            True if successful, False otherwise
        """
        try:
            client = await self._get_client()
            full_key = self._make_key(key)
            ttl_seconds = ttl if ttl is not None else self.default_ttl

            await client.setex(
                full_key,
                ttl_seconds,
                self._serialize(value),
            )

            self._metrics["sets"] += 1
            logger.debug(f"[RedisCache] SET: {key} (TTL: {ttl_seconds}s)")
            return True

        except Exception as e:
            logger.error(f"[RedisCache] SET error for {key}: {e}")
            self._metrics["errors"] += 1
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete a value from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if deleted, False otherwise
        """
        try:
            client = await self._get_client()
            full_key = self._make_key(key)
            result = await client.delete(full_key)

            self._metrics["deletes"] += 1
            logger.debug(f"[RedisCache] DELETE: {key}")
            return result > 0

        except Exception as e:
            logger.error(f"[RedisCache] DELETE error for {key}: {e}")
            self._metrics["errors"] += 1
            return False

    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        try:
            client = await self._get_client()
            full_key = self._make_key(key)
            return await client.exists(full_key) > 0
        except Exception as e:
            logger.error(f"[RedisCache] EXISTS error for {key}: {e}")
            self._metrics["errors"] += 1
            return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching a pattern.

        Args:
            pattern: Glob pattern to match (e.g., "user:*", "project:123:*")

        Returns:
            Number of keys deleted
        """
        try:
            client = await self._get_client()
            full_pattern = self._make_key(pattern)

            # Use SCAN for production-safe key iteration
            deleted_count = 0
            cursor = 0

            while True:
                cursor, keys = await client.scan(
                    cursor=cursor,
                    match=full_pattern,
                    count=100,
                )

                if keys:
                    await client.delete(*keys)
                    deleted_count += len(keys)

                if cursor == 0:
                    break

            logger.info(f"[RedisCache] Invalidated {deleted_count} keys matching: {pattern}")
            return deleted_count

        except Exception as e:
            logger.error(f"[RedisCache] INVALIDATE_PATTERN error for {pattern}: {e}")
            self._metrics["errors"] += 1
            return 0

    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl: Optional[int] = None,
    ) -> Any:
        """
        Get value from cache or compute and store it.

        Args:
            key: Cache key
            factory: Function to compute value if not cached
            ttl: Time-to-live in seconds

        Returns:
            Cached or computed value
        """
        value = await self.get(key)

        if value is not None:
            return value

        # Compute value
        if callable(factory):
            # Handle async factories
            import asyncio
            if asyncio.iscoroutinefunction(factory):
                value = await factory()
            else:
                value = factory()
        else:
            value = factory

        # Cache the result
        await self.set(key, value, ttl)
        return value

    async def increment(self, key: str, amount: int = 1) -> int:
        """Atomically increment a counter."""
        try:
            client = await self._get_client()
            full_key = self._make_key(key)
            return await client.incrby(full_key, amount)
        except Exception as e:
            logger.error(f"[RedisCache] INCREMENT error for {key}: {e}")
            self._metrics["errors"] += 1
            return 0

    async def get_ttl(self, key: str) -> int:
        """Get remaining TTL for a key in seconds (-1 if no TTL, -2 if not exists)."""
        try:
            client = await self._get_client()
            full_key = self._make_key(key)
            return await client.ttl(full_key)
        except Exception as e:
            logger.error(f"[RedisCache] TTL error for {key}: {e}")
            return -2

    async def health_check(self) -> dict:
        """
        Check Redis connection health.

        Returns:
            Health status dict with connection info
        """
        try:
            client = await self._get_client()
            start = time.time()
            await client.ping()
            latency_ms = (time.time() - start) * 1000

            info = await client.info("server")

            return {
                "status": "healthy",
                "latency_ms": round(latency_ms, 2),
                "redis_version": info.get("redis_version", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    def get_metrics(self) -> dict:
        """Get cache performance metrics."""
        total = self._metrics["hits"] + self._metrics["misses"]
        hit_rate = self._metrics["hits"] / total if total > 0 else 0.0

        return {
            **self._metrics,
            "total_requests": total,
            "hit_rate": round(hit_rate, 4),
        }

    def reset_metrics(self) -> None:
        """Reset all metrics counters."""
        self._metrics = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0,
        }

    async def close(self) -> None:
        """Close Redis connections."""
        if self._redis:
            await self._redis.close()
            self._redis = None
        if self._pool:
            await self._pool.disconnect()
            self._pool = None
        logger.info("[RedisCache] Connection closed")

    @asynccontextmanager
    async def pipeline(self):
        """
        Context manager for Redis pipeline (batch operations).

        Example:
            async with cache.pipeline() as pipe:
                await pipe.set("key1", "value1")
                await pipe.set("key2", "value2")
                await pipe.execute()
        """
        client = await self._get_client()
        pipe = client.pipeline()
        try:
            yield pipe
            await pipe.execute()
        finally:
            pass


def get_cache(
    redis_url: str = "redis://localhost:6379",
    **kwargs,
) -> RedisCache:
    """
    Get or create the global cache instance (singleton).

    Args:
        redis_url: Redis connection URL
        **kwargs: Additional RedisCache arguments

    Returns:
        RedisCache instance
    """
    global _cache_instance

    if _cache_instance is None:
        _cache_instance = RedisCache(redis_url, **kwargs)

    return _cache_instance


def cached(
    ttl: int = 3600,
    key_prefix: str = "",
    key_builder: Optional[Callable[..., str]] = None,
    cache_none: bool = False,
):
    """
    Decorator to cache async function results.

    Args:
        ttl: Cache TTL in seconds (default: 1 hour)
        key_prefix: Prefix for cache keys (default: function name)
        key_builder: Custom function to build cache key from args/kwargs
        cache_none: Whether to cache None results (default: False)

    Example:
        @cached(ttl=300, key_prefix="user")
        async def get_user(user_id: str) -> dict:
            return await db.fetch_user(user_id)

        # Custom key builder
        @cached(ttl=3600, key_builder=lambda project_id, **kw: f"project:{project_id}")
        async def get_project(project_id: str, include_details: bool = False):
            ...

    Note:
        Requires a global cache instance to be initialized via get_cache()
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            # Get cache instance
            cache = get_cache()

            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # Default key: prefix:func_name:hash(args)
                prefix = key_prefix or func.__name__
                key_data = {
                    "args": [str(a) for a in args],
                    "kwargs": {k: str(v) for k, v in sorted(kwargs.items())},
                }
                key_hash = hashlib.md5(
                    json.dumps(key_data, sort_keys=True).encode()
                ).hexdigest()[:12]
                cache_key = f"{prefix}:{key_hash}"

            # Try to get from cache
            cached_value = await cache.get(cache_key)

            if cached_value is not None:
                return cached_value

            # Call the function
            result = await func(*args, **kwargs)

            # Cache the result (optionally skip None)
            if result is not None or cache_none:
                await cache.set(cache_key, result, ttl)

            return result

        # Attach cache invalidation helper
        wrapper.invalidate = lambda *a, **kw: get_cache().delete(
            key_builder(*a, **kw) if key_builder else f"{key_prefix or func.__name__}:*"
        )

        return wrapper

    return decorator
