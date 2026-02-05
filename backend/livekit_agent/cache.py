"""
Redis Cache for LiveKit Agent

Handles phone number to clinic mapping and call state persistence.
"""

import json
import logging
import time

import redis.asyncio as redis
from sqlalchemy import select

from livekit_agent.config import agent_settings
from livekit_agent.db import SessionLocal

logger = logging.getLogger(__name__)

# Redis client
redis_client: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    """Get or create Redis client."""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(
            agent_settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return redis_client


async def warm_phone_mapping() -> None:
    """
    Warm the phone-to-clinic mapping cache on startup.

    This enables O(1) lookup for incoming phone calls instead of
    hitting the database for every call.
    """
    logger.info("Warming phone-to-clinic mapping cache...")

    # Import here to avoid circular imports
    from app.models.clinic import Clinic

    try:
        r = await get_redis()
        async with SessionLocal() as db:
            result = await db.execute(
                select(Clinic.id, Clinic.twilio_phone_number).where(
                    Clinic.voice_enabled.is_(True),
                    Clinic.twilio_phone_number.isnot(None),
                    Clinic.deleted_at.is_(None),
                )
            )
            mappings = result.all()

            for clinic_id, phone in mappings:
                await r.hset("phone_to_clinic", phone, str(clinic_id))  # type: ignore[misc]

            logger.info(f"Cached {len(mappings)} phone-to-clinic mappings")
    except Exception as e:
        logger.error(f"Failed to warm phone mapping: {e}")
        raise


async def get_clinic_for_phone(phone: str) -> str | None:
    """
    Look up clinic ID for a phone number.

    Args:
        phone: Phone number in E.164 format

    Returns:
        Clinic ID if found, None otherwise
    """
    r = await get_redis()
    clinic_id = await r.hget("phone_to_clinic", phone)  # type: ignore[misc]
    return clinic_id


async def save_call_state(room_name: str, state: dict) -> None:
    """
    Persist call state to Redis for recovery.

    Args:
        room_name: LiveKit room name
        state: Call state dictionary
    """
    r = await get_redis()
    await r.hset(  # type: ignore[misc]
        f"call:{room_name}:state",
        mapping={
            "data": json.dumps(state),
            "last_activity": str(time.time()),
        },
    )
    # Expire after 1 hour
    await r.expire(f"call:{room_name}:state", 3600)


async def get_call_state(room_name: str) -> dict | None:
    """
    Retrieve call state from Redis.

    Args:
        room_name: LiveKit room name

    Returns:
        Call state dictionary if found, None otherwise
    """
    r = await get_redis()
    data = await r.hget(f"call:{room_name}:state", "data")  # type: ignore[misc]
    if data:
        return json.loads(data)
    return None


async def clear_call_state(room_name: str) -> None:
    """Clear call state from Redis after call ends."""
    r = await get_redis()
    await r.delete(f"call:{room_name}:state")


async def health_check_redis() -> bool:
    """Check Redis connectivity for health checks."""
    try:
        r = await get_redis()
        await r.ping()
        return True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return False
