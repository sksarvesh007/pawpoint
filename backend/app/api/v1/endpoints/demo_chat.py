"""Demo chat endpoint - Simple LLM endpoint for the demo page.

This endpoint provides a standalone chatbot for the /demo page that doesn't
require a real clinic in the database. Uses hardcoded demo clinic data.
"""

import json
import time
from collections.abc import AsyncIterator

from fastapi import APIRouter, status
from fastapi.responses import StreamingResponse
from httpx import HTTPStatusError
from loguru import logger
from pydantic import BaseModel, Field

from app.ai.models.factory import ModelFactory
from app.ai.prompts import build_faq_system_prompt
from app.core.instrumentation import (
    chat_response_duration_seconds,
    record_chat_message,
    traced,
)

router = APIRouter(tags=["Demo"])

# Hardcoded demo clinic data - no database required
DEMO_CLINIC_DATA = {
    "name": "PawPoint Demo Clinic",
    "phone": "+1 (555) 123-4567",
    "email": "hello@pawpoint-demo.com",
    "website": "https://pawpoint.demo",
    "address": "123 Demo Street, San Francisco, CA 94102",
    "city": "San Francisco",
    "state": "CA",
    "timezone": "America/Los_Angeles",
    "business_hours": {
        "monday": {"open": "08:00", "close": "18:00"},
        "tuesday": {"open": "08:00", "close": "18:00"},
        "wednesday": {"open": "08:00", "close": "18:00"},
        "thursday": {"open": "08:00", "close": "18:00"},
        "friday": {"open": "08:00", "close": "17:00"},
        "saturday": {"open": "09:00", "close": "14:00"},
        "sunday": {"closed": True},
    },
    "voice_settings": {
        "personality": "friendly, warm, and professional",
        "greeting": "Welcome to PawPoint Demo Clinic! How can I help you and your pet today?",
        "services": [
            "wellness exams",
            "vaccinations",
            "dental care",
            "surgery",
            "emergency care",
            "pet grooming",
            "boarding",
        ],
    },
    "emergency_phone": "+1 (555) 911-PETS",
}


class DemoChatRequest(BaseModel):
    """Demo chat request."""

    message: str = Field(..., min_length=1, max_length=1000)
    conversation_id: str | None = None
    user_identifier: str = Field(default="demo_user")


async def stream_demo_response(
    message: str,
    conversation_id: str | None,
) -> AsyncIterator[str]:
    """Generate streaming demo chat response.

    Uses the LLM directly without database dependencies.

    Args:
        message: User message
        conversation_id: Optional conversation ID for continuity

    Yields:
        Server-Sent Events formatted chunks
    """
    llm_start_time = time.perf_counter()

    try:
        logger.info(
            f"[POST /api/v1/demo-clinic/chat/stream] Demo chat request - Message: {message[:50]}..."
        )
        # Get the model
        model = ModelFactory.get_model_for_task("faq", channel="chat")

        # Build system prompt with demo clinic data
        system_prompt = build_faq_system_prompt(DEMO_CLINIC_DATA)

        # Send conversation_id (generate one if not provided)
        import uuid

        conv_id = conversation_id or str(uuid.uuid4())
        yield f"data: {json.dumps({'type': 'conversation_id', 'conversation_id': conv_id})}\n\n"

        # Create a simple agent for streaming
        from pydantic_ai import Agent

        demo_agent = Agent(
            model=model,
            system_prompt=system_prompt,
        )

        # Stream the response
        full_response = ""
        async with demo_agent.run_stream(message) as stream_result:
            async for chunk in stream_result.stream_text():
                full_response += chunk
                yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"

        # Record LLM response duration
        llm_duration = time.perf_counter() - llm_start_time
        chat_response_duration_seconds.record(
            llm_duration,
            {"clinic_id": "demo", "agent": "demo_agent", "streaming": "true"},
        )

        # Record chat messages
        record_chat_message(clinic_id="demo", session_id=conv_id, role="user")
        record_chat_message(
            clinic_id="demo", session_id=conv_id, role="assistant", tokens=0
        )

        logger.success(
            f"✅ Demo chat complete | Response: {full_response[:50]}... | Duration: {llm_duration:.2f}s"
        )

        # Send completion
        yield f"data: {json.dumps({'type': 'done', 'tokens_used': 0})}\n\n"

    except HTTPStatusError as e:
        # HTTP errors (429 rate limit, etc.)
        if e.response.status_code == 429:
            friendly_message = (
                "Our AI assistant is currently busy. Please try again in a minute! 🐾"
            )
            yield f"data: {json.dumps({'type': 'token', 'content': friendly_message})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'tokens_used': 0})}\n\n"
        else:
            yield f"data: {json.dumps({'type': 'error', 'message': 'Something went wrong. Please try again later.'})}\n\n"

    except Exception as e:
        # Check for rate limit indicators in exception (Google API, OpenAI, etc.)
        error_type = type(e).__name__
        if error_type == "ResourceExhausted" or "rate" in error_type.lower():
            friendly_message = (
                "Our AI assistant is currently busy. Please try again in a minute! 🐾"
            )
            yield f"data: {json.dumps({'type': 'token', 'content': friendly_message})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'tokens_used': 0})}\n\n"
        else:
            yield f"data: {json.dumps({'type': 'error', 'message': 'Something went wrong. Please try again later.'})}\n\n"


@router.post(
    "/demo-clinic/chat/stream",
    status_code=status.HTTP_200_OK,
    summary="Demo chat with streaming response",
    description="Send a message to the demo chatbot and receive streaming AI response. No authentication required.",
)
@traced(span_name="endpoint.demo_chat_stream")
async def demo_chat_stream(request: DemoChatRequest) -> StreamingResponse:
    """Stream chat response from demo AI assistant.

    This endpoint is specifically for the /demo page and doesn't require
    a real clinic in the database. Uses hardcoded demo clinic configuration.

    Returns:
        Server-Sent Events (SSE) stream with AI response
    """
    return StreamingResponse(
        stream_demo_response(request.message, request.conversation_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
