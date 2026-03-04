"""ChatAnalysis model for per-conversation AI analytics.

Stores LLM-extracted sentiment, topics, resolution, and entities
from completed chat conversations. One-to-one with Conversation.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.conversation import Conversation


class ChatAnalysis(Base, TimestampMixin):
    """AI-generated analytics for a chat conversation.

    Created as a background Celery task when a chat session ends.
    Stores sentiment, topics, resolution status, and extracted entities.
    """

    __tablename__ = "chat_analyses"

    # One-to-one link to conversation
    conversation_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="analysis"
    )

    # Analysis lifecycle
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        index=True,
        comment="pending | processing | completed | failed",
    )
    error_message: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Error details if analysis failed"
    )
    analyzed_at: Mapped[datetime | None] = mapped_column(
        nullable=True, comment="When analysis completed"
    )
    analysis_model: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="LLM model used for analysis"
    )
    analysis_tokens: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Tokens consumed by analysis"
    )

    # Sentiment
    sentiment: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        index=True,
        comment="positive | neutral | negative",
    )
    sentiment_score: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="Score from -1.0 to 1.0"
    )

    # Resolution
    resolution_status: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        index=True,
        comment="resolved | unresolved | partial | escalated",
    )
    user_satisfaction: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="satisfied | neutral | dissatisfied",
    )

    # Topics
    primary_topic: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Main topic category",
    )
    topics: Mapped[list | None] = mapped_column(
        JSONB, nullable=True, comment="All topics discussed"
    )

    # Extracted entities and summary
    entities: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, comment="Pet names, species, medications, etc."
    )
    key_points: Mapped[list | None] = mapped_column(
        JSONB, nullable=True, comment="Summary bullet points"
    )
    suggested_followup: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Suggested next action"
    )

    # Indexes on conversation_id, sentiment, resolution_status, primary_topic
    # are defined inline via index=True / unique=True on each column above.

    def __repr__(self) -> str:
        return (
            f"<ChatAnalysis(id={self.id}, conversation_id={self.conversation_id}, "
            f"status={self.status}, sentiment={self.sentiment})>"
        )
