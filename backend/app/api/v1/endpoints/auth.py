"""Authentication endpoints for clinic registration and login."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db import get_db
from app.schemas.auth import (
    ClinicResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new clinic",
    description="Register a new clinic with an admin user account.",
)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Register a new clinic.

    Creates a new clinic and an admin user associated with it.
    Returns an access token for immediate authentication.
    """
    auth_service = AuthService(db)

    try:
        user, clinic, access_token = await auth_service.register_clinic(
            clinic_name=request.clinic_name,
            email=request.email,
            password=request.password,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from None

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",  # noqa: S106
        expires_in=settings.jwt_access_token_expire_minutes * 60,
        user=UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role.value,
        ),
        clinic=ClinicResponse(
            id=clinic.id,
            name=clinic.name,
            slug=clinic.slug,
        ),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login to a clinic account",
    description="Authenticate with email and password to receive an access token.",
)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Login to an existing account.

    Validates credentials and returns an access token.
    """
    auth_service = AuthService(db)

    try:
        user, clinic, access_token = await auth_service.login(
            email=request.email,
            password=request.password,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",  # noqa: S106
        expires_in=settings.jwt_access_token_expire_minutes * 60,
        user=UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role.value,
        ),
        clinic=ClinicResponse(
            id=clinic.id,
            name=clinic.name,
            slug=clinic.slug,
        ),
    )
