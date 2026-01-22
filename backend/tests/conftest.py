
import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.db import get_db
from app.main import app
from app.models.base import Base
from app.api.v1.endpoints import auth as auth_module

settings = get_settings()

# =============================================================================
# Database Fixtures
# =============================================================================


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """
    Create a test-specific async engine for each test function.
    
    This avoids event loop issues caused by reusing the app's singleton engine,
    which gets bound to a different event loop at import time.
    """
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        pool_pre_ping=True,
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup: drop tables and dispose engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession]:
    """
    Creates a fresh database session for a test.
    Uses a transaction that gets rolled back after test completes for isolation.
    """
    async_session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    async with async_session_factory() as session:
        yield session


# =============================================================================
# Client Fixtures
# =============================================================================

@pytest_asyncio.fixture
async def client(db_session: AsyncSession, test_engine) -> AsyncGenerator[AsyncClient]:
    """
    Creates an HTTP client for testing the API.
    Overrides the get_db dependency to use the test session.
    """
    
    async def override_get_db() -> AsyncGenerator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    
    # Disable rate limiting for tests by setting enabled=False on all limiter instances
    # The auth module has its own limiter that needs to be disabled separately
    if hasattr(app.state, "limiter") and app.state.limiter:
        app.state.limiter.enabled = False
    if hasattr(auth_module, "limiter"):
        auth_module.limiter.enabled = False
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    
    # Re-enable rate limiting after test
    if hasattr(app.state, "limiter") and app.state.limiter:
        app.state.limiter.enabled = True
    if hasattr(auth_module, "limiter"):
        auth_module.limiter.enabled = True
    
    app.dependency_overrides.clear()

