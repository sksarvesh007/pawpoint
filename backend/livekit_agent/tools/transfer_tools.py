"""
Call Transfer and Message Tools

Tools for transferring calls to staff and taking messages.
"""

import json
import logging
from datetime import datetime

import redis.asyncio as redis

logger = logging.getLogger(__name__)


async def transfer_call(
    redis_client: redis.Redis,
    room_name: str,
    clinic_id: str,
    reason: str,
    caller_name: str | None = None,
    caller_phone: str | None = None,
) -> str:
    """
    Transfer the call to clinic staff.

    This queues a transfer request and notifies the session to hand off.

    Args:
        redis_client: Redis client
        room_name: LiveKit room name
        clinic_id: Clinic ID
        reason: Reason for transfer
        caller_name: Caller's name if known
        caller_phone: Caller's phone number

    Returns:
        Voice message to play before transfer
    """
    try:
        # Queue transfer notification
        transfer_data = {
            "room_name": room_name,
            "clinic_id": clinic_id,
            "reason": reason,
            "caller_name": caller_name,
            "caller_phone": caller_phone,
            "timestamp": datetime.utcnow().isoformat(),
        }

        await redis_client.rpush("transfer_queue", json.dumps(transfer_data))

        # Signal the room to perform transfer
        await redis_client.publish(
            f"room:{room_name}:transfer",
            json.dumps({"action": "transfer", "reason": reason}),
        )

        return "I'm connecting you with one of our staff members now. Please hold for just a moment."

    except Exception as e:
        logger.error(f"Transfer error: {e}")
        return "I'm having trouble connecting you. Please hold while I try again."


async def take_message(
    redis_client: redis.Redis,
    clinic_id: str,
    caller_name: str,
    message: str,
    callback_number: str,
    urgency: str = "normal",
    regarding_pet: str | None = None,
) -> str:
    """
    Take a message for clinic staff.

    Messages are queued for staff review.

    Args:
        redis_client: Redis client
        clinic_id: Clinic ID
        caller_name: Name of the caller
        message: The message content
        callback_number: Number to call back
        urgency: Message urgency (normal, urgent)
        regarding_pet: Pet the message is about (optional)

    Returns:
        Voice confirmation message
    """
    try:
        message_id = datetime.utcnow().strftime("%Y%m%d%H%M%S")

        message_data = {
            "id": message_id,
            "clinic_id": clinic_id,
            "caller_name": caller_name,
            "message": message,
            "callback_number": callback_number,
            "urgency": urgency,
            "regarding_pet": regarding_pet,
            "source": "voice_ai",
            "created_at": datetime.utcnow().isoformat(),
        }

        await redis_client.rpush("message_queue", json.dumps(message_data))

        if urgency == "urgent":
            # Also notify immediately for urgent messages
            await redis_client.publish(
                f"clinic:{clinic_id}:urgent_message",
                json.dumps(message_data),
            )
            return (
                f"I've marked this as urgent and notified our staff immediately. "
                f"Someone will call you back at {callback_number} as soon as possible. "
                f"Is there anything else I can help with while you wait?"
            )
        else:
            return (
                f"I've taken your message for our staff. "
                f"Someone will call you back at {callback_number} during business hours. "
                f"Is there anything else I can help you with?"
            )

    except Exception as e:
        logger.error(f"Message taking error: {e}")
        return "I had trouble saving your message. Could you repeat the main points?"


def check_emergency_keywords(text: str, keywords: list[str]) -> bool:
    """
    Check if text contains emergency keywords.

    Args:
        text: Text to check
        keywords: List of emergency keywords

    Returns:
        True if emergency keywords found
    """
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in keywords)
