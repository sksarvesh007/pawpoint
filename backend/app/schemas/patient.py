"""Patient schemas for request/response validation."""

import math
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PatientCreate(BaseModel):
    """Schema for creating a new patient."""

    name: str = Field(..., min_length=1, max_length=100)
    species: str = Field(default="other")
    owner_first_name: str = Field(..., min_length=1, max_length=100)
    owner_last_name: str = Field(..., min_length=1, max_length=100)
    owner_phone: str = Field(..., min_length=1, max_length=20)
    breed: str | None = Field(default=None, max_length=100)
    color: str | None = Field(default=None, max_length=50)
    sex: str = Field(default="unknown")
    date_of_birth: date | None = None
    weight_kg: float | None = Field(default=None, ge=0)
    owner_email: str | None = Field(default=None, max_length=255)
    owner_phone_alt: str | None = Field(default=None, max_length=20)
    owner_address: str | None = None
    allergies: str | None = None
    medical_notes: str | None = None
    microchip_id: str | None = Field(default=None, max_length=50)
    photo_url: str | None = None


class PatientUpdate(BaseModel):
    """Schema for updating a patient (all fields optional)."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    species: str | None = None
    breed: str | None = Field(default=None, max_length=100)
    color: str | None = Field(default=None, max_length=50)
    sex: str | None = None
    date_of_birth: date | None = None
    weight_kg: float | None = Field(default=None, ge=0)
    owner_first_name: str | None = Field(default=None, min_length=1, max_length=100)
    owner_last_name: str | None = Field(default=None, min_length=1, max_length=100)
    owner_phone: str | None = Field(default=None, min_length=1, max_length=20)
    owner_email: str | None = Field(default=None, max_length=255)
    owner_phone_alt: str | None = Field(default=None, max_length=20)
    owner_address: str | None = None
    allergies: str | None = None
    medical_notes: str | None = None
    microchip_id: str | None = Field(default=None, max_length=50)
    photo_url: str | None = None
    is_deceased: bool | None = None


class PatientResponse(BaseModel):
    """Full patient response."""

    model_config = {"from_attributes": True}

    id: UUID
    clinic_id: UUID
    name: str
    species: str
    breed: str | None
    color: str | None
    sex: str
    date_of_birth: date | None
    weight_kg: float | None
    is_deceased: bool
    allergies: str | None
    medical_notes: str | None
    owner_first_name: str
    owner_last_name: str
    owner_phone: str
    owner_phone_alt: str | None
    owner_email: str | None
    owner_address: str | None
    microchip_id: str | None
    photo_url: str | None
    owner_full_name: str
    pims_id: str | None
    sync_status: str
    last_synced_at: datetime | None
    created_at: datetime
    updated_at: datetime


class PatientListItem(BaseModel):
    """Lightweight patient for list views."""

    model_config = {"from_attributes": True}

    id: UUID
    name: str
    species: str
    breed: str | None
    owner_first_name: str
    owner_last_name: str
    owner_phone: str
    owner_email: str | None
    is_deceased: bool
    photo_url: str | None
    created_at: datetime

    @property
    def owner_full_name(self) -> str:
        return f"{self.owner_first_name} {self.owner_last_name}"


class PatientsResponse(BaseModel):
    """Paginated patients response."""

    items: list[PatientListItem]
    total: int
    page: int
    limit: int

    @property
    def total_pages(self) -> int:
        return math.ceil(self.total / self.limit) if self.limit > 0 else 0
