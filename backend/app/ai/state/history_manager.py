"""PostgreSQL history manager for conversation persistence.

Provides long-term storage of conversation history with analytics capabilities.
"""

from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.state.schemas import MessageData, UsageMetrics
from app.core.instrumentation import decrement_active_chat_sessions, traced
from app.models.conversation import Conversation
from app.models.message import Message


class HistoryManager:
    """Manages conversation history in PostgreSQL.

    Responsibilities:
    - Persist conversations and messages long-term
    - Query conversation history
    - Generate analytics and summaries
    - Archive completed sessions
    """

    def __init__(self, db_session: AsyncSession) -> None:
        """Initialize history manager.

        Args:
            db_session: Async SQLAlchemy session
        """
        self.db = db_session

    @traced(span_name="history_manager.create_conversation")
    async def create_conversation(
        self,
        clinic_id: UUID,
        channel: str,
        user_identifier: str,
        context: dict | None = None,
        extra_data: dict | None = None,
    ) -> Conversation:
        """Create a new conversation record.

        Args:
            clinic_id: Clinic UUID
            channel: Communication channel (voice, chat, email)
            user_identifier: User phone, email, or ID
            context: Initial conversation context
            extra_data: Additional metadata

        Returns:
            Created Conversation instance

        Raises:
            SQLAlchemy errors
        """
        conversation = Conversation(
            clinic_id=clinic_id,
            channel=channel,
            user_identifier=user_identifier,
            context=context or {},
            extra_data=extra_data or {},
            session_active=True,
        )

        self.db.add(conversation)
        await self.db.flush()
        await self.db.refresh(conversation)

        return conversation

    @traced(span_name="history_manager.save_message")
    async def save_message(
        self,
        conversation_id: UUID,
        message_data: MessageData,
        usage: UsageMetrics | None = None,
        extra_data: dict | None = None,
    ) -> Message:
        """Save a message to the database.

        Args:
            conversation_id: Conversation UUID
            message_data: Message data to save
            usage: Optional usage metrics
            extra_data: Optional extra metadata for the message

        Returns:
            Created Message instance

        Raises:
            SQLAlchemy errors
        """
        message = Message(
            conversation_id=conversation_id,
            role=message_data.role,
            content=message_data.content,
            agent_name=message_data.agent_name,
            model_name=message_data.model_name,
            tool_calls=message_data.tool_calls,
            tool_call_id=message_data.tool_call_id,
            prompt_tokens=usage.prompt_tokens if usage else None,
            completion_tokens=usage.completion_tokens if usage else None,
            total_tokens=usage.total_tokens if usage else None,
            extra_data=extra_data or {},
        )

        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)

        # Update conversation totals
        await self._update_conversation_totals(
            conversation_id, tokens_to_add=usage.total_tokens if usage else 0
        )

        return message

    @traced(span_name="history_manager.get_conversation")
    async def get_conversation(self, conversation_id: UUID) -> Conversation | None:
        """Retrieve a conversation by ID.

        Args:
            conversation_id: Conversation UUID

        Returns:
            Conversation instance or None

        Raises:
            SQLAlchemy errors
        """
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    @traced(span_name="history_manager.get_conversation_messages")
    async def get_conversation_messages(
        self,
        conversation_id: UUID,
        limit: int | None = None,
        offset: int = 0,
    ) -> Sequence[Message]:
        """Retrieve messages for a conversation.

        Args:
            conversation_id: Conversation UUID
            limit: Maximum number of messages to return
            offset: Number of messages to skip

        Returns:
            List of Message instances

        Raises:
            SQLAlchemy errors
        """
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .offset(offset)
        )

        if limit:
            stmt = stmt.limit(limit)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    @traced(span_name="history_manager.get_recent_conversations")
    async def get_recent_conversations(
        self,
        clinic_id: UUID,
        channel: str | None = None,
        limit: int = 50,
    ) -> Sequence[Conversation]:
        """Get recent conversations for a clinic.

        Args:
            clinic_id: Clinic UUID
            channel: Optional channel filter
            limit: Maximum conversations to return

        Returns:
            List of Conversation instances

        Raises:
            SQLAlchemy errors
        """
        stmt = select(Conversation).where(Conversation.clinic_id == clinic_id)

        # Apply channel filter before ordering and limiting
        if channel:
            stmt = stmt.where(Conversation.channel == channel)

        stmt = stmt.order_by(Conversation.updated_at.desc()).limit(limit)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    @traced(span_name="history_manager.end_conversation")
    async def end_conversation(
        self, conversation_id: UUID, summary: str | None = None
    ) -> Conversation | None:
        """Mark a conversation as ended.

        Args:
            conversation_id: Conversation UUID
            summary: Optional AI-generated summary

        Returns:
            Updated Conversation or None

        Raises:
            SQLAlchemy errors
        """
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return None

        # Only decrement if session was active (avoid double-decrement)
        was_active = conversation.session_active

        conversation.session_active = False
        conversation.session_ended_at = datetime.now(UTC)

        if summary:
            conversation.summary = summary

        await self.db.flush()
        await self.db.refresh(conversation)

        # Decrement active sessions counter if session was previously active
        if was_active:
            decrement_active_chat_sessions(str(conversation.clinic_id))

        return conversation

    @traced(span_name="history_manager.update_conversation_context")
    async def update_conversation_context(
        self,
        conversation_id: UUID,
        context_updates: dict,
    ) -> Conversation | None:
        """Update conversation context data.

        Args:
            conversation_id: Conversation UUID
            context_updates: Dictionary of context updates to merge

        Returns:
            Updated Conversation or None

        Raises:
            SQLAlchemy errors
        """
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return None

        # Merge updates into existing context
        conversation.context = {**conversation.context, **context_updates}

        await self.db.flush()
        await self.db.refresh(conversation)

        return conversation

    @traced(span_name="history_manager._update_conversation_totals")
    async def _update_conversation_totals(
        self, conversation_id: UUID, tokens_to_add: int = 0
    ) -> None:
        """Update conversation message count and token totals.

        Args:
            conversation_id: Conversation UUID
            tokens_to_add: Tokens to add to total

        Raises:
            SQLAlchemy errors
        """
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return

        conversation.total_messages += 1
        conversation.total_tokens += tokens_to_add

        await self.db.flush()

    @traced(span_name="history_manager.get_conversation_usage_summary")
    async def get_conversation_usage_summary(
        self, conversation_id: UUID
    ) -> dict[str, int]:
        """Get token usage summary for a conversation.

        Args:
            conversation_id: Conversation UUID

        Returns:
            Dictionary with prompt_tokens, completion_tokens, total_tokens

        Raises:
            SQLAlchemy errors
        """
        stmt = (
            select(
                func.sum(Message.prompt_tokens).label("prompt_tokens"),
                func.sum(Message.completion_tokens).label("completion_tokens"),
                func.sum(Message.total_tokens).label("total_tokens"),
            )
            .where(Message.conversation_id == conversation_id)
            .group_by(Message.conversation_id)
        )

        result = await self.db.execute(stmt)
        row = result.first()

        if not row:
            return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        return {
            "prompt_tokens": row.prompt_tokens or 0,
            "completion_tokens": row.completion_tokens or 0,
            "total_tokens": row.total_tokens or 0,
        }
