"""Covetrus Connect PIMS adapter.

Implements the IPIMSAdapter interface for Covetrus Connect API, covering
Pulse, Cornerstone, and ImproMed PIMS products.

Authentication: OAuth2 client credentials flow.
Reads: Standard REST JSON endpoints.
Writes: REST POST/PUT for appointments.

NOTE: Some endpoint paths and field names are inferred from API patterns
and may need minor adjustments after the Covetrus partner agreement is
established. Fields marked with "TODO: verify field name" are best-guess
mappings.
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

# Covetrus appointment status mapping → canonical
COVETRUS_STATUS_MAP: dict[str, str] = {
    "Scheduled": "scheduled",
    "Confirmed": "confirmed",
    "Checked In": "checked_in",
    "In Progress": "in_progress",
    "Completed": "completed",
    "Cancelled": "cancelled",
    "No Show": "no_show",
    "Pending": "scheduled",
}


class CovetrusAdapter(IPIMSAdapter):
    """Covetrus Connect PIMS adapter (Pulse / Cornerstone / ImproMed)."""

    def __init__(
        self,
        clinic_id: UUID,
        credentials: dict,
        settings: dict | None = None,
    ) -> None:
        super().__init__(clinic_id, credentials, settings)
        self._base_url = credentials.get(
            "base_url", "https://api.covetrus.com/v1"
        ).rstrip("/")
        self._client_id = credentials.get("client_id", "")
        self._client_secret = credentials.get("client_secret", "")
        self._partner_id = credentials.get("partner_id", "")
        self._access_token: str | None = None
        self._token_expires_at: datetime | None = None

    def _get_headers(self) -> dict:
        """Get authenticated request headers."""
        return {
            "Authorization": f"Bearer {self._access_token}",
            "X-Partner-Id": self._partner_id,
            "Accept": "application/json",
        }

    async def authenticate(self) -> bool:
        """Authenticate via OAuth 2.0 client credentials flow."""
        try:
            # TODO: verify token endpoint path after partner agreement
            response = await self._request(
                "POST",
                f"{self._base_url}/oauth/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                max_retries=1,
            )
            if response.status_code != 200:
                raise PIMSAuthError(
                    f"Covetrus auth failed: {response.status_code}",
                    pims_type="covetrus",
                )

            data = response.json()
            self._access_token = data.get("access_token")
            expires_in = data.get("expires_in", 3600)
            self._token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            logger.info(
                "Covetrus authentication successful for clinic {}", self.clinic_id
            )
            return True
        except PIMSAuthError:
            raise
        except Exception as e:
            raise PIMSAuthError(
                f"Covetrus authentication error: {e}", pims_type="covetrus"
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
        """Test the connection to Covetrus Connect."""
        try:
            await self._ensure_authenticated()
            # TODO: verify health/status endpoint after partner agreement
            response = await self._request(
                "GET",
                f"{self._base_url}/patients",
                headers=self._get_headers(),
                params={"limit": 1},
            )
            if response.status_code == 200:
                return {
                    "connected": True,
                    "message": "Successfully connected to Covetrus Connect",
                    "pims_type": "covetrus",
                }
            return {
                "connected": False,
                "message": f"Covetrus returned status {response.status_code}",
                "pims_type": "covetrus",
            }
        except Exception as e:
            return {
                "connected": False,
                "message": f"Connection failed: {e}",
                "pims_type": "covetrus",
            }

    # --- Read operations (Covetrus Connect REST API) ---

    async def get_patients(
        self,
        since: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[PIMSPatient]:
        """Fetch patients from Covetrus Connect API."""
        await self._ensure_authenticated()

        params: dict = {"limit": limit, "offset": offset}
        if since:
            # TODO: verify filter param name after partner agreement
            params["modified_since"] = since.strftime("%Y-%m-%dT%H:%M:%SZ")

        response = await self._request(
            "GET",
            f"{self._base_url}/patients",
            headers=self._get_headers(),
            params=params,
        )
        if response.status_code != 200:
            raise PIMSError(
                f"Failed to fetch patients: {response.status_code}",
                pims_type="covetrus",
            )

        data = response.json()
        # TODO: verify JSON envelope key after partner agreement
        items = data.get("data", data.get("items", []))
        return [self._map_patient(item) for item in items]

    async def get_patient_by_id(self, pims_id: str) -> PIMSPatient | None:
        """Fetch a single patient by PIMS ID."""
        await self._ensure_authenticated()

        response = await self._request(
            "GET",
            f"{self._base_url}/patients/{pims_id}",
            headers=self._get_headers(),
        )
        if response.status_code == 404:
            return None
        if response.status_code != 200:
            raise PIMSError(
                f"Failed to fetch patient: {response.status_code}",
                pims_type="covetrus",
            )

        data = response.json()
        # Support both { "data": {...} } envelope and flat response
        record = data.get("data", data) if isinstance(data, dict) else data
        if not record:
            return None
        return self._map_patient(record)

    async def get_appointments(
        self,
        start_date: date,
        end_date: date,
        limit: int = 100,
        offset: int = 0,
    ) -> list[PIMSAppointment]:
        """Fetch appointments from Covetrus Connect API."""
        await self._ensure_authenticated()

        response = await self._request(
            "GET",
            f"{self._base_url}/appointments",
            headers=self._get_headers(),
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "limit": limit,
                "offset": offset,
            },
        )
        if response.status_code != 200:
            raise PIMSError(
                f"Failed to fetch appointments: {response.status_code}",
                pims_type="covetrus",
            )

        data = response.json()
        # TODO: verify JSON envelope key after partner agreement
        items = data.get("data", data.get("items", []))
        return [self._map_appointment(item) for item in items]

    async def get_providers(self) -> list[PIMSProvider]:
        """Fetch providers (employees) from Covetrus Connect API."""
        await self._ensure_authenticated()

        response = await self._request(
            "GET",
            f"{self._base_url}/employees",
            headers=self._get_headers(),
            # TODO: verify role filter param after partner agreement
            params={"role": "veterinarian,technician", "limit": 200},
        )
        if response.status_code != 200:
            raise PIMSError(
                f"Failed to fetch providers: {response.status_code}",
                pims_type="covetrus",
            )

        data = response.json()
        items = data.get("data", data.get("items", []))
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

    # --- Write operations (Covetrus Connect REST API) ---

    async def create_appointment(self, data: PIMSAppointment) -> PIMSAppointment:
        """Create an appointment via Covetrus Connect API."""
        await self._ensure_authenticated()

        body = {
            "patient_id": data.patient_pims_id,
            "provider_id": data.provider_pims_id,
            "start_time": data.start_time.isoformat() if data.start_time else None,
            "end_time": data.end_time.isoformat() if data.end_time else None,
            "appointment_type": data.appointment_type,
            "reason": data.reason,
            "notes": data.notes,
        }

        response = await self._request(
            "POST",
            f"{self._base_url}/appointments",
            headers=self._get_headers(),
            json=body,
        )
        if response.status_code not in (200, 201):
            raise PIMSWriteError(
                f"Failed to create appointment: {response.status_code}",
                pims_type="covetrus",
            )

        result = response.json()
        record = result.get("data", result)
        return self._map_appointment(record)

    async def update_appointment(
        self, pims_id: str, data: PIMSAppointment
    ) -> PIMSAppointment:
        """Update an appointment via Covetrus Connect API."""
        await self._ensure_authenticated()

        body = {
            "patient_id": data.patient_pims_id,
            "provider_id": data.provider_pims_id,
            "start_time": data.start_time.isoformat() if data.start_time else None,
            "end_time": data.end_time.isoformat() if data.end_time else None,
            "appointment_type": data.appointment_type,
            "status": data.status,
            "reason": data.reason,
            "notes": data.notes,
        }

        response = await self._request(
            "PUT",
            f"{self._base_url}/appointments/{pims_id}",
            headers=self._get_headers(),
            json=body,
        )
        if response.status_code != 200:
            raise PIMSWriteError(
                f"Failed to update appointment: {response.status_code}",
                pims_type="covetrus",
            )

        result = response.json()
        record = result.get("data", result)
        return self._map_appointment(record)

    async def cancel_appointment(self, pims_id: str, reason: str | None = None) -> bool:
        """Cancel an appointment via Covetrus Connect API."""
        await self._ensure_authenticated()

        body: dict = {"status": "Cancelled"}
        if reason:
            body["cancellation_reason"] = reason

        response = await self._request(
            "PUT",
            f"{self._base_url}/appointments/{pims_id}",
            headers=self._get_headers(),
            json=body,
        )
        if response.status_code != 200:
            raise PIMSWriteError(
                f"Failed to cancel appointment: {response.status_code}",
                pims_type="covetrus",
            )

        return True

    # --- Mapping helpers ---

    def _map_patient(self, raw: dict) -> PIMSPatient:
        """Map Covetrus patient JSON to PIMSPatient."""
        return PIMSPatient(
            # TODO: verify field name after partner agreement
            pims_id=str(raw.get("id", raw.get("Id", ""))),
            name=raw.get("name", raw.get("Name", "Unknown")),
            species=raw.get("species", raw.get("Species", "other")).lower(),
            breed=raw.get("breed", raw.get("Breed")),
            color=raw.get("color", raw.get("Color")),
            sex=raw.get("sex", raw.get("Sex", "unknown")).lower()
            if raw.get("sex", raw.get("Sex"))
            else None,
            date_of_birth=self._parse_datetime(
                raw.get("date_of_birth", raw.get("dateOfBirth", raw.get("BirthDate")))
            ),
            weight_kg=raw.get("weight", raw.get("Weight")),
            microchip_id=raw.get(
                "microchip_number",
                raw.get("microchipNumber", raw.get("MicrochipNumber")),
            ),
            is_deceased=raw.get("is_deceased", raw.get("isDeceased", False)),
            # TODO: verify owner field names after partner agreement
            owner_first_name=raw.get(
                "owner_first_name", raw.get("ownerFirstName", raw.get("OwnerFirstName"))
            ),
            owner_last_name=raw.get(
                "owner_last_name", raw.get("ownerLastName", raw.get("OwnerLastName"))
            ),
            owner_phone=raw.get(
                "owner_phone", raw.get("ownerPhone", raw.get("OwnerPhone"))
            ),
            owner_email=raw.get(
                "owner_email", raw.get("ownerEmail", raw.get("OwnerEmail"))
            ),
            is_active=raw.get("is_active", raw.get("isActive", True)),
            raw_data=raw,
        )

    def _map_appointment(self, raw: dict) -> PIMSAppointment:
        """Map Covetrus appointment JSON to PIMSAppointment."""
        # TODO: verify field name after partner agreement
        status_raw = raw.get("status", raw.get("Status", ""))
        status = COVETRUS_STATUS_MAP.get(status_raw, "scheduled")

        start_time = self._parse_datetime(
            raw.get("start_time", raw.get("startTime", raw.get("StartDate")))
        )
        end_time = self._parse_datetime(
            raw.get("end_time", raw.get("endTime", raw.get("EndDate")))
        )

        duration_minutes = None
        if start_time and end_time:
            duration_minutes = int((end_time - start_time).total_seconds() / 60)

        return PIMSAppointment(
            pims_id=str(raw.get("id", raw.get("Id", ""))),
            # TODO: verify field name after partner agreement
            patient_pims_id=str(
                raw.get("patient_id", raw.get("patientId", raw.get("PatientId", "")))
            )
            if raw.get("patient_id", raw.get("patientId", raw.get("PatientId")))
            else None,
            provider_pims_id=str(
                raw.get("provider_id", raw.get("providerId", raw.get("ProviderId", "")))
            )
            if raw.get("provider_id", raw.get("providerId", raw.get("ProviderId")))
            else None,
            start_time=start_time,
            end_time=end_time,
            appointment_type=raw.get(
                "appointment_type",
                raw.get("appointmentType", raw.get("AppointmentType")),
            ),
            status=status,
            reason=raw.get("reason", raw.get("Reason")),
            notes=raw.get("notes", raw.get("Notes")),
            duration_minutes=duration_minutes,
            raw_data=raw,
        )

    def _map_provider(self, raw: dict) -> PIMSProvider:
        """Map Covetrus employee JSON to PIMSProvider."""
        # TODO: verify field name after partner agreement
        role = raw.get("role", raw.get("Role", raw.get("employee_type", "")))
        is_vet = role.lower() in ("veterinarian", "doctor", "dvm")

        return PIMSProvider(
            pims_id=str(raw.get("id", raw.get("Id", ""))),
            first_name=raw.get(
                "first_name", raw.get("firstName", raw.get("FirstName", ""))
            ),
            last_name=raw.get(
                "last_name", raw.get("lastName", raw.get("LastName", ""))
            ),
            title=raw.get("title", raw.get("Title")),
            provider_type="veterinarian" if is_vet else "staff",
            is_active=raw.get("is_active", raw.get("isActive", True)),
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
