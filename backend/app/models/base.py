"""
Base Model and Reusable Mixins

Provides base classes and mixins for all SQLAlchemy models:
- Base: Declarative base with naming conventions
- TimestampMixin: created_at, updated_at tracking
- SoftDeleteMixin: deleted_at for soft deletes
- PIMSSyncMixin: PIMS integration fields (pims_id, sync_status, last_synced_at)
"""

import enum
from datetime import UTC, datetime
from typing import Any, ClassVar
from uuid import UUID as PyUUID, uuid4

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class SyncStatus(str, enum.Enum):
    """Status of PIMS synchronization for a record."""

    PENDING = "pending"  # Not yet synced to PIMS
    SYNCED = "synced"  # Successfully synced with PIMS
    CONFLICT = "conflict"  # Sync conflict requires manual review
    ERROR = "error"  # Sync failed with error
    LOCAL_ONLY = "local_only"  # Record only exists locally (not in PIMS)


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.

    Features:
    - UUID primary keys for all tables
    - Automatic table naming from class name (snake_case, pluralized)
    - Naming conventions for constraints and indexes
    """

    type_annotation_map: ClassVar[dict[type, Any]] = {
        datetime: DateTime(timezone=True),
    }

    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        """Generate table name from class name (snake_case + pluralize)."""
        import re

        # Convert CamelCase to snake_case
        name = re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()
        # Simple pluralization (add 's' or handle common cases)
        if name.endswith("y"):
            return name[:-1] + "ies"
        elif name.endswith("s"):
            return name + "es"
        return name + "s"

    # UUID primary key for all models
    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class TimestampMixin:
    """
    Mixin for automatic timestamp tracking.

    Adds:
    - created_at: Set automatically on insert
    - updated_at: Updates automatically on every save
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """
    Mixin for soft delete functionality.

    Instead of permanently deleting records, sets deleted_at timestamp.
    Query filters should exclude records where deleted_at is not null.
    """

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        index=True,
    )

    @property
    def is_deleted(self) -> bool:
        """Check if record is soft deleted."""
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        """Mark record as deleted."""

        self.deleted_at = datetime.now(UTC)


class PIMSSyncMixin:
    """
    Mixin for records that sync with external PIMS (Practice Information Management Systems).

    Adds:
    - pims_id: External ID in the PIMS system
    - sync_status: Current sync state (pending, synced, conflict, error)
    - last_synced_at: Timestamp of last successful sync
    - pims_version: Version/etag for conflict detection
    """

    pims_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        comment="External ID in PIMS system",
    )

    sync_status: Mapped[SyncStatus] = mapped_column(
        Enum(SyncStatus),
        default=SyncStatus.PENDING,
        nullable=False,
        index=True,
    )

    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last successful sync timestamp",
    )

    pims_version: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Version/etag from PIMS for conflict detection",
    )

    def mark_synced(self, pims_id: str | None = None) -> None:
        """Mark record as successfully synced."""

        if pims_id:
            self.pims_id = pims_id
        self.sync_status = SyncStatus.SYNCED
        self.last_synced_at = datetime.now(UTC)

    def mark_sync_error(self) -> None:
        """Mark record as having sync error."""
        self.sync_status = SyncStatus.ERROR

    def mark_sync_conflict(self) -> None:
        """Mark record as having sync conflict."""
        self.sync_status = SyncStatus.CONFLICT
