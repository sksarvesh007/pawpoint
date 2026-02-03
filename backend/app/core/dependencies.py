"""Authentication and authorization dependencies."""

from typing import Any
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db import get_db
from app.models.clinic import Clinic
from app.models.user import User


def extract_token_from_request(request: Request) -> str:
    """Extract JWT token from request cookies or Authorization header.

    Tries httpOnly cookie first, then falls back to Authorization header.

    Args:
        request: FastAPI request object

    Returns:
        JWT token string

    Raises:
        HTTPException: 401 if no token found
    """
    # Try to get token from httpOnly cookie first
    token = request.cookies.get("access_token")

    # Fallback to Authorization header if cookie not found
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token


def validate_token_payload(token: str) -> dict[str, Any]:
    """Decode and validate JWT token payload.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get the currently authenticated user from JWT token.

    Extracts token from httpOnly cookie or Authorization header,
    validates it, and returns the corresponding user.

    Args:
        request: FastAPI request object
        db: Database session

    Returns:
        Authenticated User object

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    token = extract_token_from_request(request)
    payload = validate_token_payload(token)

    # Extract user_id from token payload
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = UUID(user_id_str)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    # Query database for user (with clinics relationship loaded)
    from sqlalchemy.orm import selectinload

    result = await db.execute(
        select(User)
        .options(selectinload(User.clinics))
        .where(User.id == user_id, User.is_active == True)  # noqa: E712
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_clinic(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Clinic:
    """
    Get the current user's clinic from JWT token.

    Extracts clinic_id from the JWT token payload and verifies
    the user has access to that clinic.

    Args:
        request: FastAPI request object
        current_user: Authenticated user from get_current_user dependency
        db: Database session

    Returns:
        Clinic object

    Raises:
        HTTPException: 401 if token invalid, 403 if no access to clinic
    """
    token = extract_token_from_request(request)
    payload = validate_token_payload(token)

    clinic_id_str = payload.get("clinic_id")
    if not clinic_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No clinic ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        clinic_id = UUID(clinic_id_str)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid clinic ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    # Query database for clinic
    result = await db.execute(
        select(Clinic).where(Clinic.id == clinic_id, Clinic.is_active == True)  # noqa: E712
    )
    clinic = result.scalar_one_or_none()

    if not clinic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinic not found or inactive",
        )

    # Verify user has access to this clinic
    if not current_user.has_clinic_access(str(clinic_id)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this clinic is forbidden",
        )

    return clinic
