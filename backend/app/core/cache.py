"""Redis caching utilities."""

import functools
import json
from typing import Any

from loguru import logger

from app.core.redis import get_redis_client


async def cache_get(key: str) -> Any | None:
    """Get a value from the cache."""
    redis = get_redis_client()
    if redis is None:
        return None
    try:
        value = await redis.get(key)
        if value is not None:
            return json.loads(value)
    except Exception as e:
        logger.warning("Cache get failed for key {}: {}", key, e)
    return None


async def cache_set(key: str, value: Any, ttl_seconds: int = 300) -> None:
    """Set a value in the cache with a TTL."""
    redis = get_redis_client()
    if redis is None:
        return
    try:
        await redis.set(key, json.dumps(value, default=str), ex=ttl_seconds)
    except Exception as e:
        logger.warning("Cache set failed for key {}: {}", key, e)


async def cache_delete(key: str) -> None:
    """Delete a value from the cache."""
    redis = get_redis_client()
    if redis is None:
        return
    try:
        await redis.delete(key)
    except Exception as e:
        logger.warning("Cache delete failed for key {}: {}", key, e)


def cached(prefix: str, ttl_seconds: int = 300):
    """Decorator to cache async function results.

    Args:
        prefix: Cache key prefix (e.g., "analytics:dashboard").
        ttl_seconds: Time-to-live in seconds (default 5 minutes).
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key from prefix + relevant args (skip self/db)
            key_parts = [prefix]
            for arg in args[1:]:  # Skip self
                if hasattr(arg, "hex") or isinstance(
                    arg, (str, int, float, bool)
                ):  # UUID
                    key_parts.append(str(arg))
            for k, v in sorted(kwargs.items()):
                if k != "db":
                    key_parts.append(f"{k}={v}")
            cache_key = ":".join(key_parts)

            # Try cache first
            result = await cache_get(cache_key)
            if result is not None:
                return result

            # Call the function
            result = await func(*args, **kwargs)

            # Cache the result
            if result is not None:
                # Convert Pydantic models to dict for serialization
                cache_value = result
                if hasattr(result, "model_dump"):
                    cache_value = result.model_dump()
                await cache_set(cache_key, cache_value, ttl_seconds)

            return result

        return wrapper

    return decorator
