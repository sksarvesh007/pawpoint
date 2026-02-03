"""
Database Configuration

Provides async database engine, session factory, and dependency injection.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

settings = get_settings()

# Validate database URL is configured
if not settings.database_url:
    raise ValueError("DATABASE_URL must be set in environment")

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=False,  # Disable SQL query logging (use DATABASE_ECHO=true in .env to enable)
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession]:
    """
    Dependency injection for database sessions.

    Usage in FastAPI:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """
    Context manager for database sessions (use in non-FastAPI contexts).

    Usage:
        async with get_db_session() as session:
            result = await session.execute(...)
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database connection and create tables.

    Call this during application startup.

    Raises:
        ConnectionError: If unable to connect to the database
    """
    # Import all models to register them with Base.metadata
    from app.models import (
        Appointment,
        CallLog,
        Clinic,
        Patient,
        PIMSSyncLog,
        Provider,
        User,
    )
    from app.models.base import Base

    # In development, you might want to create tables automatically
    # In production, use Alembic migrations
    if settings.debug:
        try:
            async with engine.begin() as conn:
                # WARNING: Only for development - drops and recreates all tables
                # await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)
        except ConnectionRefusedError as e:
            db_host = (
                settings.database_url.split("@")[-1]
                if settings.database_url
                else "unknown"
            )
            raise ConnectionError(
                f"Failed to connect to PostgreSQL database at {db_host}. "
                "Is the database running? Try: docker compose up db"
            ) from e
        except Exception as e:
            raise ConnectionError(
                f"Database initialization failed: {e.__class__.__name__}: {e}"
            ) from e


async def close_db() -> None:
    """
    Close database connections.

    Call this during application shutdown.
    """
    await engine.dispose()
