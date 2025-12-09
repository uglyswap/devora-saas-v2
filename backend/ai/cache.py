"""
Response Caching System for LLM Calls

Features:
- In-memory LRU cache
- Redis backend support (optional)
- TTL (Time-To-Live) for cache entries
- Cache hit/miss metrics
- Automatic cache key generation from prompts
"""

import hashlib
import json
import logging
import time
from typing import Dict, Any, Optional, Tuple
from collections import OrderedDict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ResponseCache:
    """LRU cache with TTL for LLM responses"""

    def __init__(
        self,
        max_size: int = 1000,
        default_ttl_seconds: int = 3600,  # 1 hour
        enable_metrics: bool = True,
    ):
        self.max_size = max_size
        self.default_ttl = default_ttl_seconds
        self.enable_metrics = enable_metrics

        # LRU cache: OrderedDict maintains insertion order
        self._cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()

        # Metrics
        self._metrics = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_requests": 0,
        }

    def _generate_key(
        self,
        messages: list,
        system_prompt: Optional[str] = None,
        model: str = "",
        **kwargs
    ) -> str:
        """Generate cache key from request parameters"""
        # Create a deterministic string representation
        key_data = {
            "messages": messages,
            "system_prompt": system_prompt,
            "model": model,
            "temperature": kwargs.get("temperature", 0.7),
        }

        # Sort dict keys for consistency
        key_str = json.dumps(key_data, sort_keys=True)

        # Generate SHA256 hash
        return hashlib.sha256(key_str.encode()).hexdigest()

    def _is_expired(self, timestamp: float, ttl: Optional[int] = None) -> bool:
        """Check if cache entry is expired"""
        ttl_seconds = ttl if ttl is not None else self.default_ttl
        return time.time() - timestamp > ttl_seconds

    def _evict_oldest(self):
        """Evict the least recently used item"""
        if self._cache:
            self._cache.popitem(last=False)  # Remove first (oldest) item
            self._metrics["evictions"] += 1

    def _evict_expired(self):
        """Evict all expired entries"""
        current_time = time.time()
        keys_to_remove = []

        for key, (_, timestamp) in self._cache.items():
            if self._is_expired(timestamp):
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self._cache[key]
            self._metrics["evictions"] += 1

    def get(
        self,
        messages: list,
        system_prompt: Optional[str] = None,
        model: str = "",
        **kwargs
    ) -> Optional[Any]:
        """
        Get cached response if available

        Args:
            messages: Chat messages
            system_prompt: System prompt
            model: Model name
            **kwargs: Additional parameters

        Returns:
            Cached response or None if not found/expired
        """
        self._metrics["total_requests"] += 1

        key = self._generate_key(messages, system_prompt, model, **kwargs)

        if key in self._cache:
            response, timestamp = self._cache[key]

            # Check if expired
            if self._is_expired(timestamp):
                del self._cache[key]
                self._metrics["misses"] += 1
                return None

            # Move to end (mark as recently used)
            self._cache.move_to_end(key)

            self._metrics["hits"] += 1
            logger.debug(f"[Cache] HIT for key {key[:8]}...")
            return response

        self._metrics["misses"] += 1
        logger.debug(f"[Cache] MISS for key {key[:8]}...")
        return None

    def set(
        self,
        response: Any,
        messages: list,
        system_prompt: Optional[str] = None,
        model: str = "",
        ttl: Optional[int] = None,
        **kwargs
    ):
        """
        Cache a response

        Args:
            response: Response to cache
            messages: Chat messages
            system_prompt: System prompt
            model: Model name
            ttl: Time-to-live in seconds (uses default if None)
            **kwargs: Additional parameters
        """
        key = self._generate_key(messages, system_prompt, model, **kwargs)

        # Evict expired entries periodically
        if len(self._cache) % 100 == 0:
            self._evict_expired()

        # Evict oldest if at capacity
        if len(self._cache) >= self.max_size:
            self._evict_oldest()

        # Store with current timestamp
        self._cache[key] = (response, time.time())
        logger.debug(f"[Cache] SET for key {key[:8]}...")

    def clear(self):
        """Clear all cache entries"""
        self._cache.clear()
        logger.info("[Cache] Cleared all entries")

    def get_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics"""
        total_requests = self._metrics["total_requests"]
        hit_rate = (
            self._metrics["hits"] / total_requests
            if total_requests > 0
            else 0.0
        )

        return {
            **self._metrics,
            "hit_rate": hit_rate,
            "cache_size": len(self._cache),
            "max_size": self.max_size,
        }

    def reset_metrics(self):
        """Reset metrics counters"""
        self._metrics = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_requests": 0,
        }


class RedisCache(ResponseCache):
    """Redis-backed cache for distributed systems (optional)"""

    def __init__(
        self,
        redis_url: str,
        max_size: int = 10000,
        default_ttl_seconds: int = 3600,
        enable_metrics: bool = True,
    ):
        super().__init__(max_size, default_ttl_seconds, enable_metrics)
        self.redis_url = redis_url
        self._redis = None

    async def _get_redis(self):
        """Lazy initialization of Redis client"""
        if self._redis is None:
            try:
                import redis.asyncio as redis
                self._redis = redis.from_url(self.redis_url, decode_responses=True)
                logger.info("[Cache] Connected to Redis")
            except ImportError:
                logger.error("[Cache] redis package not installed")
                raise
            except Exception as e:
                logger.error(f"[Cache] Failed to connect to Redis: {e}")
                raise
        return self._redis

    async def get(
        self,
        messages: list,
        system_prompt: Optional[str] = None,
        model: str = "",
        **kwargs
    ) -> Optional[Any]:
        """Get from Redis cache"""
        self._metrics["total_requests"] += 1

        try:
            redis = await self._get_redis()
            key = self._generate_key(messages, system_prompt, model, **kwargs)

            value = await redis.get(f"llm_cache:{key}")

            if value:
                self._metrics["hits"] += 1
                logger.debug(f"[Cache] Redis HIT for key {key[:8]}...")
                return json.loads(value)

            self._metrics["misses"] += 1
            logger.debug(f"[Cache] Redis MISS for key {key[:8]}...")
            return None

        except Exception as e:
            logger.error(f"[Cache] Redis get error: {e}")
            return None

    async def set(
        self,
        response: Any,
        messages: list,
        system_prompt: Optional[str] = None,
        model: str = "",
        ttl: Optional[int] = None,
        **kwargs
    ):
        """Set in Redis cache"""
        try:
            redis = await self._get_redis()
            key = self._generate_key(messages, system_prompt, model, **kwargs)
            ttl_seconds = ttl if ttl is not None else self.default_ttl

            await redis.setex(
                f"llm_cache:{key}",
                ttl_seconds,
                json.dumps(response)
            )

            logger.debug(f"[Cache] Redis SET for key {key[:8]}...")

        except Exception as e:
            logger.error(f"[Cache] Redis set error: {e}")

    async def clear(self):
        """Clear all cache entries"""
        try:
            redis = await self._get_redis()
            # Delete all keys matching pattern
            keys = await redis.keys("llm_cache:*")
            if keys:
                await redis.delete(*keys)
            logger.info(f"[Cache] Cleared {len(keys)} Redis entries")
        except Exception as e:
            logger.error(f"[Cache] Redis clear error: {e}")

    async def close(self):
        """Close Redis connection"""
        if self._redis:
            await self._redis.close()
