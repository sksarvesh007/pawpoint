"""Authentication schemas for request/response validation."""

import re
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

# Common passwords to reject
COMMON_PASSWORDS = {
    "12345678",
    "password",
    "password1",
    "qwerty123",
    "abc123456",
    "letmein123",
    "welcome123",
    "admin123",
    "iloveyou1",
    "monkey123",
}


class RegisterRequest(BaseModel):
    """Request schema for clinic registration."""

    clinic_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Clinic name (letters, numbers, spaces, and basic punctuation)",
    )
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    admin_first_name: str | None = Field(
        None, min_length=1, max_length=100, description="Admin user's first name"
    )
    admin_last_name: str | None = Field(
        None, min_length=1, max_length=100, description="Admin user's last name"
    )

    @field_validator("clinic_name")
    @classmethod
    def validate_clinic_name(cls, v: str) -> str:
        """Validate clinic name for security and formatting."""
        # Strip excessive whitespace
        v = " ".join(v.split())

        # Check for HTML/script tags
        if re.search(r"<[^>]+>", v):
            raise ValueError("Clinic name cannot contain HTML tags")

        # Allow only safe characters: letters, numbers, spaces, and basic punctuation
        if not re.match(r"^[A-Za-z0-9\s&'().,\-]+$", v):
            raise ValueError(
                "Clinic name can only contain letters, numbers, spaces, "
                "and basic punctuation (&, ', (, ), ., , -)"
            )

        return v

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets security requirements."""
        errors = []

        if len(v) < 8:
            errors.append("at least 8 characters")

        if not re.search(r"[A-Z]", v):
            errors.append("one uppercase letter")

        if not re.search(r"[a-z]", v):
            errors.append("one lowercase letter")

        if not re.search(r"\d", v):
            errors.append("one digit")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>\-_=+\[\]\\;\'`~]', v):
            errors.append("one special character")

        if errors:
            raise ValueError(f"Password must contain {', '.join(errors)}")

        # Check against common passwords
        if v.lower() in COMMON_PASSWORDS:
            raise ValueError(
                "Password is too common. Please choose a stronger password"
            )

        return v


class ChangePasswordRequest(BaseModel):
    """Request schema for changing password."""

    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validate new password strength (same rules as registration)."""
        errors = []
        if len(v) < 8:
            errors.append("at least 8 characters")
        if not re.search(r"[A-Z]", v):
            errors.append("one uppercase letter")
        if not re.search(r"[a-z]", v):
            errors.append("one lowercase letter")
        if not re.search(r"\d", v):
            errors.append("one digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>\-_=+\[\]\\;\'`~]', v):
            errors.append("one special character")
        if errors:
            raise ValueError(f"Password must contain {', '.join(errors)}")
        if v.lower() in COMMON_PASSWORDS:
            raise ValueError(
                "Password is too common. Please choose a stronger password"
            )
        return v


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
