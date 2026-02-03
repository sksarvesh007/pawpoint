"""Message model for individual messages within conversations.

Stores user and assistant messages, including tool calls and metadata.
"""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.conversation import Conversation


class Message(Base, TimestampMixin):
    """Individual message within a conversation.

    Stores both user and assistant messages, including tool calls,
    function results, and usage metrics for each LLM interaction.
    """

    __tablename__ = "messages"

    # Relationship to conversation
    conversation_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="messages"
    )

    # Message role
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="Message role: user, assistant, system, or tool",
    )

    # Message content
    content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Message text content (may be null for tool calls)",
    )

    # Agent and model info
    agent_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Agent that generated this message",
    )
    model_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="LLM model used: gpt-4o, gemini-2.0-flash-exp, etc.",
    )
    provider: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Model provider: openai or gemini",
    )

    # Tool/function calling
    tool_calls: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Tool calls requested by assistant",
    )
    tool_call_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="ID of tool call this message responds to",
    )

    # Usage metrics (tokens)
    prompt_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Tokens used in prompt/input",
    )
    completion_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Tokens used in completion/output",
    )
    total_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Total tokens used in this exchange",
    )

    # Extra data
    extra_data: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Additional metadata: latency, error info, etc.",
    )

    # Provider-specific identifiers
    provider_message_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Message ID from provider API",
    )
    provider_response_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Response ID from provider (for OpenAI conversation tracking)",
    )

    # Indexes for common queries
    __table_args__ = (
        Index("ix_messages_conversation_created", "conversation_id", "created_at"),
        Index("ix_messages_conversation_role", "conversation_id", "role"),
        Index("ix_messages_model_created", "model_name", "created_at"),
    )

    def __repr__(self) -> str:
        """String representation of message."""
        content_preview = (
            self.content[:50] + "..."
            if self.content and len(self.content) > 50
            else self.content
        )
        return f"<Message(id={self.id}, role={self.role}, content='{content_preview}')>"
