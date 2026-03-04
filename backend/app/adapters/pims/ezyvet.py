"""ezyVet PIMS adapter.

Implements the IPIMSAdapter interface for ezyVet's REST API.
Uses OAuth2 client_credentials for authentication.
"""

from datetime import date, datetime, timedelta
from uuid import UUID

from loguru import logger

from app.adapters.pims.base import IPIMSAdapter
from app.adapters.pims.errors import PIMSAuthError, PIMSError
from app.adapters.pims.types import (
    PIMSAppointment,
    PIMSPatient,
    PIMSProvider,
    PIMSTimeSlot,
)

# ezyVet appointment status mapping
EZYVET_STATUS_MAP: dict[str, str] = {
    "Confirmed": "confirmed",
    "Scheduled": "scheduled",
    "Checked In": "checked_in",
    "In Progress": "in_progress",
    "Complete": "completed",
    "Cancelled": "cancelled",
    "No Show": "no_show",
}


class EzyVetAdapter(IPIMSAdapter):
    """ezyVet PIMS adapter using REST API with OAuth2 authentication."""

    def __init__(
        self,
        clinic_id: UUID,
        credentials: dict,
        settings: dict | None = None,
    ) -> None:
        super().__init__(clinic_id, credentials, settings)
        self._base_url = credentials.get("base_url", "https://api.ezyvet.com/v2")
        self._partner_id = credentials.get("partner_id", "")
        self._client_id = credentials.get("client_id", "")
        self._client_secret = credentials.get("client_secret", "")
        self._access_token: str | None = None
        self._token_expires_at: datetime | None = None

    def _get_headers(self) -> dict:
        """Get authenticated request headers."""
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
            "X-Partner-Id": self._partner_id,
        }

    async def authenticate(self) -> bool:
        """Authenticate via OAuth2 client_credentials grant."""
        try:
            response = await self._request(
                "POST",
                f"{self._base_url}/oauth/access_token",
                json={
                    "partner_id": self._partner_id,
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "grant_type": "client_credentials",
                    "scope": "read-patients,read-appointments,write-appointments,read-resources",
                },
                max_retries=1,
            )
            if response.status_code != 200:
                raise PIMSAuthError(
                    f"ezyVet auth failed: {response.status_code}",
                    pims_type="ezyvet",
                )

            data = response.json()
            self._access_token = data.get("access_token")
            expires_in = data.get("expires_in", 39600)  # Default 11h
            self._token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            logger.info(
                "ezyVet authentication successful for clinic {}", self.clinic_id
            )
            return True
        except PIMSAuthError:
            raise
        except Exception as e:
            raise PIMSAuthError(
                f"ezyVet authentication error: {e}", pims_type="ezyvet"
            ) from e

    async def _ensure_authenticated(self) -> None:
        """Ensure we have a valid token, re-authenticating if needed."""
        if (
            not self._access_token
            or not self._token_expires_at
            or datetime.now() >= self._token_expires_at - timedelta(hours=1)
        ):
            await self.authenticate()

    async def test_connection(self) -> dict:
        """Test the connection to ezyVet."""
        try:
            await self._ensure_authenticated()
            response = await self._request(
                "GET",
                f"{self._base_url}/animal",
                headers=self._get_headers(),
                params={"limit": 1},
            )
            if response.status_code == 200:
                return {
                    "connected": True,
                    "message": "Successfully connected to ezyVet",
                    "pims_type": "ezyvet",
                }
            return {
                "connected": False,
                "message": f"ezyVet returned status {response.status_code}",
                "pims_type": "ezyvet",
            }
        except Exception as e:
            return {
                "connected": False,
                "message": f"Connection failed: {e}",
                "pims_type": "ezyvet",
            }

    async def get_patients(
        self,
        since: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[PIMSPatient]:
        """Fetch patients from ezyVet."""
        await self._ensure_authenticated()

        params: dict = {"limit": limit, "offset": offset}
        if since:
            params["modified_at_gte"] = since.isoformat()

        response = await self._request(
            "GET",
            f"{self._base_url}/animal",
            headers=self._get_headers(),
            params=params,
        )
        if response.status_code != 200:
            raise PIMSError(
                f"Failed to fetch patients: {response.status_code}",
                pims_type="ezyvet",
            )

        data = response.json()
        items = data.get("items", [])
        return [self._map_patient(item) for item in items]

    async def get_patient_by_id(self, pims_id: str) -> PIMSPatient | None:
        """Fetch a single patient from ezyVet."""
        await self._ensure_authenticated()

        response = await self._request(
            "GET",
            f"{self._base_url}/animal/{pims_id}",
            headers=self._get_headers(),
        )
        if response.status_code == 404:
            return None
        if response.status_code != 200:
            raise PIMSError(
                f"Failed to fetch patient: {response.status_code}",
                pims_type="ezyvet",
            )

        data = response.json()
        items = data.get("items", [])
        if not items:
            return None
        return self._map_patient(items[0])

    async def get_appointments(
        self,
        start_date: date,
        end_date: date,
        limit: int = 100,
        offset: int = 0,
    ) -> list[PIMSAppointment]:
        """Fetch appointments from ezyVet."""
        await self._ensure_authenticated()

        response = await self._request(
            "GET",
            f"{self._base_url}/appointment",
            headers=self._get_headers(),
            params={
                "date_from": start_date.isoformat(),
                "date_to": end_date.isoformat(),
                "limit": limit,
                "offset": offset,
            },
        )
        if response.status_code != 200:
            raise PIMSError(
                f"Failed to fetch appointments: {response.status_code}",
                pims_type="ezyvet",
            )

        data = response.json()
        items = data.get("items", [])
        return [self._map_appointment(item) for item in items]

    async def create_appointment(self, data: PIMSAppointment) -> PIMSAppointment:
        """Create an appointment in ezyVet."""
        await self._ensure_authenticated()

        payload = {
            "animal_id": data.patient_pims_id,
            "resource_id": data.provider_pims_id,
            "start_at": data.start_time.isoformat() if data.start_time else None,
            "end_at": data.end_time.isoformat() if data.end_time else None,
            "type": data.appointment_type or "General",
            "description": data.reason or "",
        }

        response = await self._request(
            "POST",
            f"{self._base_url}/appointment",
            headers=self._get_headers(),
            json=payload,
        )
        if response.status_code not in (200, 201):
            raise PIMSError(
                f"Failed to create appointment: {response.status_code}",
                pims_type="ezyvet",
            )

        result = response.json()
        items = result.get("items", [])
        if not items:
            raise PIMSError(
                "ezyVet returned empty response for appointment creation",
                pims_type="ezyvet",
            )
        return self._map_appointment(items[0])

    async def update_appointment(
        self, pims_id: str, data: PIMSAppointment
    ) -> PIMSAppointment:
        """Update an appointment in ezyVet."""
        await self._ensure_authenticated()

        payload: dict = {}
        if data.start_time:
            payload["start_at"] = data.start_time.isoformat()
        if data.end_time:
            payload["end_at"] = data.end_time.isoformat()
        if data.status:
            payload["status"] = data.status
        if data.notes:
            payload["description"] = data.notes

        response = await self._request(
            "PUT",
            f"{self._base_url}/appointment/{pims_id}",
            headers=self._get_headers(),
            json=payload,
        )
        if response.status_code != 200:
            raise PIMSError(
                f"Failed to update appointment: {response.status_code}",
                pims_type="ezyvet",
            )

        result = response.json()
        items = result.get("items", [])
        if not items:
            raise PIMSError(
                "ezyVet returned empty response for appointment update",
                pims_type="ezyvet",
            )
        return self._map_appointment(items[0])

    async def cancel_appointment(self, pims_id: str, reason: str | None = None) -> bool:
        """Cancel an appointment in ezyVet."""
        await self._ensure_authenticated()

        response = await self._request(
            "PUT",
            f"{self._base_url}/appointment/{pims_id}",
            headers=self._get_headers(),
            json={"status": "Cancelled", "cancellation_reason": reason or ""},
        )
        return response.status_code == 200

    async def get_providers(self) -> list[PIMSProvider]:
        """Fetch providers (resources) from ezyVet."""
        await self._ensure_authenticated()

        response = await self._request(
            "GET",
            f"{self._base_url}/resource",
            headers=self._get_headers(),
            params={"limit": 200},
        )
        if response.status_code != 200:
            raise PIMSError(
                f"Failed to fetch providers: {response.status_code}",
                pims_type="ezyvet",
            )

        data = response.json()
        items = data.get("items", [])
        return [self._map_provider(item) for item in items]

    async def get_available_slots(
        self, provider_pims_id: str, target_date: date
    ) -> list[PIMSTimeSlot]:
        """Compute available slots from provider schedule minus booked appointments."""
        await self._ensure_authenticated()

        # Get appointments for the day
        appointments = await self.get_appointments(
            start_date=target_date,
            end_date=target_date,
        )

        # Filter to this provider's appointments
        provider_appts = [
            a
            for a in appointments
            if a.provider_pims_id == provider_pims_id
            and a.status not in ("cancelled", "no_show")
        ]

        # Generate slots (9am-5pm default, 30min intervals)
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

    # --- Mapping helpers ---

    def _map_patient(self, raw: dict) -> PIMSPatient:
        """Map ezyVet animal JSON to PIMSPatient."""
        animal = raw.get("animal", raw)
        contact = raw.get("contact", {})

        return PIMSPatient(
            pims_id=str(animal.get("id", "")),
            name=animal.get("name", "Unknown"),
            species=animal.get("species_name", "other").lower(),
            breed=animal.get("breed_name"),
            color=animal.get("colour"),
            sex=animal.get("sex", "unknown").lower(),
            date_of_birth=self._parse_date(animal.get("date_of_birth")),
            weight_kg=animal.get("weight"),
            microchip_id=animal.get("microchip_number"),
            is_deceased=animal.get("is_deceased", False),
            owner_first_name=contact.get("first_name"),
            owner_last_name=contact.get("last_name"),
            owner_phone=contact.get("phone"),
            owner_email=contact.get("email"),
            raw_data=raw,
        )

    def _map_appointment(self, raw: dict) -> PIMSAppointment:
        """Map ezyVet appointment JSON to PIMSAppointment."""
        appt = raw.get("appointment", raw)

        status_raw = appt.get("status", "")
        status = EZYVET_STATUS_MAP.get(status_raw, "scheduled")

        return PIMSAppointment(
            pims_id=str(appt.get("id", "")),
            patient_pims_id=str(appt.get("animal_id", ""))
            if appt.get("animal_id")
            else None,
            provider_pims_id=str(appt.get("resource_id", ""))
            if appt.get("resource_id")
            else None,
            start_time=self._parse_datetime(appt.get("start_at")),
            end_time=self._parse_datetime(appt.get("end_at")),
            appointment_type=appt.get("type_name"),
            status=status,
            reason=appt.get("description"),
            raw_data=raw,
        )

    def _map_provider(self, raw: dict) -> PIMSProvider:
        """Map ezyVet resource JSON to PIMSProvider."""
        resource = raw.get("resource", raw)

        return PIMSProvider(
            pims_id=str(resource.get("id", "")),
            first_name=resource.get("first_name", ""),
            last_name=resource.get("last_name", ""),
            title=resource.get("title"),
            provider_type=resource.get("type", "veterinarian"),
            is_active=resource.get("active", True),
            raw_data=raw,
        )

    @staticmethod
    def _parse_date(value: str | None) -> datetime | None:
        """Parse date string to datetime."""
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        """Parse ISO datetime string."""
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except (ValueError, TypeError):
            return None
