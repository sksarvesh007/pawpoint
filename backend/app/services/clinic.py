"""Clinic service for business logic."""

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.instrumentation import traced
from app.models.clinic import Clinic
from app.schemas.clinic import UpdateChatbotSettingsRequest

# Default chatbot settings initialized on clinic registration
DEFAULT_VOICE_SETTINGS: dict[str, Any] = {
    "chatbot_name": None,  # Will use clinic name by default if not set
    "chatbot_persona": "professional",
    "greeting_message": "Thank you for calling {clinic_name}. How can I help you today?",
    "emergency_handling": {
        "transfer_immediately": True,
        "keywords": ["emergency", "dying", "bleeding", "poison", "hit by car"],
        "emergency_message": "I'm transferring you to our emergency line right away.",
    },
    "appointment_preferences": {
        "allow_booking": True,
        "allow_cancellation": False,
        "allow_rescheduling": True,
        "booking_buffer_hours": 2,
    },
    "version": "1.0",
}


class ClinicService:
    """Service for clinic-related operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    @traced(span_name="clinic.get_chatbot_settings")
    async def get_chatbot_settings(self, clinic_id: UUID) -> dict:
        """
        Get chatbot settings for a clinic.

        Retrieves settings from voice_settings JSONB field,
        merging with defaults if keys are missing.

        Args:
            clinic_id: The clinic's UUID

        Returns:
            Dictionary containing chatbot settings

        Raises:
            ValueError: If clinic not found
        """
        result = await self.db.execute(
            select(Clinic).where(Clinic.id == clinic_id, Clinic.is_active == True)  # noqa: E712
        )
        clinic = result.scalar_one_or_none()

        if not clinic:
            raise ValueError("Clinic not found")

        # Get existing settings or use defaults
        settings = clinic.voice_settings if clinic.voice_settings else {}

        # Merge with defaults to ensure all keys exist
        merged_settings: dict[str, Any] = DEFAULT_VOICE_SETTINGS.copy()
        merged_settings.update(settings)

        # Add clinic name for response
        merged_settings["clinic_name"] = clinic.name
        merged_settings["voice_enabled"] = clinic.voice_enabled

        # Add contact information
        merged_settings["phone"] = clinic.phone
        merged_settings["email"] = clinic.email
        merged_settings["address"] = clinic.address_line1
        merged_settings["city"] = clinic.city
        merged_settings["state"] = clinic.state
        merged_settings["zip_code"] = clinic.postal_code
        merged_settings["business_hours"] = clinic.business_hours

        return merged_settings

    @traced(span_name="clinic.update_chatbot_settings")
    async def update_chatbot_settings(
        self,
        clinic_id: UUID,
        settings: UpdateChatbotSettingsRequest,
    ) -> Clinic:
        """
        Update chatbot settings for a clinic.

        Merges new settings into existing voice_settings JSONB field,
        preserving any unrelated keys.

        Args:
            clinic_id: The clinic's UUID
            settings: New chatbot settings to apply

        Returns:
            Updated Clinic object

        Raises:
            ValueError: If clinic not found
        """
        result = await self.db.execute(
            select(Clinic).where(Clinic.id == clinic_id, Clinic.is_active == True)  # noqa: E712
        )
        clinic = result.scalar_one_or_none()

        if not clinic:
            raise ValueError("Clinic not found")

        # Update contact information if provided
        if settings.phone is not None:
            clinic.phone = settings.phone
        if settings.email is not None:
            clinic.email = settings.email
        if settings.address is not None:
            clinic.address_line1 = settings.address
        if settings.city is not None:
            clinic.city = settings.city
        if settings.state is not None:
            clinic.state = settings.state
        if settings.zip_code is not None:
            clinic.postal_code = settings.zip_code
        if settings.business_hours is not None:
            clinic.business_hours = settings.business_hours

        # Get existing voice_settings or initialize empty dict
        existing_settings = clinic.voice_settings if clinic.voice_settings else {}

        # Build updated settings dict
        updated_settings = existing_settings.copy()
        updated_settings["chatbot_name"] = settings.chatbot_name
        updated_settings["chatbot_persona"] = settings.chatbot_persona
        updated_settings["greeting_message"] = settings.greeting_message
        updated_settings["additional_context"] = settings.additional_context

        # Update emergency handling if provided
        if settings.emergency_handling:
            updated_settings["emergency_handling"] = {
                "transfer_immediately": settings.emergency_handling.transfer_immediately,
                "keywords": settings.emergency_handling.keywords,
                "emergency_message": settings.emergency_handling.emergency_message,
            }
            # Also update the top-level emergency_keywords field
            clinic.emergency_keywords = settings.emergency_handling.keywords

        # Update appointment preferences if provided
        if settings.appointment_preferences:
            updated_settings["appointment_preferences"] = {
                "allow_booking": settings.appointment_preferences.allow_booking,
                "allow_cancellation": settings.appointment_preferences.allow_cancellation,
                "allow_rescheduling": settings.appointment_preferences.allow_rescheduling,
                "booking_buffer_hours": settings.appointment_preferences.booking_buffer_hours,
            }

        # Preserve version field
        updated_settings["version"] = existing_settings.get("version", "1.0")

        # Update clinic
        clinic.voice_settings = updated_settings

        # Commit changes
        await self.db.commit()
        await self.db.refresh(clinic)

        return clinic
