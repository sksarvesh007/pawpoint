"""Call logs API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_clinic
from app.db import get_db
from app.models.call_log import CallLog
from app.models.clinic import Clinic
from app.schemas.analytics import CallLogDetail, CallLogSummary

router = APIRouter()


def _extract_key_points(
    raw: list | dict | None,
) -> tuple[str | None, list[str]]:
    """Extract sentiment and normalized key_points from JSONB data.

    Returns (sentiment, key_points_list).
    """
    sentiment: str | None = None
    key_points: list[str] = []

    if isinstance(raw, list):
        key_points = [str(kp) for kp in raw]
    elif isinstance(raw, dict):
        sentiment = raw.get("sentiment")
        nested = raw.get("key_points") or raw.get("points")
        if isinstance(nested, list):
            key_points = [str(kp) for kp in nested]

    return sentiment, key_points


class CallLogsResponse(BaseModel):
    """Paginated call logs response."""

    items: list[CallLogSummary]
    total: int
    page: int
    limit: int
    total_pages: int


@router.get("/", response_model=CallLogsResponse)
async def list_call_logs(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> CallLogsResponse:
    """
    List recent call logs with pagination.

    Returns call logs with transcript summaries, sentiment, outcome,
    and AI confidence scores.
    """
    # Count total calls
    count_result = await db.execute(
        select(func.count())
        .select_from(CallLog)
        .where(
            and_(
                CallLog.clinic_id == str(current_clinic.id),
                CallLog.deleted_at.is_(None),
            )
        )
    )
    total = count_result.scalar_one()

    # Get paginated calls
    offset = (page - 1) * limit
    result = await db.execute(
        select(CallLog)
        .where(
            and_(
                CallLog.clinic_id == str(current_clinic.id),
                CallLog.deleted_at.is_(None),
            )
        )
        .order_by(CallLog.started_at.desc())
        .offset(offset)
        .limit(limit)
    )
    calls = result.scalars().all()

    # Convert to summaries
    items = []
    for call in calls:
        sentiment, _ = _extract_key_points(call.key_points)

        caller_phone = (
            call.from_phone if call.direction.value == "inbound" else call.to_phone
        )

        items.append(
            CallLogSummary(
                id=str(call.id),
                started_at=call.started_at,
                caller_phone_number=caller_phone,
                duration_seconds=call.duration_seconds,
                outcome=str(call.outcome.value) if call.outcome else "unknown",
                sentiment=sentiment,
                ai_confidence_score=call.ai_confidence_score,
                direction=str(call.direction.value),
            )
        )

    total_pages = (total + limit - 1) // limit  # Ceiling division

    return CallLogsResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
    )


@router.get("/{call_id}", response_model=CallLogDetail)
async def get_call_log(
    call_id: UUID,
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> CallLogDetail:
    """
    Get a single call log by ID.

    Returns full call details including transcript, recording, and actions.
    """
    result = await db.execute(
        select(CallLog).where(
            and_(
                CallLog.id == str(call_id),
                CallLog.clinic_id == str(current_clinic.id),
                CallLog.deleted_at.is_(None),
            )
        )
    )
    call = result.scalar_one_or_none()

    if not call:
        raise HTTPException(status_code=404, detail="Call log not found")

    caller_phone = (
        call.from_phone if call.direction.value == "inbound" else call.to_phone
    )

    sentiment, key_points = _extract_key_points(call.key_points)

    actions_taken: list[str] = []
    if isinstance(call.actions_taken, list):
        actions_taken = [str(a) for a in call.actions_taken]

    return CallLogDetail(
        id=str(call.id),
        started_at=call.started_at,
        ended_at=call.ended_at,
        caller_phone_number=caller_phone,
        duration_seconds=call.duration_seconds,
        direction=str(call.direction.value),
        outcome=str(call.outcome.value) if call.outcome else "unknown",
        sentiment=sentiment,
        ai_confidence_score=call.ai_confidence_score,
        transcript=call.transcript,
        recording_url=call.recording_url,
        summary=call.summary,
        key_points=key_points,
        actions_taken=actions_taken,
    )
