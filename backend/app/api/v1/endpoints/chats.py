"""Chat logs API endpoints."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.dependencies import get_current_clinic
from app.core.rate_limit import limiter
from app.db import get_db
from app.models.clinic import Clinic
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.analytics import ChatLogSummary
from app.schemas.chat_analysis import ChatAnalysisDetail

router = APIRouter()


class ChatLogsResponse(BaseModel):
    """Paginated chat logs response."""

    items: list[ChatLogSummary]
    total: int
    page: int
    limit: int
    total_pages: int


class MessageDetail(BaseModel):
    """Individual message in a chat conversation."""

    id: str
    role: str
    content: str | None
    created_at: datetime
    agent_name: str | None


class ChatLogDetail(BaseModel):
    """Full chat log with messages and optional analysis."""

    id: str
    started_at: datetime
    ended_at: datetime | None
    user_identifier: str
    total_messages: int
    intent: str | None
    session_active: bool
    summary: str | None
    messages: list[MessageDetail]
    analysis: ChatAnalysisDetail | None = None


@router.get("/", response_model=ChatLogsResponse)
@limiter.limit("100/minute")
async def list_chat_logs(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> ChatLogsResponse:
    """
    List recent chat logs with pagination.

    Returns chat conversations filtered by channel="chat", with analysis data.
    """
    # Count total chats
    count_result = await db.execute(
        select(func.count())
        .select_from(Conversation)
        .where(
            and_(
                Conversation.clinic_id == current_clinic.id,
                Conversation.channel == "chat",
            )
        )
    )
    total = count_result.scalar_one()

    # Get paginated chats with analysis
    offset = (page - 1) * limit
    result = await db.execute(
        select(Conversation)
        .options(joinedload(Conversation.analysis))
        .where(
            and_(
                Conversation.clinic_id == current_clinic.id,
                Conversation.channel == "chat",
            )
        )
        .order_by(Conversation.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    conversations = result.unique().scalars().all()

    # Convert to summaries with analysis data
    items = []
    for conv in conversations:
        analysis = conv.analysis
        items.append(
            ChatLogSummary(
                id=str(conv.id),
                started_at=conv.created_at,
                user_identifier=conv.user_identifier,
                total_messages=conv.total_messages,
                intent=conv.intent,
                session_active=conv.session_active,
                summary=conv.summary,
                sentiment=analysis.sentiment if analysis else None,
                resolution_status=analysis.resolution_status if analysis else None,
                primary_topic=analysis.primary_topic if analysis else None,
            )
        )

    total_pages = (total + limit - 1) // limit  # Ceiling division

    return ChatLogsResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
    )


@router.get("/{chat_id}", response_model=ChatLogDetail)
@limiter.limit("100/minute")
async def get_chat_log(
    request: Request,
    chat_id: UUID,
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> ChatLogDetail:
    """
    Get a single chat log by ID with all messages and analysis.
    """
    # Get conversation with analysis
    result = await db.execute(
        select(Conversation)
        .options(joinedload(Conversation.analysis))
        .where(
            and_(
                Conversation.id == chat_id,
                Conversation.clinic_id == current_clinic.id,
                Conversation.channel == "chat",
            )
        )
    )
    conversation = result.unique().scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Chat log not found")

    # Get messages for this conversation
    messages_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == chat_id)
        .order_by(Message.created_at.asc())
    )
    messages = messages_result.scalars().all()

    # Convert messages to response format
    message_details = [
        MessageDetail(
            id=str(msg.id),
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at,
            agent_name=msg.agent_name,
        )
        for msg in messages
    ]

    # Build analysis detail if available
    analysis_detail = None
    if conversation.analysis and conversation.analysis.status == "completed":
        a = conversation.analysis
        analysis_detail = ChatAnalysisDetail(
            sentiment=a.sentiment or "",
            sentiment_score=a.sentiment_score or 0.0,
            resolution_status=a.resolution_status or "",
            user_satisfaction=a.user_satisfaction or "",
            primary_topic=a.primary_topic or "",
            topics=a.topics or [],
            entities=a.entities or {},
            key_points=a.key_points or [],
            suggested_followup=a.suggested_followup,
            analyzed_at=a.analyzed_at,
            status=a.status,
        )

    return ChatLogDetail(
        id=str(conversation.id),
        started_at=conversation.created_at,
        ended_at=conversation.session_ended_at,
        user_identifier=conversation.user_identifier,
        total_messages=conversation.total_messages,
        intent=conversation.intent,
        session_active=conversation.session_active,
        summary=conversation.summary,
        messages=message_details,
        analysis=analysis_detail,
    )
