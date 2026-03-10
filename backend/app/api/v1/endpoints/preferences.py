"""User preferences endpoints for dashboard widget layout."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db import get_db
from app.models.user import User
from app.schemas.preferences import (
    DashboardLayoutRequest,
    DashboardLayoutResponse,
    WidgetConfig,
)

router = APIRouter()

# Default widget order when user has no saved preferences
DEFAULT_WIDGETS = [
    WidgetConfig(id="stats_cards", visible=True),
    WidgetConfig(id="calls_chart", visible=True),
    WidgetConfig(id="quick_stats", visible=True),
    WidgetConfig(id="appointment_status", visible=True),
    WidgetConfig(id="call_sentiment", visible=True),
    WidgetConfig(id="chat_sentiment", visible=True),
    WidgetConfig(id="pims_status", visible=True),
    WidgetConfig(id="pims_sync_trend", visible=True),
    WidgetConfig(id="recent_calls", visible=True),
]


@router.get(
    "/dashboard-layout",
    response_model=DashboardLayoutResponse,
    summary="Get dashboard widget layout",
)
async def get_dashboard_layout(
    current_user: User = Depends(get_current_user),
) -> DashboardLayoutResponse:
    """Return the user's saved dashboard widget layout or defaults."""
    if current_user.dashboard_layout and "widgets" in current_user.dashboard_layout:
        widgets = [WidgetConfig(**w) for w in current_user.dashboard_layout["widgets"]]
        return DashboardLayoutResponse(widgets=widgets)

    return DashboardLayoutResponse(widgets=DEFAULT_WIDGETS)


@router.put(
    "/dashboard-layout",
    response_model=DashboardLayoutResponse,
    summary="Save dashboard widget layout",
)
async def save_dashboard_layout(
    body: DashboardLayoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DashboardLayoutResponse:
    """Save the user's dashboard widget layout preferences."""
    current_user.dashboard_layout = {"widgets": [w.model_dump() for w in body.widgets]}
    await db.commit()

    return DashboardLayoutResponse(widgets=body.widgets)
