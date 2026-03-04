"""Conversation model for AI chat history and state management.

Stores conversation metadata, session info, and links to messages.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.chat_analysis import ChatAnalysis
    from app.models.clinic import Clinic
    from app.models.message import Message


class Conversation(Base, TimestampMixin):
    """Conversation session for AI interactions.

    Tracks multi-turn conversations across voice, chat, and email channels.
    Session data is cached in Redis for active conversations, with full
    history persisted here in PostgreSQL.
    """

    __tablename__ = "conversations"

    # Relationship to clinic
    clinic_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("clinics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    clinic: Mapped["Clinic"] = relationship("Clinic", back_populates="conversations")

    # Channel and user identification
    channel: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="Communication channel: voice, chat, or email",
    )
    user_identifier: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Phone number, email, or user ID",
    )

    # Conversation state
    current_agent: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Currently active agent: router, appointment, patient_record, etc.",
    )
    intent: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Detected user intent: book_appointment, ask_question, etc.",
    )

    # Session metadata
    session_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
        index=True,
        comment="Whether conversation session is still active",
    )
    session_ended_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
        comment="When the conversation session ended",
    )

    # Contextual data (flexible JSON storage)
    context: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Flexible context data: patient_id, appointment_id, etc.",
    )

    # Conversation extra data
    extra_data: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Additional metadata: device, location, referrer, etc.",
    )

    # Usage tracking
    total_messages: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total number of messages in conversation",
    )
    total_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total tokens used across all LLM calls",
    )

    # Summary for analytics
    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="AI-generated summary of conversation (created on session end)",
    )

    # Relationships
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )
    analysis: Mapped["ChatAnalysis | None"] = relationship(
        "ChatAnalysis",
        back_populates="conversation",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # Indexes for common queries
    __table_args__ = (
        Index("ix_conversations_clinic_channel", "clinic_id", "channel"),
        Index("ix_conversations_clinic_user", "clinic_id", "user_identifier"),
        Index(
            "ix_conversations_active_sessions",
            "clinic_id",
            "session_active",
            "updated_at",
        ),
    )

    def __repr__(self) -> str:
        """String representation of conversation."""
        return (
            f"<Conversation(id={self.id}, channel={self.channel}, "
            f"user={self.user_identifier}, active={self.session_active})>"
        )
