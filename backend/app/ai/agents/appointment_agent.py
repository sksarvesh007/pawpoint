"""Appointment booking agent for scheduling via AI chat/voice.

Handles patient search, slot availability, and appointment creation
through conversational interaction.
"""

from typing import Any

from loguru import logger
from pydantic_ai import RunContext

from app.ai.agents.base import AgentDependencies, BaseAgent, get_clinic_info
from app.ai.models import ModelFactory

APPOINTMENT_SYSTEM_PROMPT = """\
You are a friendly and efficient veterinary clinic appointment assistant.
Your role is to help pet owners book, check, and manage appointments.

## Capabilities
- Search for existing patients by name, owner name, or phone number
- Check available appointment slots for specific dates and providers
- Book new appointments
- Check appointment status

## Conversation Flow
1. Greet the caller and ask how you can help
2. If booking: identify the patient (search by name/owner), choose a provider and date, show available slots, confirm and book
3. If checking status: look up the appointment and provide details
4. Always confirm details before finalizing a booking

## Guidelines
- Be conversational but efficient
- Always verify patient identity before making changes
- If a patient is not found, offer to describe what information is needed
- Present available time slots clearly
- Confirm all appointment details before booking
- If PIMS is connected, mention that the appointment will sync automatically
"""


class AppointmentAgent(BaseAgent):
    """Agent for appointment booking and management."""

    def __init__(self, clinic_data: dict[str, Any] | None = None) -> None:
        model = ModelFactory.get_model_for_task("appointment_booking", channel="chat")

        prompt = APPOINTMENT_SYSTEM_PROMPT
        if clinic_data and clinic_data.get("name"):
            prompt += f"\n\nYou work for {clinic_data['name']}."
        if clinic_data and clinic_data.get("business_hours"):
            prompt += f"\nClinic hours: {clinic_data['business_hours']}"

        super().__init__(
            name="appointment_agent",
            system_prompt=prompt,
            model=model,
        )

        # Register tools
        self.agent.tool(get_clinic_info)
        self.agent.tool(search_patients)
        self.agent.tool(get_available_slots)
        self.agent.tool(book_appointment)
        self.agent.tool(check_appointment_status)


async def search_patients(
    ctx: RunContext[AgentDependencies],
    query: str,
) -> list[dict[str, Any]]:
    """Search for patients by name, owner name, or phone number.

    Args:
        ctx: Agent run context with dependencies
        query: Search query (patient name, owner name, or phone)

    Returns:
        List of matching patients with basic info
    """
    from app.services.patient import PatientService

    service = PatientService(ctx.deps.db_session)
    patients = await service.search_patients(ctx.deps.clinic_id, query, limit=5)

    return [
        {
            "id": str(p.id),
            "name": p.name,
            "species": p.species.value
            if hasattr(p.species, "value")
            else str(p.species),
            "breed": p.breed,
            "owner_name": f"{p.owner_first_name} {p.owner_last_name}",
            "owner_phone": p.owner_phone,
        }
        for p in patients
    ]


async def get_available_slots(
    ctx: RunContext[AgentDependencies],
    provider_id: str,
    date: str,
) -> list[dict[str, str]]:
    """Get available appointment slots for a provider on a given date.

    Args:
        ctx: Agent run context with dependencies
        provider_id: UUID of the provider
        date: Date string in YYYY-MM-DD format

    Returns:
        List of available time slots
    """
    from uuid import UUID as PyUUID

    from app.services.appointment import AppointmentService

    service = AppointmentService(ctx.deps.db_session)
    slots = await service.get_available_slots(
        ctx.deps.clinic_id,
        PyUUID(provider_id),
        date,
    )

    return [
        {
            "start_time": slot["start_time"],
            "end_time": slot["end_time"],
        }
        for slot in slots
    ]


async def book_appointment(
    ctx: RunContext[AgentDependencies],
    patient_id: str,
    provider_id: str,
    start_time: str,
    end_time: str,
    appointment_type: str = "checkup",
    reason: str | None = None,
) -> dict[str, Any]:
    """Book an appointment for a patient.

    Args:
        ctx: Agent run context with dependencies
        patient_id: UUID of the patient
        provider_id: UUID of the provider
        start_time: ISO 8601 datetime for start
        end_time: ISO 8601 datetime for end
        appointment_type: Type of appointment (checkup, vaccination, surgery, dental, grooming, emergency, other)
        reason: Optional reason for the appointment

    Returns:
        Appointment details or error message
    """
    from uuid import UUID as PyUUID

    from app.schemas.appointment import AppointmentCreate
    from app.services.appointment import AppointmentService

    service = AppointmentService(ctx.deps.db_session)

    try:
        data = AppointmentCreate(
            patient_id=PyUUID(patient_id),
            provider_id=PyUUID(provider_id),
            start_time=start_time,
            end_time=end_time,
            appointment_type=appointment_type,
            reason=reason,
        )
        appointment = await service.create_appointment(
            ctx.deps.clinic_id, data, source="voice_ai"
        )

        # Enqueue PIMS push if connected
        try:
            from app.workers.tasks import push_appointment_to_pims

            push_appointment_to_pims.delay(str(appointment.id))
        except Exception:
            logger.warning(
                f"Failed to enqueue PIMS push for appointment {appointment.id}"
            )

        return {
            "success": True,
            "appointment_id": str(appointment.id),
            "start_time": str(appointment.start_time),
            "end_time": str(appointment.end_time),
            "status": appointment.status.value
            if hasattr(appointment.status, "value")
            else str(appointment.status),
            "message": "Appointment booked successfully!",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


async def check_appointment_status(
    ctx: RunContext[AgentDependencies],
    appointment_id: str,
) -> dict[str, Any]:
    """Check the status of an appointment.

    Args:
        ctx: Agent run context with dependencies
        appointment_id: UUID of the appointment

    Returns:
        Appointment status details
    """
    from uuid import UUID as PyUUID

    from app.services.appointment import AppointmentService

    service = AppointmentService(ctx.deps.db_session)
    appointment = await service.get_appointment(
        ctx.deps.clinic_id, PyUUID(appointment_id)
    )

    if not appointment:
        return {"error": "Appointment not found"}

    return {
        "id": str(appointment.id),
        "start_time": str(appointment.start_time),
        "end_time": str(appointment.end_time),
        "status": appointment.status.value
        if hasattr(appointment.status, "value")
        else str(appointment.status),
        "appointment_type": appointment.appointment_type.value
        if hasattr(appointment.appointment_type, "value")
        else str(appointment.appointment_type),
        "patient_name": appointment.patient.name if appointment.patient else None,
        "provider_name": f"{appointment.provider.first_name} {appointment.provider.last_name}"
        if appointment.provider
        else None,
    }


def create_appointment_agent(
    clinic_data: dict[str, Any] | None = None,
) -> AppointmentAgent:
    """Create and return a new AppointmentAgent instance.

    Args:
        clinic_data: Optional clinic information for personalized prompts

    Returns:
        Initialized AppointmentAgent
    """
    return AppointmentAgent(clinic_data=clinic_data)
