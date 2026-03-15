"""Notification API endpoints for staff inbox."""

import asyncio
import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_clinic, get_current_user
from app.db import get_db
from app.models.clinic import Clinic
from app.models.user import User
from app.schemas.notification import (
    NotificationListResponse,
    NotificationResponse,
    UnreadCountResponse,
)
from app.services.notification import NotificationService

router = APIRouter()


@router.get(
    "/stream",
    summary="Stream unread notification count via SSE",
    response_class=StreamingResponse,
)
async def stream_notifications(
    db: AsyncSession = Depends(get_db),
    current_clinic: Clinic = Depends(get_current_clinic),
) -> StreamingResponse:
    """Stream real-time unread notification count via Server-Sent Events."""
    clinic_id = current_clinic.id

    async def event_generator():
        service = NotificationService(db)
        heartbeat_counter = 0
        try:
            while True:
                # Emit unread count every 3 seconds
                count = await service.unread_count(clinic_id)
                yield f"data: {json.dumps({'unread_count': count})}\n\n"

                heartbeat_counter += 1
                # Every 5 iterations (15s) send a heartbeat comment
                if heartbeat_counter >= 5:
                    yield ": heartbeat\n\n"
                    heartbeat_counter = 0

                await asyncio.sleep(3)
        except asyncio.CancelledError:
            pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "",
    response_model=NotificationListResponse,
    summary="List notifications",
)
async def list_notifications(
    unread_only: bool = Query(False, description="Only show unread"),
    type: str | None = Query(None, description="Filter by notification type"),
    priority: str | None = Query(None, description="Filter by priority"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_clinic: Clinic = Depends(get_current_clinic),
) -> NotificationListResponse:
    """List notifications for the current user's clinic."""
    service = NotificationService(db)
    notifications, total = await service.list(
        clinic_id=current_clinic.id,
        unread_only=unread_only,
        type_filter=type,
        priority_filter=priority,
        page=page,
        limit=limit,
    )

    return NotificationListResponse(
        notifications=[NotificationResponse.model_validate(n) for n in notifications],
        total=total,
        page=page,
        limit=limit,
    )


@router.get(
    "/unread-count",
    response_model=UnreadCountResponse,
    summary="Get unread notification count",
)
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_clinic: Clinic = Depends(get_current_clinic),
) -> UnreadCountResponse:
    """Get the number of unread notifications for badge display."""
    service = NotificationService(db)
    count = await service.unread_count(current_clinic.id)
    return UnreadCountResponse(unread_count=count)


@router.put(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    summary="Mark notification as read",
)
async def mark_notification_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NotificationResponse:
    """Mark a notification as read."""
    service = NotificationService(db)
    notification = await service.mark_read(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    await db.commit()
    await db.refresh(notification)
    return NotificationResponse.model_validate(notification)


@router.put(
    "/{notification_id}/resolve",
    response_model=NotificationResponse,
    summary="Mark notification as resolved",
)
async def mark_notification_resolved(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NotificationResponse:
    """Mark a notification as resolved by the current user."""
    service = NotificationService(db)
    notification = await service.mark_resolved(notification_id, current_user.id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    await db.commit()
    await db.refresh(notification)
    return NotificationResponse.model_validate(notification)
