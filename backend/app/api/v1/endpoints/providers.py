"""Provider API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_clinic
from app.core.rate_limit import limiter
from app.db import get_db
from app.models.clinic import Clinic
from app.schemas.provider import ProviderCreate, ProviderResponse, ProviderUpdate
from app.services.provider import ProviderService

router = APIRouter()


@router.get("/", response_model=list[ProviderResponse])
@limiter.limit("100/minute")
async def list_providers(
    request: Request,
    active_only: bool = Query(True),
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> list[ProviderResponse]:
    """List providers for the current clinic."""
    service = ProviderService(db)
    providers = await service.list_providers(current_clinic.id, active_only=active_only)
    return [ProviderResponse.model_validate(p) for p in providers]


@router.post("/", response_model=ProviderResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("100/minute")
async def create_provider(
    request: Request,
    data: ProviderCreate,
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> ProviderResponse:
    """Create a new provider."""
    service = ProviderService(db)
    provider = await service.create_provider(current_clinic.id, data)
    return ProviderResponse.model_validate(provider)


@router.get("/{provider_id}", response_model=ProviderResponse)
@limiter.limit("100/minute")
async def get_provider(
    request: Request,
    provider_id: UUID,
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> ProviderResponse:
    """Get a single provider by ID."""
    service = ProviderService(db)
    provider = await service.get_provider(current_clinic.id, provider_id)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found"
        )
    return ProviderResponse.model_validate(provider)


@router.put("/{provider_id}", response_model=ProviderResponse)
@limiter.limit("100/minute")
async def update_provider(
    request: Request,
    provider_id: UUID,
    data: ProviderUpdate,
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> ProviderResponse:
    """Update a provider."""
    service = ProviderService(db)
    provider = await service.update_provider(current_clinic.id, provider_id, data)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found"
        )
    return ProviderResponse.model_validate(provider)


@router.delete("/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("100/minute")
async def delete_provider(
    request: Request,
    provider_id: UUID,
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft delete a provider."""
    service = ProviderService(db)
    deleted = await service.delete_provider(current_clinic.id, provider_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found"
        )
