"""
MessageLog Model

Tracks all outbound SMS and email messages sent by the platform.
"""

from uuid import UUID as PyUUID

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class MessageLog(Base, TimestampMixin):
    """
    Log of outbound SMS and email messages.

    Tracks delivery status and links to related entities
    (e.g., appointment confirmations, reminders).
    """

    __tablename__ = "message_logs"

    clinic_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    channel: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="sms or email",
    )
    recipient: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Phone number or email address",
    )
    subject: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    body: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="sent",
        comment="sent, delivered, failed",
    )
    external_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Twilio SID or SendGrid Message ID",
    )
    related_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="appointment_confirmation, reminder, clinic_info",
    )
    related_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    def __repr__(self) -> str:
        return (
            f"<MessageLog(id={self.id}, channel={self.channel}, "
            f"recipient={self.recipient}, status={self.status})>"
        )
