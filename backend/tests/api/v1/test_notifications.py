"""Tests for notification API endpoints."""

from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import NotificationPriority, NotificationType
from tests.helpers import create_notification, setup_auth


@pytest.mark.asyncio
async def test_list_notifications_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/notifications")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_notifications_empty(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await setup_auth(db_session, client)
    response = await client.get("/api/v1/notifications")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["notifications"] == []


@pytest.mark.asyncio
async def test_list_notifications_returns_items(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    clinic = await setup_auth(db_session, client)
    await create_notification(db_session, clinic.id)
    await create_notification(
        db_session,
        clinic.id,
        type=NotificationType.EMERGENCY_CALL,
        priority=NotificationPriority.URGENT,
        title="Emergency",
    )
    await db_session.commit()

    response = await client.get("/api/v1/notifications")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2


@pytest.mark.asyncio
async def test_unread_count(client: AsyncClient, db_session: AsyncSession) -> None:
    clinic = await setup_auth(db_session, client)
    await create_notification(db_session, clinic.id)
    await create_notification(db_session, clinic.id)
    # Mark one as read
    n3 = await create_notification(db_session, clinic.id)
    n3.read_at = datetime.now(UTC)
    await db_session.commit()

    response = await client.get("/api/v1/notifications/unread-count")
    assert response.status_code == 200
    data = response.json()
    assert data["unread_count"] == 2


@pytest.mark.asyncio
async def test_mark_read(client: AsyncClient, db_session: AsyncSession) -> None:
    clinic = await setup_auth(db_session, client)
    n = await create_notification(db_session, clinic.id)
    await db_session.commit()

    response = await client.put(f"/api/v1/notifications/{n.id}/read")
    assert response.status_code == 200
    data = response.json()
    assert data["read_at"] is not None


@pytest.mark.asyncio
async def test_mark_resolved(client: AsyncClient, db_session: AsyncSession) -> None:
    clinic = await setup_auth(db_session, client)
    n = await create_notification(db_session, clinic.id)
    await db_session.commit()

    response = await client.put(f"/api/v1/notifications/{n.id}/resolve")
    assert response.status_code == 200
    data = response.json()
    assert data["resolved_at"] is not None


@pytest.mark.asyncio
async def test_list_notifications_unread_filter(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    clinic = await setup_auth(db_session, client)
    await create_notification(db_session, clinic.id)
    n_read = await create_notification(db_session, clinic.id)
    n_read.read_at = datetime.now(UTC)
    await db_session.commit()

    response = await client.get("/api/v1/notifications?unread_only=true")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1


@pytest.mark.asyncio
async def test_list_notifications_type_filter(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    clinic = await setup_auth(db_session, client)
    await create_notification(db_session, clinic.id)
    await create_notification(
        db_session,
        clinic.id,
        type=NotificationType.EMERGENCY_CALL,
    )
    await db_session.commit()

    response = await client.get("/api/v1/notifications?type=emergency_call")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1


@pytest.mark.asyncio
async def test_notifications_clinic_scoping(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Notifications from other clinics should not be visible."""
    from tests.helpers import create_test_clinic

    clinic = await setup_auth(db_session, client)
    other_clinic = await create_test_clinic(db_session)

    await create_notification(db_session, clinic.id)
    await create_notification(db_session, other_clinic.id)
    await db_session.commit()

    response = await client.get("/api/v1/notifications")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
