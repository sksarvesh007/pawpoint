"""
Call Log Model

Records all inbound and outbound phone calls handled by the AI voice assistant.
Stores transcripts, recordings, and call outcomes.
"""

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID as PyUUID

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.appointment import Appointment
    from app.models.clinic import Clinic


class CallDirection(StrEnum):
    """Direction of the call."""

    INBOUND = "inbound"  # Client called the clinic
    OUTBOUND = "outbound"  # Clinic/AI called the client


class CallStatus(StrEnum):
    """Status of the call."""

    RINGING = "ringing"  # Call is ringing
    IN_PROGRESS = "in_progress"  # Call is active
    COMPLETED = "completed"  # Call ended normally
    FAILED = "failed"  # Call failed to connect
    BUSY = "busy"  # Line was busy
    NO_ANSWER = "no_answer"  # No one answered
    VOICEMAIL = "voicemail"  # Went to voicemail
    TRANSFERRED = "transferred"  # Transferred to human


class CallOutcome(StrEnum):
    """Outcome/result of the call."""

    APPOINTMENT_BOOKED = "appointment_booked"
    APPOINTMENT_CANCELLED = "appointment_cancelled"
    APPOINTMENT_RESCHEDULED = "appointment_rescheduled"
    INFORMATION_PROVIDED = "information_provided"
    MESSAGE_TAKEN = "message_taken"
    TRANSFERRED_TO_STAFF = "transferred_to_staff"
    EMERGENCY_TRANSFER = "emergency_transfer"
    NO_ACTION_NEEDED = "no_action_needed"
    FOLLOW_UP_REQUIRED = "follow_up_required"
    VOICEMAIL_LEFT = "voicemail_left"
    CALL_DROPPED = "call_dropped"
    OTHER = "other"


class CallChannel(StrEnum):
    """Channel through which the call was made."""

    PHONE = "phone"  # Traditional phone call via Twilio SIP
    WEB_VOICE = "web_voice"  # Browser-based voice widget via WebRTC


class CallLog(Base, TimestampMixin, SoftDeleteMixin):
    """
    Call log model.

    Records all voice AI interactions including transcripts and outcomes.
    Links to appointments created during the call.
    """

    __tablename__ = "call_logs"

    # Foreign keys
    clinic_id: Mapped[PyUUID] = mapped_column(
        ForeignKey("clinics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Call identification (Twilio-specific)
    twilio_call_sid: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        unique=True,
        index=True,
        comment="Twilio Call SID for reference",
    )

    # LiveKit identification
    livekit_room_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="LiveKit room name for the call session",
    )
    livekit_participant_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="LiveKit participant ID for the caller",
    )

    # Call channel (phone vs web voice)
    channel: Mapped[CallChannel] = mapped_column(
        Enum(CallChannel, values_callable=lambda e: [x.value for x in e]),
        default=CallChannel.PHONE,
        nullable=False,
        index=True,
        comment="Channel: phone (Twilio SIP) or web_voice (WebRTC)",
    )

    # Call details
    direction: Mapped[CallDirection] = mapped_column(
        Enum(CallDirection, values_callable=lambda e: [x.value for x in e]),
        nullable=False,
        index=True,
    )
    status: Mapped[CallStatus] = mapped_column(
        Enum(CallStatus, values_callable=lambda e: [x.value for x in e]),
        default=CallStatus.IN_PROGRESS,
        nullable=False,
        index=True,
    )
    outcome: Mapped[CallOutcome | None] = mapped_column(
        Enum(CallOutcome, values_callable=lambda e: [x.value for x in e]),
        nullable=True,
        index=True,
    )

    # Phone numbers
    from_phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="Caller phone number (E.164 format)",
    )
    to_phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Recipient phone number",
    )

    # Caller identification
    caller_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Identified caller name (from patient lookup)",
    )
    patient_id_matched: Mapped[PyUUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        nullable=True,
        comment="Patient ID if caller was matched to existing patient",
    )

    # Timing
    started_at: Mapped[datetime] = mapped_column(nullable=False, index=True)
    ended_at: Mapped[datetime | None] = mapped_column(nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Total call duration in seconds",
    )
    ring_duration_seconds: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Time spent ringing before answer",
    )

    # AI interaction
    ai_handled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether AI handled the call (vs transferred immediately)",
    )
    ai_confidence_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="AI confidence in its handling (0-1)",
    )

    # Transcript and content
    transcript: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Full conversation transcript",
    )
    transcript_structured: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Structured transcript with speaker labels and timestamps",
    )
    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="AI-generated call summary",
    )
    key_points: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Extracted key points from the call",
    )

    # Recording
    recording_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="URL to call recording (S3/Twilio)",
    )
    recording_duration_seconds: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # Actions taken during call
    actions_taken: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="List of actions taken during call (function calls)",
    )

    # Transfer details (if transferred)
    transferred_to: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Phone number transferred to",
    )
    transfer_reason: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    # Error tracking
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Error message if call failed",
    )

    # Staff review
    reviewed_by_user_id: Mapped[PyUUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        nullable=True,
        comment="Staff member who reviewed the call",
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    requires_follow_up: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    # Additional data
    extra_data: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Additional call metadata",
    )

    # Relationships
    clinic: Mapped["Clinic"] = relationship(back_populates="call_logs")
    appointment: Mapped["Appointment | None"] = relationship(
        back_populates="call_log",
        foreign_keys="Appointment.call_log_id",
        uselist=False,
    )

    @property
    def is_emergency(self) -> bool:
        """Check if this was an emergency call."""
        return self.outcome == CallOutcome.EMERGENCY_TRANSFER

    @property
    def needs_review(self) -> bool:
        """Check if call needs staff review."""
        return (
            self.requires_follow_up
            or self.outcome == CallOutcome.FOLLOW_UP_REQUIRED
            or (self.ai_confidence_score is not None and self.ai_confidence_score < 0.7)
        )

    def __repr__(self) -> str:
        return (
            f"<CallLog(id={self.id}, "
            f"direction={self.direction}, "
            f"outcome={self.outcome}, "
            f"duration={self.duration_seconds}s)>"
        )

    # Composite indexes for common queries
    __table_args__ = (
        Index("ix_call_logs_clinic_date", "clinic_id", "started_at"),
        Index("ix_call_logs_clinic_outcome", "clinic_id", "outcome"),
        Index("ix_call_logs_follow_up", "clinic_id", "requires_follow_up"),
        Index("ix_call_logs_clinic_channel", "clinic_id", "channel"),
    )
