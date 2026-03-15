"""Recording management endpoints (upload, download, Twilio webhook)."""

import base64
import contextlib
import hashlib
import hmac
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.dependencies import get_current_clinic
from app.db import get_db
from app.models.call_log import CallLog
from app.models.clinic import Clinic
from app.schemas.recording import RecordingUploadResponse, RecordingUrlResponse
from app.services.storage import StorageService

router = APIRouter()
settings = get_settings()


def _get_storage() -> StorageService:
    return StorageService()


def _recording_key(call_id: UUID, ext: str = "wav") -> str:
    """Build a consistent S3 object key for a call recording."""
    return f"recordings/{call_id}.{ext}"


@router.post(
    "/upload/{call_id}",
    response_model=RecordingUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_recording(
    call_id: UUID,
    file: UploadFile,
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
    storage: StorageService = Depends(_get_storage),
) -> RecordingUploadResponse:
    """Upload a recording file for a call."""
    # Find the call log
    result = await db.execute(
        select(CallLog).where(
            CallLog.id == call_id,
            CallLog.clinic_id == current_clinic.id,
            CallLog.deleted_at.is_(None),
        )
    )
    call_log = result.scalar_one_or_none()
    if not call_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call log not found",
        )

    # Validate content type
    content_type = file.content_type or ""
    allowed_types = {
        "audio/wav",
        "audio/x-wav",
        "audio/wave",
        "audio/mpeg",
        "audio/mp3",
    }
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{content_type}'. Allowed: wav, mp3",
        )

    # Read file data
    data = await file.read()
    ext = "wav"
    if content_type == "audio/mpeg":
        ext = "mp3"

    key = _recording_key(call_id, ext)
    recording_url = await storage.upload_recording(key, data, content_type)

    # Update the call log
    call_log.recording_url = recording_url
    await db.flush()
    await db.refresh(call_log)

    return RecordingUploadResponse(
        call_id=call_id,
        recording_url=recording_url,
        size_bytes=len(data),
    )


@router.get("/{call_id}", response_model=RecordingUrlResponse)
async def get_recording_url(
    call_id: UUID,
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
    storage: StorageService = Depends(_get_storage),
) -> RecordingUrlResponse:
    """Get a presigned download URL for a call's recording."""
    result = await db.execute(
        select(CallLog).where(
            CallLog.id == call_id,
            CallLog.clinic_id == current_clinic.id,
            CallLog.deleted_at.is_(None),
        )
    )
    call_log = result.scalar_one_or_none()
    if not call_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call log not found",
        )

    if not call_log.recording_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No recording found for this call",
        )

    # Derive the key from the stored URL or use the standard pattern
    key = _recording_key(call_id)
    expires_in = 3600
    presigned_url = await storage.get_presigned_url(key, expires_in)

    return RecordingUrlResponse(
        call_id=call_id,
        presigned_url=presigned_url,
        expires_in=expires_in,
    )


def _validate_twilio_signature(request: Request, form_params: dict[str, str]) -> bool:
    """Validate that the request came from Twilio using X-Twilio-Signature.

    Args:
        request: The incoming request (for URL and headers).
        form_params: Parsed form fields (avoids re-reading consumed body stream).
    """
    if not settings.twilio_auth_token:
        logger.warning("TWILIO_AUTH_TOKEN not set — skipping signature validation")
        return True

    signature = request.headers.get("X-Twilio-Signature", "")
    if not signature:
        return False

    auth_token = (
        settings.twilio_auth_token.get_secret_value()
        if hasattr(settings.twilio_auth_token, "get_secret_value")
        else str(settings.twilio_auth_token)
    )

    # Twilio signs the full URL + sorted POST params
    url = str(request.url)
    sorted_params = ""
    for key in sorted(form_params.keys()):
        sorted_params += key + form_params[key]

    data_to_sign = url + sorted_params
    expected = hmac.new(
        auth_token.encode("utf-8"),
        data_to_sign.encode("utf-8"),
        hashlib.sha1,
    ).digest()

    expected_b64 = base64.b64encode(expected).decode()
    return hmac.compare_digest(expected_b64, signature)


@router.post("/webhooks/twilio", status_code=status.HTTP_204_NO_CONTENT)
async def twilio_recording_callback(
    request: Request,
    RecordingSid: str = Form(...),
    RecordingUrl: str = Form(...),
    CallSid: str = Form(...),
    RecordingDuration: str = Form(...),
    db: AsyncSession = Depends(get_db),
    storage: StorageService = Depends(_get_storage),
) -> None:
    """Handle Twilio recording status callback.

    Twilio sends this when a recording is ready. We fetch the .wav from
    Twilio and store it in our S3 bucket.
    """
    # Validate Twilio signature (reconstruct params from parsed Form fields)
    form_params = {
        "RecordingSid": RecordingSid,
        "RecordingUrl": RecordingUrl,
        "CallSid": CallSid,
        "RecordingDuration": RecordingDuration,
    }
    if not _validate_twilio_signature(request, form_params):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Twilio signature",
        )

    # Find call log by external SID
    result = await db.execute(
        select(CallLog).where(
            CallLog.twilio_call_sid == CallSid,
            CallLog.deleted_at.is_(None),
        )
    )
    call_log = result.scalar_one_or_none()
    if not call_log:
        logger.warning("Twilio recording callback for unknown CallSid: {}", CallSid)
        return

    # Fetch the recording from Twilio (.wav format)
    wav_url = f"{RecordingUrl}.wav"
    async with httpx.AsyncClient() as http_client:
        resp = await http_client.get(wav_url)
        if resp.status_code != 200:
            logger.error(
                "Failed to fetch Twilio recording {}: HTTP {}",
                RecordingSid,
                resp.status_code,
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to fetch recording from Twilio",
            )
        recording_data = resp.content

    # Upload to S3
    key = _recording_key(call_log.id)
    recording_url = await storage.upload_recording(key, recording_data, "audio/wav")

    # Update call log
    call_log.recording_url = recording_url
    with contextlib.suppress(ValueError, TypeError):
        call_log.recording_duration_seconds = int(RecordingDuration)

    await db.flush()
    logger.info(
        "Stored Twilio recording {} for call {}",
        RecordingSid,
        call_log.id,
    )
