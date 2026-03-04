"""Tests for ProviderService."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clinic import Clinic
from app.models.provider import Provider
from app.schemas.provider import ProviderCreate, ProviderUpdate
from app.services.provider import ProviderService


async def create_test_clinic(db: AsyncSession) -> Clinic:
    clinic = Clinic(
        name=f"Test Clinic {uuid.uuid4().hex[:6]}",
        slug=f"test-{uuid.uuid4().hex[:8]}",
        timezone="America/New_York",
    )
    db.add(clinic)
    await db.flush()
    return clinic


@pytest.mark.asyncio
async def test_create_provider(db_session: AsyncSession) -> None:
    clinic = await create_test_clinic(db_session)
    service = ProviderService(db_session)

    data = ProviderCreate(
        first_name="Dr. Sarah",
        last_name="Johnson",
        title="DVM",
        specialty="Surgery",
    )
    provider = await service.create_provider(clinic.id, data)

    assert provider.first_name == "Dr. Sarah"
    assert provider.last_name == "Johnson"
    assert provider.title == "DVM"
    assert provider.clinic_id == clinic.id


@pytest.mark.asyncio
async def test_list_providers(db_session: AsyncSession) -> None:
    clinic = await create_test_clinic(db_session)
    service = ProviderService(db_session)

    for name in ["Alice", "Bob"]:
        provider = Provider(
            clinic_id=clinic.id,
            first_name=name,
            last_name="Vet",
            is_active=True,
        )
        db_session.add(provider)
    await db_session.flush()

    providers = await service.list_providers(clinic.id, active_only=True)
    assert len(providers) == 2


@pytest.mark.asyncio
async def test_list_providers_active_only(db_session: AsyncSession) -> None:
    clinic = await create_test_clinic(db_session)
    service = ProviderService(db_session)

    active = Provider(
        clinic_id=clinic.id, first_name="Active", last_name="Vet", is_active=True
    )
    inactive = Provider(
        clinic_id=clinic.id, first_name="Inactive", last_name="Vet", is_active=False
    )
    db_session.add_all([active, inactive])
    await db_session.flush()

    active_providers = await service.list_providers(clinic.id, active_only=True)
    all_providers = await service.list_providers(clinic.id, active_only=False)

    assert len(active_providers) == 1
    assert len(all_providers) == 2


@pytest.mark.asyncio
async def test_get_provider(db_session: AsyncSession) -> None:
    clinic = await create_test_clinic(db_session)
    service = ProviderService(db_session)

    provider = Provider(
        clinic_id=clinic.id, first_name="Doc", last_name="McStuffins", is_active=True
    )
    db_session.add(provider)
    await db_session.flush()

    result = await service.get_provider(clinic.id, provider.id)
    assert result is not None
    assert result.first_name == "Doc"


@pytest.mark.asyncio
async def test_get_provider_not_found(db_session: AsyncSession) -> None:
    clinic = await create_test_clinic(db_session)
    service = ProviderService(db_session)

    result = await service.get_provider(clinic.id, uuid.uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_update_provider(db_session: AsyncSession) -> None:
    clinic = await create_test_clinic(db_session)
    service = ProviderService(db_session)

    provider = Provider(
        clinic_id=clinic.id, first_name="Old", last_name="Name", is_active=True
    )
    db_session.add(provider)
    await db_session.flush()

    data = ProviderUpdate(first_name="New", specialty="Dentistry")
    updated = await service.update_provider(clinic.id, provider.id, data)

    assert updated is not None
    assert updated.first_name == "New"
    assert updated.specialty == "Dentistry"


@pytest.mark.asyncio
async def test_delete_provider_soft(db_session: AsyncSession) -> None:
    clinic = await create_test_clinic(db_session)
    service = ProviderService(db_session)

    provider = Provider(
        clinic_id=clinic.id, first_name="Gone", last_name="Vet", is_active=True
    )
    db_session.add(provider)
    await db_session.flush()

    result = await service.delete_provider(clinic.id, provider.id)
    assert result is True

    # Should not appear in active list
    providers = await service.list_providers(clinic.id, active_only=True)
    assert len(providers) == 0
