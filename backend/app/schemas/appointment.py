"""Appointment schemas for request/response validation."""

import math
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AppointmentCreate(BaseModel):
    """Schema for creating an appointment."""

    start_time: datetime
    end_time: datetime
    appointment_type: str = Field(default="checkup")
    patient_id: UUID | None = None
    provider_id: UUID | None = None
    reason: str | None = Field(default=None, max_length=500)
    notes: str | None = None
    client_notes: str | None = None


class AppointmentUpdate(BaseModel):
    """Schema for updating an appointment (all fields optional)."""

    start_time: datetime | None = None
    end_time: datetime | None = None
    appointment_type: str | None = None
    patient_id: UUID | None = None
    provider_id: UUID | None = None
    reason: str | None = Field(default=None, max_length=500)
    notes: str | None = None
    client_notes: str | None = None


class AppointmentStatusUpdate(BaseModel):
    """Schema for updating appointment status."""

    status: str
    cancellation_reason: str | None = Field(default=None, max_length=500)


class AppointmentResponse(BaseModel):
    """Full appointment response."""

    model_config = {"from_attributes": True}

    id: UUID
    clinic_id: UUID
    patient_id: UUID | None
    provider_id: UUID | None
    call_log_id: UUID | None
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    appointment_type: str
    status: str
    source: str
    reason: str | None
    notes: str | None
    client_notes: str | None
    cancellation_reason: str | None
    cancelled_at: datetime | None
    patient_name: str | None = None
    provider_name: str | None = None
    pims_id: str | None
    sync_status: str
    created_at: datetime
    updated_at: datetime


class AppointmentListItem(BaseModel):
    """Lightweight appointment for list views."""

    model_config = {"from_attributes": True}

    id: UUID
    start_time: datetime
    end_time: datetime
    appointment_type: str
    status: str
    source: str
    reason: str | None
    patient_name: str | None = None
    provider_name: str | None = None


class TimeSlot(BaseModel):
    """Available time slot."""

    start_time: datetime
    end_time: datetime


class AppointmentsResponse(BaseModel):
    """Paginated appointments response."""

    items: list[AppointmentListItem]
    total: int
    page: int
    limit: int

    @property
    def total_pages(self) -> int:
        return math.ceil(self.total / self.limit) if self.limit > 0 else 0
