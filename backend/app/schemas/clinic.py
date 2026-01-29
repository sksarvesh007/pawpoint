"""Clinic schemas for request/response validation."""

import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class EmergencyHandlingSettings(BaseModel):
    """Emergency handling configuration for chatbot."""

    transfer_immediately: bool = Field(
        default=True,
        description="Whether to transfer emergency calls immediately",
    )
    keywords: list[str] = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Keywords that trigger emergency transfer",
    )
    emergency_message: str | None = Field(
        None,
        max_length=200,
        description="Custom message when transferring emergency calls",
    )

    @field_validator("keywords")
    @classmethod
    def validate_keywords(cls, v: list[str]) -> list[str]:
        """Validate emergency keywords."""
        if not v:
            raise ValueError("At least one emergency keyword is required")

        validated = []
        for keyword in v:
            # Strip whitespace
            keyword = keyword.strip()

            # Check length
            if len(keyword) < 2 or len(keyword) > 50:
                raise ValueError("Keywords must be between 2 and 50 characters")

            # Check for HTML tags
            if re.search(r"<[^>]+>", keyword):
                raise ValueError("Keywords cannot contain HTML tags")

            # Only allow safe characters
            if not re.match(r"^[A-Za-z0-9\s\-]+$", keyword):
                raise ValueError(
                    "Keywords can only contain letters, numbers, spaces, and hyphens"
                )

            validated.append(keyword)

        return validated

    @field_validator("emergency_message")
    @classmethod
    def validate_emergency_message(cls, v: str | None) -> str | None:
        """Validate emergency message."""
        if v is None:
            return v

        # Strip whitespace
        v = " ".join(v.split())

        # Check for HTML tags
        if re.search(r"<[^>]+>", v):
            raise ValueError("Emergency message cannot contain HTML tags")

        return v


class AppointmentPreferences(BaseModel):
    """Appointment handling preferences for chatbot."""

    allow_booking: bool = Field(
        default=True,
        description="Whether chatbot can book new appointments",
    )
    allow_cancellation: bool = Field(
        default=False,
        description="Whether chatbot can cancel appointments",
    )
    allow_rescheduling: bool = Field(
        default=True,
        description="Whether chatbot can reschedule appointments",
    )
    booking_buffer_hours: int = Field(
        default=2,
        ge=0,
        le=72,
        description="Minimum hours in advance required for booking",
    )


class UpdateChatbotSettingsRequest(BaseModel):
    """Request schema for updating chatbot settings."""

    chatbot_persona: Literal["professional", "friendly", "empathetic", "warm"] = Field(
        ...,
        description="The personality/tone of the chatbot",
    )
    greeting_message: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Custom greeting message when chatbot answers calls",
    )
    emergency_handling: EmergencyHandlingSettings | None = Field(
        None,
        description="Emergency detection and handling settings",
    )
    appointment_preferences: AppointmentPreferences | None = Field(
        None,
        description="Appointment booking preferences",
    )

    @field_validator("greeting_message")
    @classmethod
    def validate_greeting_message(cls, v: str) -> str:
        """Validate greeting message for security and formatting."""
        # Strip excessive whitespace
        v = " ".join(v.split())

        # Check for HTML/script tags
        if re.search(r"<[^>]+>", v):
            raise ValueError("Greeting message cannot contain HTML tags")

        return v


class ChatbotSettingsResponse(BaseModel):
    """Response schema for chatbot settings."""

    chatbot_persona: str
    greeting_message: str
    voice_enabled: bool
    emergency_handling: EmergencyHandlingSettings
    appointment_preferences: AppointmentPreferences
    clinic_name: str

    model_config = {"from_attributes": True}


class ClinicInfoResponse(BaseModel):
    """Response schema for basic clinic info."""

    id: str
    name: str
    email: str | None

    model_config = {"from_attributes": True}
