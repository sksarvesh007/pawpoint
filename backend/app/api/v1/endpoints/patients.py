"""Patient API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_clinic
from app.core.rate_limit import limiter
from app.db import get_db
from app.models.clinic import Clinic
from app.schemas.patient import (
    PatientCreate,
    PatientListItem,
    PatientResponse,
    PatientsResponse,
    PatientUpdate,
)
from app.services.patient import PatientService

router = APIRouter()


@router.get("/", response_model=PatientsResponse)
@limiter.limit("100/minute")
async def list_patients(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, max_length=200),
    species: str | None = Query(None),
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> PatientsResponse:
    """List patients with pagination, search, and species filter."""
    service = PatientService(db)
    patients, total = await service.list_patients(
        clinic_id=current_clinic.id,
        page=page,
        limit=limit,
        search=search,
        species=species,
    )
    return PatientsResponse(
        items=[PatientListItem.model_validate(p) for p in patients],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/search", response_model=list[PatientListItem])
@limiter.limit("100/minute")
async def search_patients(
    request: Request,
    q: str = Query(..., min_length=1, max_length=200),
    limit: int = Query(10, ge=1, le=50),
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> list[PatientListItem]:
    """Search patients for autocomplete (AI agent and UI)."""
    service = PatientService(db)
    patients = await service.search_patients(
        clinic_id=current_clinic.id, query=q, limit=limit
    )
    return [PatientListItem.model_validate(p) for p in patients]


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("100/minute")
async def create_patient(
    request: Request,
    data: PatientCreate,
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> PatientResponse:
    """Create a new patient."""
    service = PatientService(db)
    patient = await service.create_patient(current_clinic.id, data)
    return PatientResponse.model_validate(patient)


@router.get("/{patient_id}", response_model=PatientResponse)
@limiter.limit("100/minute")
async def get_patient(
    request: Request,
    patient_id: UUID,
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> PatientResponse:
    """Get a single patient by ID."""
    service = PatientService(db)
    patient = await service.get_patient(current_clinic.id, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )
    return PatientResponse.model_validate(patient)


@router.put("/{patient_id}", response_model=PatientResponse)
@limiter.limit("100/minute")
async def update_patient(
    request: Request,
    patient_id: UUID,
    data: PatientUpdate,
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> PatientResponse:
    """Update a patient."""
    service = PatientService(db)
    patient = await service.update_patient(current_clinic.id, patient_id, data)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )
    return PatientResponse.model_validate(patient)


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("100/minute")
async def delete_patient(
    request: Request,
    patient_id: UUID,
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft delete a patient."""
    service = PatientService(db)
    deleted = await service.delete_patient(current_clinic.id, patient_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )
