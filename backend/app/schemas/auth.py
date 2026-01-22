"""Authentication schemas for request/response validation."""

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Request schema for clinic registration."""

    clinic_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    """Request schema for user login."""

    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """Response schema for authentication tokens."""

    access_token: str
    token_type: str = "bearer"  # noqa: S105
    expires_in: int
    user: "UserResponse"
    clinic: "ClinicResponse"


class UserResponse(BaseModel):
    """Response schema for user data."""

    id: UUID
    email: str
    first_name: str
    last_name: str
    role: str

    model_config = {"from_attributes": True}


class ClinicResponse(BaseModel):
    """Response schema for clinic data."""

    id: UUID
    name: str
    slug: str

    model_config = {"from_attributes": True}


# Update forward references
TokenResponse.model_rebuild()
