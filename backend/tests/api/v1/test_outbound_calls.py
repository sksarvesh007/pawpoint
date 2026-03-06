"""Tests for outbound calls API endpoints."""

from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.call_log import CallDirection, CallLog, CallStatus
from tests.helpers import create_call_log, setup_auth


@pytest.mark.asyncio
async def test_initiate_call_requires_auth(client: AsyncClient) -> None:
    """POST /outbound-calls/ returns 401 without auth."""
    response = await client.post(
        "/api/v1/outbound-calls/",
        json={"to_phone": "+15551234567", "purpose": "reminder"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_initiate_call_no_twilio_number(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """POST /outbound-calls/ returns 400 when clinic has no twilio_phone_number."""
    await setup_auth(db_session, client)

    with patch(
        "app.services.outbound_call.OutboundCallService._get_twilio_client"
    ) as mock_client:
        mock_client.return_value = MagicMock()
        response = await client.post(
            "/api/v1/outbound-calls/",
            json={"to_phone": "+15551234567", "purpose": "reminder"},
        )

    assert response.status_code == 400
    assert "Twilio phone number" in response.json()["detail"]


@pytest.mark.asyncio
async def test_initiate_call_success(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """POST /outbound-calls/ creates a call and returns call details."""
    clinic = await setup_auth(db_session, client)
    # Set a Twilio phone number on the clinic
    clinic.twilio_phone_number = "+15559876543"
    await db_session.flush()

    mock_twilio_call = MagicMock()
    mock_twilio_call.sid = "CA" + "a" * 32

    mock_calls = MagicMock()
    mock_calls.create = MagicMock(return_value=mock_twilio_call)

    mock_twilio_client = MagicMock()
    mock_twilio_client.calls = mock_calls

    with patch(
        "app.services.outbound_call.OutboundCallService._get_twilio_client",
        return_value=mock_twilio_client,
    ):
        response = await client.post(
            "/api/v1/outbound-calls/",
            json={
                "to_phone": "+15551234567",
                "purpose": "reminder",
                "message": "Your appointment is tomorrow at 10am.",
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["twilio_call_sid"] == mock_twilio_call.sid
    assert data["status"] == "ringing"
    assert data["from_phone"] == "+15559876543"
    assert data["to_phone"] == "+15551234567"
    assert data["purpose"] == "reminder"

    # Verify CallLog was created in the DB
    from sqlalchemy import select

    result = await db_session.execute(
        select(CallLog).where(CallLog.twilio_call_sid == mock_twilio_call.sid)
    )
    call_log = result.scalar_one()
    assert call_log.direction == CallDirection.OUTBOUND
    assert call_log.clinic_id == clinic.id


@pytest.mark.asyncio
async def test_initiate_call_invalid_phone(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """POST /outbound-calls/ returns 422 for invalid phone format."""
    await setup_auth(db_session, client)
    response = await client.post(
        "/api/v1/outbound-calls/",
        json={"to_phone": "555-1234", "purpose": "reminder"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_outbound_call_status(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """GET /outbound-calls/{id} returns outbound call details."""
    clinic = await setup_auth(db_session, client)
    call = await create_call_log(
        db_session,
        clinic.id,
        direction=CallDirection.OUTBOUND,
        twilio_call_sid="CAtestget123",
        status=CallStatus.IN_PROGRESS,
        extra_data={"purpose": "follow_up"},
    )

    response = await client.get(f"/api/v1/outbound-calls/{call.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["call_id"] == str(call.id)
    assert data["twilio_call_sid"] == "CAtestget123"
    assert data["status"] == "in_progress"
    assert data["purpose"] == "follow_up"


@pytest.mark.asyncio
async def test_status_callback_updates_call(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """POST /outbound-calls/webhooks/status updates the CallLog."""
    clinic = await setup_auth(db_session, client)
    call = await create_call_log(
        db_session,
        clinic.id,
        direction=CallDirection.OUTBOUND,
        twilio_call_sid="CAstatuscb123",
        status=CallStatus.RINGING,
    )

    # Mock Twilio signature validation
    with patch("app.api.v1.endpoints.outbound_calls._validate_twilio_signature"):
        response = await client.post(
            "/api/v1/outbound-calls/webhooks/status",
            data={
                "CallSid": "CAstatuscb123",
                "CallStatus": "completed",
                "CallDuration": "45",
            },
        )

    assert response.status_code == 200

    # Verify DB was updated
    await db_session.refresh(call)
    assert call.status == CallStatus.COMPLETED
    assert call.duration_seconds == 45
    assert call.ended_at is not None


@pytest.mark.asyncio
async def test_twiml_webhook_returns_xml(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """POST /outbound-calls/webhooks/twiml returns TwiML XML."""
    clinic = await setup_auth(db_session, client)
    await create_call_log(
        db_session,
        clinic.id,
        direction=CallDirection.OUTBOUND,
        twilio_call_sid="CAtwimltest123",
        extra_data={
            "purpose": "reminder",
            "message": "Your pet appointment is tomorrow.",
        },
    )

    with patch("app.api.v1.endpoints.outbound_calls._validate_twilio_signature"):
        response = await client.post(
            "/api/v1/outbound-calls/webhooks/twiml",
            data={"CallSid": "CAtwimltest123"},
        )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/xml"
    body = response.text
    assert "<Response>" in body
    assert "<Say" in body
    assert "Your pet appointment is tomorrow." in body
