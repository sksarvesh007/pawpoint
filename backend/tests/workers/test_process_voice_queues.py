"""Tests for the booking_queue consumer in process_voice_queues.

These tests verify that appointments booked via the voice agent are:
  - written to the DB
  - trigger SMS/email confirmations
  - log delivery failures as Notifications
  - re-queue items that fail rather than silently losing them

Design note: _process_voice_queues() creates its own DB sessions via
get_db_session(), separate from the test session. We mock get_db_session
to return a controlled async context manager with a MagicMock session,
then assert on what was added/called.
"""

import json
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_booking_item(clinic_id: str, **overrides: object) -> str:
    """Build a JSON-serialised booking_queue item with sensible defaults."""
    base: dict = {
        "id": "BOOK1234",
        "clinic_id": clinic_id,
        "pet_name": "Buddy",
        "owner_name": "Jane Smith",
        "date": (datetime.now(UTC) + timedelta(days=3)).strftime("%Y-%m-%d"),
        "time": "10:00",
        "reason": "Annual checkup",
        "phone": "+15551234567",
        "owner_email": "jane@example.com",
        "provider_name": None,
        "source": "voice_ai",
        "created_at": datetime.now(UTC).isoformat(),
    }
    base.update(overrides)
    return json.dumps(base)


def _make_fake_redis(items: list[str]) -> AsyncMock:
    """Return a fake Redis whose lpop drains `items`, then returns None for every queue."""
    # We have 5 queues: booking, medication, message, emergency, missed_transfer
    # Each queue drains with None to stop. Provide enough Nones for all queues.
    nones = [None] * 10
    fake = AsyncMock()
    fake.lpop = AsyncMock(side_effect=items + nones)
    fake.rpush = AsyncMock()
    fake.aclose = AsyncMock()
    return fake


def _make_mock_db_session(clinic_id: str | None = None) -> MagicMock:
    """Return a MagicMock DB session.

    If clinic_id is given, SELECT Clinic returns a fake clinic with that id.
    """
    db = MagicMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.execute = AsyncMock()

    # Default: scalar_one_or_none returns a fake clinic
    fake_clinic = MagicMock()
    fake_clinic.name = "Test Clinic"
    fake_clinic.phone = "+15550001234"
    fake_clinic.voice_settings = {}
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = fake_clinic
    db.execute.return_value = result_mock

    return db


@asynccontextmanager
async def _fake_get_db_session(db: MagicMock):
    yield db


def _mock_sms_success() -> MagicMock:
    svc = MagicMock()
    svc.send_appointment_confirmation = AsyncMock(
        return_value={"sid": "SM123", "status": "queued"}
    )
    return svc


def _mock_sms_failure() -> MagicMock:
    svc = MagicMock()
    svc.send_appointment_confirmation = AsyncMock(
        return_value={"sid": None, "status": "failed", "error": "Invalid number"}
    )
    return svc


def _mock_email_success() -> MagicMock:
    svc = MagicMock()
    svc.send_appointment_confirmation = AsyncMock(
        return_value={"message_id": "SG456", "status": "sent"}
    )
    return svc


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_booking_queue_writes_appointment_to_db() -> None:
    """Happy path: a queued booking results in db.add() being called with an Appointment."""
    from app.models.appointment import Appointment

    clinic_id = str(uuid.uuid4())
    raw = _make_booking_item(clinic_id)

    fake_redis = _make_fake_redis([raw])
    mock_db = _make_mock_db_session(clinic_id)

    with (
        patch("redis.asyncio.Redis.from_url", return_value=fake_redis),
        patch(
            "app.db.get_db_session",
            return_value=_fake_get_db_session(mock_db),
        ),
        patch("app.services.sms.SMSService", return_value=_mock_sms_success()),
        patch("app.services.email.EmailService", return_value=_mock_email_success()),
    ):
        from app.workers.tasks import _process_voice_queues

        result = await _process_voice_queues()

    assert result["bookings"] == 1

    # Verify that db.add() was called with an Appointment as the first added object
    added_objects = [c.args[0] for c in mock_db.add.call_args_list]
    appointment_objects = [o for o in added_objects if isinstance(o, Appointment)]
    assert len(appointment_objects) == 1
    assert appointment_objects[0].reason == "Annual checkup"


@pytest.mark.asyncio
async def test_booking_queue_sends_sms_and_email() -> None:
    """After writing the appointment, SMS and email confirmations are sent."""
    clinic_id = str(uuid.uuid4())
    raw = _make_booking_item(clinic_id)

    fake_redis = _make_fake_redis([raw])
    mock_db = _make_mock_db_session(clinic_id)
    mock_sms = _mock_sms_success()
    mock_email = _mock_email_success()

    with (
        patch("redis.asyncio.Redis.from_url", return_value=fake_redis),
        patch(
            "app.db.get_db_session",
            return_value=_fake_get_db_session(mock_db),
        ),
        patch("app.services.sms.SMSService", return_value=mock_sms),
        patch("app.services.email.EmailService", return_value=mock_email),
    ):
        from app.workers.tasks import _process_voice_queues

        await _process_voice_queues()

    mock_sms.send_appointment_confirmation.assert_called_once()
    mock_email.send_appointment_confirmation.assert_called_once()


@pytest.mark.asyncio
async def test_booking_queue_no_email_skips_email_send() -> None:
    """Items without owner_email should send SMS only, not email."""
    clinic_id = str(uuid.uuid4())
    raw = _make_booking_item(clinic_id, owner_email=None)

    fake_redis = _make_fake_redis([raw])
    mock_db = _make_mock_db_session(clinic_id)
    mock_sms = _mock_sms_success()
    mock_email = _mock_email_success()

    with (
        patch("redis.asyncio.Redis.from_url", return_value=fake_redis),
        patch(
            "app.db.get_db_session",
            return_value=_fake_get_db_session(mock_db),
        ),
        patch("app.services.sms.SMSService", return_value=mock_sms),
        patch("app.services.email.EmailService", return_value=mock_email),
    ):
        from app.workers.tasks import _process_voice_queues

        await _process_voice_queues()

    mock_sms.send_appointment_confirmation.assert_called_once()
    mock_email.send_appointment_confirmation.assert_not_called()


@pytest.mark.asyncio
async def test_booking_queue_sms_failure_creates_failed_message_log() -> None:
    """When SMS delivery fails, db.add() is called with a MessageLog(status=failed)."""
    from app.models.message_log import MessageLog

    clinic_id = str(uuid.uuid4())
    raw = _make_booking_item(clinic_id, owner_email=None)  # SMS-only for simplicity

    fake_redis = _make_fake_redis([raw])
    mock_db = _make_mock_db_session(clinic_id)

    with (
        patch("redis.asyncio.Redis.from_url", return_value=fake_redis),
        patch(
            "app.db.get_db_session",
            return_value=_fake_get_db_session(mock_db),
        ),
        patch("app.services.sms.SMSService", return_value=_mock_sms_failure()),
        patch("app.services.email.EmailService", return_value=_mock_email_success()),
    ):
        from app.workers.tasks import _process_voice_queues

        await _process_voice_queues()

    added_objects = [c.args[0] for c in mock_db.add.call_args_list]
    failed_logs = [
        o for o in added_objects if isinstance(o, MessageLog) and o.status == "failed"
    ]
    assert len(failed_logs) == 1
    assert failed_logs[0].channel == "sms"


@pytest.mark.asyncio
async def test_booking_queue_missing_clinic_id_skipped() -> None:
    """Items with no clinic_id are skipped without crashing or re-queuing."""
    bad_item = json.dumps({"pet_name": "Max", "phone": "+15550000000"})

    fake_redis = _make_fake_redis([bad_item])
    mock_db = _make_mock_db_session()

    with (
        patch("redis.asyncio.Redis.from_url", return_value=fake_redis),
        patch(
            "app.db.get_db_session",
            return_value=_fake_get_db_session(mock_db),
        ),
        patch("app.services.sms.SMSService", return_value=_mock_sms_success()),
        patch("app.services.email.EmailService", return_value=_mock_email_success()),
    ):
        from app.workers.tasks import _process_voice_queues

        result = await _process_voice_queues()

    assert result["bookings"] == 0
    # Invalid items must NOT be re-queued — they'd loop forever
    assert not any(
        c == call("booking_queue", bad_item) for c in fake_redis.rpush.call_args_list
    )


@pytest.mark.asyncio
async def test_booking_queue_db_failure_requeues_item() -> None:
    """If DB write fails, the item is re-pushed to booking_queue for the next tick."""
    clinic_id = str(uuid.uuid4())
    raw = _make_booking_item(clinic_id)

    fake_redis = _make_fake_redis([raw])

    with (
        patch("redis.asyncio.Redis.from_url", return_value=fake_redis),
        patch(
            "app.db.get_db_session",
            side_effect=Exception("DB connection lost"),
        ),
        patch("app.services.sms.SMSService", return_value=_mock_sms_success()),
        patch("app.services.email.EmailService", return_value=_mock_email_success()),
    ):
        from app.workers.tasks import _process_voice_queues

        result = await _process_voice_queues()

    assert result["bookings"] == 0
    fake_redis.rpush.assert_any_call("booking_queue", raw)
