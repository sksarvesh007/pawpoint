"""Notification schemas for request/response validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class NotificationResponse(BaseModel):
    """Response schema for a single notification."""

    id: UUID
    clinic_id: UUID
    type: str
    priority: str
    title: str
    message: str
    metadata: dict | None = Field(None, alias="metadata_json")
    read_at: datetime | None = None
    resolved_at: datetime | None = None
    resolved_by: UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class NotificationListResponse(BaseModel):
    """Paginated list of notifications."""

    notifications: list[NotificationResponse]
    total: int
    page: int
    limit: int


class UnreadCountResponse(BaseModel):
    """Unread notification count for badge display."""

    unread_count: int
