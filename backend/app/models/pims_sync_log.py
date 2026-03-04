"""
PIMS Sync Log Model

Audit trail for all PIMS synchronization operations.
Tracks sync jobs, success/failure, errors, and statistics.
"""

from datetime import UTC, datetime
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID as PyUUID

from sqlalchemy import Enum, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.clinic import Clinic


class SyncType(StrEnum):
    """Type of sync operation."""

    FULL = "full"  # Full sync of all records
    INCREMENTAL = "incremental"  # Only sync changes since last sync
    PULL = "pull"  # Pull data from PIMS to local
    PUSH = "push"  # Push local changes to PIMS
    BIDIRECTIONAL = "bidirectional"  # Sync both directions


class SyncEntityType(StrEnum):
    """Entity type being synced."""

    PATIENTS = "patients"
    APPOINTMENTS = "appointments"
    PROVIDERS = "providers"
    ALL = "all"


class SyncJobStatus(StrEnum):
    """Status of the sync job."""

    PENDING = "pending"  # Queued, waiting to start
    RUNNING = "running"  # Currently executing
    COMPLETED = "completed"  # Finished successfully
    FAILED = "failed"  # Failed with error
    PARTIAL = "partial"  # Completed with some errors
    CANCELLED = "cancelled"  # Cancelled by user/system


class PIMSSyncLog(Base, TimestampMixin):
    """
    PIMS synchronization log model.

    Audit trail for all sync operations with detailed statistics
    and error tracking.
    """

    __tablename__ = "pims_sync_logs"

    # Foreign keys
    clinic_id: Mapped[PyUUID] = mapped_column(
        ForeignKey("clinics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Sync identification
    job_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Background job ID (Celery/ARQ task ID)",
    )

    # Sync type
    sync_type: Mapped[SyncType] = mapped_column(
        Enum(SyncType, values_callable=lambda e: [x.value for x in e]),
        nullable=False,
        index=True,
    )
    entity_type: Mapped[SyncEntityType] = mapped_column(
        Enum(SyncEntityType, values_callable=lambda e: [x.value for x in e]),
        nullable=False,
        index=True,
    )
    status: Mapped[SyncJobStatus] = mapped_column(
        Enum(SyncJobStatus, values_callable=lambda e: [x.value for x in e]),
        default=SyncJobStatus.PENDING,
        nullable=False,
        index=True,
    )

    # Trigger info
    triggered_by: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Who/what triggered the sync (user_id, 'scheduler', 'webhook')",
    )
    trigger_reason: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Why sync was triggered",
    )

    # Timing
    started_at: Mapped[datetime | None] = mapped_column(nullable=True, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Total sync duration",
    )

    # Statistics
    records_processed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    records_created: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    records_updated: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    records_deleted: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    records_skipped: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    records_failed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    conflicts_detected: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    conflicts_resolved: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Error details
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Main error message if failed",
    )
    error_details: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Detailed error information including stack trace",
    )
    failed_records: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="List of records that failed to sync",
    )

    # Retry info
    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    next_retry_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
        comment="When next retry is scheduled",
    )

    # Sync window (for incremental syncs)
    sync_from: Mapped[datetime | None] = mapped_column(
        nullable=True,
        comment="Start of sync window for incremental sync",
    )
    sync_to: Mapped[datetime | None] = mapped_column(
        nullable=True,
        comment="End of sync window for incremental sync",
    )

    # Additional data
    extra_data: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Additional sync metadata",
    )

    # Relationships
    clinic: Mapped["Clinic"] = relationship(back_populates="sync_logs")

    @property
    def success_rate(self) -> float:
        """Calculate sync success rate."""
        if self.records_processed == 0:
            return 1.0
        return (self.records_processed - self.records_failed) / self.records_processed

    @property
    def is_success(self) -> bool:
        """Check if sync was fully successful."""
        return self.status == SyncJobStatus.COMPLETED and self.records_failed == 0

    def start(self) -> None:
        """Mark sync job as started."""

        self.status = SyncJobStatus.RUNNING
        self.started_at = datetime.now(UTC)

    def complete(self) -> None:
        """Mark sync job as completed."""

        self.status = (
            SyncJobStatus.COMPLETED
            if self.records_failed == 0
            else SyncJobStatus.PARTIAL
        )
        completed_at = datetime.now(UTC)
        self.completed_at = completed_at
        if self.started_at:
            self.duration_seconds = (completed_at - self.started_at).total_seconds()

    def fail(self, error_message: str, error_details: dict | None = None) -> None:
        """Mark sync job as failed."""

        self.status = SyncJobStatus.FAILED
        completed_at = datetime.now(UTC)
        self.completed_at = completed_at
        self.error_message = error_message
        self.error_details = error_details
        if self.started_at:
            self.duration_seconds = (completed_at - self.started_at).total_seconds()

    def __repr__(self) -> str:
        return (
            f"<PIMSSyncLog(id={self.id}, "
            f"clinic_id={self.clinic_id}, "
            f"type={self.sync_type}, "
            f"entity={self.entity_type}, "
            f"status={self.status})>"
        )

    # Composite indexes for common queries
    __table_args__ = (
        Index("ix_pims_sync_logs_clinic_date", "clinic_id", "started_at"),
        Index("ix_pims_sync_logs_clinic_status", "clinic_id", "status"),
        Index("ix_pims_sync_logs_clinic_entity", "clinic_id", "entity_type"),
    )
