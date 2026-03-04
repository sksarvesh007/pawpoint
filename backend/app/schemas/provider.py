"""Provider schemas for request/response validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProviderCreate(BaseModel):
    """Schema for creating a provider."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    title: str | None = Field(default=None, max_length=50)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    provider_type: str = Field(default="veterinarian")
    license_number: str | None = Field(default=None, max_length=50)
    specialties: list[str] | None = None
    bio: str | None = None
    default_appointment_duration_min: int = Field(default=30, ge=5, le=480)
    availability: dict | None = None
    color: str | None = Field(default=None, max_length=7)
    photo_url: str | None = None


class ProviderUpdate(BaseModel):
    """Schema for updating a provider (all fields optional)."""

    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    title: str | None = Field(default=None, max_length=50)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    provider_type: str | None = None
    license_number: str | None = Field(default=None, max_length=50)
    specialties: list[str] | None = None
    bio: str | None = None
    default_appointment_duration_min: int | None = Field(default=None, ge=5, le=480)
    accepts_appointments: bool | None = None
    is_active: bool | None = None
    availability: dict | None = None
    color: str | None = Field(default=None, max_length=7)
    photo_url: str | None = None


class ProviderResponse(BaseModel):
    """Full provider response."""

    model_config = {"from_attributes": True}

    id: UUID
    clinic_id: UUID
    first_name: str
    last_name: str
    title: str | None
    email: str | None
    phone: str | None
    provider_type: str
    license_number: str | None
    specialties: list | None
    bio: str | None
    is_active: bool
    accepts_appointments: bool
    default_appointment_duration_min: int
    availability: dict | None
    color: str | None
    photo_url: str | None
    full_name: str
    display_name: str
    pims_id: str | None
    sync_status: str
    created_at: datetime
    updated_at: datetime


class ProviderListItem(BaseModel):
    """Lightweight provider for list views."""

    model_config = {"from_attributes": True}

    id: UUID
    first_name: str
    last_name: str
    title: str | None
    provider_type: str
    is_active: bool
    full_name: str
