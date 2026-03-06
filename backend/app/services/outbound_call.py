"""Outbound call service using Twilio."""

import asyncio
import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from twilio.rest import Client as TwilioClient
from twilio.twiml.voice_response import VoiceResponse

from app.core.config import settings
from app.models.call_log import CallChannel, CallDirection, CallLog, CallStatus
from app.models.clinic import Clinic
from app.schemas.outbound_call import CallPurpose

logger = logging.getLogger(__name__)

# Map Twilio status strings to our CallStatus enum
TWILIO_STATUS_MAP: dict[str, CallStatus] = {
    "queued": CallStatus.RINGING,
    "ringing": CallStatus.RINGING,
    "in-progress": CallStatus.IN_PROGRESS,
    "completed": CallStatus.COMPLETED,
    "busy": CallStatus.BUSY,
    "no-answer": CallStatus.NO_ANSWER,
    "failed": CallStatus.FAILED,
    "canceled": CallStatus.FAILED,
}


class OutboundCallService:
    """Service for initiating and managing outbound calls via Twilio."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _get_twilio_client(self) -> TwilioClient:
        """Create a Twilio REST client from settings."""
        if not settings.twilio_account_sid or not settings.twilio_auth_token:
            raise ValueError("Twilio credentials are not configured")
        return TwilioClient(
            settings.twilio_account_sid,
            settings.twilio_auth_token.get_secret_value(),
        )

    async def initiate_call(
        self,
        clinic: Clinic,
        to_phone: str,
        purpose: CallPurpose,
        message: str | None = None,
    ) -> CallLog:
        """Initiate an outbound call via Twilio and create a CallLog.

        Args:
            clinic: The clinic initiating the call.
            to_phone: Destination phone in E.164 format.
            purpose: Purpose of the call.
            message: Optional message to deliver.

        Returns:
            The created CallLog record.

        Raises:
            ValueError: If clinic has no Twilio phone number or creds missing.
        """
        if not clinic.twilio_phone_number:
            raise ValueError("Clinic does not have a Twilio phone number configured")

        twilio_client = self._get_twilio_client()

        base_url = settings.base_url.rstrip("/")
        status_callback_url = f"{base_url}/api/v1/outbound-calls/webhooks/status"
        twiml_url = f"{base_url}/api/v1/outbound-calls/webhooks/twiml"

        # Twilio SDK is synchronous — run in thread pool
        call = await asyncio.to_thread(
            twilio_client.calls.create,
            to=to_phone,
            from_=clinic.twilio_phone_number,
            url=twiml_url,
            status_callback=status_callback_url,
            status_callback_event=["initiated", "ringing", "answered", "completed"],
        )

        # Create CallLog record
        call_log = CallLog(
            clinic_id=clinic.id,
            twilio_call_sid=call.sid,
            direction=CallDirection.OUTBOUND,
            status=CallStatus.RINGING,
            channel=CallChannel.PHONE,
            from_phone=clinic.twilio_phone_number,
            to_phone=to_phone,
            started_at=datetime.now(UTC),
            ai_handled=True,
            extra_data={"purpose": purpose.value, "message": message},
        )
        self.db.add(call_log)
        await self.db.flush()

        logger.info(
            "Outbound call initiated: call_log_id=%s, twilio_sid=%s, to=%s",
            call_log.id,
            call.sid,
            to_phone,
        )

        return call_log

    async def get_call(self, call_id: UUID, clinic_id: UUID) -> CallLog | None:
        """Get an outbound call by ID, scoped to clinic."""
        result = await self.db.execute(
            select(CallLog).where(
                and_(
                    CallLog.id == str(call_id),
                    CallLog.clinic_id == str(clinic_id),
                    CallLog.direction == CallDirection.OUTBOUND,
                    CallLog.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    def generate_twiml(self, message: str | None = None) -> str:
        """Generate TwiML response for a connected outbound call.

        Args:
            message: Optional message to speak.

        Returns:
            TwiML XML string.
        """
        response = VoiceResponse()
        if message:
            response.say(message, voice="Polly.Joanna")
        else:
            response.say(
                "Hello, this is an automated call from your veterinary clinic. "
                "Please hold while we connect you.",
                voice="Polly.Joanna",
            )
        return str(response)

    async def handle_status_callback(
        self,
        call_sid: str,
        twilio_status: str,
        duration: int | None = None,
    ) -> CallLog | None:
        """Update CallLog from a Twilio status callback.

        Args:
            call_sid: Twilio Call SID.
            twilio_status: Twilio call status string.
            duration: Call duration in seconds (from Twilio).

        Returns:
            Updated CallLog or None if not found.
        """
        result = await self.db.execute(
            select(CallLog).where(CallLog.twilio_call_sid == call_sid)
        )
        call_log = result.scalar_one_or_none()

        if not call_log:
            logger.warning("Status callback for unknown call_sid: %s", call_sid)
            return None

        new_status = TWILIO_STATUS_MAP.get(twilio_status, CallStatus.FAILED)
        call_log.status = new_status

        if duration is not None:
            call_log.duration_seconds = duration

        if new_status in (
            CallStatus.COMPLETED,
            CallStatus.FAILED,
            CallStatus.BUSY,
            CallStatus.NO_ANSWER,
        ):
            call_log.ended_at = datetime.now(UTC)

        await self.db.flush()

        logger.info(
            "Call status updated: sid=%s, status=%s", call_sid, new_status.value
        )
        return call_log
