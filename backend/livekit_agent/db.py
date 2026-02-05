"""
Dedicated Database Connection Pool for LiveKit Agent Workers

Creates a separate connection pool from FastAPI to prevent exhausting
the main application's database connections at scale.
"""

import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from livekit_agent.config import agent_settings

logger = logging.getLogger(__name__)

# Create dedicated async engine for agent workers
engine = create_async_engine(
    agent_settings.database_url,
    pool_size=agent_settings.db_pool_size,
    max_overflow=agent_settings.db_max_overflow,
    pool_pre_ping=agent_settings.db_pool_pre_ping,
    pool_recycle=agent_settings.db_pool_recycle,
    echo=False,
)

# Session factory
SessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def warm_connection_pool() -> None:
    """
    Warm the connection pool on agent startup.

    Pre-creates connections to avoid latency on first calls.
    """
    logger.info("Warming database connection pool...")
    try:
        async with SessionLocal() as db:
            await db.execute(text("SELECT 1"))
        logger.info("Database connection pool warmed successfully")
    except Exception as e:
        logger.error(f"Failed to warm connection pool: {e}")
        raise


async def health_check_db() -> bool:
    """Check database connectivity for health checks."""
    try:
        async with SessionLocal() as db:
            await db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
