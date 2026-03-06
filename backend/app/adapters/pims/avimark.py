"""Avimark PIMS adapter.

Implements the IPIMSAdapter interface using a dual-path strategy:
- Reads: IDEXX DataPoint OData V4 REST API (OAuth 2.0)
- Writes: Covetrus Connect API (stubbed — requires partner agreement)

Avimark is Covetrus's on-premise Windows PIMS used by 11,000+ vet clinics.
It has no native API; integration goes through the IDEXX DataPoint
intermediary for reads and Covetrus Connect for writes.
"""

from datetime import date, datetime, timedelta
from uuid import UUID

from loguru import logger

from app.adapters.pims.base import IPIMSAdapter
from app.adapters.pims.errors import PIMSAuthError, PIMSError, PIMSWriteError
from app.adapters.pims.types import (
    PIMSAppointment,
    PIMSPatient,
    PIMSProvider,
    PIMSTimeSlot,
)

# Avimark appointment status mapping (DataPoint → canonical)
AVIMARK_STATUS_MAP: dict[str, str] = {
    "Scheduled": "scheduled",
    "Confirmed": "confirmed",
    "Checked In": "checked_in",
    "In Progress": "in_progress",
    "Completed": "completed",
    "Cancelled": "cancelled",
    "No Show": "no_show",
    "Missed": "no_show",
}


class AvimarkAdapter(IPIMSAdapter):
    """Avimark PIMS adapter using IDEXX DataPoint OData V4 API for reads."""

    def __init__(
        self,
        clinic_id: UUID,
        credentials: dict,
        settings: dict | None = None,
    ) -> None:
        super().__init__(clinic_id, credentials, settings)
        self._base_url = credentials.get(
            "base_url", "https://io.datapointapi.com"
        ).rstrip("/")
        self._username = credentials.get("username", "")
        self._password = credentials.get("password", "")
        self._covetrus_api_key = credentials.get("covetrus_api_key")
        self._covetrus_partner_id = credentials.get("covetrus_partner_id")
        self._access_token: str | None = None
        self._token_expires_at: datetime | None = None

    def _get_headers(self) -> dict:
        """Get authenticated request headers."""
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Accept": "application/json",
        }

    async def authenticate(self) -> bool:
        """Authenticate via OAuth 2.0 token endpoint using username/password."""
        try:
            response = await self._request(
                "POST",
                f"{self._base_url}/token",
                data={
                    "grant_type": "password",
                    "username": self._username,
                    "password": self._password,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                max_retries=1,
            )
            if response.status_code != 200:
                raise PIMSAuthError(
                    f"DataPoint auth failed: {response.status_code}",
                    pims_type="avimark",
                )

            data = response.json()
            self._access_token = data.get("access_token")
            expires_in = data.get("expires_in", 3600)
            self._token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            logger.info(
                "DataPoint authentication successful for clinic {}", self.clinic_id
            )
            return True
        except PIMSAuthError:
            raise
        except Exception as e:
            raise PIMSAuthError(
                f"DataPoint authentication error: {e}", pims_type="avimark"
            ) from e

    async def _ensure_authenticated(self) -> None:
        """Ensure we have a valid token, re-authenticating if needed."""
        if (
            not self._access_token
            or not self._token_expires_at
            or datetime.now() >= self._token_expires_at - timedelta(minutes=5)
        ):
            await self.authenticate()

    async def test_connection(self) -> dict:
        """Test the connection to IDEXX DataPoint."""
        try:
            await self._ensure_authenticated()
            response = await self._request(
                "GET",
                f"{self._base_url}/api/Patients",
                headers=self._get_headers(),
                params={"$top": 1},
            )
            if response.status_code == 200:
                return {
                    "connected": True,
                    "message": "Successfully connected to Avimark via DataPoint",
                    "pims_type": "avimark",
                }
            return {
                "connected": False,
                "message": f"DataPoint returned status {response.status_code}",
                "pims_type": "avimark",
            }
        except Exception as e:
            return {
                "connected": False,
                "message": f"Connection failed: {e}",
                "pims_type": "avimark",
            }

    # --- Read operations (IDEXX DataPoint OData V4) ---

    async def get_patients(
        self,
        since: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[PIMSPatient]:
        """Fetch patients from DataPoint OData API."""
        await self._ensure_authenticated()

        params: dict = {"$top": limit, "$skip": offset}
        if since:
            params["$filter"] = (
                f"ModifiedDate gt {since.strftime('%Y-%m-%dT%H:%M:%SZ')}"
            )

        response = await self._request(
            "GET",
            f"{self._base_url}/api/Patients",
            headers=self._get_headers(),
            params=params,
        )
        if response.status_code != 200:
            raise PIMSError(
                f"Failed to fetch patients: {response.status_code}",
                pims_type="avimark",
            )

        data = response.json()
        items = data.get("value", [])
        return [self._map_patient(item) for item in items]

    async def get_patient_by_id(self, pims_id: str) -> PIMSPatient | None:
        """Fetch a single patient from DataPoint by ID."""
        await self._ensure_authenticated()

        response = await self._request(
            "GET",
            f"{self._base_url}/api/Patients({pims_id})",
            headers=self._get_headers(),
        )
        if response.status_code == 404:
            return None
        if response.status_code != 200:
            raise PIMSError(
                f"Failed to fetch patient: {response.status_code}",
                pims_type="avimark",
            )

        data = response.json()
        if not data:
            return None
        return self._map_patient(data)

    async def get_appointments(
        self,
        start_date: date,
        end_date: date,
        limit: int = 100,
        offset: int = 0,
    ) -> list[PIMSAppointment]:
        """Fetch appointments from DataPoint OData API."""
        await self._ensure_authenticated()

        filter_str = (
            f"StartDate ge {start_date.isoformat()} "
            f"and StartDate le {end_date.isoformat()}"
        )

        response = await self._request(
            "GET",
            f"{self._base_url}/api/Appointments",
            headers=self._get_headers(),
            params={
                "$filter": filter_str,
                "$top": limit,
                "$skip": offset,
            },
        )
        if response.status_code != 200:
            raise PIMSError(
                f"Failed to fetch appointments: {response.status_code}",
                pims_type="avimark",
            )

        data = response.json()
        items = data.get("value", [])
        return [self._map_appointment(item) for item in items]

    async def get_providers(self) -> list[PIMSProvider]:
        """Fetch providers (resources) from DataPoint OData API."""
        await self._ensure_authenticated()

        response = await self._request(
            "GET",
            f"{self._base_url}/api/Resources",
            headers=self._get_headers(),
            params={"$top": 200},
        )
        if response.status_code != 200:
            raise PIMSError(
                f"Failed to fetch providers: {response.status_code}",
                pims_type="avimark",
            )

        data = response.json()
        items = data.get("value", [])
        return [self._map_provider(item) for item in items]

    async def get_available_slots(
        self, provider_pims_id: str, target_date: date
    ) -> list[PIMSTimeSlot]:
        """Compute available slots from provider schedule minus booked appointments."""
        await self._ensure_authenticated()

        appointments = await self.get_appointments(
            start_date=target_date,
            end_date=target_date,
        )

        provider_appts = [
            a
            for a in appointments
            if a.provider_pims_id == provider_pims_id
            and a.status not in ("cancelled", "no_show")
        ]

        slots = []
        start_hour = 9
        end_hour = 17

        current = datetime.combine(
            target_date, datetime.min.time().replace(hour=start_hour)
        )
        work_end = datetime.combine(
            target_date, datetime.min.time().replace(hour=end_hour)
        )
        slot_duration = timedelta(minutes=30)

        while current + slot_duration <= work_end:
            slot_end = current + slot_duration
            is_free = True
            for appt in provider_appts:
                if (
                    appt.start_time
                    and appt.end_time
                    and current < appt.end_time
                    and slot_end > appt.start_time
                ):
                    is_free = False
                    break

            if is_free:
                slots.append(
                    PIMSTimeSlot(
                        start_time=current,
                        end_time=slot_end,
                        provider_pims_id=provider_pims_id,
                    )
                )
            current = slot_end

        return slots

    # --- Write operations (Covetrus Connect — stubbed) ---

    async def create_appointment(self, data: PIMSAppointment) -> PIMSAppointment:
        """Create appointment — requires Covetrus Connect partner agreement."""
        raise PIMSWriteError(
            "Avimark appointment creation requires Covetrus Connect partner agreement",
            pims_type="avimark",
        )

    async def update_appointment(
        self, pims_id: str, data: PIMSAppointment
    ) -> PIMSAppointment:
        """Update appointment — requires Covetrus Connect partner agreement."""
        raise PIMSWriteError(
            "Avimark appointment update requires Covetrus Connect partner agreement",
            pims_type="avimark",
        )

    async def cancel_appointment(self, pims_id: str, reason: str | None = None) -> bool:
        """Cancel appointment — requires Covetrus Connect partner agreement."""
        raise PIMSWriteError(
            "Avimark appointment cancellation requires Covetrus Connect partner agreement",
            pims_type="avimark",
        )

    # --- Mapping helpers ---

    def _map_patient(self, raw: dict) -> PIMSPatient:
        """Map DataPoint patient JSON to PIMSPatient."""
        return PIMSPatient(
            pims_id=str(raw.get("Id", raw.get("id", ""))),
            name=raw.get("Name", raw.get("name", "Unknown")),
            species=raw.get("Species", raw.get("species", "other")).lower(),
            breed=raw.get("Breed", raw.get("breed")),
            color=raw.get("Color", raw.get("color")),
            sex=raw.get("Sex", raw.get("sex", "unknown")).lower()
            if raw.get("Sex", raw.get("sex"))
            else None,
            date_of_birth=self._parse_datetime(
                raw.get("BirthDate", raw.get("birthDate"))
            ),
            weight_kg=raw.get("Weight", raw.get("weight")),
            microchip_id=raw.get("MicrochipNumber", raw.get("microchipNumber")),
            is_deceased=raw.get("IsDeceased", raw.get("isDeceased", False)),
            owner_first_name=raw.get("OwnerFirstName", raw.get("ownerFirstName")),
            owner_last_name=raw.get("OwnerLastName", raw.get("ownerLastName")),
            owner_phone=raw.get("OwnerPhone", raw.get("ownerPhone")),
            owner_email=raw.get("OwnerEmail", raw.get("ownerEmail")),
            is_active=raw.get("IsActive", raw.get("isActive", True)),
            raw_data=raw,
        )

    def _map_appointment(self, raw: dict) -> PIMSAppointment:
        """Map DataPoint appointment JSON to PIMSAppointment."""
        status_raw = raw.get("Status", raw.get("status", ""))
        status = AVIMARK_STATUS_MAP.get(status_raw, "scheduled")

        start_time = self._parse_datetime(raw.get("StartDate", raw.get("startDate")))
        end_time = self._parse_datetime(raw.get("EndDate", raw.get("endDate")))

        duration_minutes = None
        if start_time and end_time:
            duration_minutes = int((end_time - start_time).total_seconds() / 60)

        return PIMSAppointment(
            pims_id=str(raw.get("Id", raw.get("id", ""))),
            patient_pims_id=str(raw.get("PatientId", raw.get("patientId", "")))
            if raw.get("PatientId", raw.get("patientId"))
            else None,
            provider_pims_id=str(raw.get("ResourceId", raw.get("resourceId", "")))
            if raw.get("ResourceId", raw.get("resourceId"))
            else None,
            start_time=start_time,
            end_time=end_time,
            appointment_type=raw.get("AppointmentType", raw.get("appointmentType")),
            status=status,
            reason=raw.get("Reason", raw.get("reason")),
            notes=raw.get("Notes", raw.get("notes")),
            duration_minutes=duration_minutes,
            raw_data=raw,
        )

    def _map_provider(self, raw: dict) -> PIMSProvider:
        """Map DataPoint resource JSON to PIMSProvider."""
        resource_type = raw.get("ResourceType", raw.get("resourceType", ""))
        is_vet = resource_type.lower() in ("veterinarian", "doctor", "dvm")

        return PIMSProvider(
            pims_id=str(raw.get("Id", raw.get("id", ""))),
            first_name=raw.get("FirstName", raw.get("firstName", "")),
            last_name=raw.get("LastName", raw.get("lastName", "")),
            title=raw.get("Title", raw.get("title")),
            provider_type="veterinarian" if is_vet else "staff",
            is_active=raw.get("IsActive", raw.get("isActive", True)),
            is_veterinarian=is_vet,
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
