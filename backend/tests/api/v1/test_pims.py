"""Tests for PIMS settings API endpoints."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clinic import Clinic


async def setup_auth(db: AsyncSession, client: AsyncClient) -> Clinic:
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

    return clinic


@pytest.mark.asyncio
async def test_get_pims_status(client: AsyncClient, db_session: AsyncSession) -> None:
    await setup_auth(db_session, client)

    response = await client.get("/api/v1/pims/status")
    assert response.status_code == 200
    data = response.json()
    assert "pims_type" in data
    assert "connection_status" in data


@pytest.mark.asyncio
async def test_get_sync_logs(client: AsyncClient, db_session: AsyncSession) -> None:
    await setup_auth(db_session, client)

    response = await client.get("/api/v1/pims/sync-logs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_pims_require_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/pims/status")
    assert response.status_code == 401
