"""Streaming endpoint for clinic AI chat."""

import json
import time
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import StreamingResponse
from loguru import logger
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
from app.api.v1.endpoints.clinic_ai import ChatRequest, build_clinic_data
from app.core.config import settings
from app.core.instrumentation import (
    chat_response_duration_seconds,
    increment_active_chat_sessions,
    record_chat_message,
    traced,
)
from app.core.redis import get_redis
from app.db import get_db as get_session

router = APIRouter()


async def stream_chat_response(
    request: ChatRequest,
    clinic: ClinicDep,
    db: AsyncSession,
    redis: Redis,
) -> AsyncIterator[str]:
    """Generate streaming chat response.

    Yields Server-Sent Events (SSE) formatted chunks.
    """
    try:
        logger.info(
            f"[POST /api/v1/{clinic.slug}/chat/stream] Chat stream request - User: {request.user_identifier}, Message: {request.message[:50]}..."
        )

        # Initialize managers
        session_manager = SessionManager(redis)
        history_manager = HistoryManager(db)

        # Get or create conversation (same logic as non-streaming)
        if request.conversation_id:
            session = await session_manager.get_session(request.conversation_id)
            if not session:
                conversation = await history_manager.get_conversation(
                    request.conversation_id
                )
                if not conversation or conversation.clinic_id != clinic.id:
                    yield f"data: {json.dumps({'error': 'Conversation not found'})}\n\n"
                    return

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
            conversation = await history_manager.create_conversation(
                clinic_id=clinic.id,
                channel="chat",
                user_identifier=request.user_identifier,
                context={"agent": "faq"},
                extra_data={"source": "clinic_chat_stream", "clinic_slug": clinic.slug},
            )
            conversation_id = conversation.id

            # Flush to database so foreign key constraint is satisfied
            await db.flush()

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
            increment_active_chat_sessions(str(clinic.id))

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

        # Build clinic data with persona
        clinic_data = build_clinic_data(clinic)

        # Create agent dependencies
        deps = AgentDependencies(
            db_session=db,
            redis_client=redis,
            session_manager=session_manager,
            history_manager=history_manager,
            clinic_id=clinic.id,
            conversation_id=conversation_id,
            pims_adapter=None,
        )

        # Create FAQ agent with clinic-specific prompt
        faq_agent = create_faq_agent(clinic_data=clinic_data)

        # Send conversation_id first
        yield f"data: {json.dumps({'type': 'conversation_id', 'conversation_id': str(conversation_id)})}\n\n"

        # Stream the response
        full_response = ""
        total_tokens = 0
        llm_start_time = time.perf_counter()

        async with faq_agent.agent.run_stream(
            user_prompt=request.message,
            deps=deps,
            message_history=[
                {"role": msg.role, "content": msg.content}
                for msg in session.message_history  # Use all messages in session
            ],
        ) as stream_result:
            async for chunk in stream_result.stream_text():
                full_response += chunk
                # Send token chunk
                yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"

            # Get usage info if available
            try:
                usage_result = stream_result.usage()
                total_tokens = (
                    usage_result.total_tokens
                    if hasattr(usage_result, "total_tokens")
                    else 0
                )
            except (AttributeError, TypeError, ValueError):
                # Log the exception but continue with 0 tokens
                # This could happen if the LLM provider doesn't return usage info
                total_tokens = 0

        # Record LLM response duration
        llm_duration = time.perf_counter() - llm_start_time
        chat_response_duration_seconds.record(
            llm_duration,
            {"clinic_id": str(clinic.id), "agent": "faq_agent", "streaming": "true"},
        )

        # Save assistant message
        assistant_message = MessageData(
            role="assistant",
            content=full_response,
            agent_name="faq_agent",
            model_name=None,
            timestamp=datetime.now(UTC),
        )
        await history_manager.save_message(conversation_id, assistant_message)

        # Record assistant message metric
        record_chat_message(
            clinic_id=str(clinic.id),
            session_id=str(conversation_id),
            role="assistant",
            tokens=total_tokens,
        )

        # Update session
        session.add_message(assistant_message)
        session.total_tokens += total_tokens
        await session_manager.update_session(session)

        # Commit DB changes
        await db.commit()

        logger.success(
            f"✅ Chat stream complete | Response: {full_response[:50]}... | Tokens: {total_tokens} | Duration: {llm_duration:.2f}s"
        )

        # Send completion message
        yield f"data: {json.dumps({'type': 'done', 'tokens_used': total_tokens})}\n\n"

    except Exception as e:
        await db.rollback()
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"


@router.post(
    "/{clinic_slug}/chat/stream",
    status_code=status.HTTP_200_OK,
    summary="Send chat message with streaming response",
    description="Send a message and receive streaming AI response via Server-Sent Events.",
)
@traced(span_name="endpoint.clinic_chat_stream")
async def clinic_chat_stream(
    request: ChatRequest,
    http_request: Request,
    clinic: ClinicDep,
    db: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
) -> StreamingResponse:
    """Stream chat response from clinic AI assistant.

    Returns Server-Sent Events (SSE) stream.
    """
    # Get origin for CORS headers
    origin = http_request.headers.get("origin", "*")

    return StreamingResponse(
        stream_chat_response(request, clinic, db, redis),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
        },
    )
