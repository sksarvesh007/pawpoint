"""Tests for the Covetrus Connect PIMS adapter."""

import uuid
from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.adapters.pims.covetrus import COVETRUS_STATUS_MAP, CovetrusAdapter
from app.adapters.pims.errors import PIMSAuthError, PIMSError, PIMSWriteError
from app.adapters.pims.types import PIMSAppointment

CLINIC_ID = uuid.uuid4()
CREDS = {
    "client_id": "test-client-id",
    "client_secret": "test-client-secret",
    "partner_id": "test-partner-id",
}


def _make_adapter(creds: dict | None = None) -> CovetrusAdapter:
    return CovetrusAdapter(CLINIC_ID, creds or CREDS)


# ------------------------------------------------------------------
# Initialisation & headers
# ------------------------------------------------------------------


class TestInit:
    def test_default_url(self) -> None:
        adapter = _make_adapter()
        assert adapter._base_url == "https://api.covetrus.com/v1"

    def test_custom_url(self) -> None:
        adapter = _make_adapter(
            {**CREDS, "base_url": "https://api.staging.covetrus.com/v1"}
        )
        assert adapter._base_url == "https://api.staging.covetrus.com/v1"

    def test_trailing_slash_stripped(self) -> None:
        adapter = _make_adapter({**CREDS, "base_url": "https://api.covetrus.com/v1/"})
        assert adapter._base_url == "https://api.covetrus.com/v1"

    def test_credentials_stored(self) -> None:
        adapter = _make_adapter()
        assert adapter._client_id == "test-client-id"
        assert adapter._client_secret == "test-client-secret"
        assert adapter._partner_id == "test-partner-id"

    def test_authorization_header(self) -> None:
        adapter = _make_adapter()
        adapter._access_token = "tok-123"
        headers = adapter._get_headers()
        assert headers["Authorization"] == "Bearer tok-123"
        assert headers["X-Partner-Id"] == "test-partner-id"
        assert headers["Accept"] == "application/json"


# ------------------------------------------------------------------
# Authentication
# ------------------------------------------------------------------


class TestAuthenticate:
    @pytest.mark.asyncio
    async def test_authenticate_success(self) -> None:
        adapter = _make_adapter()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "tok-abc",
            "expires_in": 3600,
        }
        adapter._request = AsyncMock(return_value=mock_response)

        result = await adapter.authenticate()
        assert result is True
        assert adapter._access_token == "tok-abc"
        assert adapter._token_expires_at is not None

    @pytest.mark.asyncio
    async def test_authenticate_failure_status(self) -> None:
        adapter = _make_adapter()
        mock_response = MagicMock()
        mock_response.status_code = 401
        adapter._request = AsyncMock(return_value=mock_response)

        with pytest.raises(PIMSAuthError, match="auth failed"):
            await adapter.authenticate()

    @pytest.mark.asyncio
    async def test_authenticate_failure_exception(self) -> None:
        adapter = _make_adapter()
        adapter._request = AsyncMock(side_effect=ConnectionError("network"))

        with pytest.raises(PIMSAuthError, match="authentication error"):
            await adapter.authenticate()

    @pytest.mark.asyncio
    async def test_token_caching(self) -> None:
        adapter = _make_adapter()
        adapter._access_token = "tok-cached"
        adapter._token_expires_at = datetime.now() + timedelta(hours=1)

        adapter.authenticate = AsyncMock()
        await adapter._ensure_authenticated()
        adapter.authenticate.assert_not_called()

    @pytest.mark.asyncio
    async def test_token_refresh_when_expired(self) -> None:
        adapter = _make_adapter()
        adapter._access_token = "tok-old"
        adapter._token_expires_at = datetime.now() - timedelta(minutes=1)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "tok-new",
            "expires_in": 3600,
        }
        adapter._request = AsyncMock(return_value=mock_response)

        await adapter._ensure_authenticated()
        assert adapter._access_token == "tok-new"


# ------------------------------------------------------------------
# Test connection
# ------------------------------------------------------------------


class TestConnection:
    @pytest.mark.asyncio
    async def test_test_connection_success(self) -> None:
        adapter = _make_adapter()
        adapter._ensure_authenticated = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        adapter._request = AsyncMock(return_value=mock_response)

        result = await adapter.test_connection()
        assert result["connected"] is True
        assert result["pims_type"] == "covetrus"

    @pytest.mark.asyncio
    async def test_test_connection_failure_status(self) -> None:
        adapter = _make_adapter()
        adapter._ensure_authenticated = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 500
        adapter._request = AsyncMock(return_value=mock_response)

        result = await adapter.test_connection()
        assert result["connected"] is False

    @pytest.mark.asyncio
    async def test_test_connection_exception(self) -> None:
        adapter = _make_adapter()
        adapter._ensure_authenticated = AsyncMock(
            side_effect=Exception("connect timeout")
        )

        result = await adapter.test_connection()
        assert result["connected"] is False
        assert "connect timeout" in result["message"]


# ------------------------------------------------------------------
# Patient mapping
# ------------------------------------------------------------------


SAMPLE_PATIENT = {
    "id": 100,
    "name": "Buddy",
    "species": "Canine",
    "breed": "Labrador",
    "color": "Golden",
    "sex": "Male",
    "date_of_birth": "2020-03-15",
    "weight": 30.5,
    "microchip_number": "chip-999",
    "is_deceased": False,
    "is_active": True,
    "owner_first_name": "Jane",
    "owner_last_name": "Doe",
    "owner_phone": "555-1234",
    "owner_email": "jane@example.com",
}


class TestPatientMapping:
    def test_basic_fields(self) -> None:
        adapter = _make_adapter()
        p = adapter._map_patient(SAMPLE_PATIENT)
        assert p.pims_id == "100"
        assert p.name == "Buddy"
        assert p.species == "canine"
        assert p.breed == "Labrador"
        assert p.color == "Golden"
        assert p.microchip_id == "chip-999"
        assert p.is_active is True
        assert p.is_deceased is False

    def test_owner_mapping(self) -> None:
        adapter = _make_adapter()
        p = adapter._map_patient(SAMPLE_PATIENT)
        assert p.owner_first_name == "Jane"
        assert p.owner_last_name == "Doe"
        assert p.owner_phone == "555-1234"
        assert p.owner_email == "jane@example.com"

    def test_birth_date(self) -> None:
        adapter = _make_adapter()
        p = adapter._map_patient(SAMPLE_PATIENT)
        assert p.date_of_birth == datetime(2020, 3, 15)

    def test_weight(self) -> None:
        adapter = _make_adapter()
        p = adapter._map_patient(SAMPLE_PATIENT)
        assert p.weight_kg == 30.5

    def test_sex_lowered(self) -> None:
        adapter = _make_adapter()
        p = adapter._map_patient(SAMPLE_PATIENT)
        assert p.sex == "male"

    def test_missing_sex(self) -> None:
        raw = {**SAMPLE_PATIENT}
        del raw["sex"]
        adapter = _make_adapter()
        p = adapter._map_patient(raw)
        assert p.sex is None

    def test_raw_data_preserved(self) -> None:
        adapter = _make_adapter()
        p = adapter._map_patient(SAMPLE_PATIENT)
        assert p.raw_data == SAMPLE_PATIENT


# ------------------------------------------------------------------
# Get patients
# ------------------------------------------------------------------


class TestGetPatients:
    @pytest.mark.asyncio
    async def test_get_patients(self) -> None:
        adapter = _make_adapter()
        adapter._ensure_authenticated = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [SAMPLE_PATIENT]}
        adapter._request = AsyncMock(return_value=mock_response)

        patients = await adapter.get_patients(limit=10, offset=5)
        assert len(patients) == 1
        assert patients[0].name == "Buddy"

        call_kwargs = adapter._request.call_args
        params = call_kwargs.kwargs.get("params") or call_kwargs[1].get("params")
        assert params["limit"] == 10
        assert params["offset"] == 5

    @pytest.mark.asyncio
    async def test_get_patients_with_since(self) -> None:
        adapter = _make_adapter()
        adapter._ensure_authenticated = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        adapter._request = AsyncMock(return_value=mock_response)

        since = datetime(2025, 1, 1)
        await adapter.get_patients(since=since)

        call_kwargs = adapter._request.call_args
        params = call_kwargs.kwargs.get("params") or call_kwargs[1].get("params")
        assert "modified_since" in params
        assert "2025-01-01" in params["modified_since"]

    @pytest.mark.asyncio
    async def test_get_patients_error(self) -> None:
        adapter = _make_adapter()
        adapter._ensure_authenticated = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 500
        adapter._request = AsyncMock(return_value=mock_response)

        with pytest.raises(PIMSError, match="Failed to fetch patients"):
            await adapter.get_patients()


# ------------------------------------------------------------------
# Get patient by ID
# ------------------------------------------------------------------


class TestGetPatientById:
    @pytest.mark.asyncio
    async def test_found(self) -> None:
        adapter = _make_adapter()
        adapter._ensure_authenticated = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": SAMPLE_PATIENT}
        adapter._request = AsyncMock(return_value=mock_response)

        patient = await adapter.get_patient_by_id("100")
        assert patient is not None
        assert patient.pims_id == "100"

    @pytest.mark.asyncio
    async def test_not_found(self) -> None:
        adapter = _make_adapter()
        adapter._ensure_authenticated = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 404
        adapter._request = AsyncMock(return_value=mock_response)

        patient = await adapter.get_patient_by_id("999")
        assert patient is None

    @pytest.mark.asyncio
    async def test_empty_response(self) -> None:
        adapter = _make_adapter()
        adapter._ensure_authenticated = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        adapter._request = AsyncMock(return_value=mock_response)

        patient = await adapter.get_patient_by_id("100")
        assert patient is None


# ------------------------------------------------------------------
# Appointment mapping
# ------------------------------------------------------------------


SAMPLE_APPOINTMENT = {
    "id": 500,
    "patient_id": 100,
    "provider_id": 300,
    "start_time": "2025-06-15T10:00:00",
    "end_time": "2025-06-15T10:30:00",
    "appointment_type": "Wellness Exam",
    "status": "Confirmed",
    "reason": "Annual checkup",
    "notes": "Bring vaccination records",
}


class TestAppointmentMapping:
    def test_basic_fields(self) -> None:
        adapter = _make_adapter()
        a = adapter._map_appointment(SAMPLE_APPOINTMENT)
        assert a.pims_id == "500"
        assert a.patient_pims_id == "100"
        assert a.provider_pims_id == "300"
        assert a.reason == "Annual checkup"
        assert a.notes == "Bring vaccination records"
        assert a.appointment_type == "Wellness Exam"

    def test_start_and_end(self) -> None:
        adapter = _make_adapter()
        a = adapter._map_appointment(SAMPLE_APPOINTMENT)
        assert a.start_time == datetime(2025, 6, 15, 10, 0, 0)
        assert a.end_time == datetime(2025, 6, 15, 10, 30, 0)
        assert a.duration_minutes == 30

    def test_status_normalization(self) -> None:
        adapter = _make_adapter()
        a = adapter._map_appointment(SAMPLE_APPOINTMENT)
        assert a.status == "confirmed"

    def test_missing_patient_id(self) -> None:
        raw = {**SAMPLE_APPOINTMENT, "patient_id": None}
        adapter = _make_adapter()
        a = adapter._map_appointment(raw)
        assert a.patient_pims_id is None

    def test_missing_provider_id(self) -> None:
        raw = {**SAMPLE_APPOINTMENT, "provider_id": None}
        adapter = _make_adapter()
        a = adapter._map_appointment(raw)
        assert a.provider_pims_id is None

    def test_raw_data_preserved(self) -> None:
        adapter = _make_adapter()
        a = adapter._map_appointment(SAMPLE_APPOINTMENT)
        assert a.raw_data == SAMPLE_APPOINTMENT


# ------------------------------------------------------------------
# Status mapping
# ------------------------------------------------------------------


class TestStatusMapping:
    def test_all_statuses_mapped(self) -> None:
        assert len(COVETRUS_STATUS_MAP) == 8

    @pytest.mark.parametrize(
        "covetrus,expected",
        list(COVETRUS_STATUS_MAP.items()),
    )
    def test_covetrus_to_local(self, covetrus: str, expected: str) -> None:
        adapter = _make_adapter()
        raw = {**SAMPLE_APPOINTMENT, "status": covetrus}
        a = adapter._map_appointment(raw)
        assert a.status == expected

    def test_unknown_status_defaults_to_scheduled(self) -> None:
        adapter = _make_adapter()
        raw = {**SAMPLE_APPOINTMENT, "status": "SomeUnknown"}
        a = adapter._map_appointment(raw)
        assert a.status == "scheduled"

    def test_pending_maps_to_scheduled(self) -> None:
        adapter = _make_adapter()
        raw = {**SAMPLE_APPOINTMENT, "status": "Pending"}
        a = adapter._map_appointment(raw)
        assert a.status == "scheduled"


# ------------------------------------------------------------------
# Get appointments
# ------------------------------------------------------------------


class TestGetAppointments:
    @pytest.mark.asyncio
    async def test_get_appointments(self) -> None:
        adapter = _make_adapter()
        adapter._ensure_authenticated = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [SAMPLE_APPOINTMENT]}
        adapter._request = AsyncMock(return_value=mock_response)

        results = await adapter.get_appointments(date(2025, 6, 1), date(2025, 6, 30))
        assert len(results) == 1
        assert results[0].pims_id == "500"

        call_kwargs = adapter._request.call_args
        params = call_kwargs.kwargs.get("params") or call_kwargs[1].get("params")
        assert params["start_date"] == "2025-06-01"
        assert params["end_date"] == "2025-06-30"

    @pytest.mark.asyncio
    async def test_get_appointments_with_pagination(self) -> None:
        adapter = _make_adapter()
        adapter._ensure_authenticated = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        adapter._request = AsyncMock(return_value=mock_response)

        await adapter.get_appointments(
            date(2025, 6, 1), date(2025, 6, 30), limit=50, offset=10
        )

        call_kwargs = adapter._request.call_args
        params = call_kwargs.kwargs.get("params") or call_kwargs[1].get("params")
        assert params["limit"] == 50
        assert params["offset"] == 10

    @pytest.mark.asyncio
    async def test_get_appointments_error(self) -> None:
        adapter = _make_adapter()
        adapter._ensure_authenticated = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 500
        adapter._request = AsyncMock(return_value=mock_response)

        with pytest.raises(PIMSError, match="Failed to fetch appointments"):
            await adapter.get_appointments(date(2025, 6, 1), date(2025, 6, 30))


# ------------------------------------------------------------------
# Providers
# ------------------------------------------------------------------


SAMPLE_PROVIDER = {
    "id": 300,
    "first_name": "Sarah",
    "last_name": "Smith",
    "title": "DVM",
    "role": "Veterinarian",
    "is_active": True,
}


class TestProviderMapping:
    def test_basic_fields(self) -> None:
        adapter = _make_adapter()
        p = adapter._map_provider(SAMPLE_PROVIDER)
        assert p.pims_id == "300"
        assert p.first_name == "Sarah"
        assert p.last_name == "Smith"
        assert p.title == "DVM"
        assert p.is_active is True

    def test_veterinarian_type(self) -> None:
        adapter = _make_adapter()
        p = adapter._map_provider(SAMPLE_PROVIDER)
        assert p.provider_type == "veterinarian"
        assert p.is_veterinarian is True

    def test_staff_type(self) -> None:
        raw = {**SAMPLE_PROVIDER, "role": "Technician"}
        adapter = _make_adapter()
        p = adapter._map_provider(raw)
        assert p.provider_type == "staff"
        assert p.is_veterinarian is False

    def test_raw_data_preserved(self) -> None:
        adapter = _make_adapter()
        p = adapter._map_provider(SAMPLE_PROVIDER)
        assert p.raw_data == SAMPLE_PROVIDER


class TestGetProviders:
    @pytest.mark.asyncio
    async def test_get_providers(self) -> None:
        adapter = _make_adapter()
        adapter._ensure_authenticated = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [SAMPLE_PROVIDER]}
        adapter._request = AsyncMock(return_value=mock_response)

        providers = await adapter.get_providers()
        assert len(providers) == 1
        assert providers[0].first_name == "Sarah"

    @pytest.mark.asyncio
    async def test_get_providers_error(self) -> None:
        adapter = _make_adapter()
        adapter._ensure_authenticated = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 403
        adapter._request = AsyncMock(return_value=mock_response)

        with pytest.raises(PIMSError, match="Failed to fetch providers"):
            await adapter.get_providers()


# ------------------------------------------------------------------
# Available slots
# ------------------------------------------------------------------


class TestAvailableSlots:
    @pytest.mark.asyncio
    async def test_full_day_no_appointments(self) -> None:
        adapter = _make_adapter()
        adapter._ensure_authenticated = AsyncMock()
        adapter.get_appointments = AsyncMock(return_value=[])

        slots = await adapter.get_available_slots("300", date(2025, 6, 15))
        # 9am-5pm, 30min intervals = 16 slots
        assert len(slots) == 16
        assert slots[0].start_time == datetime(2025, 6, 15, 9, 0)
        assert slots[0].end_time == datetime(2025, 6, 15, 9, 30)
        assert slots[-1].start_time == datetime(2025, 6, 15, 16, 30)
        assert slots[-1].end_time == datetime(2025, 6, 15, 17, 0)
        assert all(s.provider_pims_id == "300" for s in slots)

    @pytest.mark.asyncio
    async def test_blocked_by_appointment(self) -> None:
        adapter = _make_adapter()
        adapter._ensure_authenticated = AsyncMock()

        booked = PIMSAppointment(
            pims_id="1",
            provider_pims_id="300",
            start_time=datetime(2025, 6, 15, 10, 0),
            end_time=datetime(2025, 6, 15, 11, 0),
            status="confirmed",
        )
        adapter.get_appointments = AsyncMock(return_value=[booked])

        slots = await adapter.get_available_slots("300", date(2025, 6, 15))
        start_times = [s.start_time for s in slots]
        assert datetime(2025, 6, 15, 10, 0) not in start_times
        assert datetime(2025, 6, 15, 10, 30) not in start_times
        assert datetime(2025, 6, 15, 9, 0) in start_times
        assert datetime(2025, 6, 15, 11, 0) in start_times
        assert len(slots) == 14

    @pytest.mark.asyncio
    async def test_cancelled_appointments_ignored(self) -> None:
        adapter = _make_adapter()
        adapter._ensure_authenticated = AsyncMock()

        cancelled = PIMSAppointment(
            pims_id="1",
            provider_pims_id="300",
            start_time=datetime(2025, 6, 15, 10, 0),
            end_time=datetime(2025, 6, 15, 10, 30),
            status="cancelled",
        )
        adapter.get_appointments = AsyncMock(return_value=[cancelled])

        slots = await adapter.get_available_slots("300", date(2025, 6, 15))
        assert len(slots) == 16

    @pytest.mark.asyncio
    async def test_other_provider_appointments_ignored(self) -> None:
        adapter = _make_adapter()
        adapter._ensure_authenticated = AsyncMock()

        other_provider = PIMSAppointment(
            pims_id="1",
            provider_pims_id="999",
            start_time=datetime(2025, 6, 15, 10, 0),
            end_time=datetime(2025, 6, 15, 10, 30),
            status="confirmed",
        )
        adapter.get_appointments = AsyncMock(return_value=[other_provider])

        slots = await adapter.get_available_slots("300", date(2025, 6, 15))
        assert len(slots) == 16


# ------------------------------------------------------------------
# Write operations
# ------------------------------------------------------------------


class TestWriteOperations:
    @pytest.mark.asyncio
    async def test_create_appointment_success(self) -> None:
        adapter = _make_adapter()
        adapter._ensure_authenticated = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "data": {
                "id": 600,
                "patient_id": 100,
                "provider_id": 300,
                "start_time": "2025-06-15T10:00:00",
                "end_time": "2025-06-15T10:30:00",
                "status": "Scheduled",
                "reason": "Checkup",
            }
        }
        adapter._request = AsyncMock(return_value=mock_response)

        appt = PIMSAppointment(
            pims_id="",
            patient_pims_id="100",
            provider_pims_id="300",
            start_time=datetime(2025, 6, 15, 10, 0),
            end_time=datetime(2025, 6, 15, 10, 30),
            reason="Checkup",
        )
        result = await adapter.create_appointment(appt)
        assert result.pims_id == "600"
        assert result.status == "scheduled"

    @pytest.mark.asyncio
    async def test_update_appointment_success(self) -> None:
        adapter = _make_adapter()
        adapter._ensure_authenticated = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "id": 500,
                "patient_id": 100,
                "provider_id": 300,
                "start_time": "2025-06-15T11:00:00",
                "end_time": "2025-06-15T11:30:00",
                "status": "Confirmed",
                "reason": "Updated reason",
            }
        }
        adapter._request = AsyncMock(return_value=mock_response)

        appt = PIMSAppointment(
            pims_id="500",
            patient_pims_id="100",
            provider_pims_id="300",
            start_time=datetime(2025, 6, 15, 11, 0),
            end_time=datetime(2025, 6, 15, 11, 30),
            status="confirmed",
            reason="Updated reason",
        )
        result = await adapter.update_appointment("500", appt)
        assert result.pims_id == "500"
        assert result.reason == "Updated reason"

    @pytest.mark.asyncio
    async def test_cancel_appointment_success(self) -> None:
        adapter = _make_adapter()
        adapter._ensure_authenticated = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"id": 500, "status": "Cancelled"}}
        adapter._request = AsyncMock(return_value=mock_response)

        result = await adapter.cancel_appointment("500", reason="Client request")
        assert result is True

    @pytest.mark.asyncio
    async def test_create_appointment_error(self) -> None:
        adapter = _make_adapter()
        adapter._ensure_authenticated = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 422
        adapter._request = AsyncMock(return_value=mock_response)

        appt = PIMSAppointment(pims_id="", start_time=datetime.now())
        with pytest.raises(PIMSWriteError, match="Failed to create appointment"):
            await adapter.create_appointment(appt)

    @pytest.mark.asyncio
    async def test_update_appointment_error(self) -> None:
        adapter = _make_adapter()
        adapter._ensure_authenticated = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 500
        adapter._request = AsyncMock(return_value=mock_response)

        appt = PIMSAppointment(pims_id="500")
        with pytest.raises(PIMSWriteError, match="Failed to update appointment"):
            await adapter.update_appointment("500", appt)

    @pytest.mark.asyncio
    async def test_cancel_appointment_error(self) -> None:
        adapter = _make_adapter()
        adapter._ensure_authenticated = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 500
        adapter._request = AsyncMock(return_value=mock_response)

        with pytest.raises(PIMSWriteError, match="Failed to cancel appointment"):
            await adapter.cancel_appointment("500")
