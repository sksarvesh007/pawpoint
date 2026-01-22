"""
Appointment Model

Represents scheduled appointments between patients and providers.
The core entity for PIMS synchronization with bidirectional sync support.
"""

import enum
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, PIMSSyncMixin, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.call_log import CallLog
    from app.models.clinic import Clinic
    from app.models.patient import Patient
    from app.models.provider import Provider


class AppointmentStatus(str, enum.Enum):
    """Appointment lifecycle status."""

    SCHEDULED = "scheduled"  # Confirmed appointment
    REQUESTED = "requested"  # Request pending confirmation
    CONFIRMED = "confirmed"  # Confirmed by clinic/client
    CHECKED_IN = "checked_in"  # Patient arrived
    IN_PROGRESS = "in_progress"  # Appointment ongoing
    COMPLETED = "completed"  # Appointment finished
    CANCELLED = "cancelled"  # Cancelled by client or clinic
    NO_SHOW = "no_show"  # Patient didn't show up
    RESCHEDULED = "rescheduled"  # Moved to different time


class AppointmentType(str, enum.Enum):
    """Type of appointment."""

    CHECKUP = "checkup"  # Routine wellness exam
    VACCINATION = "vaccination"  # Vaccine appointment
    SICK_VISIT = "sick_visit"  # Illness/injury visit
    SURGERY = "surgery"  # Surgical procedure
    DENTAL = "dental"  # Dental cleaning/procedure
    GROOMING = "grooming"  # Grooming service
    BOARDING = "boarding"  # Pet boarding
    EMERGENCY = "emergency"  # Emergency visit
    FOLLOW_UP = "follow_up"  # Follow-up appointment
    CONSULTATION = "consultation"  # Initial consultation
    LAB_WORK = "lab_work"  # Lab tests/bloodwork
    OTHER = "other"


class AppointmentSource(str, enum.Enum):
    """How the appointment was created."""

    DASHBOARD = "dashboard"  # Created via clinic dashboard
    VOICE_AI = "voice_ai"  # Created by AI voice assistant
    PIMS = "pims"  # Synced from PIMS
    API = "api"  # Created via API
    ONLINE_BOOKING = "online_booking"  # Client online booking


class Appointment(Base, TimestampMixin, SoftDeleteMixin, PIMSSyncMixin):
    """
    Appointment model.

    Represents a scheduled appointment linking patient and provider.
    Supports bidirectional sync with PIMS systems.
    """

    __tablename__ = "appointments"

    # Foreign keys
    clinic_id: Mapped[str] = mapped_column(
        ForeignKey("clinics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    patient_id: Mapped[str] = mapped_column(
        ForeignKey("patients.id", ondelete="SET NULL"),
        nullable=True,  # Nullable to handle patient deletion
        index=True,
    )
    provider_id: Mapped[str | None] = mapped_column(
        ForeignKey("providers.id", ondelete="SET NULL"),
        nullable=True,  # Some appointments may not have assigned provider
        index=True,
    )
    call_log_id: Mapped[str | None] = mapped_column(
        ForeignKey("call_logs.id", ondelete="SET NULL"),
        nullable=True,
        comment="Call that created this appointment (if via voice AI)",
    )

    # Scheduling
    start_time: Mapped[datetime] = mapped_column(nullable=False, index=True)
    end_time: Mapped[datetime] = mapped_column(nullable=False)
    duration_minutes: Mapped[int] = mapped_column(
        Integer,
        default=30,
        nullable=False,
    )

    # Appointment details
    appointment_type: Mapped[AppointmentType] = mapped_column(
        Enum(AppointmentType, values_callable=lambda e: [x.value for x in e]),
        default=AppointmentType.CHECKUP,
        nullable=False,
        index=True,
    )
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus, values_callable=lambda e: [x.value for x in e]),
        default=AppointmentStatus.SCHEDULED,
        nullable=False,
        index=True,
    )
    source: Mapped[AppointmentSource] = mapped_column(
        Enum(AppointmentSource, values_callable=lambda e: [x.value for x in e]),
        default=AppointmentSource.DASHBOARD,
        nullable=False,
    )

    # Description and notes
    reason: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Reason for visit / chief complaint",
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Internal notes (not shown to clients)",
    )
    client_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Notes from client (booking reason, symptoms, etc.)",
    )

    # Reminder tracking
    reminder_sent_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
        comment="When reminder was sent",
    )
    confirmation_received_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
        comment="When client confirmed appointment",
    )

    # Rescheduling tracking
    rescheduled_from_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        comment="Original appointment ID if rescheduled",
    )
    cancellation_reason: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(nullable=True)
    cancelled_by: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Who cancelled: 'client', 'clinic', 'system'",
    )

    # PIMS-specific data
    pims_metadata: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Additional PIMS-specific fields",
    )

    # Relationships
    clinic: Mapped["Clinic"] = relationship(back_populates="appointments")
    patient: Mapped["Patient | None"] = relationship(back_populates="appointments")
    provider: Mapped["Provider | None"] = relationship(back_populates="appointments")
    call_log: Mapped["CallLog | None"] = relationship(back_populates="appointment")

    @property
    def is_past(self) -> bool:
        """Check if appointment is in the past."""

        return self.end_time < datetime.now(UTC)

    @property
    def is_today(self) -> bool:
        """Check if appointment is today."""

        now = datetime.now(UTC)
        return self.start_time.date() == now.date()

    @property
    def can_cancel(self) -> bool:
        """Check if appointment can still be cancelled."""
        return self.status not in [
            AppointmentStatus.COMPLETED,
            AppointmentStatus.CANCELLED,
            AppointmentStatus.NO_SHOW,
        ]

    def __repr__(self) -> str:
        return (
            f"<Appointment(id={self.id}, "
            f"patient_id={self.patient_id}, "
            f"start={self.start_time}, "
            f"status={self.status})>"
        )

    # Composite indexes for common queries
    __table_args__ = (
        Index("ix_appointments_clinic_date", "clinic_id", "start_time"),
        Index("ix_appointments_provider_date", "provider_id", "start_time"),
        Index("ix_appointments_patient_date", "patient_id", "start_time"),
        Index("ix_appointments_clinic_status", "clinic_id", "status"),
    )
