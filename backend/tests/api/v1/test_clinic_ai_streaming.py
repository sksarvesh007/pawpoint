"""Tests for the SSE streaming clinic AI chat endpoint (/{clinic_slug}/chat/stream)."""

import json
from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
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


def _build_stream_mock(tokens: list[str] | None = None) -> MagicMock:
    """Build a mock that mimics pydantic-ai's Agent.run_stream() context manager.

    The streaming endpoint uses:
        async with clinic_agent.agent.run_stream(...) as stream_result:
            async for chunk in stream_result.stream_text():
                ...
    """
    if tokens is None:
        tokens = ["Hello", "! ", "How can I help?"]

    async def fake_stream_text() -> AsyncIterator[str]:
        for token in tokens:
            yield token

    usage_mock = MagicMock()
    usage_mock.total_tokens = 10

    stream_result = MagicMock()
    stream_result.stream_text = fake_stream_text
    stream_result.usage = MagicMock(return_value=usage_mock)

    @asynccontextmanager
    async def fake_run_stream(*args, **kwargs):  # type: ignore[no-untyped-def]
        yield stream_result

    return fake_run_stream


# ---------------------------------------------------------------------------
# Clinic existence (slug lookup)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_stream_requires_auth(client: AsyncClient) -> None:
    """POST to a non-existent slug returns 404 (slug-based existence check)."""
    response = await client.post(
        "/api/v1/nonexistent-clinic/chat/stream",
        json=_chat_payload(),
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Content-type / status
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_stream_returns_event_stream(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """A valid streaming request returns HTTP 200 with text/event-stream media type."""
    clinic = await setup_auth(db_session, client)
    mock_redis = _make_mock_redis()
    app.dependency_overrides[get_redis] = _redis_override(mock_redis)
    fake_run_stream = _build_stream_mock([])

    try:
        with patch(
            "pydantic_ai.Agent.run_stream",
            new=fake_run_stream,
        ):
            response = await client.post(
                f"/api/v1/{clinic.slug}/chat/stream",
                json=_chat_payload(),
            )
    finally:
        app.dependency_overrides.pop(get_redis, None)

    assert response.status_code == 200
    assert "text/event-stream" in response.headers.get("content-type", "")


# ---------------------------------------------------------------------------
# SSE token delivery
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_stream_delivers_tokens(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """The response body must contain SSE data: lines with token content."""
    clinic = await setup_auth(db_session, client)
    mock_redis = _make_mock_redis()
    app.dependency_overrides[get_redis] = _redis_override(mock_redis)
    fake_run_stream = _build_stream_mock(["Hello", " there!"])

    try:
        with patch(
            "pydantic_ai.Agent.run_stream",
            new=fake_run_stream,
        ):
            response = await client.post(
                f"/api/v1/{clinic.slug}/chat/stream",
                json=_chat_payload(),
            )
    finally:
        app.dependency_overrides.pop(get_redis, None)

    assert response.status_code == 200

    body = response.text
    # Each SSE line is: "data: <json>\n\n"
    data_lines = [
        line[len("data: ") :] for line in body.splitlines() if line.startswith("data: ")
    ]
    assert len(data_lines) > 0, "Expected at least one SSE data: line"

    # Parse all events
    events = [json.loads(line) for line in data_lines]
    event_types = [e.get("type") for e in events]

    # Must have a conversation_id event at the start
    assert "conversation_id" in event_types

    # Must have token events
    token_events = [e for e in events if e.get("type") == "token"]
    assert len(token_events) == 2
    assert token_events[0]["content"] == "Hello"
    assert token_events[1]["content"] == " there!"

    # Must have a done event at the end
    assert "done" in event_types


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_stream_empty_message_rejected(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """An empty message is rejected with 422 before streaming begins."""
    clinic = await setup_auth(db_session, client)
    mock_redis = _make_mock_redis()
    app.dependency_overrides[get_redis] = _redis_override(mock_redis)

    try:
        response = await client.post(
            f"/api/v1/{clinic.slug}/chat/stream",
            json={"message": "", "user_identifier": "user@example.com"},
        )
    finally:
        app.dependency_overrides.pop(get_redis, None)

    assert response.status_code == 422
