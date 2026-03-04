"""Tests for appointment API endpoints."""

import uuid
from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clinic import Clinic


async def setup_auth(db: AsyncSession, client: AsyncClient) -> tuple[Clinic, str]:
    """Create a clinic + user and log in."""
    clinic = Clinic(
        name=f"TestClinic-{uuid.uuid4().hex[:6]}",
        slug=f"test-{uuid.uuid4().hex[:8]}",
        timezone="America/New_York",
    )
    db.add(clinic)
    await db.flush()

    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    register_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "TestPass123!",
            "clinic_name": clinic.name,
        },
    )
    assert register_resp.status_code == 201

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "TestPass123!"},
    )
    assert login_resp.status_code == 200

    return clinic, login_resp.cookies.get("access_token", "")


async def create_patient_and_provider(
    client: AsyncClient,
) -> tuple[str, str]:
    """Create a test patient and provider via API, returning their IDs."""
    patient_resp = await client.post(
        "/api/v1/patients/",
        json={
            "name": "TestPet",
            "species": "dog",
            "owner_first_name": "Test",
            "owner_last_name": "Owner",
            "owner_phone": "555-0200",
        },
    )
    assert patient_resp.status_code == 201

    provider_resp = await client.post(
        "/api/v1/providers/",
        json={"first_name": "Dr. Test", "last_name": "Vet"},
    )
    assert provider_resp.status_code == 201

    return patient_resp.json()["id"], provider_resp.json()["id"]


@pytest.mark.asyncio
async def test_list_appointments_empty(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await setup_auth(db_session, client)

    response = await client.get("/api/v1/appointments/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_create_appointment(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await setup_auth(db_session, client)
    patient_id, provider_id = await create_patient_and_provider(client)

    start = (datetime.now() + timedelta(days=1)).isoformat()
    end = (datetime.now() + timedelta(days=1, minutes=30)).isoformat()

    response = await client.post(
        "/api/v1/appointments/",
        json={
            "patient_id": patient_id,
            "provider_id": provider_id,
            "start_time": start,
            "end_time": end,
            "appointment_type": "checkup",
            "reason": "Annual exam",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["reason"] == "Annual exam"


@pytest.mark.asyncio
async def test_get_appointment(client: AsyncClient, db_session: AsyncSession) -> None:
    await setup_auth(db_session, client)
    patient_id, provider_id = await create_patient_and_provider(client)

    start = (datetime.now() + timedelta(days=2)).isoformat()
    end = (datetime.now() + timedelta(days=2, minutes=30)).isoformat()

    create_resp = await client.post(
        "/api/v1/appointments/",
        json={
            "patient_id": patient_id,
            "provider_id": provider_id,
            "start_time": start,
            "end_time": end,
            "appointment_type": "vaccination",
        },
    )
    appt_id = create_resp.json()["id"]

    get_resp = await client.get(f"/api/v1/appointments/{appt_id}")
    assert get_resp.status_code == 200


@pytest.mark.asyncio
async def test_update_appointment_status(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await setup_auth(db_session, client)
    patient_id, provider_id = await create_patient_and_provider(client)

    start = (datetime.now() + timedelta(days=3)).isoformat()
    end = (datetime.now() + timedelta(days=3, minutes=30)).isoformat()

    create_resp = await client.post(
        "/api/v1/appointments/",
        json={
            "patient_id": patient_id,
            "provider_id": provider_id,
            "start_time": start,
            "end_time": end,
            "appointment_type": "checkup",
        },
    )
    appt_id = create_resp.json()["id"]

    status_resp = await client.patch(
        f"/api/v1/appointments/{appt_id}/status",
        json={"status": "confirmed"},
    )
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "confirmed"


@pytest.mark.asyncio
async def test_today_appointments(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await setup_auth(db_session, client)

    response = await client.get("/api/v1/appointments/today")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_appointments_require_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/appointments/")
    assert response.status_code == 401
