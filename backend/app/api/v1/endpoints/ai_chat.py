"""AI Chat endpoint for testing the conversation system.

Simple REST endpoint to test FAQ agent and conversation flow.
"""

import time
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.agents import AgentDependencies, create_faq_agent
from app.ai.state import (
    ConversationContext,
    ConversationSession,
    HistoryManager,
    MessageData,
    SessionManager,
)
from app.core.config import settings
from app.core.instrumentation import (
    chat_response_duration_seconds,
    record_chat_message,
    traced,
)
from app.core.redis import get_redis
from app.db import get_db as get_session

router = APIRouter(prefix="/ai/chat", tags=["AI Chat"])


# Request/Response Models
class ChatRequest(BaseModel):
    """Chat request from user."""

    message: str = Field(..., min_length=1, max_length=1000)
    conversation_id: UUID | None = None
    clinic_id: UUID = Field(..., description="Clinic UUID")
    user_identifier: str = Field(..., description="User phone/email/ID")


class ChatResponse(BaseModel):
    """Chat response to user."""

    conversation_id: UUID
    message: str
    agent_name: str
    model_used: str | None = None
    tokens_used: int | None = None


@router.post("/message", response_model=ChatResponse, status_code=status.HTTP_200_OK)
@traced(span_name="endpoint.ai_chat_message")
async def send_chat_message(
    request: ChatRequest,
    db: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
) -> ChatResponse:
    """Send a chat message and get AI response.

    This is a simple test endpoint for the FAQ agent.

    Args:
        request: Chat request with message and context
        db: Database session
        redis: Redis client

    Returns:
        ChatResponse with AI reply

    Raises:
        HTTPException: If clinic not found or other errors
    """
    # Initialize managers
    session_manager = SessionManager(redis)
    history_manager = HistoryManager(db)

    # Get or create conversation
    if request.conversation_id:
        # Resume existing conversation
        session = await session_manager.get_session(request.conversation_id)
        if not session:
            # Session expired in Redis, fetch from DB
            conversation = await history_manager.get_conversation(
                request.conversation_id
            )
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found",
                )

            # Recreate session from DB
            session = ConversationSession(
                conversation_id=conversation.id,
                context=ConversationContext(
                    conversation_id=conversation.id,
                    clinic_id=conversation.clinic_id,
                    channel="chat",
                    user_identifier=conversation.user_identifier,
                    current_agent="faq",
                    intent=conversation.intent,
                    metadata=conversation.context,
                ),
                message_history=[],
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
                expires_at=datetime.now(UTC)
                + timedelta(seconds=settings.conversation_session_ttl_seconds),
            )
            await session_manager.create_session(session)

        conversation_id = session.conversation_id
    else:
        # Create new conversation
        conversation = await history_manager.create_conversation(
            clinic_id=request.clinic_id,
            channel="chat",
            user_identifier=request.user_identifier,
            context={"agent": "faq"},
            extra_data={"source": "test_endpoint"},
        )
        conversation_id = conversation.id

        # Create session in Redis
        session = ConversationSession(
            conversation_id=conversation_id,
            context=ConversationContext(
                conversation_id=conversation_id,
                clinic_id=request.clinic_id,
                channel="chat",
                user_identifier=request.user_identifier,
                current_agent="faq",
                metadata={},
            ),
            message_history=[],
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            expires_at=datetime.now(UTC)
            + timedelta(seconds=settings.conversation_session_ttl_seconds),
        )
        await session_manager.create_session(session)

    # Save user message
    user_message = MessageData(
        role="user",
        content=request.message,
        timestamp=datetime.now(UTC),
    )
    await history_manager.save_message(conversation_id, user_message)
    session.add_message(user_message)

    # Record user message metric
    record_chat_message(
        clinic_id=str(request.clinic_id),
        session_id=str(conversation_id),
        role="user",
    )

    # Fetch clinic data for dynamic prompt
    from sqlalchemy import select

    from app.models.clinic import Clinic

    stmt = select(Clinic).where(Clinic.id == request.clinic_id)
    result = await db.execute(stmt)
    clinic = result.scalar_one_or_none()

    if not clinic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinic not found",
        )

    # Build clinic data dictionary for agent
    clinic_data = {
        "name": clinic.name,
        "phone": clinic.phone,
        "email": clinic.email,
        "website": clinic.website,
        "address": f"{clinic.address_line1 or ''}, {clinic.city or ''}, {clinic.state or ''} {clinic.postal_code or ''}".strip(
            ", "
        ),
        "city": clinic.city,
        "state": clinic.state,
        "timezone": clinic.timezone,
        "business_hours": clinic.business_hours,
        "voice_settings": clinic.voice_settings,
        "emergency_phone": clinic.emergency_phone,
    }

    # Create agent dependencies
    deps = AgentDependencies(
        db_session=db,
        redis_client=redis,
        session_manager=session_manager,
        history_manager=history_manager,
        clinic_id=request.clinic_id,
        conversation_id=conversation_id,
        pims_adapter=None,  # Not configured for test
    )

    # Run FAQ agent with clinic-specific prompt
    faq_agent = create_faq_agent(clinic_data=clinic_data)

    try:
        # Time the LLM response
        start_time = time.perf_counter()
        result = await faq_agent.run(
            user_input=request.message,
            deps=deps,
            message_history=[
                {"role": msg.role, "content": msg.content}
                for msg in session.message_history[-5:]  # Last 5 messages
            ],
        )
        response_duration = time.perf_counter() - start_time

        # Record chat response duration
        chat_response_duration_seconds.record(
            response_duration,
            {"clinic_id": str(request.clinic_id), "agent": "faq_agent"},
        )

        # Extract response
        assistant_response = (
            str(result.output) if hasattr(result, "output") else str(result)
        )

        # Get usage info if available
        tokens_used = None
        if hasattr(result, "usage") and result.usage:
            tokens_used = result.usage().total_tokens

        # Save assistant message
        assistant_message = MessageData(
            role="assistant",
            content=assistant_response,
            agent_name="faq_agent",
            model_name=result.model if hasattr(result, "model") else None,
            timestamp=datetime.now(UTC),
        )
        await history_manager.save_message(conversation_id, assistant_message)

        # Record assistant message metric
        record_chat_message(
            clinic_id=str(request.clinic_id),
            session_id=str(conversation_id),
            role="assistant",
            tokens=tokens_used or 0,
        )

        # Update session
        session.add_message(assistant_message)
        session.total_tokens += tokens_used or 0
        await session_manager.update_session(session)

        # Commit DB changes
        await db.commit()

        return ChatResponse(
            conversation_id=conversation_id,
            message=assistant_response,
            agent_name="faq_agent",
            model_used=result.model if hasattr(result, "model") else None,
            tokens_used=tokens_used,
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat: {e!s}",
        ) from e


@router.get(
    "/history/{conversation_id}",
    response_model=list[dict[str, Any]],
    status_code=status.HTTP_200_OK,
)
@traced(span_name="endpoint.ai_chat_history")
async def get_chat_history(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_session),
) -> list[dict[str, Any]]:
    """Get conversation history.

    Args:
        conversation_id: Conversation UUID
        db: Database session

    Returns:
        List of messages

    Raises:
        HTTPException: If conversation not found
    """
    history_manager = HistoryManager(db)

    conversation = await history_manager.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    messages = await history_manager.get_conversation_messages(conversation_id)

    return [
        {
            "id": str(msg.id),
            "role": msg.role,
            "content": msg.content,
            "agent_name": msg.agent_name,
            "model_name": msg.model_name,
            "created_at": msg.created_at.isoformat(),
        }
        for msg in messages
    ]
