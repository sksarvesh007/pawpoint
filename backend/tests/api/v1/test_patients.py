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

    return clinic, login_resp.cookies.get("access_token") or ""


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


@pytest.mark.asyncio
async def test_search_patients(client: AsyncClient, db_session: AsyncSession) -> None:
    """Search by patient name returns matching patients."""
    _clinic, _ = await setup_auth(db_session, client)

    await client.post(
        "/api/v1/patients/",
        json={
            "name": "Whiskers",
            "species": "cat",
            "owner_first_name": "Alice",
            "owner_last_name": "Wong",
            "owner_phone": "555-0201",
        },
    )

    response = await client.get("/api/v1/patients/search", params={"q": "Whiskers"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(p["name"] == "Whiskers" for p in data)


@pytest.mark.asyncio
async def test_search_patients_by_owner(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Search by owner last name returns matching patients."""
    _clinic, _ = await setup_auth(db_session, client)

    await client.post(
        "/api/v1/patients/",
        json={
            "name": "Rex",
            "species": "dog",
            "owner_first_name": "Bob",
            "owner_last_name": "Kowalski",
            "owner_phone": "555-0202",
        },
    )

    response = await client.get("/api/v1/patients/search", params={"q": "Kowalski"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(p["owner_last_name"] == "Kowalski" for p in data)


@pytest.mark.asyncio
async def test_search_patients_no_results(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Search for a nonexistent name returns an empty list."""
    _clinic, _ = await setup_auth(db_session, client)

    response = await client.get(
        "/api/v1/patients/search", params={"q": "ZzZzNonExistentPet99"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data == []


@pytest.mark.asyncio
async def test_list_patients_filter_by_species(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Filtering by species=dog returns only dogs."""
    _clinic, _ = await setup_auth(db_session, client)

    await client.post(
        "/api/v1/patients/",
        json={
            "name": "Fido",
            "species": "dog",
            "owner_first_name": "Carol",
            "owner_last_name": "Adams",
            "owner_phone": "555-0301",
        },
    )
    await client.post(
        "/api/v1/patients/",
        json={
            "name": "Mittens",
            "species": "cat",
            "owner_first_name": "Carol",
            "owner_last_name": "Adams",
            "owner_phone": "555-0302",
        },
    )

    response = await client.get("/api/v1/patients/", params={"species": "dog"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert item["species"] == "dog"
    names = [p["name"] for p in data["items"]]
    assert "Fido" in names
    assert "Mittens" not in names


@pytest.mark.asyncio
async def test_list_patients_pagination(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Creating 5 patients and fetching with limit=2 returns correct pagination info."""
    _clinic, _ = await setup_auth(db_session, client)

    for i in range(5):
        await client.post(
            "/api/v1/patients/",
            json={
                "name": f"PaginationPet{i}",
                "species": "dog",
                "owner_first_name": "Dave",
                "owner_last_name": "Page",
                "owner_phone": f"555-04{i:02d}",
            },
        )

    response = await client.get("/api/v1/patients/", params={"limit": 2, "page": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 5
    assert len(data["items"]) == 2
    assert data["limit"] == 2
    assert data["page"] == 1


@pytest.mark.asyncio
async def test_get_patient_not_found(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """GET a random UUID returns 404."""
    _clinic, _ = await setup_auth(db_session, client)

    random_id = str(uuid.uuid4())
    response = await client.get(f"/api/v1/patients/{random_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_patient_not_found(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """DELETE a random UUID returns 404."""
    _clinic, _ = await setup_auth(db_session, client)

    random_id = str(uuid.uuid4())
    response = await client.delete(f"/api/v1/patients/{random_id}")
    assert response.status_code == 404
