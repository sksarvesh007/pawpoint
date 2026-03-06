"""Tests for AppointmentService."""

import uuid
from datetime import datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment import Appointment
from app.models.clinic import Clinic
from app.models.patient import Patient
from app.models.provider import Provider
from app.schemas.appointment import AppointmentCreate
from app.services.appointment import AppointmentService


async def create_test_clinic(db: AsyncSession) -> Clinic:
    clinic = Clinic(
        name=f"Test Clinic {uuid.uuid4().hex[:6]}",
        slug=f"test-{uuid.uuid4().hex[:8]}",
        timezone="America/New_York",
    )
    db.add(clinic)
    await db.flush()
    return clinic


async def create_test_patient(db: AsyncSession, clinic_id: uuid.UUID) -> Patient:
    patient = Patient(
        clinic_id=clinic_id,
        name="TestPet",
        species="dog",
        owner_first_name="Test",
        owner_last_name="Owner",
        owner_phone="555-0100",
    )
    db.add(patient)
    await db.flush()
    return patient


async def create_test_provider(db: AsyncSession, clinic_id: uuid.UUID) -> Provider:
    provider = Provider(
        clinic_id=clinic_id,
        first_name="Dr. Test",
        last_name="Vet",
        is_active=True,
    )
    db.add(provider)
    await db.flush()
    return provider


@pytest.mark.asyncio
async def test_create_appointment(db_session: AsyncSession) -> None:
    clinic = await create_test_clinic(db_session)
    patient = await create_test_patient(db_session, clinic.id)
    provider = await create_test_provider(db_session, clinic.id)
    service = AppointmentService(db_session)

    start = datetime.now() + timedelta(days=1)
    end = start + timedelta(minutes=30)

    data = AppointmentCreate(
        patient_id=patient.id,
        provider_id=provider.id,
        start_time=start.isoformat(),
        end_time=end.isoformat(),
        appointment_type="checkup",
        reason="Annual wellness exam",
    )
    appointment = await service.create_appointment(clinic.id, data)

    assert appointment.patient_id == patient.id
    assert appointment.provider_id == provider.id
    assert appointment.reason == "Annual wellness exam"


@pytest.mark.asyncio
async def test_list_appointments(db_session: AsyncSession) -> None:
    clinic = await create_test_clinic(db_session)
    patient = await create_test_patient(db_session, clinic.id)
    provider = await create_test_provider(db_session, clinic.id)
    service = AppointmentService(db_session)

    # Create two appointments
    for i in range(2):
        start = datetime.now() + timedelta(days=i + 1)
        end = start + timedelta(minutes=30)
        appt = Appointment(
            clinic_id=clinic.id,
            patient_id=patient.id,
            provider_id=provider.id,
            start_time=start,
            end_time=end,
            appointment_type="checkup",
            status="scheduled",
        )
        db_session.add(appt)
    await db_session.flush()

    appointments, total = await service.list_appointments(clinic.id, page=1, limit=10)

    assert total == 2
    assert len(appointments) == 2


@pytest.mark.asyncio
async def test_get_appointment(db_session: AsyncSession) -> None:
    clinic = await create_test_clinic(db_session)
    patient = await create_test_patient(db_session, clinic.id)
    provider = await create_test_provider(db_session, clinic.id)

    start = datetime.now() + timedelta(days=1)
    appt = Appointment(
        clinic_id=clinic.id,
        patient_id=patient.id,
        provider_id=provider.id,
        start_time=start,
        end_time=start + timedelta(minutes=30),
        appointment_type="vaccination",
        status="scheduled",
    )
    db_session.add(appt)
    await db_session.flush()

    service = AppointmentService(db_session)
    result = await service.get_appointment(clinic.id, appt.id)

    assert result is not None
    assert result["appointment_type"] == "vaccination"


@pytest.mark.asyncio
async def test_get_appointment_not_found(db_session: AsyncSession) -> None:
    clinic = await create_test_clinic(db_session)
    service = AppointmentService(db_session)

    result = await service.get_appointment(clinic.id, uuid.uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_update_appointment_status(db_session: AsyncSession) -> None:
    clinic = await create_test_clinic(db_session)
    patient = await create_test_patient(db_session, clinic.id)
    provider = await create_test_provider(db_session, clinic.id)

    start = datetime.now() + timedelta(days=1)
    appt = Appointment(
        clinic_id=clinic.id,
        patient_id=patient.id,
        provider_id=provider.id,
        start_time=start,
        end_time=start + timedelta(minutes=30),
        appointment_type="checkup",
        status="scheduled",
    )
    db_session.add(appt)
    await db_session.flush()

    service = AppointmentService(db_session)
    updated = await service.update_status(clinic.id, appt.id, "confirmed")

    assert updated is not None
    assert updated.status.value == "confirmed"


@pytest.mark.asyncio
async def test_clinic_scoping(db_session: AsyncSession) -> None:
    """Appointments from one clinic should not be visible to another."""
    clinic_a = await create_test_clinic(db_session)
    clinic_b = await create_test_clinic(db_session)
    patient_a = await create_test_patient(db_session, clinic_a.id)
    provider_a = await create_test_provider(db_session, clinic_a.id)

    start = datetime.now() + timedelta(days=1)
    appt = Appointment(
        clinic_id=clinic_a.id,
        patient_id=patient_a.id,
        provider_id=provider_a.id,
        start_time=start,
        end_time=start + timedelta(minutes=30),
        appointment_type="checkup",
        status="scheduled",
    )
    db_session.add(appt)
    await db_session.flush()

    service = AppointmentService(db_session)

    # Clinic A should see it
    result_a = await service.get_appointment(clinic_a.id, appt.id)
    assert result_a is not None

    # Clinic B should not
    result_b = await service.get_appointment(clinic_b.id, appt.id)
    assert result_b is None
