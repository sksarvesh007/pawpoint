"""FAQ Agent for general clinic information and common questions.

Handles queries about clinic hours, services, location, policies, etc.
"""

from typing import Any

from app.ai.agents.base import BaseAgent, get_clinic_info
from app.ai.models import ModelFactory
from app.ai.prompts import build_faq_system_prompt


class FAQAgent(BaseAgent):
    """Agent for handling frequently asked questions about the clinic."""

    def __init__(self, clinic_data: dict[str, Any] | None = None) -> None:
        """Initialize FAQ agent with clinic-specific prompt.

        Args:
            clinic_data: Optional clinic information for dynamic prompts.
                        If None, uses a generic prompt.
        """
        model = ModelFactory.get_model_for_task("faq", channel="chat")

        # Build dynamic system prompt based on clinic data
        if clinic_data:
            system_prompt = build_faq_system_prompt(clinic_data)
        else:
            # Fallback generic prompt
            system_prompt = """You are a helpful veterinary clinic assistant.

Answer questions about the clinic, including business hours, services, location, and policies.
Be friendly, concise, and professional. Use the get_clinic_info tool for accurate details."""

        super().__init__(
            name="faq_agent",
            system_prompt=system_prompt,
            model=model,
        )

        # Register tools
        self.agent.tool(get_clinic_info)


# Convenience function to create FAQ agent
def create_faq_agent(clinic_data: dict[str, Any] | None = None) -> FAQAgent:
    """Create and return a new FAQ agent instance.

    Args:
        clinic_data: Optional clinic information for personalized prompts

    Returns:
        Initialized FAQAgent with clinic-specific configuration
    """
    return FAQAgent(clinic_data=clinic_data)
