"""Clinic-specific AI endpoints with slug-based routing.

Each clinic gets its own AI assistant at:
  /{clinic-slug}/chat
  /{clinic-slug}/voice
  /{clinic-slug}/appointments

The AI assistant automatically loads clinic-specific configuration
and uses dynamic prompts based on the clinic's settings.
"""

import time
from datetime import UTC, datetime, timedelta
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
from app.api.dependencies import ClinicDep
from app.core.config import settings
from app.core.instrumentation import (
    active_chat_sessions,
    chat_response_duration_seconds,
    record_chat_message,
    traced,
)
from app.core.redis import get_redis
from app.db import get_db as get_session
from app.models.clinic import Clinic

router = APIRouter()


# Request/Response Models
class ChatRequest(BaseModel):
    """Chat request from user."""

    message: str = Field(..., min_length=1, max_length=1000)
    conversation_id: UUID | None = None
    user_identifier: str = Field(
        ...,
        description="User phone/email/ID for conversation tracking",
    )


class ChatResponse(BaseModel):
    """Chat response to user."""

    conversation_id: UUID
    message: str
    agent_name: str
    clinic_name: str
    model_used: str | None = None
    tokens_used: int | None = None


def build_clinic_data(clinic: Clinic) -> dict[str, object]:
    """Build clinic data dictionary for AI agents.

    Args:
        clinic: Clinic model instance

    Returns:
        Dictionary with clinic information for dynamic prompts
    """
    return {
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


@router.post(
    "/{clinic_slug}/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send chat message to clinic AI",
    description="Send a message to the clinic's AI assistant. Automatically loads clinic configuration.",
)
@traced(span_name="endpoint.clinic_chat")
async def clinic_chat(
    request: ChatRequest,
    clinic: ClinicDep,  # Automatically loaded from {clinic_slug}
    db: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
) -> ChatResponse:
    """Send a chat message to clinic-specific AI assistant.

    The AI assistant automatically:
    - Loads clinic's business hours, services, policies
    - Uses clinic's custom personality and greeting
    - Includes clinic-specific instructions

    Args:
        clinic_slug: Clinic slug from URL (e.g., 'happy-paws-vet')
        request: Chat request with message and user info
        clinic: Automatically injected clinic instance
        db: Database session
        redis: Redis client

    Returns:
        ChatResponse with AI reply and metadata

    Raises:
        HTTPException 404: If clinic not found
        HTTPException 500: If processing fails
    """
    from loguru import logger

    logger.info(
        f"[POST /api/v1/{clinic.slug}/chat] Chat request - User: {request.user_identifier}, Message: {request.message[:50]}..."
    )

    # Initialize managers
    logger.debug("Initializing session manager with Redis")
    session_manager = SessionManager(redis)
    history_manager = HistoryManager(db)

    # Get or create conversation
    if request.conversation_id:
        # Resume existing conversation
        logger.info(
            f"[POST /api/v1/{clinic.slug}/chat] Resuming conversation: {request.conversation_id}"
        )
        session = await session_manager.get_session(request.conversation_id)

        if not session:
            # Session expired in Redis, fetch from DB
            logger.warning(
                f"[POST /api/v1/{clinic.slug}/chat] Session {request.conversation_id} expired in Redis, loading from database"
            )
            conversation = await history_manager.get_conversation(
                request.conversation_id
            )
            if not conversation or conversation.clinic_id != clinic.id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found or doesn't belong to this clinic",
                )

            # Load recent message history from DB
            recent_messages = await history_manager.get_conversation_messages(
                conversation_id=conversation.id,
                limit=settings.conversation_max_history,  # Load last 20 messages
            )

            # Convert DB messages to MessageData for session
            message_history = [
                MessageData(
                    role=msg.role,  # type: ignore[arg-type]
                    content=msg.content or "",
                    agent_name=msg.agent_name,
                    model_name=msg.model_name,
                    timestamp=msg.created_at,
                    tool_calls=msg.tool_calls,
                    tool_call_id=msg.tool_call_id,
                )
                for msg in recent_messages
            ]

            # Recreate session from DB with message history
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
                message_history=message_history,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
                expires_at=datetime.now(UTC)
                + timedelta(seconds=settings.conversation_session_ttl_seconds),
            )
            await session_manager.create_session(session)

        conversation_id = session.conversation_id
    else:
        # Create new conversation
        logger.info(
            f"[POST /api/v1/{clinic.slug}/chat] Creating new conversation for user: {request.user_identifier}"
        )
        conversation = await history_manager.create_conversation(
            clinic_id=clinic.id,
            channel="chat",
            user_identifier=request.user_identifier,
            context={"agent": "faq"},
            extra_data={"source": "clinic_chat_endpoint", "clinic_slug": clinic.slug},
        )
        conversation_id = conversation.id

        # Create session in Redis
        session = ConversationSession(
            conversation_id=conversation_id,
            context=ConversationContext(
                conversation_id=conversation_id,
                clinic_id=clinic.id,
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

        # Track new active session
        active_chat_sessions.add(1, {"clinic_id": str(clinic.id)})

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
        clinic_id=str(clinic.id),
        session_id=str(conversation_id),
        role="user",
    )

    # Build clinic data for dynamic prompt
    clinic_data = build_clinic_data(clinic)

    # Create agent dependencies
    deps = AgentDependencies(
        db_session=db,
        redis_client=redis,
        session_manager=session_manager,
        history_manager=history_manager,
        clinic_id=clinic.id,
        conversation_id=conversation_id,
        pims_adapter=None,  # Will be added in Phase 2
    )

    # Create FAQ agent with clinic-specific prompt
    faq_agent = create_faq_agent(clinic_data=clinic_data)

    try:
        # Run agent with full session history (up to conversation_max_history messages)
        logger.info(
            f"[POST /api/v1/{clinic.slug}/chat] Running FAQ agent - History: {len(session.message_history)} messages, Conversation: {conversation_id}"
        )

        # Time the LLM response
        start_time = time.perf_counter()
        result = await faq_agent.run(
            user_input=request.message,
            deps=deps,
            message_history=[
                {"role": msg.role, "content": msg.content}
                for msg in session.message_history  # Use all messages in session
            ],
        )
        response_duration = time.perf_counter() - start_time

        # Record chat response duration
        chat_response_duration_seconds.record(
            response_duration,
            {"clinic_id": str(clinic.id), "agent": "faq_agent"},
        )

        # Extract response
        assistant_response = (
            str(result.output) if hasattr(result, "output") else str(result)
        )

        # Get usage info if available
        tokens_used = None
        if hasattr(result, "usage") and result.usage:
            usage_result = result.usage()
            tokens_used = (
                usage_result.total_tokens
                if hasattr(usage_result, "total_tokens")
                else None
            )

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
            clinic_id=str(clinic.id),
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

        logger.success(
            f"✅ Chat complete | Response: {assistant_response[:50]}... | Tokens: {tokens_used}"
        )

        return ChatResponse(
            conversation_id=conversation_id,
            message=assistant_response,
            agent_name="faq_agent",
            clinic_name=clinic.name,
            model_used=result.model if hasattr(result, "model") else None,
            tokens_used=tokens_used,
        )

    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Chat error: {e!s}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat: {e!s}",
        ) from e


@router.get(
    "/{clinic_slug}/chat/history/{conversation_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get conversation history",
)
@traced(span_name="endpoint.clinic_chat_history")
async def get_clinic_chat_history(
    conversation_id: UUID,
    clinic: ClinicDep,
    db: AsyncSession = Depends(get_session),
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """Get conversation history for a clinic with pagination.

    Args:
        clinic_slug: Clinic slug from URL
        conversation_id: Conversation UUID
        clinic: Automatically injected clinic instance
        db: Database session
        limit: Maximum number of messages to return (default: 50, max: 200)
        offset: Number of messages to skip (default: 0)

    Returns:
        Dictionary with messages list and pagination metadata

    Raises:
        HTTPException 404: If conversation not found or doesn't belong to clinic
        HTTPException 400: If limit exceeds maximum
    """
    # Validate limit
    if limit > settings.message_history_max_limit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Limit cannot exceed {settings.message_history_max_limit} messages",
        )
    if limit < settings.message_history_min_limit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Limit must be at least {settings.message_history_min_limit}",
        )

    history_manager = HistoryManager(db)

    conversation = await history_manager.get_conversation(conversation_id)
    if not conversation or conversation.clinic_id != clinic.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or doesn't belong to this clinic",
        )

    messages = await history_manager.get_conversation_messages(
        conversation_id, limit=limit, offset=offset
    )

    return {
        "conversation_id": str(conversation_id),
        "total_messages": conversation.total_messages,
        "limit": limit,
        "offset": offset,
        "returned": len(messages),
        "messages": [
            {
                "id": str(msg.id),
                "role": msg.role,
                "content": msg.content,
                "agent_name": msg.agent_name,
                "model_name": msg.model_name,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in messages
        ],
    }


@router.get(
    "/{clinic_slug}/info",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get clinic AI configuration",
)
async def get_clinic_ai_info(
    clinic: ClinicDep,
) -> dict:
    """Get clinic's AI configuration and capabilities.

    Useful for embedding widgets or showing what the AI knows about.

    Args:
        clinic_slug: Clinic slug from URL
        clinic: Automatically injected clinic instance

    Returns:
        Dictionary with clinic AI capabilities
    """
    voice_settings = clinic.voice_settings or {}

    return {
        "clinic_name": clinic.name,
        "slug": clinic.slug,
        "ai_enabled": True,
        "voice_enabled": clinic.voice_enabled,
        "chatbot_name": voice_settings.get("chatbot_name"),
        "greeting_message": voice_settings.get(
            "greeting_message",
            voice_settings.get(
                "greeting",
                "Thank you for contacting us. How can I help you and your pet today?",
            ),
        ),
        "chatbot_persona": voice_settings.get(
            "chatbot_persona", voice_settings.get("personality", "professional")
        ),
        "capabilities": [
            "General questions",
            "Business hours",
            "Services information",
            "Pet care advice",
        ],
        "personality": voice_settings.get(
            "chatbot_persona",
            voice_settings.get("personality", "friendly and professional"),
        ),
        "available_channels": ["chat", "voice"] if clinic.voice_enabled else ["chat"],
        # Contact information
        "phone": clinic.phone,
        "email": clinic.email,
        "address": clinic.address_line1,
        "city": clinic.city,
        "state": clinic.state,
        "zip_code": clinic.postal_code,
        "business_hours": clinic.business_hours,
    }
