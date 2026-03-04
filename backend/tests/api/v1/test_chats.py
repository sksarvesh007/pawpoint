"""Tests for chat log API endpoints."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import (
    create_chat_analysis,
    create_conversation,
    create_message,
    setup_auth,
)


@pytest.mark.asyncio
async def test_list_chats_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/chats/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_chats_empty(client: AsyncClient, db_session: AsyncSession) -> None:
    await setup_auth(db_session, client)
    response = await client.get("/api/v1/chats/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_list_chats_returns_items(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    clinic = await setup_auth(db_session, client)
    for _ in range(2):
        await create_conversation(db_session, clinic.id)

    response = await client.get("/api/v1/chats/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2

    item = data["items"][0]
    assert "id" in item
    assert "started_at" in item
    assert "user_identifier" in item
    assert "total_messages" in item


@pytest.mark.asyncio
async def test_list_chats_excludes_voice(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    clinic = await setup_auth(db_session, client)
    await create_conversation(db_session, clinic.id, channel="chat")
    await create_conversation(db_session, clinic.id, channel="voice")

    response = await client.get("/api/v1/chats/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1


@pytest.mark.asyncio
async def test_list_chats_pagination(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    clinic = await setup_auth(db_session, client)
    for _ in range(5):
        await create_conversation(db_session, clinic.id)

    response = await client.get("/api/v1/chats/?limit=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
    assert data["total_pages"] == 3


@pytest.mark.asyncio
async def test_list_chats_includes_analysis(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    clinic = await setup_auth(db_session, client)
    conv = await create_conversation(db_session, clinic.id)
    await create_chat_analysis(
        db_session,
        conv.id,
        sentiment="negative",
        resolution_status="unresolved",
        primary_topic="billing",
    )

    response = await client.get("/api/v1/chats/")
    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["sentiment"] == "negative"
    assert item["resolution_status"] == "unresolved"
    assert item["primary_topic"] == "billing"


@pytest.mark.asyncio
async def test_list_chats_analysis_null_without(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    clinic = await setup_auth(db_session, client)
    await create_conversation(db_session, clinic.id)

    response = await client.get("/api/v1/chats/")
    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["sentiment"] is None
    assert item["resolution_status"] is None
    assert item["primary_topic"] is None


@pytest.mark.asyncio
async def test_get_chat_by_id(client: AsyncClient, db_session: AsyncSession) -> None:
    clinic = await setup_auth(db_session, client)
    conv = await create_conversation(
        db_session, clinic.id, total_messages=2, intent="book_appointment"
    )
    await create_message(db_session, conv.id, role="user", content="Hi")
    await create_message(db_session, conv.id, role="assistant", content="Hello!")
    await create_chat_analysis(db_session, conv.id)

    response = await client.get(f"/api/v1/chats/{conv.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(conv.id)
    assert data["intent"] == "book_appointment"
    assert len(data["messages"]) == 2
    assert data["analysis"] is not None
    assert data["analysis"]["sentiment"] == "positive"


@pytest.mark.asyncio
async def test_get_chat_not_found(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await setup_auth(db_session, client)
    response = await client.get(f"/api/v1/chats/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_chat_messages_ordered(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    clinic = await setup_auth(db_session, client)
    conv = await create_conversation(db_session, clinic.id, total_messages=3)

    # Create messages with explicit timestamps to guarantee order
    base = datetime(2026, 1, 1, 10, 0, 0, tzinfo=UTC)
    await create_message(db_session, conv.id, content="first", created_at=base)
    await create_message(
        db_session, conv.id, content="second", created_at=base + timedelta(minutes=1)
    )
    await create_message(
        db_session, conv.id, content="third", created_at=base + timedelta(minutes=2)
    )

    response = await client.get(f"/api/v1/chats/{conv.id}")
    assert response.status_code == 200
    messages = response.json()["messages"]
    assert len(messages) == 3
    assert messages[0]["content"] == "first"
    assert messages[1]["content"] == "second"
    assert messages[2]["content"] == "third"
