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


class CallFlowRules(BaseModel):
    """Call flow and escalation rules for voice agent."""

    transfer_failure_action: Literal[
        "retry", "voicemail", "take_message", "callback_request"
    ] = Field(
        default="take_message",
        description="What to do when staff transfer fails",
    )
    max_hold_seconds: Literal[30, 60, 120] = Field(
        default=60,
        description="Max seconds to hold before falling back",
    )
    voicemail_enabled: bool = Field(
        default=True,
        description="Whether to offer voicemail option",
    )
    callback_requests_enabled: bool = Field(
        default=True,
        description="Whether to accept callback requests",
    )


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

    # Contact Information
    phone: str | None = Field(
        None,
        max_length=20,
        description="Clinic phone number",
    )
    email: str | None = Field(
        None,
        max_length=255,
        description="Clinic email address",
    )
    address: str | None = Field(
        None,
        max_length=255,
        description="Street address",
    )
    city: str | None = Field(
        None,
        max_length=100,
        description="City",
    )
    state: str | None = Field(
        None,
        max_length=100,
        description="State",
    )
    zip_code: str | None = Field(
        None,
        max_length=20,
        description="ZIP/Postal code",
    )
    business_hours: dict | None = Field(
        None,
        description="Business hours by day of week",
    )

    # Chatbot Settings
    chatbot_name: str | None = Field(
        None,
        min_length=2,
        max_length=50,
        description="The name of the AI chatbot assistant",
    )
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
    additional_context: str | None = Field(
        None,
        max_length=2000,
        description="Extra information about the clinic to include in AI context (services, specialties, policies, etc.)",
    )
    emergency_handling: EmergencyHandlingSettings | None = Field(
        None,
        description="Emergency detection and handling settings",
    )
    appointment_preferences: AppointmentPreferences | None = Field(
        None,
        description="Appointment booking preferences",
    )
    call_flow_rules: CallFlowRules | None = Field(
        None,
        description="Call flow and escalation rules",
    )

    @field_validator("chatbot_name")
    @classmethod
    def validate_chatbot_name(cls, v: str | None) -> str | None:
        """Validate chatbot name for security and formatting."""
        if v is None:
            return v

        # Strip excessive whitespace
        v = " ".join(v.split())

        # Check for HTML/script tags
        if re.search(r"<[^>]+>", v):
            raise ValueError("Chatbot name cannot contain HTML tags")

        # Only allow safe characters (letters, spaces, hyphens)
        if not re.match(r"^[A-Za-z\s\-]+$", v):
            raise ValueError(
                "Chatbot name can only contain letters, spaces, and hyphens"
            )

        return v if v else None

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

    @field_validator("additional_context")
    @classmethod
    def validate_additional_context(cls, v: str | None) -> str | None:
        """Validate additional context for security."""
        if v is None:
            return v

        # Strip excessive whitespace
        v = " ".join(v.split())

        # Check for HTML/script tags
        if re.search(r"<[^>]+>", v):
            raise ValueError("Additional context cannot contain HTML tags")

        return v if v else None


class ChatbotSettingsResponse(BaseModel):
    """Response schema for chatbot settings."""

    chatbot_name: str | None = None
    chatbot_persona: str
    greeting_message: str
    additional_context: str | None
    voice_enabled: bool
    emergency_handling: EmergencyHandlingSettings
    appointment_preferences: AppointmentPreferences
    call_flow_rules: CallFlowRules
    clinic_name: str
    # Contact information
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    business_hours: dict | None = None

    model_config = {"from_attributes": True}


class ClinicInfoResponse(BaseModel):
    """Response schema for basic clinic info."""

    id: str
    name: str
    email: str | None
    slug: str

    model_config = {"from_attributes": True}
