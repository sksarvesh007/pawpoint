"""AI agents for handling different conversation types."""

from app.ai.agents.analytics_agent import create_analytics_agent
from app.ai.agents.appointment_agent import AppointmentAgent, create_appointment_agent
from app.ai.agents.base import AgentDependencies, BaseAgent
from app.ai.agents.clinic_agent import ClinicAssistantAgent, create_clinic_agent
from app.ai.agents.faq_agent import FAQAgent, create_faq_agent

__all__ = [
    "AgentDependencies",
    "AppointmentAgent",
    "BaseAgent",
    "ClinicAssistantAgent",
    "FAQAgent",
    "create_analytics_agent",
    "create_appointment_agent",
    "create_clinic_agent",
    "create_faq_agent",
]
