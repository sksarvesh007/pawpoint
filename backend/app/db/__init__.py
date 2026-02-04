"""
Database Configuration

Provides async database engine, session factory, and dependency injection.
"""

import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.instrumentation import db_queries_total, db_query_duration_seconds

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


# =============================================================================
# Database Query Instrumentation
# =============================================================================
def _get_operation_from_statement(statement: str) -> str:
    """Extract operation type from SQL statement."""
    statement = statement.strip().upper()
    if statement.startswith("SELECT"):
        return "select"
    elif statement.startswith("INSERT"):
        return "insert"
    elif statement.startswith("UPDATE"):
        return "update"
    elif statement.startswith("DELETE"):
        return "delete"
    return "other"


def _get_table_from_statement(statement: str) -> str:
    """Extract table name from SQL statement (best effort)."""
    statement = statement.strip().upper()
    words = statement.split()
    try:
        if statement.startswith("SELECT"):
            # SELECT ... FROM table_name
            if "FROM" in words:
                idx = words.index("FROM")
                if idx + 1 < len(words):
                    return words[idx + 1].lower().strip("\"'`")
        elif statement.startswith("INSERT"):
            # INSERT INTO table_name
            if "INTO" in words:
                idx = words.index("INTO")
                if idx + 1 < len(words):
                    return words[idx + 1].lower().strip("\"'`")
        elif statement.startswith("UPDATE"):
            # UPDATE table_name
            if len(words) > 1:
                return words[1].lower().strip("\"'`")
        elif statement.startswith("DELETE"):
            # DELETE FROM table_name
            if "FROM" in words:
                idx = words.index("FROM")
                if idx + 1 < len(words):
                    return words[idx + 1].lower().strip("\"'`")
    except (IndexError, ValueError):
        pass
    return "unknown"


@event.listens_for(engine.sync_engine, "before_cursor_execute")
def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Record query start time."""
    conn.info["query_start_time"] = time.perf_counter()


@event.listens_for(engine.sync_engine, "after_cursor_execute")
def _after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Record query metrics after execution."""
    start_time = conn.info.pop("query_start_time", None)
    if start_time is None:
        return

    duration = time.perf_counter() - start_time
    operation = _get_operation_from_statement(statement)
    table = _get_table_from_statement(statement)

    attributes = {"operation": operation, "table": table}
    db_queries_total.add(1, attributes)
    db_query_duration_seconds.record(duration, attributes)


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
