"""Conflict resolution for PIMS sync operations.

When the same record exists both locally and in PIMS with different data,
these strategies determine which version wins.
"""

from enum import StrEnum
from typing import Any


class ConflictStrategy(StrEnum):
    """Strategy for resolving sync conflicts."""

    PIMS_WINS = "pims_wins"  # PIMS data takes precedence (default)
    LOCAL_WINS = "local_wins"  # Local data takes precedence
    LATEST_WINS = "latest_wins"  # Most recently updated wins
    MANUAL = "manual"  # Flag for manual review


def resolve_patient_conflict(
    local_data: dict[str, Any],
    pims_data: dict[str, Any],
    strategy: ConflictStrategy = ConflictStrategy.PIMS_WINS,
) -> dict[str, Any]:
    """Resolve conflict between local and PIMS patient data.

    Args:
        local_data: Current local patient fields.
        pims_data: Incoming PIMS patient fields.
        strategy: Which version should win.

    Returns:
        Dict of fields to update on the local record.
    """
    if strategy == ConflictStrategy.PIMS_WINS:
        return {k: v for k, v in pims_data.items() if v is not None}

    if strategy == ConflictStrategy.LOCAL_WINS:
        return {}

    if strategy == ConflictStrategy.LATEST_WINS:
        local_updated = local_data.get("updated_at")
        pims_updated = pims_data.get("updated_at")
        if local_updated and pims_updated and pims_updated > local_updated:
            return {k: v for k, v in pims_data.items() if v is not None}
        return {}

    # MANUAL: return empty updates but caller should flag for review
    return {}


def resolve_appointment_conflict(
    local_data: dict[str, Any],
    pims_data: dict[str, Any],
    strategy: ConflictStrategy = ConflictStrategy.PIMS_WINS,
) -> dict[str, Any]:
    """Resolve conflict between local and PIMS appointment data.

    Same strategy logic as patient conflict resolution.
    """
    if strategy == ConflictStrategy.PIMS_WINS:
        return {k: v for k, v in pims_data.items() if v is not None}

    if strategy == ConflictStrategy.LOCAL_WINS:
        return {}

    if strategy == ConflictStrategy.LATEST_WINS:
        local_updated = local_data.get("updated_at")
        pims_updated = pims_data.get("updated_at")
        if local_updated and pims_updated and pims_updated > local_updated:
            return {k: v for k, v in pims_data.items() if v is not None}
        return {}

    return {}
