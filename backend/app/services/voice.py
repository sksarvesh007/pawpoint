"""
Voice Service

Handles voice-related business logic including token generation
and call management.
"""

import hashlib
import hmac
import json
import logging
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from livekit import api
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.call_log import (
    CallChannel,
    CallDirection,
    CallLog,
    CallOutcome,
    CallStatus,
)
from app.models.clinic import Clinic

logger = logging.getLogger(__name__)


class VoiceService:
    """Service for voice call management."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def generate_voice_token(
        self,
        clinic: Clinic,
        user_id: str,
        user_name: str | None = None,
    ) -> dict:
        """
        Generate a LiveKit access token for the browser voice widget.

        Args:
            clinic: The clinic object
            user_id: User's ID for identity
            user_name: User's display name (optional)

        Returns:
            Dict with token and room info

        Raises:
            ValueError: If voice is not enabled or LiveKit not configured
        """
        if not clinic.voice_enabled:
            raise ValueError("Voice is not enabled for this clinic")

        if not settings.livekit_api_key or not settings.livekit_api_secret:
            raise ValueError("LiveKit is not configured")

        # Generate unique room name
        room_name = f"voice-{clinic.id}-{uuid4()}"

        # Create room metadata
        room_metadata = {
            "clinic_id": str(clinic.id),
            "channel": "web_voice",
            "user_id": user_id,
        }

        # Create the room with metadata using LiveKit API
        # This ensures the agent receives the metadata when it joins
        # Convert ws:// to http:// for the API client (LiveKit API uses HTTP REST)
        api_url = settings.livekit_url.replace("ws://", "http://").replace(
            "wss://", "https://"
        )
        livekit_api = api.LiveKitAPI(
            api_url,
            settings.livekit_api_key,
            settings.livekit_api_secret.get_secret_value(),
        )

        try:
            await livekit_api.room.create_room(
                api.CreateRoomRequest(
                    name=room_name,
                    metadata=json.dumps(room_metadata),
                    empty_timeout=300,  # 5 minutes
                    max_participants=3,  # User + Agent + optional observer
                )
            )
            logger.info(
                f"Created LiveKit room: {room_name} with metadata: {room_metadata}"
            )
        except Exception as e:
            # Log the error but continue - agent can parse clinic_id from room name
            logger.warning(
                f"Failed to pre-create room {room_name}: {e}. "
                "Agent will parse clinic_id from room name."
            )
        finally:
            await livekit_api.aclose()

        # Create LiveKit token
        token = api.AccessToken(
            settings.livekit_api_key,
            settings.livekit_api_secret.get_secret_value(),
        )

        # Set identity and metadata
        token.with_identity(user_id)
        if user_name:
            token.with_name(user_name)

        # Set room grants
        token.with_grants(
            api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
                can_publish_data=False,  # Prevent data channel abuse
            )
        )

        # Set TTL
        token.with_ttl(timedelta(minutes=settings.livekit_token_ttl_minutes))

        return {
            "token": token.to_jwt(),
            "room_name": room_name,
            "ws_url": settings.livekit_ws_url,
            "metadata": room_metadata,
        }

    async def check_voice_status(self, clinic: Clinic) -> dict:
        """
        Check if voice is available for a clinic.

        Args:
            clinic: The clinic object

        Returns:
            Dict with voice availability status
        """
        # Check if voice is enabled
        if not clinic.voice_enabled:
            return {
                "available": False,
                "reason": "Voice not enabled for this clinic",
            }

        # Check if LiveKit is configured
        if not settings.livekit_api_key or not settings.livekit_api_secret:
            return {
                "available": False,
                "reason": "Voice service not configured",
            }

        # Get voice settings
        voice_settings = clinic.voice_settings or {}

        return {
            "available": True,
            "greeting_message": voice_settings.get(
                "greeting_message",
                f"Thank you for calling {clinic.name}. How can I help you today?",
            ),
            "chatbot_persona": voice_settings.get("chatbot_persona", "professional"),
        }

    async def create_call_log(
        self,
        clinic_id: str,
        room_name: str,
        channel: CallChannel,
        direction: CallDirection = CallDirection.INBOUND,
        from_phone: str = "web",
        to_phone: str = "agent",
        participant_id: str | None = None,
    ) -> CallLog:
        """
        Create a new call log entry.

        Args:
            clinic_id: Clinic ID
            room_name: LiveKit room name
            channel: Call channel (phone/web_voice)
            direction: Call direction
            from_phone: Caller phone/identifier
            to_phone: Recipient phone/identifier
            participant_id: LiveKit participant ID

        Returns:
            Created CallLog object
        """
        call_log = CallLog(
            clinic_id=clinic_id,
            livekit_room_name=room_name,
            livekit_participant_id=participant_id,
            channel=channel,
            direction=direction,
            status=CallStatus.IN_PROGRESS,
            from_phone=from_phone,
            to_phone=to_phone,
            started_at=datetime.now(UTC),
            ai_handled=True,
        )

        self.db.add(call_log)
        await self.db.commit()
        await self.db.refresh(call_log)

        return call_log

    async def update_call_log(
        self,
        room_name: str,
        **updates,
    ) -> CallLog | None:
        """
        Update a call log by room name.

        Args:
            room_name: LiveKit room name
            **updates: Fields to update

        Returns:
            Updated CallLog or None if not found
        """
        result = await self.db.execute(
            select(CallLog).where(CallLog.livekit_room_name == room_name)
        )
        call_log = result.scalar_one_or_none()

        if not call_log:
            return None

        for key, value in updates.items():
            if hasattr(call_log, key):
                setattr(call_log, key, value)

        await self.db.commit()
        await self.db.refresh(call_log)

        return call_log

    async def end_call(
        self,
        room_name: str,
        outcome: str | None = None,
        transcript: str | None = None,
        summary: str | None = None,
        actions_taken: list | None = None,
    ) -> CallLog | None:
        """
        Mark a call as ended and update final details.

        Args:
            room_name: LiveKit room name
            outcome: Call outcome
            transcript: Full transcript
            summary: AI-generated summary
            actions_taken: List of actions taken during call

        Returns:
            Updated CallLog or None if not found
        """
        result = await self.db.execute(
            select(CallLog).where(CallLog.livekit_room_name == room_name)
        )
        call_log = result.scalar_one_or_none()

        if not call_log:
            return None

        now = datetime.now(UTC)
        call_log.ended_at = now
        call_log.status = CallStatus.COMPLETED

        if call_log.started_at:
            call_log.duration_seconds = int((now - call_log.started_at).total_seconds())

        if outcome:
            call_log.outcome = CallOutcome(outcome)
        if transcript:
            call_log.transcript = transcript
        if summary:
            call_log.summary = summary
        if actions_taken:
            call_log.actions_taken = actions_taken

        await self.db.commit()
        await self.db.refresh(call_log)

        return call_log


def verify_livekit_webhook(body: bytes, signature: str) -> bool:
    """
    Verify LiveKit webhook signature.

    Args:
        body: Raw request body
        signature: X-LiveKit-Signature header value

    Returns:
        True if signature is valid
    """
    if not settings.livekit_api_secret:
        return False

    expected_sig = hmac.new(
        settings.livekit_api_secret.get_secret_value().encode(),
        body,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(signature, expected_sig)
