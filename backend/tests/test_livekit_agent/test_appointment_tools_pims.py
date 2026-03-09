"""Tests for PIMS-aware appointment tool functions."""

import json
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.adapters.pims.errors import PIMSConnectionError
from app.adapters.pims.types import PIMSAppointment, PIMSProvider, PIMSTimeSlot
from livekit_agent.tools.appointment_tools import (
    book_appointment_pims,
    cancel_appointment_pims,
    check_available_appointments_pims,
    reschedule_appointment_pims,
)


@pytest.fixture
def mock_adapter():
    adapter = AsyncMock()
    adapter.get_available_slots = AsyncMock()
    adapter.get_appointments = AsyncMock()
    adapter.create_appointment = AsyncMock()
    adapter.cancel_appointment = AsyncMock()
    adapter.update_appointment = AsyncMock()
    return adapter


@pytest.fixture
def sample_providers():
    return [
        PIMSProvider(
            pims_id="prov-1",
            first_name="Jane",
            last_name="Smith",
            is_active=True,
            is_veterinarian=True,
        ),
        PIMSProvider(
            pims_id="prov-2",
            first_name="John",
            last_name="Doe",
            is_active=True,
            is_veterinarian=True,
        ),
    ]


@pytest.fixture
def tomorrow_str():
    return (datetime.now().date() + timedelta(days=1)).strftime("%Y-%m-%d")


# --- check_available_appointments_pims ---


@pytest.mark.asyncio
async def test_check_available_pims_returns_slots(
    mock_adapter, sample_providers, tomorrow_str
):
    """PIMS adapter returns slots for providers."""
    tomorrow = datetime.strptime(tomorrow_str, "%Y-%m-%d").date()
    mock_adapter.get_available_slots.return_value = [
        PIMSTimeSlot(
            start_time=datetime.combine(
                tomorrow, datetime.strptime("09:00", "%H:%M").time()
            ).replace(tzinfo=UTC),
            end_time=datetime.combine(
                tomorrow, datetime.strptime("09:30", "%H:%M").time()
            ).replace(tzinfo=UTC),
            provider_pims_id="prov-1",
        ),
        PIMSTimeSlot(
            start_time=datetime.combine(
                tomorrow, datetime.strptime("10:00", "%H:%M").time()
            ).replace(tzinfo=UTC),
            end_time=datetime.combine(
                tomorrow, datetime.strptime("10:30", "%H:%M").time()
            ).replace(tzinfo=UTC),
            provider_pims_id="prov-1",
        ),
    ]

    result = await check_available_appointments_pims(
        adapter=mock_adapter,
        date_str=tomorrow_str,
        cached_providers=sample_providers,
    )

    assert "openings" in result.lower() or "we have" in result.lower()
    assert mock_adapter.get_available_slots.called


@pytest.mark.asyncio
async def test_check_available_pims_past_date(mock_adapter):
    """Rejects past dates without calling adapter."""
    yesterday = (datetime.now().date() - timedelta(days=1)).strftime("%Y-%m-%d")

    result = await check_available_appointments_pims(
        adapter=mock_adapter,
        date_str=yesterday,
    )

    assert "past" in result.lower()
    mock_adapter.get_available_slots.assert_not_called()
    mock_adapter.get_appointments.assert_not_called()


@pytest.mark.asyncio
async def test_check_available_pims_no_slots(
    mock_adapter, sample_providers, tomorrow_str
):
    """Returns 'no available' message when PIMS has no slots."""
    mock_adapter.get_available_slots.return_value = []

    result = await check_available_appointments_pims(
        adapter=mock_adapter,
        date_str=tomorrow_str,
        cached_providers=sample_providers,
    )

    assert "don't have any" in result.lower() or "no available" in result.lower()


# --- book_appointment_pims ---


@pytest.mark.asyncio
async def test_book_appointment_pims_success(mock_adapter, tomorrow_str):
    """Successful PIMS booking returns confirmation with PIMS ID."""
    mock_adapter.create_appointment.return_value = PIMSAppointment(
        pims_id="PIMS-12345",
        start_time=datetime.now(UTC),
        end_time=datetime.now(UTC) + timedelta(minutes=30),
        status="scheduled",
    )
    mock_redis = AsyncMock()

    result = await book_appointment_pims(
        adapter=mock_adapter,
        redis_client=mock_redis,
        clinic_id="clinic-1",
        pet_name="Buddy",
        owner_name="Alice",
        date_str=tomorrow_str,
        time_str="10:00",
        reason="Checkup",
        phone="555-1234",
    )

    assert "PIMS-12345" in result
    assert "Buddy" in result
    mock_adapter.create_appointment.assert_called_once()


@pytest.mark.asyncio
async def test_book_appointment_pims_also_queues_redis(mock_adapter, tomorrow_str):
    """Booking also queues a Redis entry for local DB sync."""
    mock_adapter.create_appointment.return_value = PIMSAppointment(
        pims_id="PIMS-99",
        start_time=datetime.now(UTC),
        end_time=datetime.now(UTC) + timedelta(minutes=30),
    )
    mock_redis = AsyncMock()

    await book_appointment_pims(
        adapter=mock_adapter,
        redis_client=mock_redis,
        clinic_id="clinic-1",
        pet_name="Max",
        owner_name="Bob",
        date_str=tomorrow_str,
        time_str="14:00",
        reason="Vaccination",
        phone="555-9999",
    )

    mock_redis.rpush.assert_called_once()
    queued_data = json.loads(mock_redis.rpush.call_args[0][1])
    assert queued_data["source"] == "voice_ai_pims"
    assert queued_data["pims_id"] == "PIMS-99"


# --- cancel_appointment_pims ---


@pytest.mark.asyncio
async def test_cancel_appointment_pims_success(mock_adapter):
    """Cancels in PIMS and updates local DB."""
    mock_db = AsyncMock()
    mock_appointment = MagicMock()
    mock_appointment.pims_id = "PIMS-CANCEL-1"
    mock_appointment.start_time = datetime.now(UTC) + timedelta(days=1)
    mock_appointment.status = "SCHEDULED"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_appointment
    mock_db.execute.return_value = mock_result

    mock_adapter.cancel_appointment.return_value = True

    result = await cancel_appointment_pims(
        adapter=mock_adapter,
        db=mock_db,
        clinic_id="clinic-1",
        confirmation_code="ABC123",
    )

    assert "cancelled" in result.lower()
    mock_adapter.cancel_appointment.assert_called_once_with(
        "PIMS-CANCEL-1", reason="Cancelled via voice AI"
    )
    mock_db.commit.assert_called_once()


# --- reschedule_appointment_pims ---


@pytest.mark.asyncio
async def test_reschedule_appointment_pims_success(mock_adapter, tomorrow_str):
    """Reschedules in PIMS and updates local DB."""
    mock_db = AsyncMock()
    mock_redis = AsyncMock()
    mock_appointment = MagicMock()
    mock_appointment.pims_id = "PIMS-RESCH-1"
    mock_appointment.start_time = datetime.now(UTC) + timedelta(days=1)
    mock_appointment.duration_minutes = 30
    mock_appointment.reason = "Checkup"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_appointment
    mock_db.execute.return_value = mock_result

    mock_adapter.update_appointment.return_value = PIMSAppointment(
        pims_id="PIMS-RESCH-1",
    )

    result = await reschedule_appointment_pims(
        adapter=mock_adapter,
        db=mock_db,
        redis_client=mock_redis,
        clinic_id="clinic-1",
        confirmation_code="RESCH1",
        new_date=tomorrow_str,
        new_time="15:00",
    )

    assert "rescheduled" in result.lower()
    mock_adapter.update_appointment.assert_called_once()
    mock_db.commit.assert_called_once()


# --- Error propagation ---


@pytest.mark.asyncio
async def test_pims_error_propagates(mock_adapter, tomorrow_str, sample_providers):
    """PIMSError is raised (not swallowed) so caller can fall back."""
    mock_adapter.get_available_slots.side_effect = PIMSConnectionError(
        "Connection refused", pims_type="ezyvet"
    )

    with pytest.raises(PIMSConnectionError):
        await check_available_appointments_pims(
            adapter=mock_adapter,
            date_str=tomorrow_str,
            cached_providers=sample_providers,
        )
