"""Tests for the missed calls analytics endpoint."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.call_log import CallOutcome, CallStatus
from tests.helpers import create_call_log, setup_auth

MISSED_CALLS_URL = "/api/v1/analytics/missed-calls"

DEFAULT_PARAMS = {
    "start_date": "2020-01-01",
    "end_date": "2099-12-31",
}


# =============================================================================
# Authentication
# =============================================================================


@pytest.mark.asyncio
async def test_missed_calls_requires_auth(client: AsyncClient) -> None:
    """Unauthenticated request returns 401."""
    response = await client.get(MISSED_CALLS_URL, params=DEFAULT_PARAMS)
    assert response.status_code == 401


# =============================================================================
# Empty state
# =============================================================================


@pytest.mark.asyncio
async def test_missed_calls_empty(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """When there are no calls, all metrics should be zero."""
    await setup_auth(db_session, client)

    response = await client.get(MISSED_CALLS_URL, params=DEFAULT_PARAMS)
    assert response.status_code == 200

    data = response.json()
    assert data["total_missed"] == 0
    assert data["missed_rate"] == 0.0
    assert data["missed_by_day"] == []
    assert data["vs_previous_period"] is None


# =============================================================================
# Counting logic
# =============================================================================


@pytest.mark.asyncio
async def test_missed_calls_counted(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """2 dropped calls + 1 booked call → total_missed=2, missed_rate≈66.7%."""
    clinic = await setup_auth(db_session, client)

    # Create 2 missed calls (call_dropped outcome)
    await create_call_log(
        db_session,
        clinic.id,
        outcome=CallOutcome.CALL_DROPPED,
        status=CallStatus.COMPLETED,
    )
    await create_call_log(
        db_session,
        clinic.id,
        outcome=CallOutcome.VOICEMAIL_LEFT,
        status=CallStatus.COMPLETED,
    )

    # Create 1 successfully handled call
    await create_call_log(
        db_session,
        clinic.id,
        outcome=CallOutcome.APPOINTMENT_BOOKED,
        status=CallStatus.COMPLETED,
    )

    response = await client.get(MISSED_CALLS_URL, params=DEFAULT_PARAMS)
    assert response.status_code == 200

    data = response.json()
    assert data["total_missed"] == 2
    # 2 out of 3 calls missed → ~66.67%
    assert abs(data["missed_rate"] - 66.67) < 0.1
    assert isinstance(data["missed_by_day"], list)
    assert len(data["missed_by_day"]) >= 1
    # Each day entry has date and count
    for entry in data["missed_by_day"]:
        assert "date" in entry
        assert "count" in entry
