"""Schemas for outbound call API."""

import re
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class CallPurpose(StrEnum):
    """Purpose of the outbound call."""

    REMINDER = "reminder"
    FOLLOW_UP = "follow_up"
    CUSTOM = "custom"


# E.164 phone format: + followed by 10-15 digits
E164_PATTERN = re.compile(r"^\+[1-9]\d{9,14}$")


class OutboundCallRequest(BaseModel):
    """Request to initiate an outbound call."""

    to_phone: str = Field(
        ...,
        description="Destination phone number in E.164 format (e.g. +15551234567)",
    )
    purpose: CallPurpose = Field(
        ...,
        description="Purpose of the call",
    )
    message: str | None = Field(
        None,
        max_length=1000,
        description="Message to deliver (used for reminder/custom purposes)",
    )

    @field_validator("to_phone")
    @classmethod
    def validate_e164(cls, v: str) -> str:
        if not E164_PATTERN.match(v):
            raise ValueError("Phone number must be in E.164 format (e.g. +15551234567)")
        return v


class OutboundCallResponse(BaseModel):
    """Response after initiating an outbound call."""

    call_id: str
    twilio_call_sid: str
    status: str
    from_phone: str
    to_phone: str
    purpose: str


class OutboundCallStatus(BaseModel):
    """Status of an outbound call."""

    call_id: str
    twilio_call_sid: str | None
    status: str
    from_phone: str
    to_phone: str
    purpose: str | None
    duration_seconds: int | None
    started_at: datetime
    ended_at: datetime | None


class TwilioStatusCallback(BaseModel):
    """Twilio status callback form fields.

    Twilio sends these as application/x-www-form-urlencoded.
    """

    CallSid: str
    CallStatus: str
    CallDuration: str | None = None
    Direction: str | None = None
    From: str | None = None
    To: str | None = None
