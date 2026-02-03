"""Base agent class with shared dependencies and common patterns.

All specialized agents inherit from this base to get consistent setup.
"""

from dataclasses import dataclass
from typing import Any, Protocol
from uuid import UUID

from pydantic_ai import Agent, RunContext
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.state import HistoryManager, SessionManager


# Simple PIMS adapter protocol (actual implementation in Phase 2)
class IPIMSAdapter(Protocol):
    """Protocol for PIMS adapter interface.

    This is a placeholder protocol for PIMS (Practice Information Management System)
    integration. Concrete implementations will be added in Phase 2 for:
    - ezyVet
    - Vetspire
    - Other PIMS providers

    Methods to be added:
    - get_patient(patient_id: str) -> Patient
    - get_appointment(appointment_id: str) -> Appointment
    - create_appointment(...) -> Appointment
    - get_available_slots(...) -> list[TimeSlot]
    """

    ...


@dataclass
class AgentDependencies:
    """Shared dependencies for all AI agents.

    Provides access to:
    - Database session (PostgreSQL)
    - Redis client (caching/sessions)
    - Session manager (active conversations)
    - History manager (conversation persistence)
    - PIMS adapter (if configured)
    - Clinic context
    """

    db_session: AsyncSession
    redis_client: Redis
    session_manager: SessionManager
    history_manager: HistoryManager
    clinic_id: UUID
    conversation_id: UUID
    pims_adapter: IPIMSAdapter | None = None


class BaseAgent:
    """Base class for all Pydantic AI agents.

    Provides:
    - Consistent agent initialization
    - Shared tool patterns
    - Dependency injection setup
    - Error handling patterns
    """

    def __init__(
        self,
        name: str,
        system_prompt: str,
        model: Any,  # OpenAIChatModel
        output_type: type | None = None,
    ) -> None:
        """Initialize base agent.

        Args:
            name: Agent name for logging/tracking
            system_prompt: System prompt defining agent behavior
            model: LLM model instance from ModelFactory
            output_type: Optional structured output type
        """
        self.agent_name = name

        # Create Pydantic AI agent
        self.agent: Agent[AgentDependencies, Any] = Agent(
            model=model,
            deps_type=AgentDependencies,
            system_prompt=system_prompt,
            output_type=output_type or str,
            name=name,
        )

    def tool(self, func: Any) -> Any:
        """Register a tool with this agent.

        Wrapper around @agent.tool decorator for cleaner syntax.

        Args:
            func: Tool function to register

        Returns:
            Decorated function
        """
        return self.agent.tool(func)

    async def run(
        self,
        user_input: str,
        deps: AgentDependencies,
        message_history: Any = None,
    ) -> Any:
        """Run the agent with user input.

        Args:
            user_input: User message/query
            deps: Agent dependencies
            message_history: Optional conversation history (list of message dicts or ModelMessage objects)

        Returns:
            Agent result
        """
        return await self.agent.run(
            user_input,
            deps=deps,
            message_history=message_history,
        )

    async def run_sync_wrapper(
        self,
        user_input: str,
        deps: AgentDependencies,
        message_history: Any = None,
    ) -> Any:
        """Synchronous wrapper for running agent (for testing).

        Args:
            user_input: User message/query
            deps: Agent dependencies
            message_history: Optional conversation history (list of message dicts or ModelMessage objects)

        Returns:
            Agent result
        """
        return self.agent.run_sync(
            user_input,
            deps=deps,
            message_history=message_history,
        )


# Common tool patterns for all agents


async def get_clinic_info(ctx: RunContext[AgentDependencies]) -> dict[str, Any]:
    """Get clinic information.

    Common tool that all agents can use to fetch clinic details.

    Args:
        ctx: Agent run context with dependencies

    Returns:
        Dictionary with clinic information
    """
    from sqlalchemy import select

    from app.models.clinic import Clinic

    stmt = select(Clinic).where(Clinic.id == ctx.deps.clinic_id)
    result = await ctx.deps.db_session.execute(stmt)
    clinic = result.scalar_one_or_none()

    if not clinic:
        return {"error": "Clinic not found"}

    return {
        "name": clinic.name,
        "phone": clinic.phone,
        "email": clinic.email,
        "address": f"{clinic.address_line1}, {clinic.city}, {clinic.state} {clinic.postal_code}",
        "timezone": clinic.timezone,
        "business_hours": clinic.business_hours,
        "voice_enabled": clinic.voice_enabled,
    }


async def get_conversation_context(
    ctx: RunContext[AgentDependencies],
) -> dict[str, Any]:
    """Get current conversation context from Redis.

    Args:
        ctx: Agent run context with dependencies

    Returns:
        Current conversation context
    """
    session = await ctx.deps.session_manager.get_session(ctx.deps.conversation_id)

    if not session:
        return {"error": "Session not found"}

    return session.context.model_dump()


async def update_conversation_context(
    ctx: RunContext[AgentDependencies], context_updates: dict[str, Any]
) -> bool:
    """Update conversation context.

    Args:
        ctx: Agent run context with dependencies
        context_updates: Dictionary of context updates

    Returns:
        True if successful
    """
    # Update in PostgreSQL
    await ctx.deps.history_manager.update_conversation_context(
        ctx.deps.conversation_id, context_updates
    )

    # Update in Redis session
    session = await ctx.deps.session_manager.get_session(ctx.deps.conversation_id)
    if session:
        # Only update known fields on ConversationContext, store others in metadata
        known_fields = {
            "current_agent",
            "intent",
            "patient_id",
            "appointment_id",
        }
        for key, value in context_updates.items():
            if key in known_fields:
                setattr(session.context, key, value)
            else:
                # Store unknown keys in metadata
                session.context.metadata[key] = value
        await ctx.deps.session_manager.update_session(session)

    return True
