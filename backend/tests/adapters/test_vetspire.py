"""Tests for the Vetspire PIMS adapter."""

import uuid
from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.adapters.pims.errors import PIMSError
from app.adapters.pims.types import PIMSAppointment
from app.adapters.pims.vetspire import (
    LOCAL_TO_VETSPIRE_STATUS,
    VETSPIRE_STATUS_MAP,
    VetspireAdapter,
)

CLINIC_ID = uuid.uuid4()
CREDS = {"api_key": "test-key-123", "location_id": "loc-1"}


def _make_adapter(creds: dict | None = None) -> VetspireAdapter:
    return VetspireAdapter(CLINIC_ID, creds or CREDS)


# ------------------------------------------------------------------
# Initialisation & headers
# ------------------------------------------------------------------


class TestInit:
    def test_default_url(self) -> None:
        adapter = _make_adapter()
        assert adapter._base_url == "https://api2.vetspire.com/graphql"

    def test_custom_url(self) -> None:
        adapter = _make_adapter(
            {"api_key": "k", "base_url": "https://custom.example.com/graphql"}
        )
        assert adapter._base_url == "https://custom.example.com/graphql"

    def test_authorization_header(self) -> None:
        adapter = _make_adapter()
        headers = adapter._get_headers()
        assert headers["Authorization"] == "test-key-123"
        assert "X-API-Key" not in headers

    def test_location_id_stored(self) -> None:
        adapter = _make_adapter()
        assert adapter._location_id == "loc-1"


# ------------------------------------------------------------------
# Authentication
# ------------------------------------------------------------------


class TestAuthenticate:
    @pytest.mark.asyncio
    async def test_authenticate_success(self) -> None:
        adapter = _make_adapter()
        adapter._graphql = AsyncMock(return_value={"viewer": {"id": "42"}})
        assert await adapter.authenticate() is True

    @pytest.mark.asyncio
    async def test_authenticate_failure_empty_viewer(self) -> None:
        adapter = _make_adapter()
        adapter._graphql = AsyncMock(return_value={"viewer": None})
        assert await adapter.authenticate() is False

    @pytest.mark.asyncio
    async def test_authenticate_failure_exception(self) -> None:
        adapter = _make_adapter()
        adapter._graphql = AsyncMock(side_effect=PIMSError("fail", "vetspire"))
        assert await adapter.authenticate() is False


# ------------------------------------------------------------------
# Test connection
# ------------------------------------------------------------------


class TestConnection:
    @pytest.mark.asyncio
    async def test_test_connection_success(self) -> None:
        adapter = _make_adapter()
        adapter.authenticate = AsyncMock(return_value=True)
        adapter.get_locations = AsyncMock(
            return_value=[{"id": "1", "name": "Main Clinic"}]
        )

        result = await adapter.test_connection()
        assert result["connected"] is True
        assert result["pims_type"] == "vetspire"
        assert len(result["locations"]) == 1

    @pytest.mark.asyncio
    async def test_test_connection_auth_failure(self) -> None:
        adapter = _make_adapter()
        adapter.authenticate = AsyncMock(return_value=False)

        result = await adapter.test_connection()
        assert result["connected"] is False


# ------------------------------------------------------------------
# Patient mapping
# ------------------------------------------------------------------


SAMPLE_PATIENT = {
    "id": "100",
    "name": "Buddy",
    "species": "Canine",
    "breed": "Labrador",
    "color": "Golden",
    "sex": "Male",
    "birthDate": "2020-03-15",
    "microchip": "chip-999",
    "isActive": True,
    "isDeceased": False,
    "notes": "Friendly dog",
    "clientId": "200",
    "client": {
        "id": "200",
        "givenName": "Jane",
        "familyName": "Doe",
        "email": "jane@example.com",
        "phoneNumbers": [
            {"id": "p1", "number": "555-1234", "type": "MOBILE"},
        ],
        "addresses": [
            {
                "id": "a1",
                "line1": "123 Main St",
                "line2": "",
                "city": "Springfield",
                "state": "IL",
                "postalCode": "62704",
            }
        ],
    },
    "allergies": [{"id": "al1", "name": "Penicillin"}, {"id": "al2", "name": "Latex"}],
    "latestWeight": {"weight": 30.5, "unit": "kg", "insertedAt": "2025-01-01"},
    "insertedAt": "2024-01-01",
    "updatedAt": "2025-06-01",
}


class TestPatientMapping:
    def test_basic_fields(self) -> None:
        adapter = _make_adapter()
        p = adapter._map_patient(SAMPLE_PATIENT)
        assert p.pims_id == "100"
        assert p.name == "Buddy"
        assert p.species == "canine"
        assert p.breed == "Labrador"
        assert p.microchip_id == "chip-999"
        assert p.is_active is True
        assert p.is_deceased is False
        assert p.notes == "Friendly dog"

    def test_client_mapping(self) -> None:
        adapter = _make_adapter()
        p = adapter._map_patient(SAMPLE_PATIENT)
        assert p.owner_first_name == "Jane"
        assert p.owner_last_name == "Doe"
        assert p.owner_email == "jane@example.com"
        assert p.owner_phone == "555-1234"
        assert p.client_pims_id == "200"

    def test_owner_address(self) -> None:
        adapter = _make_adapter()
        p = adapter._map_patient(SAMPLE_PATIENT)
        assert "123 Main St" in p.owner_address
        assert "Springfield" in p.owner_address
        assert "IL" in p.owner_address

    def test_birth_date(self) -> None:
        adapter = _make_adapter()
        p = adapter._map_patient(SAMPLE_PATIENT)
        assert p.date_of_birth == datetime(2020, 3, 15)

    def test_allergies_joined(self) -> None:
        adapter = _make_adapter()
        p = adapter._map_patient(SAMPLE_PATIENT)
        assert p.allergies == "Penicillin, Latex"

    def test_weight(self) -> None:
        adapter = _make_adapter()
        p = adapter._map_patient(SAMPLE_PATIENT)
        assert p.weight_kg == 30.5

    def test_missing_client(self) -> None:
        raw = {**SAMPLE_PATIENT, "client": None, "clientId": None}
        adapter = _make_adapter()
        p = adapter._map_patient(raw)
        assert p.owner_first_name is None
        assert p.owner_phone is None
        assert p.client_pims_id is None

    def test_empty_allergies(self) -> None:
        raw = {**SAMPLE_PATIENT, "allergies": []}
        adapter = _make_adapter()
        p = adapter._map_patient(raw)
        assert p.allergies is None


class TestGetPatients:
    @pytest.mark.asyncio
    async def test_get_patients(self) -> None:
        adapter = _make_adapter()
        adapter._graphql = AsyncMock(return_value={"patients": [SAMPLE_PATIENT]})

        patients = await adapter.get_patients(limit=10)
        assert len(patients) == 1
        assert patients[0].name == "Buddy"

        # Verify variables passed
        call_vars = adapter._graphql.call_args[0][1]
        assert call_vars["limit"] == 10

    @pytest.mark.asyncio
    async def test_get_patients_with_since(self) -> None:
        adapter = _make_adapter()
        adapter._graphql = AsyncMock(return_value={"patients": []})
        since = datetime(2025, 1, 1)
        await adapter.get_patients(since=since)

        call_vars = adapter._graphql.call_args[0][1]
        assert "updatedAtStart" in call_vars

    @pytest.mark.asyncio
    async def test_get_patient_by_id(self) -> None:
        adapter = _make_adapter()
        adapter._graphql = AsyncMock(return_value={"patient": SAMPLE_PATIENT})

        patient = await adapter.get_patient_by_id("100")
        assert patient is not None
        assert patient.pims_id == "100"

    @pytest.mark.asyncio
    async def test_get_patient_by_id_not_found(self) -> None:
        adapter = _make_adapter()
        adapter._graphql = AsyncMock(return_value={"patient": None})

        patient = await adapter.get_patient_by_id("999")
        assert patient is None


# ------------------------------------------------------------------
# Appointment mapping
# ------------------------------------------------------------------


SAMPLE_APPOINTMENT = {
    "id": "500",
    "patientId": "100",
    "providerId": "300",
    "start": "2025-06-15T10:00:00",
    "duration": 30,
    "status": "CONFIRMED",
    "reason": "Annual checkup",
    "note": "Bring vaccination records",
    "type": {"id": "t1", "name": "Wellness Exam"},
    "patient": {"id": "100", "name": "Buddy"},
    "provider": {"id": "300", "givenName": "Dr", "familyName": "Smith"},
    "location": {"id": "loc-1", "name": "Main Clinic"},
    "isConfirmed": True,
    "confirmedAt": "2025-06-14T09:00:00",
    "checkedInAt": None,
    "completedAt": None,
    "insertedAt": "2025-06-01",
    "updatedAt": "2025-06-14",
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
        assert a.is_confirmed is True

    def test_start_and_computed_end(self) -> None:
        adapter = _make_adapter()
        a = adapter._map_appointment(SAMPLE_APPOINTMENT)
        assert a.start_time == datetime(2025, 6, 15, 10, 0, 0)
        assert a.end_time == datetime(2025, 6, 15, 10, 30, 0)
        assert a.duration_minutes == 30

    def test_appointment_type_from_object(self) -> None:
        adapter = _make_adapter()
        a = adapter._map_appointment(SAMPLE_APPOINTMENT)
        assert a.appointment_type == "Wellness Exam"
        assert a.appointment_type_id == "t1"

    def test_location_mapping(self) -> None:
        adapter = _make_adapter()
        a = adapter._map_appointment(SAMPLE_APPOINTMENT)
        assert a.location_pims_id == "loc-1"

    def test_status_normalization(self) -> None:
        adapter = _make_adapter()
        a = adapter._map_appointment(SAMPLE_APPOINTMENT)
        assert a.status == "confirmed"

    def test_no_duration(self) -> None:
        raw = {**SAMPLE_APPOINTMENT, "duration": None}
        adapter = _make_adapter()
        a = adapter._map_appointment(raw)
        assert a.end_time is None
        assert a.duration_minutes is None


# ------------------------------------------------------------------
# Status mapping (all 15 statuses)
# ------------------------------------------------------------------


class TestStatusMapping:
    def test_all_vetspire_statuses_mapped(self) -> None:
        assert len(VETSPIRE_STATUS_MAP) == 15

    @pytest.mark.parametrize(
        "vetspire,expected",
        list(VETSPIRE_STATUS_MAP.items()),
    )
    def test_vetspire_to_local(self, vetspire: str, expected: str) -> None:
        adapter = _make_adapter()
        raw = {**SAMPLE_APPOINTMENT, "status": vetspire}
        a = adapter._map_appointment(raw)
        assert a.status == expected

    def test_round_trip(self) -> None:
        for vetspire, local in VETSPIRE_STATUS_MAP.items():
            assert LOCAL_TO_VETSPIRE_STATUS[local] == vetspire


# ------------------------------------------------------------------
# Appointment CRUD
# ------------------------------------------------------------------


class TestAppointmentCRUD:
    @pytest.mark.asyncio
    async def test_get_appointments(self) -> None:
        adapter = _make_adapter()
        adapter._graphql = AsyncMock(
            return_value={"appointments": [SAMPLE_APPOINTMENT]}
        )

        results = await adapter.get_appointments(date(2025, 6, 1), date(2025, 6, 30))
        assert len(results) == 1
        assert results[0].pims_id == "500"

        call_vars = adapter._graphql.call_args[0][1]
        assert "start" in call_vars
        assert "end" in call_vars
        assert call_vars["locationId"] == "loc-1"

    @pytest.mark.asyncio
    async def test_create_appointment(self) -> None:
        adapter = _make_adapter()
        adapter._graphql = AsyncMock(
            return_value={"createAppointment": SAMPLE_APPOINTMENT}
        )

        appt = PIMSAppointment(
            pims_id="",
            patient_pims_id="100",
            provider_pims_id="300",
            start_time=datetime(2025, 6, 15, 10, 0),
            end_time=datetime(2025, 6, 15, 10, 30),
            reason="Checkup",
        )
        result = await adapter.create_appointment(appt)
        assert result.pims_id == "500"

        # Verify duration was computed
        call_input = adapter._graphql.call_args[0][1]["input"]
        assert call_input["duration"] == 30
        assert call_input["locationId"] == "loc-1"

    @pytest.mark.asyncio
    async def test_create_appointment_with_duration_minutes(self) -> None:
        adapter = _make_adapter()
        adapter._graphql = AsyncMock(
            return_value={"createAppointment": SAMPLE_APPOINTMENT}
        )

        appt = PIMSAppointment(
            pims_id="",
            patient_pims_id="100",
            start_time=datetime(2025, 6, 15, 10, 0),
            duration_minutes=45,
        )
        result = await adapter.create_appointment(appt)
        call_input = adapter._graphql.call_args[0][1]["input"]
        assert call_input["duration"] == 45
        assert result.pims_id == "500"

    @pytest.mark.asyncio
    async def test_create_appointment_empty_response_raises(self) -> None:
        adapter = _make_adapter()
        adapter._graphql = AsyncMock(return_value={"createAppointment": None})

        appt = PIMSAppointment(pims_id="", start_time=datetime.now())
        with pytest.raises(PIMSError, match="empty response"):
            await adapter.create_appointment(appt)

    @pytest.mark.asyncio
    async def test_update_appointment(self) -> None:
        adapter = _make_adapter()
        adapter._graphql = AsyncMock(
            return_value={"updateAppointment": SAMPLE_APPOINTMENT}
        )

        appt = PIMSAppointment(
            pims_id="500",
            status="cancelled",
            reason="Owner request",
        )
        result = await adapter.update_appointment("500", appt)
        assert result.pims_id == "500"

        call_input = adapter._graphql.call_args[0][1]["input"]
        assert call_input["status"] == "CANCELLED"
        assert call_input["reason"] == "Owner request"

    @pytest.mark.asyncio
    async def test_cancel_appointment_simple(self) -> None:
        adapter = _make_adapter()
        adapter._graphql = AsyncMock(return_value={"deleteAppointment": {"id": "500"}})

        result = await adapter.cancel_appointment("500")
        assert result is True
        # Only deleteAppointment called (no reason)
        assert adapter._graphql.call_count == 1

    @pytest.mark.asyncio
    async def test_cancel_appointment_with_reason(self) -> None:
        adapter = _make_adapter()
        adapter._graphql = AsyncMock(
            side_effect=[
                {"updateAppointment": {"id": "500"}},  # status update
                {"deleteAppointment": {"id": "500"}},  # delete
            ]
        )

        result = await adapter.cancel_appointment("500", reason="No longer needed")
        assert result is True
        assert adapter._graphql.call_count == 2


# ------------------------------------------------------------------
# Provider mapping
# ------------------------------------------------------------------


SAMPLE_PROVIDER = {
    "id": "300",
    "givenName": "Sarah",
    "familyName": "Smith",
    "name": "Dr. Sarah Smith",
    "title": "DVM",
    "suffix": "PhD",
    "email": "sarah@clinic.com",
    "isActive": True,
    "isVeterinarian": True,
    "isGroomer": False,
    "profileImageUrl": "https://example.com/photo.jpg",
    "departments": [
        {"id": "d1", "name": "Surgery"},
        {"id": "d2", "name": "Internal Medicine"},
    ],
    "defaultLocationId": "loc-1",
    "insertedAt": "2024-01-01",
    "updatedAt": "2025-01-01",
}


class TestProviderMapping:
    def test_basic_fields(self) -> None:
        adapter = _make_adapter()
        p = adapter._map_provider(SAMPLE_PROVIDER)
        assert p.pims_id == "300"
        assert p.first_name == "Sarah"
        assert p.last_name == "Smith"
        assert p.title == "DVM"
        assert p.suffix == "PhD"
        assert p.email == "sarah@clinic.com"
        assert p.is_active is True

    def test_veterinarian_type(self) -> None:
        adapter = _make_adapter()
        p = adapter._map_provider(SAMPLE_PROVIDER)
        assert p.provider_type == "veterinarian"
        assert p.is_veterinarian is True

    def test_staff_type(self) -> None:
        raw = {**SAMPLE_PROVIDER, "isVeterinarian": False}
        adapter = _make_adapter()
        p = adapter._map_provider(raw)
        assert p.provider_type == "staff"
        assert p.is_veterinarian is False

    def test_departments_as_specialties(self) -> None:
        adapter = _make_adapter()
        p = adapter._map_provider(SAMPLE_PROVIDER)
        assert p.specialties == ["Surgery", "Internal Medicine"]

    def test_profile_and_location(self) -> None:
        adapter = _make_adapter()
        p = adapter._map_provider(SAMPLE_PROVIDER)
        assert p.profile_image_url == "https://example.com/photo.jpg"
        assert p.default_location_id == "loc-1"


class TestGetProviders:
    @pytest.mark.asyncio
    async def test_get_providers(self) -> None:
        adapter = _make_adapter()
        adapter._graphql = AsyncMock(return_value={"providers": [SAMPLE_PROVIDER]})

        providers = await adapter.get_providers()
        assert len(providers) == 1
        assert providers[0].first_name == "Sarah"

        call_vars = adapter._graphql.call_args[0][1]
        assert call_vars["onlyActive"] is True
        assert call_vars["locationId"] == "loc-1"


# ------------------------------------------------------------------
# Available slots
# ------------------------------------------------------------------


class TestAvailableSlots:
    @pytest.mark.asyncio
    async def test_get_available_slots(self) -> None:
        adapter = _make_adapter()
        adapter._graphql = AsyncMock(
            return_value={
                "availableTimes": [
                    {
                        "id": "s1",
                        "date": "2025-06-15",
                        "time": "10:00:00",
                        "providerId": "300",
                        "provider": {
                            "id": "300",
                            "givenName": "Dr",
                            "familyName": "Smith",
                        },
                        "scheduleId": "sch1",
                    },
                    {
                        "id": "s2",
                        "date": "2025-06-15",
                        "time": "10:30:00",
                        "providerId": "300",
                        "provider": {
                            "id": "300",
                            "givenName": "Dr",
                            "familyName": "Smith",
                        },
                        "scheduleId": "sch1",
                    },
                ]
            }
        )

        slots = await adapter.get_available_slots(
            "300",
            date(2025, 6, 15),
            appointment_type_id="t1",
            location_id="loc-1",
        )
        assert len(slots) == 2
        assert slots[0].start_time == datetime(2025, 6, 15, 10, 0)
        assert slots[0].end_time == datetime(2025, 6, 15, 10, 30)
        assert slots[0].provider_pims_id == "300"
        assert slots[0].schedule_id == "sch1"
        assert slots[0].slot_id == "s1"

    @pytest.mark.asyncio
    async def test_missing_appointment_type_returns_empty(self) -> None:
        adapter = _make_adapter()
        slots = await adapter.get_available_slots("300", date(2025, 6, 15))
        assert slots == []

    @pytest.mark.asyncio
    async def test_filters_by_provider(self) -> None:
        adapter = _make_adapter()
        adapter._graphql = AsyncMock(
            return_value={
                "availableTimes": [
                    {
                        "id": "s1",
                        "date": "2025-06-15",
                        "time": "10:00:00",
                        "providerId": "300",
                        "provider": None,
                        "scheduleId": None,
                    },
                    {
                        "id": "s2",
                        "date": "2025-06-15",
                        "time": "11:00:00",
                        "providerId": "400",
                        "provider": None,
                        "scheduleId": None,
                    },
                ]
            }
        )

        slots = await adapter.get_available_slots(
            "300",
            date(2025, 6, 15),
            appointment_type_id="t1",
        )
        assert len(slots) == 1
        assert slots[0].provider_pims_id == "300"


# ------------------------------------------------------------------
# Helper queries
# ------------------------------------------------------------------


class TestHelperQueries:
    @pytest.mark.asyncio
    async def test_get_locations(self) -> None:
        adapter = _make_adapter()
        adapter._graphql = AsyncMock(
            return_value={
                "locations": [
                    {"id": "1", "name": "Main"},
                    {"id": "2", "name": "Branch"},
                ]
            }
        )
        locs = await adapter.get_locations()
        assert len(locs) == 2

    @pytest.mark.asyncio
    async def test_get_appointment_types_with_location(self) -> None:
        adapter = _make_adapter()
        adapter._graphql = AsyncMock(
            return_value={
                "locationAppointmentTypes": [{"id": "t1", "name": "Wellness"}]
            }
        )
        types = await adapter.get_appointment_types()
        assert types[0]["name"] == "Wellness"

    @pytest.mark.asyncio
    async def test_get_appointment_types_global(self) -> None:
        adapter = _make_adapter({"api_key": "k"})  # no location_id
        adapter._graphql = AsyncMock(
            return_value={"appointmentTypes": [{"id": "t1", "name": "Surgery"}]}
        )
        types = await adapter.get_appointment_types()
        assert types[0]["name"] == "Surgery"

    @pytest.mark.asyncio
    async def test_search_clients(self) -> None:
        adapter = _make_adapter()
        adapter._graphql = AsyncMock(
            return_value={
                "searchAccounts": [
                    {
                        "id": "1",
                        "givenName": "Jane",
                        "familyName": "Doe",
                        "email": "j@e.com",
                        "phoneNumbers": [],
                    },
                ]
            }
        )
        results = await adapter.search_clients("Jane")
        assert len(results) == 1
        assert results[0]["givenName"] == "Jane"


# ------------------------------------------------------------------
# GraphQL error handling
# ------------------------------------------------------------------


class TestGraphQLErrors:
    @pytest.mark.asyncio
    async def test_graphql_error_in_response(self) -> None:
        adapter = _make_adapter()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"errors": [{"message": "Field not found"}]}
        adapter._request = AsyncMock(return_value=mock_response)

        with pytest.raises(PIMSError, match="Field not found"):
            await adapter._graphql("{ bad }")

    @pytest.mark.asyncio
    async def test_graphql_non_200_status(self) -> None:
        adapter = _make_adapter()

        mock_response = MagicMock()
        mock_response.status_code = 500
        adapter._request = AsyncMock(return_value=mock_response)

        with pytest.raises(PIMSError, match="500"):
            await adapter._graphql("{ bad }")
