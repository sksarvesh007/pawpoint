"""PIMS integration schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, Field


class PIMSCredentialsInput(BaseModel):
    """Input for saving PIMS credentials."""

    pims_type: str = Field(..., description="PIMS type (ezyvet, vetspire, etc.)")
    credentials: dict = Field(
        ..., description="PIMS-specific credential key-value pairs"
    )


class PIMSConnectionStatus(BaseModel):
    """PIMS connection status response."""

    pims_type: str
    connection_status: str
    last_sync_at: datetime | None = None
    message: str | None = None


class PIMSTestConnectionResponse(BaseModel):
    """Response from testing PIMS connection."""

    connected: bool
    message: str
    details: dict | None = None


class PIMSSyncTriggerResponse(BaseModel):
    """Response from triggering a sync."""

    task_id: str
    entity_type: str
    status: str = "queued"


class PIMSSyncLogResponse(BaseModel):
    """PIMS sync log entry response."""

    model_config = {"from_attributes": True}

    id: str
    sync_type: str
    entity_type: str
    status: str
    triggered_by: str | None
    started_at: datetime | None
    completed_at: datetime | None
    duration_seconds: float | None
    records_processed: int
    records_created: int
    records_updated: int
    records_failed: int
    conflicts_detected: int
    error_message: str | None
    created_at: datetime
