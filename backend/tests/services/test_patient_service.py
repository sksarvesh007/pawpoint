"""Tests for PatientService."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clinic import Clinic
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate
from app.services.patient import PatientService


async def create_test_clinic(db: AsyncSession) -> Clinic:
    """Helper to create a test clinic."""
    clinic = Clinic(
        name=f"Test Clinic {uuid.uuid4().hex[:6]}",
        slug=f"test-{uuid.uuid4().hex[:8]}",
        timezone="America/New_York",
    )
    db.add(clinic)
    await db.flush()
    return clinic


async def create_test_patient(
    db: AsyncSession,
    clinic_id: uuid.UUID,
    name: str = "Buddy",
    species: str = "dog",
) -> Patient:
    """Helper to create a test patient."""
    patient = Patient(
        clinic_id=clinic_id,
        name=name,
        species=species,
        owner_first_name="John",
        owner_last_name="Doe",
        owner_phone="555-0100",
    )
    db.add(patient)
    await db.flush()
    return patient


@pytest.mark.asyncio
async def test_create_patient(db_session: AsyncSession) -> None:
    clinic = await create_test_clinic(db_session)
    service = PatientService(db_session)

    data = PatientCreate(
        name="Max",
        species="dog",
        breed="Labrador",
        owner_first_name="Jane",
        owner_last_name="Smith",
        owner_phone="555-0101",
    )
    patient = await service.create_patient(clinic.id, data)

    assert patient.name == "Max"
    assert patient.species.value == "dog"
    assert patient.breed == "Labrador"
    assert patient.owner_first_name == "Jane"
    assert patient.clinic_id == clinic.id


@pytest.mark.asyncio
async def test_list_patients(db_session: AsyncSession) -> None:
    clinic = await create_test_clinic(db_session)
    service = PatientService(db_session)

    # Create multiple patients
    for name in ["Alpha", "Bravo", "Charlie"]:
        await create_test_patient(db_session, clinic.id, name=name)

    patients, total = await service.list_patients(clinic.id, page=1, limit=10)

    assert total == 3
    assert len(patients) == 3


@pytest.mark.asyncio
async def test_list_patients_with_search(db_session: AsyncSession) -> None:
    clinic = await create_test_clinic(db_session)
    service = PatientService(db_session)

    await create_test_patient(db_session, clinic.id, name="Buddy")
    await create_test_patient(db_session, clinic.id, name="Bella")

    patients, total = await service.list_patients(
        clinic.id, page=1, limit=10, search="Bella"
    )

    assert total == 1
    assert patients[0].name == "Bella"


@pytest.mark.asyncio
async def test_list_patients_with_species_filter(db_session: AsyncSession) -> None:
    clinic = await create_test_clinic(db_session)
    service = PatientService(db_session)

    await create_test_patient(db_session, clinic.id, name="Doggo", species="dog")
    await create_test_patient(db_session, clinic.id, name="Kitty", species="cat")

    patients, total = await service.list_patients(
        clinic.id, page=1, limit=10, species="cat"
    )

    assert total == 1
    assert patients[0].name == "Kitty"


@pytest.mark.asyncio
async def test_get_patient(db_session: AsyncSession) -> None:
    clinic = await create_test_clinic(db_session)
    service = PatientService(db_session)

    patient = await create_test_patient(db_session, clinic.id, name="Rex")
    result = await service.get_patient(clinic.id, patient.id)

    assert result is not None
    assert result.name == "Rex"


@pytest.mark.asyncio
async def test_get_patient_not_found(db_session: AsyncSession) -> None:
    clinic = await create_test_clinic(db_session)
    service = PatientService(db_session)

    result = await service.get_patient(clinic.id, uuid.uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_update_patient(db_session: AsyncSession) -> None:
    clinic = await create_test_clinic(db_session)
    service = PatientService(db_session)

    patient = await create_test_patient(db_session, clinic.id, name="Buddy")
    data = PatientUpdate(name="Buddy Jr.", breed="Golden Retriever")
    updated = await service.update_patient(clinic.id, patient.id, data)

    assert updated is not None
    assert updated.name == "Buddy Jr."
    assert updated.breed == "Golden Retriever"


@pytest.mark.asyncio
async def test_delete_patient_soft(db_session: AsyncSession) -> None:
    clinic = await create_test_clinic(db_session)
    service = PatientService(db_session)

    patient = await create_test_patient(db_session, clinic.id, name="ToDelete")
    result = await service.delete_patient(clinic.id, patient.id)
    assert result is True

    # Should not appear in list
    _patients, total = await service.list_patients(clinic.id, page=1, limit=10)
    assert total == 0


@pytest.mark.asyncio
async def test_search_patients(db_session: AsyncSession) -> None:
    clinic = await create_test_clinic(db_session)
    service = PatientService(db_session)

    await create_test_patient(db_session, clinic.id, name="Whiskers")
    await create_test_patient(db_session, clinic.id, name="Fluffy")

    results = await service.search_patients(clinic.id, "Whisk", limit=5)
    assert len(results) == 1
    assert results[0].name == "Whiskers"


@pytest.mark.asyncio
async def test_clinic_scoping(db_session: AsyncSession) -> None:
    """Patients from one clinic should not be visible to another."""
    clinic_a = await create_test_clinic(db_session)
    clinic_b = await create_test_clinic(db_session)
    service = PatientService(db_session)

    await create_test_patient(db_session, clinic_a.id, name="ClinicA_Pet")
    await create_test_patient(db_session, clinic_b.id, name="ClinicB_Pet")

    patients_a, total_a = await service.list_patients(clinic_a.id, page=1, limit=10)
    patients_b, total_b = await service.list_patients(clinic_b.id, page=1, limit=10)

    assert total_a == 1
    assert total_b == 1
    assert patients_a[0].name == "ClinicA_Pet"
    assert patients_b[0].name == "ClinicB_Pet"
