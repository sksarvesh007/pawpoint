"""Analytics API endpoints."""

import asyncio

from fastapi import APIRouter, Depends, Query, Request
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.core.dependencies import get_current_clinic
from app.core.rate_limit import limiter
from app.db import get_db
from app.models.clinic import Clinic
from app.schemas.analytics import (
    CallAnalytics,
    DashboardAnalytics,
    EnhancedChatAnalytics,
)
from app.services.analytics import AnalyticsService

router = APIRouter()


@router.get("/dashboard", response_model=DashboardAnalytics)
@limiter.limit("60/minute")
async def get_dashboard_analytics(
    request: Request,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> DashboardAnalytics:
    """
    Get complete dashboard analytics.

    Returns aggregated metrics for calls, appointments, patients, PIMS sync,
    sentiment analysis, and recent call logs.
    """
    service = AnalyticsService(db)
    analytics: DashboardAnalytics = await service.get_dashboard_analytics(
        current_clinic.id, days=days
    )
    return analytics


@router.get("/calls", response_model=CallAnalytics)
@limiter.limit("60/minute")
async def get_call_analytics(
    request: Request,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> CallAnalytics:
    """
    Get call analytics for the past N days.

    Returns call volume, duration, AI performance, and outcome statistics.
    """
    service = AnalyticsService(db)
    analytics = await service.get_call_analytics(current_clinic.id, days=days)
    return analytics


@router.get("/chats", response_model=EnhancedChatAnalytics)
@limiter.limit("60/minute")
async def get_chat_analytics(
    request: Request,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> EnhancedChatAnalytics:
    """
    Get enhanced chat analytics with sentiment, resolution, and topic insights.
    """
    service = AnalyticsService(db)
    return await service.get_chat_analytics(current_clinic.id, days=days)


@router.get("/stream")
@limiter.limit("10/minute")
async def stream_dashboard_analytics(
    request: Request,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
):
    """
    Stream real-time dashboard analytics via Server-Sent Events.

    Updates every 10 seconds with fresh analytics data.
    Automatically handles client disconnection.
    """

    async def event_generator():
        """Generate analytics update events."""
        try:
            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    break

                # Get fresh analytics (uses parallel queries for speed)
                service = AnalyticsService(db)
                analytics = await service.get_dashboard_analytics(
                    current_clinic.id, days=days
                )

                # Send analytics update event
                yield {
                    "event": "analytics_update",
                    "data": analytics.model_dump_json(),
                }

                # Wait 10 seconds before next update
                await asyncio.sleep(10)

        except Exception as e:
            # Log error and send error event to client
            logger.error(f"Error in analytics stream: {e}")
            yield {
                "event": "error",
                "data": '{"error": "Stream error occurred"}',
            }

    # Get origin from request for CORS
    origin = request.headers.get("origin", "*")

    return EventSourceResponse(
        event_generator(),
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
        },
    )
