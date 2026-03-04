"""Normalized data transfer objects for PIMS data.

These DTOs provide a provider-agnostic representation of PIMS data.
Each adapter maps its provider-specific responses to these types.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class PIMSPatient:
    """Normalized patient record from PIMS."""

    pims_id: str
    name: str
    species: str
    breed: str | None = None
    color: str | None = None
    sex: str | None = None
    date_of_birth: datetime | None = None
    weight_kg: float | None = None
    microchip_id: str | None = None
    is_deceased: bool = False
    owner_first_name: str | None = None
    owner_last_name: str | None = None
    owner_phone: str | None = None
    owner_email: str | None = None
    owner_address: str | None = None
    allergies: str | None = None
    medical_notes: str | None = None
    client_pims_id: str | None = None
    is_active: bool = True
    notes: str | None = None
    raw_data: dict[str, Any] = field(default_factory=dict)


@dataclass
class PIMSAppointment:
    """Normalized appointment record from PIMS."""

    pims_id: str
    patient_pims_id: str | None = None
    provider_pims_id: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    appointment_type: str | None = None
    status: str | None = None
    reason: str | None = None
    notes: str | None = None
    location_pims_id: str | None = None
    appointment_type_id: str | None = None
    duration_minutes: int | None = None
    is_confirmed: bool = False
    raw_data: dict[str, Any] = field(default_factory=dict)


@dataclass
class PIMSProvider:
    """Normalized provider record from PIMS."""

    pims_id: str
    first_name: str
    last_name: str
    title: str | None = None
    provider_type: str | None = None
    specialties: list[str] | None = None
    email: str | None = None
    phone: str | None = None
    is_active: bool = True
    is_veterinarian: bool = False
    profile_image_url: str | None = None
    default_location_id: str | None = None
    suffix: str | None = None
    raw_data: dict[str, Any] = field(default_factory=dict)


@dataclass
class PIMSTimeSlot:
    """Available time slot from PIMS."""

    start_time: datetime
    end_time: datetime
    provider_pims_id: str | None = None
    schedule_id: str | None = None
    slot_id: str | None = None
