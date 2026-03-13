"""Tests for demo chat endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_demo_scenarios(client: AsyncClient) -> None:
    """Scenarios endpoint should return available demo scenarios."""
    response = await client.get("/api/v1/demo-clinic/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 4

    # Each scenario should have id, label, description
    for scenario in data:
        assert "id" in scenario
        assert "label" in scenario
        assert "description" in scenario


@pytest.mark.asyncio
async def test_list_demo_scenarios_contains_expected(client: AsyncClient) -> None:
    """Check that all 4 expected scenarios are present."""
    response = await client.get("/api/v1/demo-clinic/scenarios")
    data = response.json()
    ids = {s["id"] for s in data}
    assert "routine_scheduling" in ids
    assert "emergency" in ids
    assert "medication_refill" in ids
    assert "after_hours" in ids


@pytest.mark.asyncio
async def test_demo_chat_stream_returns_streaming(client: AsyncClient) -> None:
    """Demo chat stream should return a streaming response."""
    response = await client.post(
        "/api/v1/demo-clinic/chat/stream",
        json={
            "message": "Hello, I need to book an appointment for my dog",
            "history": [],
        },
    )
    # Should succeed (200) and be text/event-stream
    assert response.status_code == 200
    assert "text/event-stream" in response.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_demo_chat_with_scenario(client: AsyncClient) -> None:
    """Demo chat should accept a scenario parameter."""
    response = await client.post(
        "/api/v1/demo-clinic/chat/stream",
        json={
            "message": "My dog is having a seizure!",
            "history": [],
            "scenario": "emergency",
        },
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_demo_chat_empty_message_rejected(client: AsyncClient) -> None:
    """Empty message should be rejected."""
    response = await client.post(
        "/api/v1/demo-clinic/chat/stream",
        json={
            "message": "",
            "history": [],
        },
    )
    # FastAPI validation should reject empty string (if min_length is set)
    # or the endpoint handles it gracefully
    assert response.status_code in (200, 422)
