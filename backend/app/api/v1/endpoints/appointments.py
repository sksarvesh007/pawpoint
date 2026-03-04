"""Appointment API endpoints."""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_clinic
from app.core.rate_limit import limiter
from app.db import get_db
from app.models.clinic import Clinic
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentListItem,
    AppointmentResponse,
    AppointmentsResponse,
    AppointmentStatusUpdate,
    TimeSlot,
)
from app.services.appointment import AppointmentService

router = APIRouter()


@router.get("/", response_model=AppointmentsResponse)
@limiter.limit("100/minute")
async def list_appointments(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    appointment_status: str | None = Query(None, alias="status"),
    provider_id: UUID | None = Query(None),
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> AppointmentsResponse:
    """List appointments with filters and pagination."""
    service = AppointmentService(db)
    items, total = await service.list_appointments(
        clinic_id=current_clinic.id,
        page=page,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        status=appointment_status,
        provider_id=provider_id,
    )
    return AppointmentsResponse(
        items=[AppointmentListItem.model_validate(item) for item in items],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/today", response_model=list[AppointmentListItem])
@limiter.limit("100/minute")
async def get_today_appointments(
    request: Request,
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> list[AppointmentListItem]:
    """Get today's appointments."""
    service = AppointmentService(db)
    items = await service.get_today_appointments(current_clinic.id)
    return [AppointmentListItem.model_validate(item) for item in items]


@router.get("/available-slots", response_model=list[TimeSlot])
@limiter.limit("100/minute")
async def get_available_slots(
    request: Request,
    provider_id: UUID = Query(...),
    target_date: date = Query(..., alias="date"),
    duration: int = Query(30, ge=5, le=480),
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> list[TimeSlot]:
    """Get available appointment slots for a provider on a given date."""
    service = AppointmentService(db)
    slots = await service.get_available_slots(
        clinic_id=current_clinic.id,
        provider_id=provider_id,
        target_date=target_date,
        duration_minutes=duration,
    )
    return [TimeSlot(**slot) for slot in slots]


@router.post(
    "/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit("100/minute")
async def create_appointment(
    request: Request,
    data: AppointmentCreate,
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> AppointmentResponse:
    """Create a new appointment."""
    service = AppointmentService(db)
    appointment = await service.create_appointment(current_clinic.id, data)
    # Re-fetch with names
    result = await service.get_appointment(current_clinic.id, appointment.id)
    return AppointmentResponse.model_validate(result)


@router.get("/{appointment_id}", response_model=AppointmentResponse)
@limiter.limit("100/minute")
async def get_appointment(
    request: Request,
    appointment_id: UUID,
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> AppointmentResponse:
    """Get a single appointment by ID."""
    service = AppointmentService(db)
    result = await service.get_appointment(current_clinic.id, appointment_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found"
        )
    return AppointmentResponse.model_validate(result)


@router.put("/{appointment_id}", response_model=AppointmentResponse)
@limiter.limit("100/minute")
async def update_appointment(
    request: Request,
    appointment_id: UUID,
    data: AppointmentCreate,
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> AppointmentResponse:
    """Update an appointment."""
    from app.schemas.appointment import AppointmentUpdate

    update_data = AppointmentUpdate(**data.model_dump())
    service = AppointmentService(db)
    appointment = await service.update_appointment(
        current_clinic.id, appointment_id, update_data
    )
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found"
        )
    result = await service.get_appointment(current_clinic.id, appointment.id)
    return AppointmentResponse.model_validate(result)


@router.patch("/{appointment_id}/status", response_model=AppointmentResponse)
@limiter.limit("100/minute")
async def update_appointment_status(
    request: Request,
    appointment_id: UUID,
    data: AppointmentStatusUpdate,
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> AppointmentResponse:
    """Update appointment status."""
    service = AppointmentService(db)
    appointment = await service.update_status(
        current_clinic.id, appointment_id, data.status, data.cancellation_reason
    )
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found"
        )
    result = await service.get_appointment(current_clinic.id, appointment.id)
    return AppointmentResponse.model_validate(result)
