"""Tests for clinic-scoped AI chat endpoint (/{clinic_slug}/chat)."""

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import get_redis
from app.main import app
from tests.helpers import create_test_clinic, setup_auth

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_agent_result(text: str = "Hello! I can help with that.") -> MagicMock:
    """Build a fake pydantic-ai RunResult."""
    result = MagicMock()
    result.output = text
    result.model = "deepseek-chat"
    result.usage = None
    return result


def _chat_payload(message: str = "What are your hours?") -> dict:
    return {
        "message": message,
        "user_identifier": "test-user@example.com",
    }


def _make_mock_redis() -> AsyncMock:
    """Build a Redis mock that satisfies SessionManager operations."""
    mock_redis = AsyncMock()
    mock_redis.setex = AsyncMock(return_value=True)
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.delete = AsyncMock(return_value=True)
    return mock_redis


def _redis_override(mock_redis: AsyncMock):
    """Return a FastAPI dependency override that yields mock_redis."""

    async def _override() -> AsyncGenerator:
        yield mock_redis

    return _override


# ---------------------------------------------------------------------------
# Clinic existence (slug lookup)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_clinic_chat_requires_auth(client: AsyncClient) -> None:
    """POST to a non-existent clinic slug returns 404.

    The endpoint has no JWT authentication; instead, the clinic must exist in
    the database. A missing slug should return 404.
    """
    response = await client.post(
        "/api/v1/does-not-exist/chat",
        json=_chat_payload(),
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Valid request with mocked agent
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_clinic_chat_returns_response(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """A valid chat request to a known clinic with mocked LLM returns 200."""
    clinic = await setup_auth(db_session, client)
    mock_result = _mock_agent_result("We are open Monday to Friday, 9am to 5pm.")
    mock_redis = _make_mock_redis()
    app.dependency_overrides[get_redis] = _redis_override(mock_redis)

    try:
        with patch(
            "app.ai.agents.base.BaseAgent.run",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            response = await client.post(
                f"/api/v1/{clinic.slug}/chat",
                json=_chat_payload(),
            )
    finally:
        app.dependency_overrides.pop(get_redis, None)

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "conversation_id" in data
    assert data["agent_name"] == "clinic_assistant"
    assert data["clinic_name"] == clinic.name


# ---------------------------------------------------------------------------
# Wrong / inactive clinic slug
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_clinic_chat_wrong_clinic_rejected(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """A slug that doesn't exist returns 404."""
    await setup_auth(db_session, client)

    response = await client.post(
        "/api/v1/totally-wrong-clinic-slug/chat",
        json=_chat_payload(),
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_clinic_chat_inactive_clinic_rejected(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """A deactivated clinic slug returns 404."""
    clinic = await create_test_clinic(db_session)
    clinic.is_active = False
    await db_session.flush()

    response = await client.post(
        f"/api/v1/{clinic.slug}/chat",
        json=_chat_payload(),
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_clinic_chat_empty_message_rejected(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """An empty message is rejected with 422."""
    clinic = await setup_auth(db_session, client)
    mock_redis = _make_mock_redis()
    app.dependency_overrides[get_redis] = _redis_override(mock_redis)

    try:
        response = await client.post(
            f"/api/v1/{clinic.slug}/chat",
            json={"message": "", "user_identifier": "user@example.com"},
        )
    finally:
        app.dependency_overrides.pop(get_redis, None)

    assert response.status_code == 422
