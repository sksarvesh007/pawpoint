"""Recording schemas for request/response validation."""

from uuid import UUID

from pydantic import BaseModel, Field


class RecordingUploadResponse(BaseModel):
    """Response after uploading a recording."""

    call_id: UUID
    recording_url: str
    size_bytes: int


class RecordingUrlResponse(BaseModel):
    """Response with a presigned download URL."""

    call_id: UUID
    presigned_url: str
    expires_in: int = Field(description="URL expiration in seconds")


class TwilioRecordingCallback(BaseModel):
    """Twilio recording status callback fields (form-encoded)."""

    RecordingSid: str
    RecordingUrl: str
    CallSid: str
    RecordingDuration: str
