"""Authentication endpoints for clinic registration and login."""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from loguru import logger
from slowapi import Limiter
from slowapi.util import get_remote_address
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


def _set_auth_cookie(response: Response, access_token: str) -> None:
    """Set the access token cookie with environment-appropriate settings.

    In production (HTTPS): secure=True, samesite="none" for cross-site cookies.
    In development (HTTP): secure=False, samesite="lax" so the browser accepts the cookie.
    """
    is_prod = settings.is_production
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=is_prod,
        samesite="none" if is_prod else "lax",
        max_age=settings.jwt_access_token_expire_minutes * 60,
        path="/",
    )

# Rate limiter instance - uses the app's limiter state
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new clinic",
    description="Register a new clinic with an admin user account.",
    responses={
        201: {"description": "Registration successful"},
        400: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {"detail": "Password must contain at least 8 characters"}
                }
            },
        },
        429: {
            "description": "Too many requests",
            "content": {
                "application/json": {
                    "example": {"detail": "Rate limit exceeded: 3 per 1 hour"}
                }
            },
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {"example": {"detail": "Internal server error"}}
            },
        },
    },
)
@limiter.limit("3/hour")
async def register(
    request: Request,
    response: Response,
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Register a new clinic.

    Creates a new clinic and an admin user associated with it.
    Returns an access token for immediate authentication.
    """
    logger.info(
        f"[POST /api/v1/auth/register] Registration attempt for email: {body.email}, clinic: {body.clinic_name}"
    )
    auth_service = AuthService(db)

    try:
        user, clinic, access_token = await auth_service.register_clinic(
            clinic_name=body.clinic_name,
            email=body.email,
            password=body.password,
            admin_first_name=body.admin_first_name,
            admin_last_name=body.admin_last_name,
        )
        logger.info(
            f"[POST /api/v1/auth/register] Registration successful - Email: {body.email}, Clinic: {clinic.name}, Slug: {clinic.slug}"
        )
    except ValueError as e:
        logger.warning(
            f"[POST /api/v1/auth/register] Registration failed - Email: {body.email}, Reason: {e!s}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from None

    _set_auth_cookie(response, access_token)

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
    responses={
        200: {"description": "Login successful"},
        400: {
            "description": "Validation error",
            "content": {
                "application/json": {"example": {"detail": "Invalid email format"}}
            },
        },
        401: {
            "description": "Authentication failed",
            "content": {
                "application/json": {"example": {"detail": "Invalid email or password"}}
            },
        },
        429: {
            "description": "Too many requests",
            "content": {
                "application/json": {
                    "example": {"detail": "Rate limit exceeded: 5 per 1 minute"}
                }
            },
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {"example": {"detail": "Internal server error"}}
            },
        },
    },
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Login to an existing account.

    Validates credentials and returns an access token.
    """
    logger.info(f"[POST /api/v1/auth/login] Login attempt - Email: {body.email}")
    auth_service = AuthService(db)

    try:
        user, clinic, access_token = await auth_service.login(
            email=body.email,
            password=body.password,
        )
        logger.info(
            f"[POST /api/v1/auth/login] Login successful - Email: {body.email}, User: {user.first_name} {user.last_name}, Clinic: {clinic.name}"
        )
    except ValueError as e:
        logger.warning(
            f"[POST /api/v1/auth/login] Login failed - Email: {body.email}, Reason: {e!s}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    _set_auth_cookie(response, access_token)

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
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout from account",
    description="Clear authentication cookies to logout.",
)
async def logout(response: Response) -> None:
    """
    Logout from the current session.

    Clears the access token cookie.
    """
    logger.info(
        "[POST /api/v1/auth/logout] User logout - clearing authentication cookie"
    )
    is_prod = settings.is_production
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=is_prod,
        samesite="none" if is_prod else "lax",
        path="/",
    )
