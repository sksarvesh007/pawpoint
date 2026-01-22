"""
Patient Model

Represents pets/animals managed by the clinic.
Syncs with PIMS and includes owner contact information.
"""

import enum
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, Enum, Float, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, PIMSSyncMixin, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.appointment import Appointment
    from app.models.clinic import Clinic


class Species(str, enum.Enum):
    """Common pet species."""

    DOG = "dog"
    CAT = "cat"
    BIRD = "bird"
    RABBIT = "rabbit"
    HAMSTER = "hamster"
    GUINEA_PIG = "guinea_pig"
    REPTILE = "reptile"
    FISH = "fish"
    HORSE = "horse"
    OTHER = "other"


class Sex(str, enum.Enum):
    """Patient sex."""

    MALE = "male"
    FEMALE = "female"
    MALE_NEUTERED = "male_neutered"
    FEMALE_SPAYED = "female_spayed"
    UNKNOWN = "unknown"


class Patient(Base, TimestampMixin, SoftDeleteMixin, PIMSSyncMixin):
    """
    Pet/animal patient model.

    Stores pet information along with owner contact details.
    Syncs bidirectionally with external PIMS.
    """

    __tablename__ = "patients"

    # Foreign keys
    clinic_id: Mapped[str] = mapped_column(
        ForeignKey("clinics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Pet information
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    species: Mapped[Species] = mapped_column(
        Enum(Species, values_callable=lambda e: [x.value for x in e]),
        default=Species.OTHER,
        nullable=False,
        index=True,
    )
    breed: Mapped[str | None] = mapped_column(String(100), nullable=True)
    color: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sex: Mapped[Sex] = mapped_column(
        Enum(Sex, values_callable=lambda e: [x.value for x in e]),
        default=Sex.UNKNOWN,
        nullable=False,
    )
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    microchip_id: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )

    # Health status
    is_deceased: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    allergies: Mapped[str | None] = mapped_column(Text, nullable=True)
    medical_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Owner information (denormalized for quick access)
    owner_first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    owner_last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    owner_phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="Primary contact phone for appointments/reminders",
    )
    owner_phone_alt: Mapped[str | None] = mapped_column(String(20), nullable=True)
    owner_email: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True
    )
    owner_address: Mapped[str | None] = mapped_column(Text, nullable=True)

    # PIMS-specific data (stored as JSON for flexibility)
    pims_metadata: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Additional PIMS-specific fields",
    )

    # Photo
    photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    clinic: Mapped["Clinic"] = relationship(back_populates="patients")
    appointments: Mapped[list["Appointment"]] = relationship(
        back_populates="patient",
        lazy="noload",  # Load explicitly - patients can have many appointments over time
    )

    @property
    def owner_full_name(self) -> str:
        """Get owner's full name."""
        return f"{self.owner_first_name} {self.owner_last_name}"

    @property
    def age_years(self) -> int | None:
        """Calculate patient's age in years."""
        if not self.date_of_birth:
            return None
        from datetime import date as date_module

        today = date_module.today()
        return (
            today.year
            - self.date_of_birth.year
            - (
                (today.month, today.day)
                < (self.date_of_birth.month, self.date_of_birth.day)
            )
        )

    def __repr__(self) -> str:
        return f"<Patient(id={self.id}, name={self.name}, species={self.species})>"

    # Composite indexes for common queries
    __table_args__ = (
        Index("ix_patients_clinic_owner_phone", "clinic_id", "owner_phone"),
        Index("ix_patients_clinic_name", "clinic_id", "name"),
    )
