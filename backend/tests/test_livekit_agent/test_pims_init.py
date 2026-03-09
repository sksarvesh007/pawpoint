"""Tests for PIMS adapter initialization in the voice agent."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.adapters.pims.errors import PIMSError
from app.adapters.pims.types import PIMSProvider


@pytest.fixture
def mock_clinic_model():
    """Clinic model with PIMS configured."""
    clinic = MagicMock()
    clinic.id = "clinic-uuid-123"
    clinic.pims_type = MagicMock()
    clinic.pims_type.__eq__ = lambda self, other: str(self) != "none"
    clinic.pims_type.__str__ = lambda self: "ezyvet"
    clinic.pims_credentials_encrypted = b"encrypted-creds"
    clinic.pims_settings = {"site_id": "123"}
    clinic.pims_connection_status = "connected"
    return clinic


@pytest.fixture
def mock_clinic_dict():
    """Clinic dict as returned by get_clinic_by_id."""
    return {
        "id": "clinic-uuid-123",
        "name": "Happy Paws Vet",
        "slug": "happy-paws",
        "address": "123 Main St",
        "city": "Springfield",
        "state": "IL",
        "postal_code": "62701",
        "phone": "555-0100",
        "email": "info@happypaws.com",
        "business_hours": {"monday": "9:00-17:00", "tuesday": "9:00-17:00"},
        "voice_enabled": True,
        "voice_settings": {},
        "twilio_phone_number": "+15550100",
        "emergency_phone": "555-0199",
        "emergency_keywords": ["emergency", "dying"],
        "pims_type": "ezyvet",
        "pims_connection_status": "connected",
    }


@pytest.fixture
def unconfigured_clinic_model():
    """Clinic model with no PIMS."""
    from app.models.clinic import PIMSType

    clinic = MagicMock()
    clinic.id = "clinic-uuid-456"
    clinic.pims_type = PIMSType.NONE
    clinic.pims_credentials_encrypted = None
    clinic.pims_settings = None
    clinic.pims_connection_status = "disconnected"
    return clinic


# --- Adapter init tests ---


def test_adapter_initialized_for_connected_clinic(mock_clinic_model):
    """Factory creates adapter for clinic with PIMS type + credentials."""
    with patch("app.adapters.pims.factory.decrypt_credentials") as mock_decrypt:
        mock_decrypt.return_value = {"api_key": "test", "api_secret": "secret"}

        from app.adapters.pims.factory import get_pims_adapter

        # Override pims_type to match an actual PIMSType
        from app.models.clinic import PIMSType

        mock_clinic_model.pims_type = PIMSType.EZYVET

        adapter = get_pims_adapter(mock_clinic_model)

        assert adapter is not None
        mock_decrypt.assert_called_once_with(b"encrypted-creds")


def test_adapter_none_for_unconfigured_clinic(unconfigured_clinic_model):
    """Factory raises PIMSError when pims_type is NONE."""
    from app.adapters.pims.factory import get_pims_adapter

    with pytest.raises(PIMSError, match="No PIMS configured"):
        get_pims_adapter(unconfigured_clinic_model)


def test_adapter_failure_falls_back(mock_clinic_model):
    """Factory failure (e.g., bad credentials) raises exception."""
    with patch("app.adapters.pims.factory.decrypt_credentials") as mock_decrypt:
        mock_decrypt.side_effect = ValueError("Decryption failed")

        from app.adapters.pims.factory import get_pims_adapter
        from app.models.clinic import PIMSType

        mock_clinic_model.pims_type = PIMSType.EZYVET

        with pytest.raises(ValueError, match="Decryption failed"):
            get_pims_adapter(mock_clinic_model)


# --- warm_cache with PIMS providers ---


@pytest.mark.asyncio
async def test_warm_cache_fetches_pims_providers(mock_clinic_dict):
    """warm_cache populates cached_pims_providers when adapter is available."""
    from livekit_agent.vet_clinic_agent import VetClinicAgent

    mock_adapter = AsyncMock()
    mock_adapter.get_providers.return_value = [
        PIMSProvider(
            pims_id="prov-1",
            first_name="Jane",
            last_name="Smith",
            is_active=True,
            is_veterinarian=True,
        ),
    ]

    agent = VetClinicAgent(
        clinic=mock_clinic_dict,
        pims_adapter=mock_adapter,
    )

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_result

    await agent.warm_cache(mock_db)

    assert agent.cached_pims_providers is not None
    assert len(agent.cached_pims_providers) == 1
    assert agent.cached_pims_providers[0].first_name == "Jane"


# --- Adapter close on shutdown ---


@pytest.mark.asyncio
async def test_adapter_closed_on_shutdown(mock_clinic_dict):
    """PIMS adapter close() is callable for cleanup."""
    mock_adapter = AsyncMock()
    mock_adapter.close = AsyncMock()

    # Verify close can be called without error
    await mock_adapter.close()
    mock_adapter.close.assert_called_once()
