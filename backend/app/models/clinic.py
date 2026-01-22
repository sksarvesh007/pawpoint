"""
Clinic Model

Represents veterinary clinics/practices with PIMS integration settings.
Each clinic can connect to one PIMS and has its own patients, providers, and appointments.
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.appointment import Appointment
    from app.models.call_log import CallLog
    from app.models.patient import Patient
    from app.models.pims_sync_log import PIMSSyncLog
    from app.models.provider import Provider
    from app.models.user import User


class PIMSType(str, enum.Enum):
    """Supported Practice Information Management Systems."""

    EZYVET = "ezyvet"
    VETSPIRE = "vetspire"
    AVIMARK = "avimark"  # Covetrus
    CORNERSTONE = "cornerstone"  # Covetrus
    PULSE = "pulse"  # Covetrus
    IMPROMED = "impromed"  # Covetrus
    NONE = "none"  # No PIMS integration


class PIMSConnectionStatus(str, enum.Enum):
    """PIMS connection health status."""

    CONNECTED = "connected"  # Successfully connected and syncing
    DISCONNECTED = "disconnected"  # Not configured
    ERROR = "error"  # Connection error
    AUTH_EXPIRED = "auth_expired"  # Authentication needs renewal
    SYNCING = "syncing"  # Currently syncing


class Clinic(Base, TimestampMixin, SoftDeleteMixin):
    """
    Veterinary clinic/practice model.

    Stores clinic information, PIMS integration settings, and voice configuration.
    PIMS credentials are stored encrypted in pims_credentials_encrypted.
    """

    __tablename__ = "clinics"

    # Basic info
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="URL-friendly identifier",
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Contact info
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Address
    address_line1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_line2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    country: Mapped[str] = mapped_column(String(2), default="US", nullable=False)
    timezone: Mapped[str] = mapped_column(
        String(50),
        default="America/New_York",
        nullable=False,
        comment="IANA timezone (e.g., America/New_York)",
    )

    # Business settings
    business_hours: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Business hours by day of week",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    # PIMS Integration
    pims_type: Mapped[PIMSType] = mapped_column(
        Enum(PIMSType, values_callable=lambda e: [x.value for x in e]),
        default=PIMSType.NONE,
        nullable=False,
        index=True,
    )
    pims_credentials_encrypted: Mapped[bytes | None] = mapped_column(
        nullable=True,
        comment="AES-256 encrypted PIMS API credentials",
    )
    pims_connection_status: Mapped[PIMSConnectionStatus] = mapped_column(
        Enum(PIMSConnectionStatus, values_callable=lambda e: [x.value for x in e]),
        default=PIMSConnectionStatus.DISCONNECTED,
        nullable=False,
    )
    pims_last_sync_at: Mapped[datetime | None] = mapped_column(nullable=True)
    pims_settings: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Additional PIMS-specific settings",
    )

    # Voice/Twilio Integration
    twilio_phone_number: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        unique=True,
        comment="Twilio phone number assigned to this clinic",
    )
    voice_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    voice_settings: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Voice AI configuration (prompt, greeting, etc.)",
    )

    # Emergency settings
    emergency_phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Phone to transfer emergency calls",
    )
    emergency_keywords: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        default=["emergency", "dying", "bleeding", "poison", "hit by car"],
        comment="Keywords that trigger emergency transfer",
    )

    # Relationships
    users: Mapped[list["User"]] = relationship(
        secondary="user_clinic_associations",
        back_populates="clinics",
        lazy="selectin",
    )
    patients: Mapped[list["Patient"]] = relationship(
        back_populates="clinic",
        lazy="noload",  # Large collection - load explicitly with filters
        cascade="all, delete-orphan",
    )
    providers: Mapped[list["Provider"]] = relationship(
        back_populates="clinic",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    appointments: Mapped[list["Appointment"]] = relationship(
        back_populates="clinic",
        lazy="noload",  # Large collection - load explicitly with date filters
        cascade="all, delete-orphan",
    )
    call_logs: Mapped[list["CallLog"]] = relationship(
        back_populates="clinic",
        lazy="noload",  # Large collection - load explicitly with date filters
        cascade="all, delete-orphan",
    )
    sync_logs: Mapped[list["PIMSSyncLog"]] = relationship(
        back_populates="clinic",
        lazy="noload",  # Large collection - load explicitly with filters
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Clinic(id={self.id}, name={self.name}, pims={self.pims_type})>"
