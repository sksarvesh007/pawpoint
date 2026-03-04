"""Tests for patient API endpoints."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clinic import Clinic


async def setup_auth(db: AsyncSession, client: AsyncClient) -> tuple[Clinic, str]:
    """Create a clinic + user and log in, returning (clinic, token)."""
    clinic = Clinic(
        name=f"TestClinic-{uuid.uuid4().hex[:6]}",
        slug=f"test-{uuid.uuid4().hex[:8]}",
        timezone="America/New_York",
    )
    db.add(clinic)
    await db.flush()

    # Register and login
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


@pytest.mark.asyncio
async def test_list_patients_empty(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    _clinic, _ = await setup_auth(db_session, client)

    response = await client.get("/api/v1/patients/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_create_patient(client: AsyncClient, db_session: AsyncSession) -> None:
    _clinic, _ = await setup_auth(db_session, client)

    response = await client.post(
        "/api/v1/patients/",
        json={
            "name": "Buddy",
            "species": "dog",
            "breed": "Labrador",
            "owner_first_name": "John",
            "owner_last_name": "Doe",
            "owner_phone": "555-0101",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Buddy"
    assert data["species"] == "dog"


@pytest.mark.asyncio
async def test_create_and_get_patient(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    _clinic, _ = await setup_auth(db_session, client)

    create_resp = await client.post(
        "/api/v1/patients/",
        json={
            "name": "Max",
            "species": "cat",
            "owner_first_name": "Jane",
            "owner_last_name": "Smith",
            "owner_phone": "555-0102",
        },
    )
    assert create_resp.status_code == 201
    patient_id = create_resp.json()["id"]

    get_resp = await client.get(f"/api/v1/patients/{patient_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Max"


@pytest.mark.asyncio
async def test_delete_patient(client: AsyncClient, db_session: AsyncSession) -> None:
    _clinic, _ = await setup_auth(db_session, client)

    create_resp = await client.post(
        "/api/v1/patients/",
        json={
            "name": "ToDelete",
            "species": "dog",
            "owner_first_name": "A",
            "owner_last_name": "B",
            "owner_phone": "555-0103",
        },
    )
    patient_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/api/v1/patients/{patient_id}")
    assert delete_resp.status_code == 204


@pytest.mark.asyncio
async def test_patients_require_auth(client: AsyncClient) -> None:
    """Unauthenticated requests should fail."""
    response = await client.get("/api/v1/patients/")
    assert response.status_code == 401
