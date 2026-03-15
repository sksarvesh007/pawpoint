"""Tests for doctor-unavailability → offer-alternative-slots logic in check_available_appointments_pims."""

from datetime import UTC, date, datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from app.adapters.pims.types import PIMSProvider, PIMSTimeSlot
from livekit_agent.tools.appointment_tools import check_available_appointments_pims

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_slot(
    d: date, hour: int, minute: int = 0, provider_id: str = "prov-1"
) -> PIMSTimeSlot:
    start = datetime(d.year, d.month, d.day, hour, minute, tzinfo=UTC)
    end = datetime(
        d.year,
        d.month,
        d.day,
        hour,
        minute + 30 if minute < 30 else hour + 1,
        0,
        tzinfo=UTC,
    )
    return PIMSTimeSlot(start_time=start, end_time=end, provider_pims_id=provider_id)


def _next_weekday(start: date, days_ahead: int = 1) -> date:
    """Return `start` + `days_ahead` business days (Mon-Fri)."""
    current = start
    added = 0
    while added < days_ahead:
        current += timedelta(days=1)
        if current.weekday() < 5:
            added += 1
    return current


@pytest.fixture
def preferred_provider() -> PIMSProvider:
    return PIMSProvider(
        pims_id="prov-1",
        first_name="Alice",
        last_name="Smith",
        is_active=True,
        is_veterinarian=True,
    )


@pytest.fixture
def other_provider() -> PIMSProvider:
    return PIMSProvider(
        pims_id="prov-2",
        first_name="Bob",
        last_name="Jones",
        is_active=True,
        is_veterinarian=True,
    )


@pytest.fixture
def tomorrow() -> date:
    return datetime.now().date() + timedelta(days=1)


@pytest.fixture
def tomorrow_str(tomorrow: date) -> str:
    return tomorrow.strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Test: preferred provider unavailable → alternative day with same provider
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_preferred_provider_unavailable_returns_alternatives(
    preferred_provider: PIMSProvider,
    other_provider: PIMSProvider,
    tomorrow: date,
    tomorrow_str: str,
) -> None:
    """When preferred provider has no slots on requested date but has slots the
    next business day, the tool response should include that alternative day."""

    next_biz_day = _next_weekday(tomorrow, 1)

    async def fake_get_available_slots(
        provider_pims_id: str, target_date: date
    ) -> list[PIMSTimeSlot]:
        if provider_pims_id == "prov-1" and target_date == tomorrow:
            return []  # No slots for preferred provider on requested day
        if provider_pims_id == "prov-1" and target_date == next_biz_day:
            return [_make_slot(next_biz_day, 10, 0, "prov-1")]
        return []

    adapter = AsyncMock()
    adapter.get_available_slots = AsyncMock(side_effect=fake_get_available_slots)

    result = await check_available_appointments_pims(
        adapter=adapter,
        date_str=tomorrow_str,
        cached_providers=[preferred_provider, other_provider],
        preferred_provider=preferred_provider,
    )

    assert "isn't available" in result.lower() or "sorry" in result.lower()
    assert (
        "alice" in result.lower()
        or "smith" in result.lower()
        or "dr." in result.lower()
    )
    # Should mention the alternative day
    assert (
        next_biz_day.strftime("%A") in result or next_biz_day.strftime("%B") in result
    )
    # Should ask if the alternative works
    assert "work" in result.lower() or "would" in result.lower()


# ---------------------------------------------------------------------------
# Test: preferred provider unavailable → offer other provider same day
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_preferred_provider_unavailable_offers_other_provider(
    preferred_provider: PIMSProvider,
    other_provider: PIMSProvider,
    tomorrow: date,
    tomorrow_str: str,
) -> None:
    """When preferred provider has no slots but another provider has same-day
    slots, the tool response should mention the other provider."""

    async def fake_get_available_slots(
        provider_pims_id: str, target_date: date
    ) -> list[PIMSTimeSlot]:
        if provider_pims_id == "prov-1":
            return []  # Preferred provider has nothing
        if provider_pims_id == "prov-2" and target_date == tomorrow:
            return [_make_slot(tomorrow, 14, 0, "prov-2")]
        return []

    adapter = AsyncMock()
    adapter.get_available_slots = AsyncMock(side_effect=fake_get_available_slots)

    result = await check_available_appointments_pims(
        adapter=adapter,
        date_str=tomorrow_str,
        cached_providers=[preferred_provider, other_provider],
        preferred_provider=preferred_provider,
    )

    assert (
        "bob" in result.lower()
        or "jones" in result.lower()
        or "alternative" in result.lower()
    )
    assert "work" in result.lower() or "would" in result.lower()


# ---------------------------------------------------------------------------
# Test: all unavailable → helpful message about waitlist / call back
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_all_unavailable_returns_helpful_message(
    preferred_provider: PIMSProvider,
    other_provider: PIMSProvider,
    tomorrow_str: str,
) -> None:
    """When no slots exist for the preferred provider on the requested day or
    the next 2 business days, and no other providers have same-day slots, the
    tool should return a message suggesting the caller call back or be waitlisted."""

    adapter = AsyncMock()
    adapter.get_available_slots = AsyncMock(return_value=[])

    result = await check_available_appointments_pims(
        adapter=adapter,
        date_str=tomorrow_str,
        cached_providers=[preferred_provider, other_provider],
        preferred_provider=preferred_provider,
    )

    # Should suggest calling back or waitlist — not just "no availability"
    assert (
        "call back" in result.lower()
        or "waitlist" in result.lower()
        or "wait list" in result.lower()
        or "message" in result.lower()
    )
