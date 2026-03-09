"""Tests for patient search tools (PIMS and local)."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.adapters.pims.types import PIMSPatient
from livekit_agent.tools.patient_tools import search_patient_local, search_patient_pims


@pytest.fixture
def mock_adapter():
    adapter = AsyncMock()
    adapter.get_patients = AsyncMock()
    return adapter


def _make_pims_patient(
    name: str = "Buddy",
    species: str = "Dog",
    breed: str | None = "Labrador",
    owner_first: str = "Alice",
    owner_last: str = "Johnson",
    phone: str = "555-1234",
    allergies: str | None = None,
) -> PIMSPatient:
    return PIMSPatient(
        pims_id=f"pims-{name.lower()}",
        name=name,
        species=species,
        breed=breed,
        owner_first_name=owner_first,
        owner_last_name=owner_last,
        owner_phone=phone,
        allergies=allergies,
    )


# --- search_patient_pims ---


@pytest.mark.asyncio
async def test_search_pims_single_match(mock_adapter):
    """Single patient match returns name, species, and owner."""
    mock_adapter.get_patients.return_value = [
        _make_pims_patient(name="Buddy", species="Dog", owner_first="Alice"),
    ]

    result = await search_patient_pims(mock_adapter, "Buddy")

    assert "Buddy" in result
    assert "Dog" in result
    assert "Alice" in result


@pytest.mark.asyncio
async def test_search_pims_multiple_matches(mock_adapter):
    """Multiple matches returns count and list."""
    mock_adapter.get_patients.return_value = [
        _make_pims_patient(name="Max", owner_first="Bob"),
        _make_pims_patient(name="Maxie", owner_first="Carol"),
        _make_pims_patient(name="Maxwell", owner_first="Dave"),
    ]

    result = await search_patient_pims(mock_adapter, "Max")

    assert "3 patients" in result


@pytest.mark.asyncio
async def test_search_pims_no_matches(mock_adapter):
    """No matches returns 'couldn't find' message."""
    mock_adapter.get_patients.return_value = [
        _make_pims_patient(name="Buddy"),
    ]

    result = await search_patient_pims(mock_adapter, "Whiskers")

    assert "couldn't find" in result.lower()


# --- search_patient_local ---


@pytest.mark.asyncio
async def test_search_local_single_match():
    """Local DB search with single match returns patient info."""
    mock_db = AsyncMock()
    mock_patient = MagicMock()
    mock_patient.name = "Luna"
    mock_patient.species = MagicMock()
    mock_patient.species.value = "Cat"
    mock_patient.breed = "Persian"
    mock_patient.owner_full_name = "Eve Wilson"
    mock_patient.allergies = None

    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [mock_patient]
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_result

    result = await search_patient_local(mock_db, "clinic-1", "Luna")

    assert "Luna" in result
    assert "Cat" in result
    assert "Eve Wilson" in result


@pytest.mark.asyncio
async def test_search_local_no_matches():
    """Local DB search with no matches returns appropriate message."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_result

    result = await search_patient_local(mock_db, "clinic-1", "NonexistentPet")

    assert "couldn't find" in result.lower()
