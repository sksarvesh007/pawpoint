"""
Patient Search Tools

Tools for searching patient records via PIMS adapter or local database.
"""

import logging

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.pims.base import IPIMSAdapter
from app.adapters.pims.types import PIMSPatient

logger = logging.getLogger(__name__)


def _format_patient_for_voice(patient: PIMSPatient) -> str:
    """Format a single PIMS patient record for voice output."""
    parts = [f"{patient.name}"]
    if patient.species:
        parts[0] += f", a {patient.species}"
    if patient.breed:
        parts[0] += f" {patient.breed}"
    if patient.owner_first_name or patient.owner_last_name:
        owner = (
            f"{patient.owner_first_name or ''} {patient.owner_last_name or ''}".strip()
        )
        parts.append(f"owned by {owner}")
    return ", ".join(parts)


async def search_patient_pims(
    adapter: IPIMSAdapter,
    query: str,
) -> str:
    """Search for patients in PIMS by name, owner, or phone.

    Args:
        adapter: PIMS adapter instance
        query: Search query (pet name, owner name, or phone number)

    Returns:
        Voice-friendly result string

    Raises:
        PIMSError subclasses on adapter failures (caller handles fallback)
    """
    patients = await adapter.get_patients(limit=200)

    query_lower = query.lower().strip()
    matches: list[PIMSPatient] = []

    for p in patients:
        searchable = " ".join(
            filter(
                None,
                [
                    p.name,
                    p.owner_first_name,
                    p.owner_last_name,
                    p.owner_phone,
                ],
            )
        ).lower()
        if query_lower in searchable:
            matches.append(p)

    if not matches:
        return (
            f"I couldn't find any patients matching '{query}'. "
            "Could you try a different name, owner name, or phone number?"
        )

    if len(matches) == 1:
        p = matches[0]
        result = f"I found {_format_patient_for_voice(p)}."
        if p.allergies:
            result += f" Note: allergies listed as {p.allergies}."
        return result

    # Multiple matches
    names = [_format_patient_for_voice(m) for m in matches[:5]]
    listing = "; ".join(names)
    result = f"I found {len(matches)} patients matching that. Here are some: {listing}."
    if len(matches) > 5:
        result += " There are more results. Could you be more specific?"
    return result


async def search_patient_local(
    db: AsyncSession,
    clinic_id: str,
    query: str,
) -> str:
    """Search for patients in local database.

    Args:
        db: Database session
        clinic_id: Clinic ID
        query: Search query (pet name, owner name, or phone number)

    Returns:
        Voice-friendly result string
    """
    from app.models.patient import Patient

    search_term = f"%{query}%"
    result = await db.execute(
        select(Patient).where(
            Patient.clinic_id == clinic_id,
            Patient.deleted_at.is_(None),
            or_(
                Patient.name.ilike(search_term),
                Patient.owner_first_name.ilike(search_term),
                Patient.owner_last_name.ilike(search_term),
                Patient.owner_phone.ilike(search_term),
            ),
        )
    )
    patients = result.scalars().all()

    if not patients:
        return (
            f"I couldn't find any patients matching '{query}'. "
            "Could you try a different name, owner name, or phone number?"
        )

    if len(patients) == 1:
        p = patients[0]
        owner = p.owner_full_name
        info = f"I found {p.name}, a {p.species.value}"
        if p.breed:
            info += f" {p.breed}"
        info += f", owned by {owner}."
        if p.allergies:
            info += f" Note: allergies listed as {p.allergies}."
        return info

    # Multiple matches
    names = [
        f"{p.name} ({p.species.value}, owned by {p.owner_full_name})"
        for p in patients[:5]
    ]
    listing = "; ".join(names)
    info = f"I found {len(patients)} patients matching that. Here are some: {listing}."
    if len(patients) > 5:
        info += " There are more results. Could you be more specific?"
    return info
