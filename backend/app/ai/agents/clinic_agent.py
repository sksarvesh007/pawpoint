"""Unified clinic assistant agent with all tools.

Combines FAQ, appointment booking, provider lookup, medication refill,
and callback request capabilities into a single agent.
"""

from typing import Any

from loguru import logger
from pydantic_ai import RunContext

from app.ai.agents.appointment_agent import (
    book_appointment,
    check_appointment_status,
    get_available_slots,
    search_patients,
)
from app.ai.agents.base import (
    AgentDependencies,
    BaseAgent,
    get_clinic_info,
    update_conversation_context,
)
from app.ai.models import ModelFactory
from app.ai.prompts import build_clinic_assistant_system_prompt


class ClinicAssistantAgent(BaseAgent):
    """Unified agent for all clinic assistant capabilities."""

    def __init__(self, clinic_data: dict[str, Any] | None = None) -> None:
        model = ModelFactory.get_model_for_task("faq", channel="chat")

        if clinic_data:
            system_prompt = build_clinic_assistant_system_prompt(clinic_data)
        else:
            system_prompt = (
                "You are a helpful veterinary clinic assistant. "
                "You can answer questions, book appointments, look up providers, "
                "handle medication refill requests, and record callback requests."
            )

        super().__init__(
            name="clinic_assistant",
            system_prompt=system_prompt,
            model=model,
        )

        # Register all tools
        self.agent.tool(get_clinic_info)
        self.agent.tool(search_patients)
        self.agent.tool(get_available_slots)
        self.agent.tool(book_appointment)
        self.agent.tool(check_appointment_status)
        self.agent.tool(get_providers_list)
        self.agent.tool(request_medication_refill)
        self.agent.tool(request_callback)


async def get_providers_list(
    ctx: RunContext[AgentDependencies],
) -> list[dict[str, Any]]:
    """List available providers/veterinarians at the clinic.

    Args:
        ctx: Agent run context with dependencies

    Returns:
        List of providers with basic info
    """
    from app.services.provider import ProviderService

    service = ProviderService(ctx.deps.db_session)
    providers = await service.list_providers(ctx.deps.clinic_id, active_only=True)

    return [
        {
            "id": str(p.id),
            "name": p.full_name,
            "title": p.title,
            "provider_type": p.provider_type.value
            if hasattr(p.provider_type, "value")
            else str(p.provider_type),
            "specialties": p.specialties or [],
            "accepts_appointments": p.accepts_appointments,
        }
        for p in providers
    ]


async def request_medication_refill(
    ctx: RunContext[AgentDependencies],
    patient_name: str,
    medication_name: str,
    owner_name: str,
    owner_phone: str,
) -> dict[str, Any]:
    """Record a medication refill request for staff follow-up.

    Args:
        ctx: Agent run context with dependencies
        patient_name: Name of the pet
        medication_name: Name of the medication to refill
        owner_name: Name of the pet owner
        owner_phone: Phone number to reach the owner

    Returns:
        Confirmation message with request details
    """
    logger.info(
        f"Medication refill request: {medication_name} for {patient_name} (owner: {owner_name})"
    )

    await update_conversation_context(
        ctx,
        {
            "medication_refill_request": {
                "patient_name": patient_name,
                "medication_name": medication_name,
                "owner_name": owner_name,
                "owner_phone": owner_phone,
                "status": "pending",
            },
            "intent": "medication_refill",
        },
    )

    return {
        "success": True,
        "message": (
            f"Medication refill request recorded for {patient_name}'s {medication_name}. "
            f"A staff member will contact {owner_name} at {owner_phone} to process this request."
        ),
        "patient_name": patient_name,
        "medication_name": medication_name,
        "owner_name": owner_name,
        "owner_phone": owner_phone,
    }


async def request_callback(
    ctx: RunContext[AgentDependencies],
    caller_name: str,
    phone_number: str,
    reason: str,
) -> dict[str, Any]:
    """Record a callback request for staff follow-up.

    Args:
        ctx: Agent run context with dependencies
        caller_name: Name of the person requesting the callback
        phone_number: Phone number to call back
        reason: Reason for the callback request

    Returns:
        Confirmation message with request details
    """
    logger.info(f"Callback request from {caller_name} ({phone_number}): {reason}")

    await update_conversation_context(
        ctx,
        {
            "callback_request": {
                "caller_name": caller_name,
                "phone_number": phone_number,
                "reason": reason,
                "status": "pending",
            },
            "intent": "callback_request",
        },
    )

    return {
        "success": True,
        "message": (
            f"Callback request recorded for {caller_name} at {phone_number}. "
            "A staff member will call you back within 1-2 business hours."
        ),
        "caller_name": caller_name,
        "phone_number": phone_number,
        "reason": reason,
    }


def create_clinic_agent(
    clinic_data: dict[str, Any] | None = None,
) -> ClinicAssistantAgent:
    """Create and return a new ClinicAssistantAgent instance.

    Args:
        clinic_data: Optional clinic information for personalized prompts

    Returns:
        Initialized ClinicAssistantAgent
    """
    return ClinicAssistantAgent(clinic_data=clinic_data)
