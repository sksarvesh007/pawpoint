"""Vetspire PIMS adapter.

Implements the IPIMSAdapter interface using Vetspire's GraphQL API.
Uses Authorization header authentication against api2.vetspire.com.

API reference: https://developer.vetspire.com/
"""

from datetime import date, datetime, timedelta
from typing import Any
from uuid import UUID

from loguru import logger

from app.adapters.pims.base import IPIMSAdapter
from app.adapters.pims.errors import PIMSError
from app.adapters.pims.types import (
    PIMSAppointment,
    PIMSPatient,
    PIMSProvider,
    PIMSTimeSlot,
)

# Vetspire AppointmentStatus enum → normalized status
VETSPIRE_STATUS_MAP: dict[str, str] = {
    "PENDING": "scheduled",
    "CONFIRMED": "confirmed",
    "CHECKED_IN": "checked_in",
    "ADMITTED": "admitted",
    "INPROGRESS": "in_progress",
    "CHECKING_OUT": "checking_out",
    "CHECKED_OUT": "checked_out",
    "COMPLETED": "completed",
    "CANCELLED": "cancelled",
    "NOSHOW": "no_show",
    "WAITLIST": "waitlist",
    "DAYCARE": "daycare",
    "MEDBOARD": "medical_board",
    "PLANNED": "planned",
    "READY_FOR_DISCHARGE": "ready_for_discharge",
}
LOCAL_TO_VETSPIRE_STATUS: dict[str, str] = {
    v: k for k, v in VETSPIRE_STATUS_MAP.items()
}

# Default appointment duration when not known (minutes)
_DEFAULT_SLOT_DURATION = 30


class VetspireAdapter(IPIMSAdapter):
    """Vetspire PIMS adapter using GraphQL API."""

    def __init__(
        self,
        clinic_id: UUID,
        credentials: dict,
        settings: dict | None = None,
    ) -> None:
        super().__init__(clinic_id, credentials, settings)
        self._base_url = credentials.get(
            "base_url", "https://api2.vetspire.com/graphql"
        )
        self._api_key = credentials.get("api_key", "")
        self._location_id: str | None = credentials.get("location_id")

    def _get_headers(self) -> dict[str, str]:
        """Get authenticated request headers."""
        return {
            "Authorization": self._api_key,
            "Content-Type": "application/json",
        }

    async def _graphql(
        self, query: str, variables: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Execute a GraphQL query against Vetspire."""
        payload: dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables

        response = await self._request(
            "POST",
            self._base_url,
            headers=self._get_headers(),
            json=payload,
        )

        if response.status_code != 200:
            raise PIMSError(
                f"Vetspire GraphQL error: {response.status_code}",
                pims_type="vetspire",
            )

        data = response.json()
        if "errors" in data:
            errors = data["errors"]
            error_msg = (
                errors[0].get("message", "Unknown error") if errors else "Unknown error"
            )
            raise PIMSError(
                f"Vetspire GraphQL error: {error_msg}",
                pims_type="vetspire",
            )

        return data.get("data", {})

    # ------------------------------------------------------------------
    # Authentication & connection
    # ------------------------------------------------------------------

    async def authenticate(self) -> bool:
        """Verify API key by querying the authenticated viewer."""
        try:
            result = await self._graphql("{ viewer { id } }")
            return bool(result.get("viewer"))
        except Exception as e:
            logger.error("Vetspire auth check failed: {}", e)
            return False

    async def test_connection(self) -> dict[str, Any]:
        """Test connection and return location info."""
        try:
            is_auth = await self.authenticate()
            if not is_auth:
                return {
                    "connected": False,
                    "message": "Vetspire authentication failed",
                    "pims_type": "vetspire",
                }

            locations = await self.get_locations()
            return {
                "connected": True,
                "message": "Successfully connected to Vetspire",
                "pims_type": "vetspire",
                "locations": locations,
            }
        except Exception as e:
            return {
                "connected": False,
                "message": f"Connection failed: {e}",
                "pims_type": "vetspire",
            }

    # ------------------------------------------------------------------
    # Patients
    # ------------------------------------------------------------------

    _PATIENT_FIELDS = """
        id
        name
        species
        breed
        color
        sex
        birthDate
        microchip
        isActive
        isDeceased
        notes
        clientId
        client {
            id
            givenName
            familyName
            email
            phoneNumbers { id number type }
            addresses { id line1 line2 city state postalCode }
        }
        allergies { id name }
        latestWeight { weight unit insertedAt }
        insertedAt
        updatedAt
    """

    async def get_patients(
        self,
        since: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[PIMSPatient]:
        """Fetch patients from Vetspire via GraphQL."""
        query = f"""
        query GetPatients(
            $limit: Int,
            $offset: Int,
            $updatedAtStart: NaiveDateTime,
            $updatedAtEnd: NaiveDateTime,
            $filters: PatientFilters
        ) {{
            patients(
                limit: $limit,
                offset: $offset,
                updatedAtStart: $updatedAtStart,
                updatedAtEnd: $updatedAtEnd,
                filters: $filters
            ) {{
                {self._PATIENT_FIELDS}
            }}
        }}
        """
        variables: dict[str, Any] = {"limit": limit, "offset": offset}
        if since:
            variables["updatedAtStart"] = since.isoformat()

        data = await self._graphql(query, variables)
        patients = data.get("patients", [])
        return [self._map_patient(p) for p in patients]

    async def get_patient_by_id(self, pims_id: str) -> PIMSPatient | None:
        """Fetch a single patient from Vetspire."""
        query = f"""
        query GetPatient($id: ID!) {{
            patient(id: $id) {{
                {self._PATIENT_FIELDS}
            }}
        }}
        """
        data = await self._graphql(query, {"id": pims_id})
        patient = data.get("patient")
        if not patient:
            return None
        return self._map_patient(patient)

    # ------------------------------------------------------------------
    # Appointments
    # ------------------------------------------------------------------

    _APPOINTMENT_FIELDS = """
        id
        patientId
        providerId
        start
        duration
        status
        reason
        note
        type { id name }
        patient { id name }
        provider { id givenName familyName }
        location { id name }
        isConfirmed
        confirmedAt
        checkedInAt
        completedAt
        insertedAt
        updatedAt
    """

    async def get_appointments(
        self,
        start_date: date,
        end_date: date,
        limit: int = 100,
        offset: int = 0,
    ) -> list[PIMSAppointment]:
        """Fetch appointments from Vetspire."""
        query = f"""
        query GetAppointments(
            $start: DateTime,
            $end: DateTime,
            $limit: Int,
            $offset: Int,
            $statuses: [AppointmentStatus],
            $providerId: ID,
            $locationId: ID
        ) {{
            appointments(
                start: $start,
                end: $end,
                limit: $limit,
                offset: $offset,
                statuses: $statuses,
                providerId: $providerId,
                locationId: $locationId
            ) {{
                {self._APPOINTMENT_FIELDS}
            }}
        }}
        """
        variables: dict[str, Any] = {
            "start": datetime.combine(start_date, datetime.min.time()).isoformat(),
            "end": datetime.combine(end_date, datetime.max.time()).isoformat(),
            "limit": limit,
            "offset": offset,
        }
        if self._location_id:
            variables["locationId"] = self._location_id

        data = await self._graphql(query, variables)
        appointments = data.get("appointments", [])
        return [self._map_appointment(a) for a in appointments]

    async def create_appointment(self, data: PIMSAppointment) -> PIMSAppointment:
        """Create an appointment in Vetspire."""
        mutation = f"""
        mutation CreateAppointment($input: AppointmentInput!) {{
            createAppointment(input: $input) {{
                {self._APPOINTMENT_FIELDS}
            }}
        }}
        """
        # Compute duration in minutes from start/end
        duration: int | None = None
        if data.duration_minutes:
            duration = data.duration_minutes
        elif data.start_time and data.end_time:
            delta = data.end_time - data.start_time
            duration = int(delta.total_seconds() / 60)

        input_data: dict[str, Any] = {
            "patientId": data.patient_pims_id,
            "providerId": data.provider_pims_id,
            "start": data.start_time.isoformat() if data.start_time else None,
            "duration": duration,
            "reason": data.reason or "",
            "note": data.notes or "",
            "status": LOCAL_TO_VETSPIRE_STATUS.get(
                data.status or "scheduled", "PENDING"
            ),
        }
        if data.appointment_type_id:
            input_data["appointmentTypeId"] = data.appointment_type_id
        if data.location_pims_id or self._location_id:
            input_data["locationId"] = data.location_pims_id or self._location_id

        result = await self._graphql(mutation, {"input": input_data})
        created = result.get("createAppointment")
        if not created:
            raise PIMSError(
                "Vetspire returned empty response for appointment creation",
                pims_type="vetspire",
            )
        return self._map_appointment(created)

    async def update_appointment(
        self, pims_id: str, data: PIMSAppointment
    ) -> PIMSAppointment:
        """Update an appointment in Vetspire."""
        mutation = f"""
        mutation UpdateAppointment($id: ID!, $input: AppointmentInput!) {{
            updateAppointment(id: $id, input: $input) {{
                {self._APPOINTMENT_FIELDS}
            }}
        }}
        """
        input_data: dict[str, Any] = {}
        if data.start_time:
            input_data["start"] = data.start_time.isoformat()
        if data.duration_minutes:
            input_data["duration"] = data.duration_minutes
        elif data.start_time and data.end_time:
            delta = data.end_time - data.start_time
            input_data["duration"] = int(delta.total_seconds() / 60)
        if data.status:
            input_data["status"] = LOCAL_TO_VETSPIRE_STATUS.get(
                data.status, data.status.upper()
            )
        if data.reason:
            input_data["reason"] = data.reason
        if data.notes:
            input_data["note"] = data.notes
        if data.appointment_type_id:
            input_data["appointmentTypeId"] = data.appointment_type_id
        if data.provider_pims_id:
            input_data["providerId"] = data.provider_pims_id

        result = await self._graphql(mutation, {"id": pims_id, "input": input_data})
        updated = result.get("updateAppointment")
        if not updated:
            raise PIMSError(
                "Vetspire returned empty response for appointment update",
                pims_type="vetspire",
            )
        return self._map_appointment(updated)

    async def cancel_appointment(self, pims_id: str, reason: str | None = None) -> bool:
        """Cancel an appointment in Vetspire.

        Vetspire uses deleteAppointment(id) — there is no cancel-with-reason.
        If a reason is provided we first update the status to CANCELLED with
        the reason stored in the note, then delete.
        """
        if reason:
            try:
                update_mutation = """
                mutation UpdateAppointment($id: ID!, $input: AppointmentInput!) {
                    updateAppointment(id: $id, input: $input) { id }
                }
                """
                await self._graphql(
                    update_mutation,
                    {
                        "id": pims_id,
                        "input": {"status": "CANCELLED", "note": reason},
                    },
                )
            except PIMSError:
                logger.warning(
                    "Failed to set CANCELLED status before delete for {}",
                    pims_id,
                )

        mutation = """
        mutation DeleteAppointment($id: ID!) {
            deleteAppointment(id: $id) { id }
        }
        """
        result = await self._graphql(mutation, {"id": pims_id})
        return bool(result.get("deleteAppointment"))

    # ------------------------------------------------------------------
    # Providers
    # ------------------------------------------------------------------

    async def get_providers(self) -> list[PIMSProvider]:
        """Fetch providers from Vetspire."""
        query = """
        query GetProviders($locationId: ID, $onlyActive: Boolean) {
            providers(locationId: $locationId, onlyActive: $onlyActive) {
                id
                givenName
                familyName
                name
                title
                suffix
                email
                isActive
                isVeterinarian
                isGroomer
                profileImageUrl
                departments { id name }
                defaultLocationId
                insertedAt
                updatedAt
            }
        }
        """
        variables: dict[str, Any] = {"onlyActive": True}
        if self._location_id:
            variables["locationId"] = self._location_id

        data = await self._graphql(query, variables)
        providers = data.get("providers", [])
        return [self._map_provider(p) for p in providers]

    # ------------------------------------------------------------------
    # Available slots
    # ------------------------------------------------------------------

    async def get_available_slots(
        self,
        provider_pims_id: str,
        target_date: date,
        *,
        appointment_type_id: str | None = None,
        location_id: str | None = None,
    ) -> list[PIMSTimeSlot]:
        """Get available time slots from Vetspire.

        Vetspire's ``availableTimes`` requires ``appointmentTypeId``,
        ``date``, and ``locationId``. If not provided, falls back to
        adapter-level ``location_id``.
        """
        effective_location = location_id or self._location_id
        if not appointment_type_id or not effective_location:
            logger.warning(
                "get_available_slots requires appointment_type_id and location_id "
                "for Vetspire; returning empty list"
            )
            return []

        query = """
        query GetAvailableTimes(
            $appointmentTypeId: ID!,
            $date: Date!,
            $locationId: ID!
        ) {
            availableTimes(
                appointmentTypeId: $appointmentTypeId,
                date: $date,
                locationId: $locationId
            ) {
                id
                date
                time
                providerId
                provider { id givenName familyName }
                scheduleId
            }
        }
        """
        data = await self._graphql(
            query,
            {
                "appointmentTypeId": appointment_type_id,
                "date": target_date.isoformat(),
                "locationId": effective_location,
            },
        )
        raw_slots = data.get("availableTimes", [])

        slots: list[PIMSTimeSlot] = []
        for s in raw_slots:
            slot_provider = s.get("providerId")
            # Filter to requested provider if specified
            if provider_pims_id and slot_provider != provider_pims_id:
                continue

            start = self._parse_slot_datetime(s.get("date"), s.get("time"))
            if not start:
                continue

            slots.append(
                PIMSTimeSlot(
                    start_time=start,
                    end_time=start + timedelta(minutes=_DEFAULT_SLOT_DURATION),
                    provider_pims_id=slot_provider,
                    schedule_id=s.get("scheduleId"),
                    slot_id=s.get("id"),
                )
            )

        return slots

    # ------------------------------------------------------------------
    # Helper queries (not part of the abstract interface)
    # ------------------------------------------------------------------

    async def get_appointment_types(
        self, location_id: str | None = None
    ) -> list[dict[str, Any]]:
        """Fetch appointment types from Vetspire."""
        effective_location = location_id or self._location_id
        if effective_location:
            query = """
            query GetLocationAppointmentTypes($locationId: ID!) {
                locationAppointmentTypes(locationId: $locationId) {
                    id name
                }
            }
            """
            data = await self._graphql(query, {"locationId": effective_location})
            return data.get("locationAppointmentTypes", [])

        query = "{ appointmentTypes { id name } }"
        data = await self._graphql(query)
        return data.get("appointmentTypes", [])

    async def get_locations(self) -> list[dict[str, Any]]:
        """Fetch locations for the organization."""
        query = "{ locations { id name } }"
        data = await self._graphql(query)
        return data.get("locations", [])

    async def search_clients(
        self, query_str: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        """Search for client accounts by name/phone/email."""
        query = """
        query SearchAccounts($query: String!) {
            searchAccounts(query: $query) {
                id givenName familyName email
                phoneNumbers { number type }
            }
        }
        """
        data = await self._graphql(query, {"query": query_str})
        results = data.get("searchAccounts", [])
        return results[:limit]

    # ------------------------------------------------------------------
    # Mapping helpers
    # ------------------------------------------------------------------

    def _map_patient(self, raw: dict[str, Any]) -> PIMSPatient:
        """Map Vetspire patient to PIMSPatient."""
        client: dict[str, Any] = raw.get("client") or {}

        # Build owner address from first address object
        owner_address: str | None = None
        addresses = client.get("addresses") or []
        if addresses:
            addr = addresses[0]
            parts = [
                addr.get("line1", ""),
                addr.get("line2", ""),
                addr.get("city", ""),
                addr.get("state", ""),
                addr.get("postalCode", ""),
            ]
            owner_address = ", ".join(p for p in parts if p)

        # First phone number
        phone_numbers = client.get("phoneNumbers") or []
        owner_phone = phone_numbers[0]["number"] if phone_numbers else None

        # Allergies → comma-separated string
        allergy_list = raw.get("allergies") or []
        allergies = ", ".join(a.get("name", "") for a in allergy_list) or None

        # Latest weight
        weight: float | None = None
        latest_weight = raw.get("latestWeight")
        if latest_weight and latest_weight.get("weight") is not None:
            weight = float(latest_weight["weight"])

        return PIMSPatient(
            pims_id=str(raw.get("id", "")),
            name=raw.get("name", "Unknown"),
            species=(raw.get("species") or "other").lower(),
            breed=raw.get("breed"),
            color=raw.get("color"),
            sex=(raw.get("sex") or "unknown").lower(),
            date_of_birth=self._parse_datetime(raw.get("birthDate")),
            weight_kg=weight,
            microchip_id=raw.get("microchip"),
            is_deceased=raw.get("isDeceased", False),
            owner_first_name=client.get("givenName"),
            owner_last_name=client.get("familyName"),
            owner_phone=owner_phone,
            owner_email=client.get("email"),
            owner_address=owner_address,
            allergies=allergies,
            notes=raw.get("notes"),
            client_pims_id=str(client["id"])
            if client.get("id")
            else raw.get("clientId"),
            is_active=raw.get("isActive", True),
            raw_data=raw,
        )

    def _map_appointment(self, raw: dict[str, Any]) -> PIMSAppointment:
        """Map Vetspire appointment to PIMSAppointment."""
        start = self._parse_datetime(raw.get("start"))
        duration = raw.get("duration")

        end: datetime | None = None
        if start and duration is not None:
            end = start + timedelta(minutes=int(duration))

        appt_type = raw.get("type") or {}
        location = raw.get("location") or {}
        vetspire_status = raw.get("status", "")
        normalized_status = VETSPIRE_STATUS_MAP.get(
            vetspire_status, vetspire_status.lower() if vetspire_status else "scheduled"
        )

        return PIMSAppointment(
            pims_id=str(raw.get("id", "")),
            patient_pims_id=(str(raw["patientId"]) if raw.get("patientId") else None),
            provider_pims_id=(
                str(raw["providerId"]) if raw.get("providerId") else None
            ),
            start_time=start,
            end_time=end,
            appointment_type=appt_type.get("name")
            if isinstance(appt_type, dict)
            else None,
            appointment_type_id=str(appt_type["id"])
            if isinstance(appt_type, dict) and appt_type.get("id")
            else None,
            status=normalized_status,
            reason=raw.get("reason"),
            notes=raw.get("note"),
            location_pims_id=str(location["id"]) if location.get("id") else None,
            duration_minutes=int(duration) if duration is not None else None,
            is_confirmed=raw.get("isConfirmed", False),
            raw_data=raw,
        )

    def _map_provider(self, raw: dict[str, Any]) -> PIMSProvider:
        """Map Vetspire provider to PIMSProvider."""
        departments = raw.get("departments") or []
        specialties = [d.get("name", "") for d in departments if d.get("name")]

        is_vet = raw.get("isVeterinarian", False)
        provider_type = "veterinarian" if is_vet else "staff"

        return PIMSProvider(
            pims_id=str(raw.get("id", "")),
            first_name=raw.get("givenName", ""),
            last_name=raw.get("familyName", ""),
            title=raw.get("title"),
            suffix=raw.get("suffix"),
            provider_type=provider_type,
            specialties=specialties or None,
            email=raw.get("email"),
            is_active=raw.get("isActive", True),
            is_veterinarian=is_vet,
            profile_image_url=raw.get("profileImageUrl"),
            default_location_id=raw.get("defaultLocationId"),
            raw_data=raw,
        )

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        """Parse ISO datetime string."""
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _parse_slot_datetime(
        date_str: str | None, time_str: str | None
    ) -> datetime | None:
        """Parse separate date and time strings into a datetime."""
        if not date_str or not time_str:
            return None
        try:
            return datetime.fromisoformat(f"{date_str}T{time_str}")
        except (ValueError, TypeError):
            return None
