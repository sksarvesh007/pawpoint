"""Pydantic schemas for conversation state management.

Used for serializing conversation data in Redis and validating state structures.
"""

from datetime import UTC, datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ConversationContext(BaseModel):
    """Context data for an active conversation.

    Stored in Redis for quick access during active sessions.
    """

    conversation_id: UUID
    clinic_id: UUID
    channel: Literal["voice", "chat", "email"]
    user_identifier: str  # Phone, email, or user ID

    # Current state
    current_agent: str | None = None  # router, appointment, patient_record, etc.
    intent: str | None = None  # book_appointment, ask_question, etc.

    # Referenced entities
    patient_id: UUID | None = None
    appointment_id: UUID | None = None

    # Flexible metadata
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic config."""

        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }


class MessageData(BaseModel):
    """Individual message data for session cache."""

    role: Literal["user", "assistant", "system", "tool"]
    content: str | None = None
    agent_name: str | None = None
    model_name: str | None = None
    tool_calls: list[dict[str, Any]] | None = None
    tool_call_id: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Config:
        """Pydantic config."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class ConversationSession(BaseModel):
    """Active conversation session stored in Redis.

    Contains recent message history and current context for fast access.
    Full history is stored in PostgreSQL.
    """

    conversation_id: UUID
    context: ConversationContext
    message_history: list[MessageData] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    expires_at: datetime

    # Usage tracking
    total_messages: int = 0
    total_tokens: int = 0

    class Config:
        """Pydantic config."""

        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }

    def add_message(self, message: MessageData, max_history: int = 20) -> None:
        """Add a message to the session history.

        Keeps only the most recent N messages in memory (older ones in DB).

        Args:
            message: Message to add
            max_history: Maximum messages to keep in session (default 20)
        """
        self.message_history.append(message)
        self.total_messages += 1

        # Trim to max history (keep most recent)
        if len(self.message_history) > max_history:
            self.message_history = self.message_history[-max_history:]

        self.updated_at = datetime.now(UTC)


class UsageMetrics(BaseModel):
    """Token usage metrics for an LLM interaction."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    class Config:
        """Pydantic config."""

        frozen = True
