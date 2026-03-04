"""Tests for clinic API endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import setup_auth


@pytest.mark.asyncio
async def test_get_clinic_me_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/clinics/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_clinic_me(client: AsyncClient, db_session: AsyncSession) -> None:
    clinic = await setup_auth(db_session, client)
    response = await client.get("/api/v1/clinics/me")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(clinic.id)
    assert data["name"] == clinic.name
    assert data["slug"] == clinic.slug


@pytest.mark.asyncio
async def test_get_chatbot_settings_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/clinics/chatbot-settings")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_chatbot_settings_defaults(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await setup_auth(db_session, client)
    response = await client.get("/api/v1/clinics/chatbot-settings")
    assert response.status_code == 200
    data = response.json()
    assert data["chatbot_persona"] == "professional"
    assert "emergency_handling" in data
    assert "appointment_preferences" in data


@pytest.mark.asyncio
async def test_update_chatbot_settings(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await setup_auth(db_session, client)
    response = await client.put(
        "/api/v1/clinics/chatbot-settings",
        json={
            "chatbot_persona": "friendly",
            "greeting_message": "Hello there! How can we help your pet today?",
            "chatbot_name": "PawBot",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["chatbot_persona"] == "friendly"
    assert data["chatbot_name"] == "PawBot"
    assert "How can we help" in data["greeting_message"]


@pytest.mark.asyncio
async def test_update_chatbot_settings_persists(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await setup_auth(db_session, client)
    await client.put(
        "/api/v1/clinics/chatbot-settings",
        json={
            "chatbot_persona": "empathetic",
            "greeting_message": "We care about your pet. How can we assist you today?",
            "chatbot_name": "CarePaw",
        },
    )

    response = await client.get("/api/v1/clinics/chatbot-settings")
    assert response.status_code == 200
    data = response.json()
    assert data["chatbot_persona"] == "empathetic"
    assert data["chatbot_name"] == "CarePaw"


@pytest.mark.asyncio
async def test_update_chatbot_settings_contact_info(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await setup_auth(db_session, client)
    response = await client.put(
        "/api/v1/clinics/chatbot-settings",
        json={
            "chatbot_persona": "professional",
            "greeting_message": "Thank you for contacting us. How may I assist you?",
            "phone": "555-0100",
            "email": "clinic@example.com",
            "address": "123 Vet Lane",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["phone"] == "555-0100"
    assert data["email"] == "clinic@example.com"
    assert data["address"] == "123 Vet Lane"


@pytest.mark.asyncio
async def test_update_chatbot_settings_requires_auth(client: AsyncClient) -> None:
    response = await client.put(
        "/api/v1/clinics/chatbot-settings",
        json={
            "chatbot_persona": "friendly",
            "greeting_message": "Hello there! How can we help your pet today?",
        },
    )
    assert response.status_code == 401
