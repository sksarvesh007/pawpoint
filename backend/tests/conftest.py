"""Test configuration and fixtures for backend tests."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.api.v1.endpoints import auth as auth_module
from app.core.config import get_settings
from app.db import get_db
from app.main import app
from app.models.base import Base

settings = get_settings()


# =============================================================================
# Rate Limiter Context Manager
# =============================================================================


@asynccontextmanager
async def disable_rate_limiting() -> AsyncGenerator[None]:
    """
    Context manager to disable rate limiting during tests.

    Uses try/finally to ensure rate limiting is re-enabled even if tests fail.
    """
    # Store original states
    app_limiter_enabled: bool | None = None
    auth_limiter_enabled: bool | None = None

    try:
        # Disable app state limiter
        if hasattr(app.state, "limiter") and app.state.limiter:
            app_limiter_enabled = getattr(app.state.limiter, "enabled", True)
            app.state.limiter.enabled = False

        # Disable auth module limiter
        if hasattr(auth_module, "limiter"):
            auth_limiter_enabled = getattr(auth_module.limiter, "enabled", True)
            auth_module.limiter.enabled = False

        yield
    finally:
        # Restore original states
        if app_limiter_enabled is not None and hasattr(app.state, "limiter"):
            app.state.limiter.enabled = app_limiter_enabled
        if auth_limiter_enabled is not None and hasattr(auth_module, "limiter"):
            auth_module.limiter.enabled = auth_limiter_enabled


# =============================================================================
# Database Fixtures
# =============================================================================


@pytest_asyncio.fixture(scope="function")
async def test_engine() -> AsyncGenerator[AsyncEngine]:
    """
    Create a test-specific async engine for each test function.

    This avoids event loop issues caused by reusing the app's singleton engine,
    which gets bound to a different event loop at import time.
    """
    assert settings.database_url is not None, "DATABASE_URL must be set for tests"
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        pool_pre_ping=True,
    )

    # Create tables once at the start
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup: drop tables and dispose engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession]:
    """
    Creates a database session with transaction rollback for test isolation.

    Each test runs in a transaction that gets rolled back after completion,
    ensuring complete isolation between tests without expensive table drops.
    """
    # Create a connection and begin a transaction
    connection = await test_engine.connect()
    transaction = await connection.begin()

    # Create session bound to this connection
    async_session_factory = async_sessionmaker(
        bind=connection,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session_factory() as session:
        yield session

    # Rollback the transaction to restore clean state
    await transaction.rollback()
    await connection.close()


# =============================================================================
# Client Fixtures
# =============================================================================


@pytest_asyncio.fixture
async def client(
    db_session: AsyncSession, test_engine: AsyncEngine
) -> AsyncGenerator[AsyncClient]:
    """
    Creates an HTTP client for testing the API.

    - Overrides get_db dependency to use the test session
    - Disables rate limiting for the duration of the test
    - Properly cleans up after test completion
    """

    async def override_get_db() -> AsyncGenerator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with disable_rate_limiting():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            yield c

    app.dependency_overrides.clear()
