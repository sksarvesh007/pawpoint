"""Tests for the legacy AI chat endpoint (/api/v1/ai/chat/message)."""

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import get_redis
from app.main import app
from tests.helpers import setup_auth

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

CHAT_URL = "/api/v1/ai/chat/message"


def _mock_agent_result(text: str = "Hello! How can I help?") -> MagicMock:
    """Build a fake pydantic-ai RunResult that BaseAgent.run() returns."""
    result = MagicMock()
    result.output = text
    result.model = "deepseek-chat"
    result.usage = None
    return result


def _chat_payload(clinic_id: str) -> dict:
    return {
        "message": "What are your hours?",
        "clinic_id": clinic_id,
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
# Authentication / Validation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ai_chat_empty_body_returns_422(client: AsyncClient) -> None:
    """Sending no body at all returns 422 (validation error, no auth required)."""
    mock_redis = _make_mock_redis()
    app.dependency_overrides[get_redis] = _redis_override(mock_redis)
    try:
        response = await client.post(CHAT_URL, json={})
    finally:
        app.dependency_overrides.pop(get_redis, None)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_ai_chat_empty_message_rejected(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """A message of empty string must be rejected with 422."""
    clinic = await setup_auth(db_session, client)
    mock_redis = _make_mock_redis()
    app.dependency_overrides[get_redis] = _redis_override(mock_redis)
    try:
        response = await client.post(
            CHAT_URL,
            json={
                "message": "",
                "clinic_id": str(clinic.id),
                "user_identifier": "test-user@example.com",
            },
        )
    finally:
        app.dependency_overrides.pop(get_redis, None)

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Valid request with mocked agent
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ai_chat_returns_response(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """A valid chat request with mocked LLM returns 200 with response fields."""
    clinic = await setup_auth(db_session, client)
    mock_result = _mock_agent_result("Our clinic is open 9-5!")
    mock_redis = _make_mock_redis()
    app.dependency_overrides[get_redis] = _redis_override(mock_redis)

    try:
        with patch(
            "app.ai.agents.base.BaseAgent.run",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            response = await client.post(
                CHAT_URL,
                json=_chat_payload(str(clinic.id)),
            )
    finally:
        app.dependency_overrides.pop(get_redis, None)

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "conversation_id" in data
    assert data["agent_name"] == "faq_agent"


# ---------------------------------------------------------------------------
# Clinic not found
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ai_chat_missing_clinic_id_returns_422(client: AsyncClient) -> None:
    """A request missing the required clinic_id field returns 422."""
    mock_redis = _make_mock_redis()
    app.dependency_overrides[get_redis] = _redis_override(mock_redis)
    try:
        response = await client.post(
            CHAT_URL,
            json={
                "message": "Hello",
                # clinic_id intentionally omitted
                "user_identifier": "user@example.com",
            },
        )
    finally:
        app.dependency_overrides.pop(get_redis, None)

    assert response.status_code == 422
