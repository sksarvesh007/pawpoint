"""Clinic endpoints for chatbot settings and configuration."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_clinic, get_current_user
from app.db import get_db
from app.models.clinic import Clinic
from app.models.user import User
from app.schemas.clinic import (
    AppointmentPreferences,
    CallFlowRules,
    ChatbotSettingsResponse,
    ClinicInfoResponse,
    EmergencyHandlingSettings,
    UpdateChatbotSettingsRequest,
)
from app.services.clinic import ClinicService

router = APIRouter()

# Rate limiter instance - uses the app's limiter state
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/me",
    response_model=ClinicInfoResponse,
    summary="Get current clinic info",
    description="Get basic info for the authenticated clinic.",
    responses={
        200: {"description": "Clinic info retrieved successfully"},
        401: {"description": "Not authenticated"},
    },
)
async def get_clinic_info(
    current_clinic: Clinic = Depends(get_current_clinic),
) -> ClinicInfoResponse:
    """Get basic clinic info for authenticated user."""
    return ClinicInfoResponse(
        id=str(current_clinic.id),
        name=current_clinic.name,
        email=current_clinic.email,
        slug=current_clinic.slug,
    )


@router.get(
    "/chatbot-settings",
    response_model=ChatbotSettingsResponse,
    summary="Get chatbot settings",
    description="Get current chatbot configuration for the authenticated clinic.",
    responses={
        200: {"description": "Chatbot settings retrieved successfully"},
        401: {
            "description": "Not authenticated",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated"}}
            },
        },
        404: {
            "description": "Clinic not found",
            "content": {
                "application/json": {"example": {"detail": "Clinic not found"}}
            },
        },
    },
)
async def get_chatbot_settings(
    current_user: User = Depends(get_current_user),
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> ChatbotSettingsResponse:
    """
    Get chatbot configuration for authenticated clinic.

    Returns current chatbot settings including persona, greeting message,
    emergency handling, and appointment preferences.
    """
    clinic_service = ClinicService(db)

    try:
        settings = await clinic_service.get_chatbot_settings(current_clinic.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from None

    # Build response from settings dict
    return ChatbotSettingsResponse(
        chatbot_name=settings.get("chatbot_name"),
        chatbot_persona=settings.get("chatbot_persona", "professional"),
        greeting_message=settings.get(
            "greeting_message",
            f"Thank you for calling {current_clinic.name}. How can I help you today?",
        ),
        additional_context=settings.get("additional_context"),
        voice_enabled=settings.get("voice_enabled", False),
        emergency_handling=EmergencyHandlingSettings(
            **settings.get("emergency_handling", {})
        ),
        appointment_preferences=AppointmentPreferences(
            **settings.get("appointment_preferences", {})
        ),
        call_flow_rules=CallFlowRules(**settings.get("call_flow_rules", {})),
        clinic_name=settings.get("clinic_name", current_clinic.name),
        # Contact information
        phone=settings.get("phone"),
        email=settings.get("email"),
        address=settings.get("address"),
        city=settings.get("city"),
        state=settings.get("state"),
        zip_code=settings.get("zip_code"),
        business_hours=settings.get("business_hours"),
    )


@router.put(
    "/chatbot-settings",
    response_model=ChatbotSettingsResponse,
    summary="Update chatbot settings",
    description="Update chatbot configuration for the authenticated clinic.",
    responses={
        200: {"description": "Chatbot settings updated successfully"},
        400: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {"detail": "Greeting message cannot contain HTML tags"}
                }
            },
        },
        401: {
            "description": "Not authenticated",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated"}}
            },
        },
        403: {
            "description": "Access forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "Access to this clinic is forbidden"}
                }
            },
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "greeting_message"],
                                "msg": "String should have at least 10 characters",
                                "type": "string_too_short",
                            }
                        ]
                    }
                }
            },
        },
        429: {
            "description": "Too many requests",
            "content": {
                "application/json": {
                    "example": {"detail": "Rate limit exceeded: 20 per 1 minute"}
                }
            },
        },
    },
)
@limiter.limit("20/minute")
async def update_chatbot_settings(
    request: Request,
    body: UpdateChatbotSettingsRequest,
    current_user: User = Depends(get_current_user),
    current_clinic: Clinic = Depends(get_current_clinic),
    db: AsyncSession = Depends(get_db),
) -> ChatbotSettingsResponse:
    """
    Update chatbot configuration for authenticated clinic.

    Updates chatbot settings including persona, greeting message,
    emergency handling, and appointment preferences.
    Rate limited to 20 requests per minute per IP.
    """
    clinic_service = ClinicService(db)

    try:
        updated_clinic = await clinic_service.update_chatbot_settings(
            clinic_id=current_clinic.id,
            settings=body,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from None

    # Get updated settings to return in response
    settings = await clinic_service.get_chatbot_settings(updated_clinic.id)

    return ChatbotSettingsResponse(
        chatbot_name=settings.get("chatbot_name"),
        chatbot_persona=settings.get("chatbot_persona", "professional"),
        greeting_message=settings.get(
            "greeting_message",
            f"Thank you for calling {updated_clinic.name}. How can I help you today?",
        ),
        additional_context=settings.get("additional_context"),
        voice_enabled=settings.get("voice_enabled", False),
        emergency_handling=EmergencyHandlingSettings(
            **settings.get("emergency_handling", {})
        ),
        appointment_preferences=AppointmentPreferences(
            **settings.get("appointment_preferences", {})
        ),
        call_flow_rules=CallFlowRules(**settings.get("call_flow_rules", {})),
        clinic_name=settings.get("clinic_name", updated_clinic.name),
        # Contact information
        phone=settings.get("phone"),
        email=settings.get("email"),
        address=settings.get("address"),
        city=settings.get("city"),
        state=settings.get("state"),
        zip_code=settings.get("zip_code"),
        business_hours=settings.get("business_hours"),
    )
