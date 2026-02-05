"""
Voice API Endpoints

Endpoints for browser voice widget integration and LiveKit webhooks.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import ClinicDep
from app.core.dependencies import get_current_user
from app.db import get_db
from app.models.call_log import CallChannel, CallDirection
from app.models.user import User
from app.services.voice import VoiceService, verify_livekit_webhook

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class VoiceTokenResponse(BaseModel):
    """Response for voice token generation."""

    token: str
    room_name: str
    ws_url: str


class VoiceStatusResponse(BaseModel):
    """Response for voice availability check."""

    available: bool
    reason: str | None = None
    greeting_message: str | None = None
    chatbot_persona: str | None = None


class WebhookResponse(BaseModel):
    """Response for webhook processing."""

    status: str


# Dependencies
CurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.post(
    "/{clinic_slug}/voice/token",
    response_model=VoiceTokenResponse,
    summary="Generate voice token",
    description="Generate a LiveKit access token for the browser voice widget. Requires authentication.",
)
async def generate_voice_token(
    clinic: ClinicDep,
    current_user: CurrentUserDep,
    db: AsyncSession = Depends(get_db),
) -> VoiceTokenResponse:
    """
    Generate a LiveKit access token for the browser voice widget.

    Requires JWT authentication and access to the specified clinic.
    """
    # Verify user has access to this clinic
    # For now, we allow any authenticated user to use the voice widget
    # In production, you may want to check clinic membership

    voice_service = VoiceService(db)

    try:
        result = await voice_service.generate_voice_token(
            clinic=clinic,
            user_id=str(current_user.id),
            user_name=current_user.full_name,
        )

        return VoiceTokenResponse(
            token=result["token"],
            room_name=result["room_name"],
            ws_url=result["ws_url"],
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"Token generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate voice token",
        ) from e


@router.get(
    "/{clinic_slug}/voice/status",
    response_model=VoiceStatusResponse,
    summary="Check voice availability",
    description="Check if voice calling is available for a clinic. Public endpoint.",
)
async def get_voice_status(
    clinic: ClinicDep,
    db: AsyncSession = Depends(get_db),
) -> VoiceStatusResponse:
    """
    Check if voice is available for a clinic.

    This is a public endpoint that doesn't require authentication.
    """
    voice_service = VoiceService(db)
    result = await voice_service.check_voice_status(clinic)

    return VoiceStatusResponse(**result)


@router.post(
    "/webhooks/livekit",
    response_model=WebhookResponse,
    summary="LiveKit webhook handler",
    description="Handle LiveKit room events (call start/end). Requires HMAC signature.",
)
async def livekit_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_livekit_signature: str | None = Header(None, alias="X-Livekit-Signature"),
) -> WebhookResponse:
    """
    Handle LiveKit webhook events.

    Validates HMAC signature and processes room events.
    """
    # Read raw body for signature verification
    body = await request.body()

    # Verify signature
    if not x_livekit_signature:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing signature header",
        )

    if not verify_livekit_webhook(body, x_livekit_signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature",
        )

    # Parse event
    try:
        event = await request.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON body",
        ) from e

    event_type = event.get("event")
    room = event.get("room", {})
    room_name = room.get("name")

    logger.info(f"LiveKit webhook: event={event_type}, room={room_name}")

    voice_service = VoiceService(db)

    try:
        if event_type == "room_started":
            # Create call log when room starts
            metadata = room.get("metadata", {})
            clinic_id = metadata.get("clinic_id")
            channel = metadata.get("channel", "phone")

            if clinic_id and room_name:
                await voice_service.create_call_log(
                    clinic_id=clinic_id,
                    room_name=room_name,
                    channel=CallChannel(channel),
                    direction=CallDirection.INBOUND,
                )

        elif event_type == "room_finished":
            # Update call log when room ends
            if room_name:
                await voice_service.end_call(room_name=room_name)

        elif event_type == "participant_joined":
            # Track participant joining
            participant = event.get("participant", {})
            participant_id = participant.get("identity")

            if room_name and participant_id:
                await voice_service.update_call_log(
                    room_name=room_name,
                    livekit_participant_id=participant_id,
                )

        return WebhookResponse(status="ok")

    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        # Return OK to prevent retries for non-critical errors
        return WebhookResponse(status="error")
