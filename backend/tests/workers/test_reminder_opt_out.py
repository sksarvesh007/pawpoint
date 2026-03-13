"""Tests for communication opt-out behaviour in appointment reminders.

Verifies that SMS and email reminders are suppressed when a patient
has set communication_opt_out flags, and that they are still sent
when no opt-out is configured.

Design: mock get_db_session to return controlled fake DB sessions with
scripted execute() return values matching the exact query sequence in
_send_appointment_reminders():
  1. execute(select Appointment 24h window) → [appt] or []
  2. execute(select Clinic)                 → clinic
  3. execute(select Patient)               → patient  (only if appt.patient_id set)
  4. execute(select Appointment 2h window) → []
"""

import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Mock builders
# ---------------------------------------------------------------------------


def _fake_execute_result(scalar_value: object = None, scalars_all: list | None = None):
    """Return a mock execute() result.

    - scalar_value: what scalar_one_or_none() returns
    - scalars_all: what scalars().all() returns
    """
    r = MagicMock()
    r.scalar_one_or_none.return_value = scalar_value
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = scalars_all or []
    r.scalars.return_value = scalars_mock
    return r


def _make_appointment(clinic_id: object, patient_id: object) -> MagicMock:
    appt = MagicMock()
    appt.id = uuid.uuid4()
    appt.clinic_id = clinic_id
    appt.patient_id = patient_id
    appt.start_time = datetime.now(UTC) + timedelta(hours=24)
    appt.reminder_sent_at = None
    appt.reminder_2h_sent_at = None
    return appt


def _make_clinic() -> MagicMock:
    clinic = MagicMock()
    clinic.id = uuid.uuid4()
    clinic.name = "Test Clinic"
    clinic.phone = "+15550001234"
    clinic.voice_settings = {
        "reminder_24h_enabled": True,
        "reminder_2h_enabled": True,
    }
    return clinic


def _make_patient(opt_out: dict) -> MagicMock:
    patient = MagicMock()
    patient.id = uuid.uuid4()
    patient.name = "Buddy"
    patient.owner_first_name = "Jane"
    patient.owner_last_name = "Smith"
    patient.owner_phone = "+15551234567"
    patient.owner_email = "jane@example.com"
    patient.communication_opt_out = opt_out
    return patient


def _make_fake_db(appt, clinic, patient) -> MagicMock:
    """Build a mock DB session with scripted execute() side effects.

    Query sequence for _send_appointment_reminders with 1 appointment:
      [0] 24h window appointment query → [appt]
      [1] clinic query                 → clinic
      [2] patient query                → patient
      [3] 2h window appointment query  → []
    """
    db = MagicMock()
    db.commit = AsyncMock()
    db.add = MagicMock()
    db.execute = AsyncMock(
        side_effect=[
            _fake_execute_result(scalars_all=[appt]),  # 24h window
            _fake_execute_result(scalar_value=clinic),  # clinic
            _fake_execute_result(scalar_value=patient),  # patient
            _fake_execute_result(scalars_all=[]),  # 2h window (no appointments)
        ]
    )
    return db


@asynccontextmanager
async def _fake_get_db_session(db):
    yield db


def _mock_sms() -> MagicMock:
    svc = MagicMock()
    svc.send_appointment_reminder = AsyncMock(
        return_value={"sid": "SM123", "status": "queued"}
    )
    return svc


def _mock_email() -> MagicMock:
    svc = MagicMock()
    svc.send_appointment_reminder = AsyncMock(
        return_value={"message_id": "SG456", "status": "sent"}
    )
    return svc


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_sms_opt_out_suppresses_sms_reminder() -> None:
    """Patient with opt_out.sms=True must not receive an SMS reminder."""
    clinic = _make_clinic()
    patient = _make_patient(opt_out={"sms": True})
    appt = _make_appointment(clinic.id, patient.id)

    mock_db = _make_fake_db(appt, clinic, patient)
    mock_sms = _mock_sms()
    mock_email = _mock_email()

    with (
        patch("app.db.get_db_session", return_value=_fake_get_db_session(mock_db)),
        patch("app.services.sms.SMSService", return_value=mock_sms),
        patch("app.services.email.EmailService", return_value=mock_email),
    ):
        from app.workers.tasks import _send_appointment_reminders

        class _FakeTask:
            request = MagicMock(retries=0)

        result = await _send_appointment_reminders(_FakeTask())

    mock_sms.send_appointment_reminder.assert_not_called()
    mock_email.send_appointment_reminder.assert_called_once()
    assert result["sent"] == 1


@pytest.mark.asyncio
async def test_email_opt_out_suppresses_email_reminder() -> None:
    """Patient with opt_out.email=True must not receive an email reminder."""
    clinic = _make_clinic()
    patient = _make_patient(opt_out={"email": True})
    appt = _make_appointment(clinic.id, patient.id)

    mock_db = _make_fake_db(appt, clinic, patient)
    mock_sms = _mock_sms()
    mock_email = _mock_email()

    with (
        patch("app.db.get_db_session", return_value=_fake_get_db_session(mock_db)),
        patch("app.services.sms.SMSService", return_value=mock_sms),
        patch("app.services.email.EmailService", return_value=mock_email),
    ):
        from app.workers.tasks import _send_appointment_reminders

        class _FakeTask:
            request = MagicMock(retries=0)

        result = await _send_appointment_reminders(_FakeTask())

    mock_email.send_appointment_reminder.assert_not_called()
    mock_sms.send_appointment_reminder.assert_called_once()
    assert result["sent"] == 1


@pytest.mark.asyncio
async def test_full_opt_out_sends_no_reminders() -> None:
    """Patient with both sms=True and email=True receives no reminders."""
    clinic = _make_clinic()
    patient = _make_patient(opt_out={"sms": True, "email": True})
    appt = _make_appointment(clinic.id, patient.id)

    mock_db = _make_fake_db(appt, clinic, patient)
    mock_sms = _mock_sms()
    mock_email = _mock_email()

    with (
        patch("app.db.get_db_session", return_value=_fake_get_db_session(mock_db)),
        patch("app.services.sms.SMSService", return_value=mock_sms),
        patch("app.services.email.EmailService", return_value=mock_email),
    ):
        from app.workers.tasks import _send_appointment_reminders

        class _FakeTask:
            request = MagicMock(retries=0)

        result = await _send_appointment_reminders(_FakeTask())

    mock_sms.send_appointment_reminder.assert_not_called()
    mock_email.send_appointment_reminder.assert_not_called()
    assert result["sent"] == 0


@pytest.mark.asyncio
async def test_no_opt_out_sends_both_reminders() -> None:
    """Patient with empty opt-out dict receives both SMS and email reminders."""
    clinic = _make_clinic()
    patient = _make_patient(opt_out={})
    appt = _make_appointment(clinic.id, patient.id)

    mock_db = _make_fake_db(appt, clinic, patient)
    mock_sms = _mock_sms()
    mock_email = _mock_email()

    with (
        patch("app.db.get_db_session", return_value=_fake_get_db_session(mock_db)),
        patch("app.services.sms.SMSService", return_value=mock_sms),
        patch("app.services.email.EmailService", return_value=mock_email),
    ):
        from app.workers.tasks import _send_appointment_reminders

        class _FakeTask:
            request = MagicMock(retries=0)

        result = await _send_appointment_reminders(_FakeTask())

    mock_sms.send_appointment_reminder.assert_called_once()
    mock_email.send_appointment_reminder.assert_called_once()
    assert result["sent"] == 2
