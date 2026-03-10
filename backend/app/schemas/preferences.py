"""User preferences schemas for dashboard widget layout."""

from pydantic import BaseModel, Field


class WidgetConfig(BaseModel):
    """Configuration for a single dashboard widget."""

    id: str
    visible: bool = True


class DashboardLayoutRequest(BaseModel):
    """Request schema for saving dashboard widget layout."""

    widgets: list[WidgetConfig] = Field(
        ..., description="Ordered list of widgets with visibility flags"
    )


class DashboardLayoutResponse(BaseModel):
    """Response schema for dashboard widget layout."""

    widgets: list[WidgetConfig]
