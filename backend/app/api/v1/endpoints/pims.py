"""PIMS integration API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_clinic
from app.core.rate_limit import limiter
from app.db import get_db
from app.models.clinic import Clinic
from app.schemas.pims import (
    PIMSConnectionStatus,
    PIMSCredentialsInput,
    PIMSSyncLogResponse,
    PIMSSyncTriggerResponse,
    PIMSTestConnectionResponse,
)
from app.services.pims import PIMSService

router = APIRouter()


@router.get("/status", response_model=PIMSConnectionStatus)
@limiter.limit("100/minute")
async def get_pims_status(
    request: Request,
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> PIMSConnectionStatus:
    """Get current PIMS connection status."""
    service = PIMSService(db)
    result = await service.get_connection_status(current_clinic.id)
    return PIMSConnectionStatus(**result)


@router.post("/credentials", response_model=PIMSConnectionStatus)
@limiter.limit("20/minute")
async def save_pims_credentials(
    request: Request,
    data: PIMSCredentialsInput,
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> PIMSConnectionStatus:
    """Save encrypted PIMS credentials."""
    service = PIMSService(db)
    result = await service.save_credentials(
        current_clinic.id, data.pims_type, data.credentials
    )
    return PIMSConnectionStatus(**result)


@router.post("/test-connection", response_model=PIMSTestConnectionResponse)
@limiter.limit("10/minute")
async def test_pims_connection(
    request: Request,
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> PIMSTestConnectionResponse:
    """Test the current PIMS connection."""
    service = PIMSService(db)
    result = await service.test_connection(current_clinic.id)
    return PIMSTestConnectionResponse(
        connected=result.get("connected", False),
        message=result.get("message", "Unknown"),
        details=result,
    )


@router.delete("/disconnect", response_model=PIMSConnectionStatus)
@limiter.limit("10/minute")
async def disconnect_pims(
    request: Request,
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> PIMSConnectionStatus:
    """Disconnect PIMS and clear credentials."""
    service = PIMSService(db)
    result = await service.disconnect(current_clinic.id)
    return PIMSConnectionStatus(**result)


@router.post("/sync/{entity}", response_model=PIMSSyncTriggerResponse)
@limiter.limit("10/minute")
async def trigger_sync(
    request: Request,
    entity: str,
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> PIMSSyncTriggerResponse:
    """Trigger a PIMS sync for a specific entity type."""
    from app.workers.tasks import (
        sync_appointments_from_pims,
        sync_patients_from_pims,
        sync_providers_from_pims,
    )

    task_map = {
        "patients": sync_patients_from_pims,
        "appointments": sync_appointments_from_pims,
        "providers": sync_providers_from_pims,
    }

    if entity not in task_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid entity type: {entity}. Must be one of: {', '.join(task_map.keys())}",
        )

    task = task_map[entity]
    result = task.delay(str(current_clinic.id))

    return PIMSSyncTriggerResponse(
        task_id=result.id,
        entity_type=entity,
        status="queued",
    )


@router.get("/sync-logs", response_model=list[PIMSSyncLogResponse])
@limiter.limit("100/minute")
async def get_sync_logs(
    request: Request,
    limit: int = Query(20, ge=1, le=100),
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> list[PIMSSyncLogResponse]:
    """Get recent PIMS sync logs."""
    service = PIMSService(db)
    logs = await service.get_sync_logs(current_clinic.id, limit=limit)
    return [
        PIMSSyncLogResponse(
            id=str(log.id),
            sync_type=str(log.sync_type),
            entity_type=str(log.entity_type),
            status=str(log.status),
            triggered_by=log.triggered_by,
            started_at=log.started_at,
            completed_at=log.completed_at,
            duration_seconds=log.duration_seconds,
            records_processed=log.records_processed,
            records_created=log.records_created,
            records_updated=log.records_updated,
            records_failed=log.records_failed,
            conflicts_detected=log.conflicts_detected,
            error_message=log.error_message,
            created_at=log.created_at,
        )
        for log in logs
    ]
