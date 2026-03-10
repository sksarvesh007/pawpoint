"""Tests for voice API endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import setup_auth


@pytest.mark.asyncio
async def test_voice_status_returns_availability(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """GET /{slug}/voice/status returns a response with an 'available' field."""
    clinic = await setup_auth(db_session, client)
    response = await client.get(f"/api/v1/{clinic.slug}/voice/status")
    assert response.status_code == 200
    data = response.json()
    assert "available" in data
    assert isinstance(data["available"], bool)


@pytest.mark.asyncio
async def test_voice_token_requires_auth(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """POST /{slug}/voice/token without auth returns 401."""
    clinic = await setup_auth(db_session, client)

    # Clear cookies to remove auth session
    client.cookies.clear()

    response = await client.post(f"/api/v1/{clinic.slug}/voice/token")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_webhook_missing_signature(client: AsyncClient) -> None:
    """POST /webhooks/livekit without X-Livekit-Signature returns 401."""
    response = await client.post(
        "/api/v1/webhooks/livekit",
        json={"event": "room_started", "room": {"name": "test-room"}},
    )
    assert response.status_code == 401
    assert "Missing signature" in response.json()["detail"]


@pytest.mark.asyncio
async def test_webhook_invalid_signature(client: AsyncClient) -> None:
    """POST /webhooks/livekit with an incorrect signature returns 401."""
    response = await client.post(
        "/api/v1/webhooks/livekit",
        json={"event": "room_started", "room": {"name": "test-room"}},
        headers={"X-Livekit-Signature": "invalid-signature-value"},
    )
    assert response.status_code == 401
    assert "Invalid signature" in response.json()["detail"]
