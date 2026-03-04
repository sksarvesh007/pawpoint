"""Abstract base adapter for PIMS integrations.

Defines the interface all PIMS adapters must implement, plus a shared
HTTP helper with retry, rate-limit handling, and error wrapping.
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import date, datetime
from uuid import UUID

import httpx
from loguru import logger

from app.adapters.pims.errors import (
    PIMSAuthError,
    PIMSConnectionError,
    PIMSError,
    PIMSRateLimitError,
)
from app.adapters.pims.types import (
    PIMSAppointment,
    PIMSPatient,
    PIMSProvider,
    PIMSTimeSlot,
)


class IPIMSAdapter(ABC):
    """Abstract base class for all PIMS adapters.

    Each concrete adapter (ezyVet, Vetspire, etc.) implements this interface
    to normalize PIMS-specific APIs into a common data model.
    """

    def __init__(
        self,
        clinic_id: UUID,
        credentials: dict,
        settings: dict | None = None,
    ) -> None:
        self.clinic_id = clinic_id
        self.credentials = credentials
        self.settings = settings or {}
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    # --- Abstract methods all adapters must implement ---

    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the PIMS system.

        Returns True if authentication was successful.
        """
        ...

    @abstractmethod
    async def test_connection(self) -> dict:
        """Test the connection to the PIMS system.

        Returns a dict with connection status details.
        """
        ...

    @abstractmethod
    async def get_patients(
        self,
        since: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[PIMSPatient]:
        """Fetch patients from PIMS."""
        ...

    @abstractmethod
    async def get_patient_by_id(self, pims_id: str) -> PIMSPatient | None:
        """Fetch a single patient by PIMS ID."""
        ...

    @abstractmethod
    async def get_appointments(
        self,
        start_date: date,
        end_date: date,
        limit: int = 100,
        offset: int = 0,
    ) -> list[PIMSAppointment]:
        """Fetch appointments from PIMS within a date range."""
        ...

    @abstractmethod
    async def create_appointment(self, data: PIMSAppointment) -> PIMSAppointment:
        """Create an appointment in the PIMS system."""
        ...

    @abstractmethod
    async def update_appointment(
        self, pims_id: str, data: PIMSAppointment
    ) -> PIMSAppointment:
        """Update an appointment in the PIMS system."""
        ...

    @abstractmethod
    async def cancel_appointment(self, pims_id: str, reason: str | None = None) -> bool:
        """Cancel an appointment in the PIMS system."""
        ...

    @abstractmethod
    async def get_providers(self) -> list[PIMSProvider]:
        """Fetch all providers from PIMS."""
        ...

    @abstractmethod
    async def get_available_slots(
        self, provider_pims_id: str, target_date: date
    ) -> list[PIMSTimeSlot]:
        """Get available appointment slots for a provider."""
        ...

    # --- Shared HTTP helper with retry, rate-limit, and error handling ---

    async def _request(
        self,
        method: str,
        url: str,
        headers: dict | None = None,
        max_retries: int = 3,
        **kwargs,
    ) -> httpx.Response:
        """Make HTTP request with retry, rate-limit handling, and error wrapping.

        - Retries on 5xx errors with exponential backoff
        - Retries on 401 after re-authentication
        - Respects Retry-After header on 429
        - Wraps network errors in PIMSConnectionError
        """
        client = await self._get_client()
        last_exception: Exception | None = None

        for attempt in range(max_retries):
            try:
                response = await client.request(method, url, headers=headers, **kwargs)

                if response.status_code == 401:
                    if attempt < max_retries - 1:
                        logger.warning(
                            "PIMS 401 received, re-authenticating (attempt {}/{})",
                            attempt + 1,
                            max_retries,
                        )
                        await self.authenticate()
                        continue
                    raise PIMSAuthError(
                        "Authentication failed after retry",
                        pims_type=self.__class__.__name__,
                    )

                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", "60"))
                    if attempt < max_retries - 1:
                        logger.warning(
                            "PIMS rate limited, waiting {}s (attempt {}/{})",
                            retry_after,
                            attempt + 1,
                            max_retries,
                        )
                        await asyncio.sleep(min(retry_after, 120))
                        continue
                    raise PIMSRateLimitError(
                        "Rate limit exceeded",
                        pims_type=self.__class__.__name__,
                        retry_after=retry_after,
                    )

                if response.status_code == 404:
                    return response

                if response.status_code >= 500:
                    if attempt < max_retries - 1:
                        wait = 2**attempt
                        logger.warning(
                            "PIMS server error {}, retrying in {}s (attempt {}/{})",
                            response.status_code,
                            wait,
                            attempt + 1,
                            max_retries,
                        )
                        await asyncio.sleep(wait)
                        continue
                    raise PIMSError(
                        f"Server error: {response.status_code}",
                        pims_type=self.__class__.__name__,
                    )

                return response

            except httpx.TimeoutException as e:
                last_exception = e
                if attempt < max_retries - 1:
                    wait = 2**attempt
                    logger.warning(
                        "PIMS request timeout, retrying in {}s (attempt {}/{})",
                        wait,
                        attempt + 1,
                        max_retries,
                    )
                    await asyncio.sleep(wait)
                    continue

            except httpx.ConnectError as e:
                last_exception = e
                if attempt < max_retries - 1:
                    wait = 2**attempt
                    await asyncio.sleep(wait)
                    continue

            except (PIMSAuthError, PIMSRateLimitError, PIMSError):
                raise

            except Exception as e:
                last_exception = e
                break

        raise PIMSConnectionError(
            f"Connection failed after {max_retries} attempts: {last_exception}",
            pims_type=self.__class__.__name__,
        )
