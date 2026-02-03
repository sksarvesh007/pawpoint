"""FastAPI dependencies for multi-tenant clinic routing.

Provides reusable dependencies for extracting clinic context from URL slugs.
"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, Path, status
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import get_redis
from app.db import get_db as get_session
from app.models.clinic import Clinic


# Cache clinic slugs to reduce database queries
_clinic_slug_cache: dict[str, Clinic] = {}


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
    # Check cache first (optional optimization) - DISABLED due to detached instance issues
    # if clinic_slug in _clinic_slug_cache:
    #     cached_clinic = _clinic_slug_cache[clinic_slug]
    #     if cached_clinic.is_active:
    #         return cached_clinic

    # Query database
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

    # Cache for future requests (DISABLED - causes detached instance issues)
    # _clinic_slug_cache[clinic_slug] = clinic

    return clinic


def invalidate_clinic_cache(clinic_slug: str) -> None:
    """Invalidate cached clinic data.

    Call this when a clinic is updated.

    Args:
        clinic_slug: Clinic slug to invalidate
    """
    if clinic_slug in _clinic_slug_cache:
        del _clinic_slug_cache[clinic_slug]


def clear_clinic_cache() -> None:
    """Clear entire clinic cache."""
    _clinic_slug_cache.clear()


# Type alias for cleaner annotations
ClinicDep = Annotated[Clinic, Depends(get_clinic_by_slug)]
