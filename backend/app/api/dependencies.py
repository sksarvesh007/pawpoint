"""FastAPI dependencies for multi-tenant clinic routing.

Provides reusable dependencies for extracting clinic context from URL slugs.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db as get_session
from app.models.clinic import Clinic


async def get_clinic_by_slug(
    clinic_slug: Annotated[
        str,
        Path(
            description="Unique clinic slug (e.g., 'happy-paws-vet')",
            pattern="^[a-z0-9-]+$",
            min_length=3,
            max_length=100,
        ),
    ],
    db: AsyncSession = Depends(get_session),
) -> Clinic:
    """Get clinic by slug from URL path.

    This dependency extracts the clinic slug from the URL path and loads
    the clinic configuration. Used for multi-tenant routing.

    Args:
        clinic_slug: Clinic slug from URL path (e.g., 'happy-paws-vet')
        db: Database session

    Returns:
        Clinic instance with full configuration

    Raises:
        HTTPException 404: If clinic not found or inactive

    Example:
        @router.get("/{clinic_slug}/chat")
        async def chat_endpoint(
            clinic: Clinic = Depends(get_clinic_by_slug)
        ):
            # clinic is automatically loaded from slug
            return {"clinic": clinic.name}
    """
    stmt = select(Clinic).where(
        Clinic.slug == clinic_slug,
        Clinic.is_active == True,  # noqa: E712
        Clinic.deleted_at.is_(None),  # Not soft-deleted
    )

    result = await db.execute(stmt)
    clinic = result.scalar_one_or_none()

    if not clinic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clinic '{clinic_slug}' not found or inactive",
        )

    return clinic


# Type alias for cleaner annotations
ClinicDep = Annotated[Clinic, Depends(get_clinic_by_slug)]
