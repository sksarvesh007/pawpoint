"""Shared test data factories for backend tests.

Factory functions to insert ORM objects directly for endpoints
that have no creation APIs (calls, chats, analytics).
"""

import uuid
from datetime import UTC, datetime

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.call_log import CallDirection, CallLog, CallOutcome, CallStatus
from app.models.chat_analysis import ChatAnalysis
from app.models.clinic import Clinic
from app.models.conversation import Conversation
from app.models.message import Message


async def setup_auth(db: AsyncSession, client: AsyncClient) -> Clinic:
    """Register a clinic + user and log in. Returns the authenticated clinic.

    The register endpoint creates its own Clinic, so we fetch
    the actual ORM object from the response's clinic ID.
    """
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    clinic_name = f"TestClinic-{uuid.uuid4().hex[:6]}"

    register_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "TestPass123!",
            "clinic_name": clinic_name,
        },
    )
    assert register_resp.status_code == 201
    clinic_id = register_resp.json()["clinic"]["id"]

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "TestPass123!"},
    )
    assert login_resp.status_code == 200

    # Fetch the actual Clinic ORM object created by the register endpoint
    result = await db.execute(select(Clinic).where(Clinic.id == uuid.UUID(clinic_id)))
    return result.scalar_one()


async def create_test_clinic(db: AsyncSession) -> Clinic:
    """Create a bare clinic (no user/auth) for scoping tests."""
    clinic = Clinic(
        name=f"TestClinic-{uuid.uuid4().hex[:6]}",
        slug=f"test-{uuid.uuid4().hex[:8]}",
        timezone="America/New_York",
    )
    db.add(clinic)
    await db.flush()
    return clinic


async def create_call_log(
    db: AsyncSession,
    clinic_id: uuid.UUID,
    **kwargs: object,
) -> CallLog:
    """Create a CallLog with sensible defaults."""
    defaults: dict[str, object] = {
        "clinic_id": clinic_id,
        "direction": CallDirection.INBOUND,
        "status": CallStatus.COMPLETED,
        "outcome": CallOutcome.INFORMATION_PROVIDED,
        "from_phone": "+15551234567",
        "to_phone": "+15559876543",
        "started_at": datetime.now(UTC),
        "duration_seconds": 120,
        "ai_handled": True,
        "ai_confidence_score": 0.95,
    }
    defaults.update(kwargs)
    call = CallLog(**defaults)
    db.add(call)
    await db.flush()
    return call


async def create_conversation(
    db: AsyncSession,
    clinic_id: uuid.UUID,
    **kwargs: object,
) -> Conversation:
    """Create a Conversation with sensible defaults (channel=chat)."""
    defaults: dict[str, object] = {
        "clinic_id": clinic_id,
        "channel": "chat",
        "user_identifier": f"user-{uuid.uuid4().hex[:8]}@example.com",
        "session_active": False,
        "total_messages": 0,
        "total_tokens": 0,
    }
    defaults.update(kwargs)
    conv = Conversation(**defaults)
    db.add(conv)
    await db.flush()
    return conv


async def create_message(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    **kwargs: object,
) -> Message:
    """Create a Message with sensible defaults."""
    defaults: dict[str, object] = {
        "conversation_id": conversation_id,
        "role": "user",
        "content": "Hello",
    }
    defaults.update(kwargs)
    msg = Message(**defaults)
    db.add(msg)
    await db.flush()
    return msg


async def create_chat_analysis(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    **kwargs: object,
) -> ChatAnalysis:
    """Create a ChatAnalysis with sensible defaults (completed, positive)."""
    defaults: dict[str, object] = {
        "conversation_id": conversation_id,
        "status": "completed",
        "sentiment": "positive",
        "sentiment_score": 0.8,
        "resolution_status": "resolved",
        "user_satisfaction": "satisfied",
        "primary_topic": "appointment_inquiry",
        "topics": ["appointments", "scheduling"],
        "entities": {"pet_names": ["Max"], "pet_species": ["dog"]},
        "key_points": ["Client asked about appointment availability"],
        "analyzed_at": datetime.now(UTC),
    }
    defaults.update(kwargs)
    analysis = ChatAnalysis(**defaults)
    db.add(analysis)
    await db.flush()
    return analysis
