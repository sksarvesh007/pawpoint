"""Tests for call log API endpoints."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.call_log import CallDirection, CallOutcome
from tests.helpers import create_call_log, create_test_clinic, setup_auth


@pytest.mark.asyncio
async def test_list_calls_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/calls/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_calls_empty(client: AsyncClient, db_session: AsyncSession) -> None:
    await setup_auth(db_session, client)
    response = await client.get("/api/v1/calls/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_list_calls_returns_items(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    clinic = await setup_auth(db_session, client)
    for i in range(3):
        await create_call_log(
            db_session,
            clinic.id,
            started_at=datetime.now(UTC) - timedelta(hours=i),
        )

    response = await client.get("/api/v1/calls/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3

    item = data["items"][0]
    assert "id" in item
    assert "started_at" in item
    assert "caller_phone_number" in item
    assert "duration_seconds" in item
    assert "outcome" in item
    assert "direction" in item


@pytest.mark.asyncio
async def test_list_calls_pagination(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    clinic = await setup_auth(db_session, client)
    for i in range(5):
        await create_call_log(
            db_session,
            clinic.id,
            started_at=datetime.now(UTC) - timedelta(hours=i),
        )

    response = await client.get("/api/v1/calls/?limit=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
    assert data["total_pages"] == 3


@pytest.mark.asyncio
async def test_list_calls_clinic_scoping(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    clinic_a = await setup_auth(db_session, client)
    clinic_b = await create_test_clinic(db_session)

    await create_call_log(db_session, clinic_a.id)
    await create_call_log(db_session, clinic_b.id)

    response = await client.get("/api/v1/calls/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1


@pytest.mark.asyncio
async def test_get_call_by_id(client: AsyncClient, db_session: AsyncSession) -> None:
    clinic = await setup_auth(db_session, client)
    call = await create_call_log(
        db_session,
        clinic.id,
        outcome=CallOutcome.APPOINTMENT_BOOKED,
        direction=CallDirection.INBOUND,
        duration_seconds=180,
        ai_confidence_score=0.92,
        transcript="AI: Hello\nCaller: I need an appointment",
        summary="Client requested appointment for dog checkup",
        recording_url="https://storage.example.com/rec/abc123.wav",
        key_points=["appointment requested", "dog checkup"],
        actions_taken=["appointment_booked"],
    )

    response = await client.get(f"/api/v1/calls/{call.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(call.id)
    assert data["outcome"] == "appointment_booked"
    assert data["direction"] == "inbound"
    assert data["duration_seconds"] == 180
    assert data["ai_confidence_score"] == 0.92
    # CallLogDetail fields
    assert data["ended_at"] is None  # not set in fixture
    assert data["transcript"] == "AI: Hello\nCaller: I need an appointment"
    assert data["summary"] == "Client requested appointment for dog checkup"
    assert data["recording_url"] == "https://storage.example.com/rec/abc123.wav"
    assert data["key_points"] == ["appointment requested", "dog checkup"]
    assert data["actions_taken"] == ["appointment_booked"]


@pytest.mark.asyncio
async def test_get_call_detail_dict_key_points(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """key_points stored as dict should extract sentiment and nested points."""
    clinic = await setup_auth(db_session, client)
    call = await create_call_log(
        db_session,
        clinic.id,
        key_points={
            "sentiment": "positive",
            "key_points": ["owner asked about vaccines", "follow-up scheduled"],
        },
    )

    response = await client.get(f"/api/v1/calls/{call.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["sentiment"] == "positive"
    assert data["key_points"] == [
        "owner asked about vaccines",
        "follow-up scheduled",
    ]


@pytest.mark.asyncio
async def test_get_call_not_found(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await setup_auth(db_session, client)
    response = await client.get(f"/api/v1/calls/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_call_wrong_clinic(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await setup_auth(db_session, client)  # auth as clinic A
    clinic_b = await create_test_clinic(db_session)
    call = await create_call_log(db_session, clinic_b.id)

    response = await client.get(f"/api/v1/calls/{call.id}")
    assert response.status_code == 404
