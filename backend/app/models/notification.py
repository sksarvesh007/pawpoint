"""
Notification Model

Staff notifications for events requiring attention:
emergency calls, missed transfers, medication requests, etc.
"""

from datetime import datetime
from enum import StrEnum
from uuid import UUID as PyUUID

from sqlalchemy import Enum, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class NotificationType(StrEnum):
    """Types of staff notifications."""

    EMERGENCY_CALL = "emergency_call"
    MISSED_TRANSFER = "missed_transfer"
    MEDICATION_REQUEST = "medication_request"
    APPOINTMENT_REQUEST = "appointment_request"
    CALLBACK_NEEDED = "callback_needed"
    FAILED_DELIVERY = "failed_delivery"
    LOW_CONFIDENCE_CALL = "low_confidence_call"


class NotificationPriority(StrEnum):
    """Notification urgency levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Notification(Base, TimestampMixin):
    """
    Staff notification model.

    Tracks events that require staff attention, with read/resolve tracking.
    """

    __tablename__ = "notifications"

    clinic_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType, values_callable=lambda e: [x.value for x in e]),
        nullable=False,
        index=True,
    )
    priority: Mapped[NotificationPriority] = mapped_column(
        Enum(NotificationPriority, values_callable=lambda e: [x.value for x in e]),
        default=NotificationPriority.NORMAL,
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    metadata_json: Mapped[dict | None] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
        comment="Related entity info (call_log_id, patient_name, etc.)",
    )
    read_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    resolved_by: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        comment="User ID who resolved this notification",
    )

    def __repr__(self) -> str:
        return (
            f"<Notification(id={self.id}, type={self.type}, "
            f"priority={self.priority}, title={self.title})>"
        )
