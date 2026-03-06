"""Outbound calls API endpoints."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from twilio.request_validator import RequestValidator

from app.core.config import settings
from app.core.dependencies import get_current_clinic
from app.db import get_db
from app.models.clinic import Clinic
from app.schemas.outbound_call import (
    OutboundCallRequest,
    OutboundCallResponse,
    OutboundCallStatus,
)
from app.services.outbound_call import OutboundCallService

logger = logging.getLogger(__name__)

router = APIRouter()


def _validate_twilio_signature(request: Request, params: dict[str, str]) -> None:
    """Validate that the request came from Twilio.

    Raises HTTPException 403 if validation fails.
    """
    if not settings.twilio_auth_token:
        raise HTTPException(status_code=500, detail="Twilio auth token not configured")

    signature = request.headers.get("X-Twilio-Signature", "")
    validator = RequestValidator(settings.twilio_auth_token.get_secret_value())
    url = str(request.url)

    if not validator.validate(url, params, signature):
        logger.warning("Invalid Twilio signature for %s", url)
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")


@router.post("/", response_model=OutboundCallResponse)
async def initiate_outbound_call(
    body: OutboundCallRequest,
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> OutboundCallResponse:
    """Initiate an outbound phone call via Twilio.

    Requires authentication. The call is placed from the clinic's
    Twilio phone number to the specified destination.
    """
    service = OutboundCallService(db)
    try:
        call_log = await service.initiate_call(
            clinic=current_clinic,
            to_phone=body.to_phone,
            purpose=body.purpose,
            message=body.message,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return OutboundCallResponse(
        call_id=str(call_log.id),
        twilio_call_sid=call_log.twilio_call_sid or "",
        status=call_log.status.value,
        from_phone=call_log.from_phone,
        to_phone=call_log.to_phone,
        purpose=body.purpose.value,
    )


@router.get("/{call_id}", response_model=OutboundCallStatus)
async def get_outbound_call(
    call_id: UUID,
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> OutboundCallStatus:
    """Get the status of an outbound call."""
    service = OutboundCallService(db)
    call_log = await service.get_call(call_id, current_clinic.id)

    if not call_log:
        raise HTTPException(status_code=404, detail="Outbound call not found")

    extra = call_log.extra_data or {}
    return OutboundCallStatus(
        call_id=str(call_log.id),
        twilio_call_sid=call_log.twilio_call_sid,
        status=call_log.status.value,
        from_phone=call_log.from_phone,
        to_phone=call_log.to_phone,
        purpose=extra.get("purpose"),
        duration_seconds=call_log.duration_seconds,
        started_at=call_log.started_at,
        ended_at=call_log.ended_at,
    )


@router.post("/webhooks/twiml")
async def twiml_webhook(
    request: Request,
    CallSid: str = Form(""),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """TwiML webhook — Twilio calls this when the outbound call connects.

    Returns TwiML XML telling Twilio what to say/do.
    """
    # Build params dict from form data for signature validation
    form_data = await request.form()
    params = {k: str(v) for k, v in form_data.items()}

    _validate_twilio_signature(request, params)

    service = OutboundCallService(db)

    # Try to find the call's stored message
    message: str | None = None
    if CallSid:
        from sqlalchemy import select

        from app.models.call_log import CallLog

        result = await db.execute(
            select(CallLog).where(CallLog.twilio_call_sid == CallSid)
        )
        call_log = result.scalar_one_or_none()
        if call_log and call_log.extra_data:
            message = call_log.extra_data.get("message")

    twiml = service.generate_twiml(message)
    return Response(content=twiml, media_type="application/xml")


@router.post("/webhooks/status")
async def status_callback(
    request: Request,
    CallSid: str = Form(...),
    CallStatus: str = Form(...),
    CallDuration: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Status callback webhook — Twilio posts call status updates here."""
    form_data = await request.form()
    params = {k: str(v) for k, v in form_data.items()}

    _validate_twilio_signature(request, params)

    duration = int(CallDuration) if CallDuration else None
    service = OutboundCallService(db)
    await service.handle_status_callback(CallSid, CallStatus, duration)

    return {"status": "ok"}
