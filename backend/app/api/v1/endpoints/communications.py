"""Communication history API — unified view of calls, chats, SMS, and emails."""

from typing import Literal

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_clinic
from app.db import get_db
from app.models.call_log import CallLog
from app.models.clinic import Clinic
from app.models.conversation import Conversation
from app.models.message_log import MessageLog

router = APIRouter()

ChannelFilter = Literal["call", "chat", "sms", "email"] | None


class CommunicationItem(BaseModel):
    """A single communication event in the timeline."""

    id: str
    channel: str  # "call", "chat", "sms", "email"
    timestamp: str
    contact: str  # phone, email, or user identifier
    summary: str | None = None
    status: str | None = None
    direction: str | None = None  # inbound/outbound for calls


class CommunicationsResponse(BaseModel):
    """Paginated communication history."""

    items: list[CommunicationItem]
    total: int
    page: int
    limit: int
    total_pages: int


@router.get("/", response_model=CommunicationsResponse)
async def list_communications(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    channel: ChannelFilter = Query(None, description="Filter: call, chat, sms, email"),
    search: str | None = Query(None, description="Search by contact"),
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> CommunicationsResponse:
    """List all communications (calls, chats, SMS, emails) in a unified timeline.

    Pagination note: when no channel filter is set, items from all sources are
    merged and sorted by timestamp. Total is the sum of per-channel counts.
    """
    clinic_id = current_clinic.id
    offset = (page - 1) * limit

    include_calls = channel is None or channel == "call"
    include_chats = channel is None or channel == "chat"
    include_messages = channel is None or channel in ("sms", "email")

    # Initialize condition lists (populated per-channel below)
    call_conditions: list = []
    chat_conditions: list = []
    msg_conditions: list = []

    # ------------------------------------------------------------------ #
    # Step 1: count each active channel so we know the real total         #
    # ------------------------------------------------------------------ #
    total = 0

    if include_calls:
        call_conditions = [
            CallLog.clinic_id == str(clinic_id),
            CallLog.deleted_at.is_(None),
        ]
        if search:
            call_conditions.append(
                CallLog.from_phone.ilike(f"%{search}%")
                | CallLog.to_phone.ilike(f"%{search}%")
                | CallLog.caller_name.ilike(f"%{search}%")
            )
        call_count: int = (
            await db.execute(
                select(func.count()).select_from(
                    select(CallLog.id).where(and_(*call_conditions)).subquery()
                )
            )
        ).scalar() or 0
        total += call_count

    if include_chats:
        chat_conditions = [Conversation.clinic_id == clinic_id]
        if search:
            chat_conditions.append(Conversation.user_identifier.ilike(f"%{search}%"))
        chat_count: int = (
            await db.execute(
                select(func.count()).select_from(
                    select(Conversation.id).where(and_(*chat_conditions)).subquery()
                )
            )
        ).scalar() or 0
        total += chat_count

    if include_messages:
        msg_conditions = [MessageLog.clinic_id == clinic_id]
        if channel in ("sms", "email"):
            msg_conditions.append(MessageLog.channel == channel)
        if search:
            msg_conditions.append(MessageLog.recipient.ilike(f"%{search}%"))
        msg_count: int = (
            await db.execute(
                select(func.count()).select_from(
                    select(MessageLog.id).where(and_(*msg_conditions)).subquery()
                )
            )
        ).scalar() or 0
        total += msg_count

    if total == 0:
        return CommunicationsResponse(
            items=[], total=0, page=page, limit=limit, total_pages=1
        )

    # ------------------------------------------------------------------ #
    # Step 2: fetch only the page-relevant slice from each source         #
    # When a single channel is selected, a simple offset/limit works.     #
    # For multi-channel, over-fetch proportionally then trim.             #
    # ------------------------------------------------------------------ #
    items: list[CommunicationItem] = []

    if channel is not None:
        # Single channel — offset/limit applies directly
        if channel == "call":
            result = await db.execute(
                select(CallLog)
                .where(and_(*call_conditions))  # type: ignore[possibly-undefined]
                .order_by(CallLog.started_at.desc())
                .offset(offset)
                .limit(limit)
            )
            for c in result.scalars().all():
                phone = c.from_phone if c.direction.value == "inbound" else c.to_phone
                items.append(
                    CommunicationItem(
                        id=str(c.id),
                        channel="call",
                        timestamp=c.started_at.isoformat(),
                        contact=phone or "Unknown",
                        summary=c.summary,
                        status=str(c.outcome.value) if c.outcome else "unknown",
                        direction=str(c.direction.value),
                    )
                )

        elif channel == "chat":
            result = await db.execute(
                select(Conversation)
                .where(and_(*chat_conditions))  # type: ignore[possibly-undefined]
                .order_by(Conversation.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
            for c in result.scalars().all():
                items.append(
                    CommunicationItem(
                        id=str(c.id),
                        channel="chat",
                        timestamp=c.created_at.isoformat(),
                        contact=c.user_identifier,
                        summary=c.summary,
                        status="active" if c.session_active else "ended",
                    )
                )

        else:  # sms or email
            result = await db.execute(
                select(MessageLog)
                .where(and_(*msg_conditions))  # type: ignore[possibly-undefined]
                .order_by(MessageLog.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
            for m in result.scalars().all():
                items.append(
                    CommunicationItem(
                        id=str(m.id),
                        channel=m.channel,
                        timestamp=m.created_at.isoformat(),
                        contact=m.recipient,
                        summary=m.subject or m.body[:100],
                        status=m.status,
                    )
                )

    else:
        # Multi-channel: fetch enough from each source to fill this page,
        # merge-sort, then slice. Over-fetch by (offset + limit) per source
        # so we have all candidates for the current page after sorting.
        fetch_limit = offset + limit

        call_items: list[CommunicationItem] = []
        chat_items: list[CommunicationItem] = []
        msg_items: list[CommunicationItem] = []

        result = await db.execute(
            select(CallLog)
            .where(and_(*call_conditions))
            .order_by(CallLog.started_at.desc())
            .limit(fetch_limit)
        )
        for c in result.scalars().all():
            phone = c.from_phone if c.direction.value == "inbound" else c.to_phone
            call_items.append(
                CommunicationItem(
                    id=str(c.id),
                    channel="call",
                    timestamp=c.started_at.isoformat(),
                    contact=phone or "Unknown",
                    summary=c.summary,
                    status=str(c.outcome.value) if c.outcome else "unknown",
                    direction=str(c.direction.value),
                )
            )

        result = await db.execute(
            select(Conversation)
            .where(and_(*chat_conditions))
            .order_by(Conversation.created_at.desc())
            .limit(fetch_limit)
        )
        for c in result.scalars().all():
            chat_items.append(
                CommunicationItem(
                    id=str(c.id),
                    channel="chat",
                    timestamp=c.created_at.isoformat(),
                    contact=c.user_identifier,
                    summary=c.summary,
                    status="active" if c.session_active else "ended",
                )
            )

        result = await db.execute(
            select(MessageLog)
            .where(and_(*msg_conditions))
            .order_by(MessageLog.created_at.desc())
            .limit(fetch_limit)
        )
        for m in result.scalars().all():
            msg_items.append(
                CommunicationItem(
                    id=str(m.id),
                    channel=m.channel,
                    timestamp=m.created_at.isoformat(),
                    contact=m.recipient,
                    summary=m.subject or m.body[:100],
                    status=m.status,
                )
            )

        all_items = call_items + chat_items + msg_items
        all_items.sort(key=lambda x: x.timestamp, reverse=True)
        items = all_items[offset : offset + limit]

    total_pages = (total + limit - 1) // limit if total > 0 else 1

    return CommunicationsResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
    )
