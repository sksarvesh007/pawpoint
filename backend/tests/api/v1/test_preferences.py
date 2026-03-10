"""Tests for user preferences API endpoints (dashboard widget layout)."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import setup_auth

# Default widget IDs returned for a new user (9 widgets, all visible)
DEFAULT_WIDGET_IDS = [
    "stats_cards",
    "calls_chart",
    "quick_stats",
    "appointment_status",
    "call_sentiment",
    "chat_sentiment",
    "pims_status",
    "pims_sync_trend",
    "recent_calls",
]


# =============================================================================
# GET /api/v1/preferences/dashboard-layout
# =============================================================================


@pytest.mark.asyncio
async def test_get_layout_requires_auth(client: AsyncClient) -> None:
    """Unauthenticated request to GET dashboard-layout returns 401."""
    response = await client.get("/api/v1/preferences/dashboard-layout")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_layout_returns_defaults(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """A new user with no saved preferences gets the 7 default widgets, all visible."""
    await setup_auth(db_session, client)

    response = await client.get("/api/v1/preferences/dashboard-layout")
    assert response.status_code == 200

    data = response.json()
    widgets = data["widgets"]

    # Exactly 9 default widgets
    assert len(widgets) == 9, f"Expected 9 default widgets, got {len(widgets)}"

    # All visible
    for widget in widgets:
        assert widget["visible"] is True, (
            f"Default widget '{widget['id']}' should be visible"
        )

    # Correct IDs in correct order
    widget_ids = [w["id"] for w in widgets]
    assert widget_ids == DEFAULT_WIDGET_IDS


# =============================================================================
# PUT /api/v1/preferences/dashboard-layout
# =============================================================================


@pytest.mark.asyncio
async def test_save_layout(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """PUT a custom layout, then GET it back and verify it persists."""
    await setup_auth(db_session, client)

    custom_widgets = [
        {"id": "stats_cards", "visible": True},
        {"id": "recent_calls", "visible": True},
        {"id": "calls_chart", "visible": True},
    ]

    # Save
    put_response = await client.put(
        "/api/v1/preferences/dashboard-layout",
        json={"widgets": custom_widgets},
    )
    assert put_response.status_code == 200

    put_data = put_response.json()
    assert len(put_data["widgets"]) == 3

    # Read back
    get_response = await client.get("/api/v1/preferences/dashboard-layout")
    assert get_response.status_code == 200

    get_data = get_response.json()
    returned_ids = [w["id"] for w in get_data["widgets"]]
    assert returned_ids == ["stats_cards", "recent_calls", "calls_chart"]

    for widget in get_data["widgets"]:
        assert widget["visible"] is True


@pytest.mark.asyncio
async def test_save_layout_partial_visibility(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Save a layout with some widgets hidden and verify visibility flags persist."""
    await setup_auth(db_session, client)

    widgets_with_hidden = [
        {"id": "stats_cards", "visible": True},
        {"id": "calls_chart", "visible": False},
        {"id": "quick_stats", "visible": True},
        {"id": "call_sentiment", "visible": False},
        {"id": "chat_sentiment", "visible": True},
        {"id": "pims_status", "visible": False},
        {"id": "recent_calls", "visible": True},
    ]

    # Save
    put_response = await client.put(
        "/api/v1/preferences/dashboard-layout",
        json={"widgets": widgets_with_hidden},
    )
    assert put_response.status_code == 200

    # Read back
    get_response = await client.get("/api/v1/preferences/dashboard-layout")
    assert get_response.status_code == 200

    get_data = get_response.json()
    widgets = get_data["widgets"]
    assert len(widgets) == 7

    # Build a lookup for easy assertion
    visibility = {w["id"]: w["visible"] for w in widgets}
    assert visibility["stats_cards"] is True
    assert visibility["calls_chart"] is False
    assert visibility["quick_stats"] is True
    assert visibility["call_sentiment"] is False
    assert visibility["chat_sentiment"] is True
    assert visibility["pims_status"] is False
    assert visibility["recent_calls"] is True


@pytest.mark.asyncio
async def test_save_layout_reorder(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Save widgets in a non-default order and verify the order persists."""
    await setup_auth(db_session, client)

    reordered_widgets = [
        {"id": "recent_calls", "visible": True},
        {"id": "pims_status", "visible": True},
        {"id": "chat_sentiment", "visible": True},
        {"id": "call_sentiment", "visible": True},
        {"id": "quick_stats", "visible": True},
        {"id": "calls_chart", "visible": True},
        {"id": "stats_cards", "visible": True},
    ]

    # Save reordered layout
    put_response = await client.put(
        "/api/v1/preferences/dashboard-layout",
        json={"widgets": reordered_widgets},
    )
    assert put_response.status_code == 200

    # Verify PUT response itself has the right order
    put_ids = [w["id"] for w in put_response.json()["widgets"]]
    expected_order = [
        "recent_calls",
        "pims_status",
        "chat_sentiment",
        "call_sentiment",
        "quick_stats",
        "calls_chart",
        "stats_cards",
    ]
    assert put_ids == expected_order

    # Read back and verify persisted order
    get_response = await client.get("/api/v1/preferences/dashboard-layout")
    assert get_response.status_code == 200

    get_ids = [w["id"] for w in get_response.json()["widgets"]]
    assert get_ids == expected_order
