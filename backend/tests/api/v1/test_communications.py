"""Tests for communications history API endpoints."""

from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import (
    create_call_log,
    create_conversation,
    create_message_log,
    setup_auth,
)


@pytest.mark.asyncio
async def test_list_communications_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/communications/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_communications_empty(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await setup_auth(db_session, client)
    response = await client.get("/api/v1/communications/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_list_communications_aggregates_calls_and_chats(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    clinic = await setup_auth(db_session, client)
    await create_call_log(db_session, clinic.id)
    await create_conversation(db_session, clinic.id)
    await db_session.commit()

    response = await client.get("/api/v1/communications/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2

    channels = {item["channel"] for item in data["items"]}
    assert "call" in channels
    assert "chat" in channels


@pytest.mark.asyncio
async def test_list_communications_channel_filter(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    clinic = await setup_auth(db_session, client)
    await create_call_log(db_session, clinic.id)
    await create_conversation(db_session, clinic.id)
    await db_session.commit()

    # Filter calls only
    response = await client.get("/api/v1/communications/?channel=call")
    assert response.status_code == 200
    data = response.json()
    assert all(item["channel"] == "call" for item in data["items"])

    # Filter chats only
    response = await client.get("/api/v1/communications/?channel=chat")
    assert response.status_code == 200
    data = response.json()
    assert all(item["channel"] == "chat" for item in data["items"])


@pytest.mark.asyncio
async def test_list_communications_sorted_by_time(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    clinic = await setup_auth(db_session, client)
    await create_call_log(
        db_session,
        clinic.id,
        started_at=datetime(2025, 1, 1, tzinfo=UTC),
    )
    await create_call_log(
        db_session,
        clinic.id,
        started_at=datetime(2025, 6, 1, tzinfo=UTC),
    )
    await db_session.commit()

    response = await client.get("/api/v1/communications/")
    assert response.status_code == 200
    data = response.json()
    timestamps = [item["timestamp"] for item in data["items"]]
    assert timestamps == sorted(timestamps, reverse=True)


@pytest.mark.asyncio
async def test_list_communications_includes_sms_and_email(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    clinic = await setup_auth(db_session, client)
    await create_message_log(
        db_session, clinic.id, channel="sms", recipient="+15550001111"
    )
    await create_message_log(
        db_session, clinic.id, channel="email", recipient="owner@example.com"
    )
    await db_session.commit()

    response = await client.get("/api/v1/communications/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    channels = {item["channel"] for item in data["items"]}
    assert "sms" in channels
    assert "email" in channels


@pytest.mark.asyncio
async def test_list_communications_sms_filter(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    clinic = await setup_auth(db_session, client)
    await create_message_log(db_session, clinic.id, channel="sms")
    await create_message_log(db_session, clinic.id, channel="email")
    await create_call_log(db_session, clinic.id)
    await db_session.commit()

    response = await client.get("/api/v1/communications/?channel=sms")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert all(item["channel"] == "sms" for item in data["items"])


@pytest.mark.asyncio
async def test_list_communications_invalid_channel_rejected(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await setup_auth(db_session, client)
    response = await client.get("/api/v1/communications/?channel=invalid")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_communications_pagination_total_is_accurate(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Total count must reflect all records, not just the fetched page."""
    clinic = await setup_auth(db_session, client)
    # Create 5 items across all channels
    for _ in range(3):
        await create_call_log(db_session, clinic.id)
    for _ in range(2):
        await create_message_log(db_session, clinic.id, channel="sms")
    await db_session.commit()

    # Request page 1 with limit=2 — total should still be 5
    response = await client.get("/api/v1/communications/?limit=2&page=1")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert data["total_pages"] == 3
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_list_communications_pagination_page2(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Page 2 must return different items than page 1."""
    clinic = await setup_auth(db_session, client)
    for _ in range(4):
        await create_call_log(db_session, clinic.id)
    await db_session.commit()

    page1 = (await client.get("/api/v1/communications/?limit=2&page=1")).json()
    page2 = (await client.get("/api/v1/communications/?limit=2&page=2")).json()

    ids_p1 = {item["id"] for item in page1["items"]}
    ids_p2 = {item["id"] for item in page2["items"]}
    assert ids_p1.isdisjoint(ids_p2), "Page 1 and page 2 must not share items"
    assert page2["total"] == 4
