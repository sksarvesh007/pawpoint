"""
Provider Model

Represents veterinarians and other healthcare providers at a clinic.
Syncs with PIMS for availability and appointment scheduling.
"""

import enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, PIMSSyncMixin, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.appointment import Appointment
    from app.models.clinic import Clinic


class ProviderType(str, enum.Enum):
    """Type of healthcare provider."""

    VETERINARIAN = "veterinarian"
    VET_TECHNICIAN = "vet_technician"
    VET_ASSISTANT = "vet_assistant"
    RECEPTIONIST = "receptionist"
    SPECIALIST = "specialist"
    OTHER = "other"


class Provider(Base, TimestampMixin, SoftDeleteMixin, PIMSSyncMixin):
    """
    Veterinary provider/staff model.

    Represents vets and other staff who can have appointments scheduled.
    Syncs with PIMS for availability management.
    """

    __tablename__ = "providers"

    # Foreign keys
    clinic_id: Mapped[str] = mapped_column(
        ForeignKey("clinics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Basic info
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Professional title (DVM, VMD, etc.)",
    )
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Professional info
    provider_type: Mapped[ProviderType] = mapped_column(
        Enum(ProviderType),
        default=ProviderType.VETERINARIAN,
        nullable=False,
        index=True,
    )
    license_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    specialties: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="List of specialties (surgery, dentistry, etc.)",
    )
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Scheduling settings
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )
    accepts_appointments: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether this provider can have appointments scheduled",
    )
    default_appointment_duration_min: Mapped[int] = mapped_column(
        Integer,
        default=30,
        nullable=False,
        comment="Default appointment duration in minutes",
    )
    availability: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Weekly availability schedule",
    )

    # Display settings
    color: Mapped[str | None] = mapped_column(
        String(7),
        nullable=True,
        comment="Hex color for calendar display (e.g., #4A90D9)",
    )
    photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Order in provider lists/dropdowns",
    )

    # PIMS-specific data
    pims_metadata: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Additional PIMS-specific fields",
    )

    # Relationships
    clinic: Mapped["Clinic"] = relationship(back_populates="providers")
    appointments: Mapped[list["Appointment"]] = relationship(
        back_populates="provider",
        lazy="selectin",
    )

    @property
    def full_name(self) -> str:
        """Get provider's full name with title."""
        if self.title:
            return f"{self.title} {self.first_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    @property
    def display_name(self) -> str:
        """Get display name for UI (Dr. Last or First Last)."""
        if self.title and self.provider_type == ProviderType.VETERINARIAN:
            return f"Dr. {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"<Provider(id={self.id}, name={self.full_name}, type={self.provider_type})>"
