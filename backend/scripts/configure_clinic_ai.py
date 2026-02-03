"""Helper script to configure clinic-specific AI settings.

This shows how to set up voice_settings for a clinic, which will be used
to generate dynamic system prompts for AI agents.
"""

import asyncio
from uuid import UUID

from sqlalchemy import select

from app.db import get_db_session
from app.models.clinic import Clinic


async def configure_clinic_ai_settings(
    clinic_id: UUID | str,
    settings: dict,
) -> None:
    """Configure AI settings for a clinic.

    Args:
        clinic_id: Clinic UUID
        settings: Dictionary of AI settings

    Example settings:
        {
            "greeting": "warm and friendly",
            "personality": "professional yet approachable",
            "services": [
                "Wellness exams",
                "Vaccinations",
                "Surgery",
                "Dental care",
                "Emergency services"
            ],
            "special_instructions": "Always mention our new puppy wellness program",
            "appointment_settings": {
                "cancellation_policy": "24 hours notice required",
                "booking_lead_time": "We recommend booking 1-2 weeks in advance"
            }
        }
    """
    async with get_db_session() as db:
        # Fetch clinic
        stmt = select(Clinic).where(Clinic.id == clinic_id)
        result = await db.execute(stmt)
        clinic = result.scalar_one_or_none()

        if not clinic:
            print(f"❌ Clinic {clinic_id} not found")
            return

        # Update voice_settings
        clinic.voice_settings = settings

        await db.commit()
        print(f"✅ AI settings configured for {clinic.name}")
        print(f"   Settings: {settings}")


async def get_clinic_ai_settings(clinic_id: UUID | str) -> dict | None:
    """Get current AI settings for a clinic.

    Args:
        clinic_id: Clinic UUID

    Returns:
        Dictionary of AI settings or None
    """
    async with get_db_session() as db:
        stmt = select(Clinic).where(Clinic.id == clinic_id)
        result = await db.execute(stmt)
        clinic = result.scalar_one_or_none()

        if not clinic:
            print(f"❌ Clinic {clinic_id} not found")
            return None

        print(f"Clinic: {clinic.name}")
        print(f"Voice Settings: {clinic.voice_settings}")
        return clinic.voice_settings


# Example usage
async def main() -> None:
    """Example: Configure AI settings for first clinic."""
    from app.models.clinic import Clinic
    from sqlalchemy import select

    async with get_db_session() as db:
        # Get first clinic
        stmt = select(Clinic).limit(1)
        result = await db.execute(stmt)
        clinic = result.scalar_one_or_none()

        if not clinic:
            print("❌ No clinics found. Create a clinic first.")
            return

        print(f"Configuring AI for: {clinic.name} ({clinic.id})")

        # Example AI configuration
        ai_settings = {
            "greeting": "warm, friendly, and professional",
            "personality": "helpful and empathetic, like a trusted friend who cares about pets",
            "services": [
                "Wellness exams and preventive care",
                "Vaccinations and parasite prevention",
                "Surgery (spay/neuter, soft tissue, orthopedic)",
                "Dental cleanings and oral surgery",
                "Diagnostic imaging (X-ray, ultrasound)",
                "In-house laboratory testing",
                "Emergency and urgent care",
                "Microchipping",
                "Nutritional counseling",
                "Behavioral consultations",
            ],
            "special_instructions": (
                "Emphasize our Fear Free certified approach. "
                "Mention we offer payment plans through CareCredit. "
                "New clients get 10% off their first wellness exam."
            ),
            "appointment_settings": {
                "cancellation_policy": "We require 24 hours notice for cancellations to avoid a $50 fee",
                "booking_lead_time": "Book 1-2 weeks ahead for routine care. Same-day appointments available for urgent needs.",
            },
        }

        await configure_clinic_ai_settings(clinic.id, ai_settings)

        # Verify
        print("\n📋 Current settings:")
        await get_clinic_ai_settings(clinic.id)


if __name__ == "__main__":
    print("🏥 Clinic AI Configuration Tool\n")
    asyncio.run(main())
