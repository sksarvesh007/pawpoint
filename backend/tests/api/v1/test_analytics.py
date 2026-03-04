"""Tests for analytics API endpoints."""

from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.call_log import CallOutcome
from tests.helpers import (
    create_call_log,
    create_chat_analysis,
    create_conversation,
    setup_auth,
)


@pytest.mark.asyncio
async def test_dashboard_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/analytics/dashboard")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_dashboard_empty_state(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await setup_auth(db_session, client)
    response = await client.get("/api/v1/analytics/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data["calls"]["total_calls"] == 0
    assert data["appointments"]["total_appointments"] == 0


@pytest.mark.asyncio
async def test_dashboard_response_structure(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await setup_auth(db_session, client)
    response = await client.get("/api/v1/analytics/dashboard")
    assert response.status_code == 200
    data = response.json()
    for key in (
        "calls",
        "appointments",
        "patients",
        "pims",
        "sentiment",
        "recent_calls",
    ):
        assert key in data, f"Missing key: {key}"


@pytest.mark.asyncio
async def test_dashboard_with_calls(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    clinic = await setup_auth(db_session, client)
    for i in range(3):
        await create_call_log(
            db_session,
            clinic.id,
            started_at=datetime.now(UTC) - timedelta(hours=i),
        )

    response = await client.get("/api/v1/analytics/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data["calls"]["total_calls"] == 3


@pytest.mark.asyncio
async def test_call_analytics_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/analytics/calls")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_call_analytics_with_data(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    clinic = await setup_auth(db_session, client)
    now = datetime.now(UTC)
    await create_call_log(
        db_session,
        clinic.id,
        outcome=CallOutcome.APPOINTMENT_BOOKED,
        started_at=now,
    )
    await create_call_log(
        db_session,
        clinic.id,
        outcome=CallOutcome.INFORMATION_PROVIDED,
        started_at=now - timedelta(hours=1),
    )
    await create_call_log(
        db_session,
        clinic.id,
        outcome=CallOutcome.EMERGENCY_TRANSFER,
        started_at=now - timedelta(hours=2),
    )

    response = await client.get("/api/v1/analytics/calls")
    assert response.status_code == 200
    data = response.json()
    assert data["total_calls"] == 3
    assert data["appointments_booked"] == 1
    assert data["emergency_transfers"] == 1


@pytest.mark.asyncio
async def test_chat_analytics_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/analytics/chats")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_chat_analytics_with_data(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    clinic = await setup_auth(db_session, client)
    conv1 = await create_conversation(db_session, clinic.id, channel="chat")
    conv2 = await create_conversation(db_session, clinic.id, channel="chat")
    await create_chat_analysis(db_session, conv1.id, sentiment="positive")
    await create_chat_analysis(db_session, conv2.id, sentiment="negative")

    response = await client.get("/api/v1/analytics/chats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_chats"] == 2
    assert data["analyzed_count"] == 2
