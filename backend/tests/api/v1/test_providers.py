"""Tests for provider API endpoints."""

import uuid

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


@pytest.mark.asyncio
async def test_list_providers_empty(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await setup_auth(db_session, client)

    response = await client.get("/api/v1/providers/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_provider(client: AsyncClient, db_session: AsyncSession) -> None:
    await setup_auth(db_session, client)

    response = await client.post(
        "/api/v1/providers/",
        json={
            "first_name": "Dr. Sarah",
            "last_name": "Johnson",
            "title": "DVM",
            "specialty": "Surgery",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Dr. Sarah"
    assert data["last_name"] == "Johnson"


@pytest.mark.asyncio
async def test_create_and_get_provider(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await setup_auth(db_session, client)

    create_resp = await client.post(
        "/api/v1/providers/",
        json={
            "first_name": "Dr. Mike",
            "last_name": "Ross",
        },
    )
    assert create_resp.status_code == 201
    provider_id = create_resp.json()["id"]

    get_resp = await client.get(f"/api/v1/providers/{provider_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["first_name"] == "Dr. Mike"


@pytest.mark.asyncio
async def test_update_provider(client: AsyncClient, db_session: AsyncSession) -> None:
    await setup_auth(db_session, client)

    create_resp = await client.post(
        "/api/v1/providers/",
        json={"first_name": "Old", "last_name": "Name"},
    )
    provider_id = create_resp.json()["id"]

    update_resp = await client.put(
        f"/api/v1/providers/{provider_id}",
        json={"first_name": "New", "specialty": "Cardiology"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["first_name"] == "New"


@pytest.mark.asyncio
async def test_delete_provider(client: AsyncClient, db_session: AsyncSession) -> None:
    await setup_auth(db_session, client)

    create_resp = await client.post(
        "/api/v1/providers/",
        json={"first_name": "ToDelete", "last_name": "Vet"},
    )
    provider_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/api/v1/providers/{provider_id}")
    assert delete_resp.status_code == 204


@pytest.mark.asyncio
async def test_providers_require_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/providers/")
    assert response.status_code == 401
