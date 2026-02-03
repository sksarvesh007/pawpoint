"""Redis session manager for active conversation state.

Provides fast access to active conversation sessions with automatic expiration.
"""

from datetime import UTC, datetime
from typing import cast
from uuid import UUID

from redis.asyncio import Redis

from app.ai.state.schemas import ConversationSession, MessageData
from app.core.config import settings


class SessionManager:
    """Manages conversation sessions in Redis.

    Responsibilities:
    - Store/retrieve active conversation sessions
    - Automatic session expiration (TTL)
    - Fast message history access
    - Session state updates
    """

    def __init__(self, redis_client: Redis) -> None:
        """Initialize session manager.

        Args:
            redis_client: Async Redis client instance
        """
        self.redis = redis_client
        self.ttl_seconds = settings.conversation_session_ttl_seconds
        self.ttl_extension = settings.conversation_session_ttl_extension
        self.key_prefix = settings.redis_key_prefix_session
        self.clinic_sessions_prefix = settings.redis_key_prefix_clinic_sessions

    def _get_key(self, conversation_id: UUID | str) -> str:
        """Generate Redis key for a conversation session.

        Args:
            conversation_id: Conversation UUID

        Returns:
            Redis key string
        """
        return f"{self.key_prefix}{conversation_id}"

    def _get_clinic_sessions_key(self, clinic_id: UUID | str) -> str:
        """Generate Redis key for a clinic's active sessions set.

        Args:
            clinic_id: Clinic UUID

        Returns:
            Redis key string
        """
        return self.clinic_sessions_prefix.format(clinic_id=clinic_id)

    async def create_session(self, session: ConversationSession) -> None:
        """Create a new conversation session in Redis.

        Args:
            session: ConversationSession to store

        Raises:
            Redis connection errors
        """
        key = self._get_key(session.conversation_id)
        session_json = session.model_dump_json()

        # Store the session
        await self.redis.setex(
            key,
            self.ttl_seconds,
            session_json,
        )

        # Add to clinic's active sessions set for fast counting
        clinic_set_key = self._get_clinic_sessions_key(session.context.clinic_id)
        await self.redis.sadd(clinic_set_key, str(session.conversation_id))  # type: ignore[misc]
        # Set expiration on the set (slightly longer than session TTL)
        await self.redis.expire(clinic_set_key, self.ttl_seconds + self.ttl_extension)

    async def get_session(
        self, conversation_id: UUID | str
    ) -> ConversationSession | None:
        """Retrieve a conversation session from Redis.

        Args:
            conversation_id: Conversation UUID

        Returns:
            ConversationSession if found, None otherwise

        Raises:
            Redis connection errors
        """
        key = self._get_key(conversation_id)
        session_json = await self.redis.get(key)

        if not session_json:
            return None

        return ConversationSession.model_validate_json(session_json)

    async def update_session(self, session: ConversationSession) -> None:
        """Update an existing conversation session.

        Resets the TTL on update to keep active conversations alive.

        Args:
            session: Updated ConversationSession

        Raises:
            Redis connection errors
        """
        session.updated_at = datetime.now(UTC)
        key = self._get_key(session.conversation_id)
        session_json = session.model_dump_json()

        await self.redis.setex(
            key,
            self.ttl_seconds,
            session_json,
        )

    async def add_message(
        self,
        conversation_id: UUID | str,
        message: MessageData,
        update_tokens: int = 0,
    ) -> ConversationSession | None:
        """Add a message to a conversation session.

        Args:
            conversation_id: Conversation UUID
            message: Message to add
            update_tokens: Token count to add to session total

        Returns:
            Updated ConversationSession, or None if session not found

        Raises:
            Redis connection errors
        """
        session = await self.get_session(conversation_id)
        if not session:
            return None

        # Add message and update metrics
        session.add_message(message, max_history=settings.conversation_max_history)
        session.total_tokens += update_tokens

        # Save updated session
        await self.update_session(session)

        return session

    async def delete_session(self, conversation_id: UUID | str) -> bool:
        """Delete a conversation session from Redis.

        Args:
            conversation_id: Conversation UUID

        Returns:
            True if session was deleted, False if not found

        Raises:
            Redis connection errors
        """
        # Get session to find clinic_id before deleting
        session = await self.get_session(conversation_id)

        key = self._get_key(conversation_id)
        deleted_count = await self.redis.delete(key)

        # Remove from clinic's active sessions set
        if session:
            clinic_set_key = self._get_clinic_sessions_key(session.context.clinic_id)
            await self.redis.srem(clinic_set_key, str(conversation_id))  # type: ignore[misc]

        return deleted_count > 0

    async def extend_session(
        self, conversation_id: UUID | str, extra_seconds: int = 0
    ) -> bool:
        """Extend the TTL of an active session.

        Args:
            conversation_id: Conversation UUID
            extra_seconds: Extra seconds to add (default: reset to full TTL)

        Returns:
            True if session exists and TTL was extended

        Raises:
            Redis connection errors
        """
        key = self._get_key(conversation_id)

        # If extra_seconds not specified, reset to full TTL
        ttl = extra_seconds if extra_seconds > 0 else self.ttl_seconds

        return cast(bool, await self.redis.expire(key, ttl))

    async def get_active_sessions_count(self, clinic_id: UUID | str) -> int:
        """Get count of active sessions for a clinic.

        Validates each session in the set still exists, removing stale entries.

        Args:
            clinic_id: Clinic UUID

        Returns:
            Number of active sessions

        Raises:
            Redis connection errors
        """
        clinic_set_key = self._get_clinic_sessions_key(clinic_id)
        session_ids = await self.redis.smembers(clinic_set_key)  # type: ignore[misc]

        if not session_ids:
            return 0

        # Validate each session still exists and remove stale entries
        active_count = 0
        stale_ids: list[str] = []

        for session_id in session_ids:
            key = self._get_key(session_id)
            exists = await self.redis.exists(key)
            if exists:
                active_count += 1
            else:
                stale_ids.append(session_id)

        # Remove stale session IDs from the set
        if stale_ids:
            await self.redis.srem(clinic_set_key, *stale_ids)  # type: ignore[misc]

        return active_count

    async def cleanup_expired_sessions(self) -> int:
        """Clean up any expired sessions (Redis handles this automatically).

        This is mostly a no-op as Redis handles TTL expiration.
        Included for explicit cleanup if needed.

        Returns:
            Number of sessions cleaned up (usually 0)
        """
        # Redis handles TTL cleanup automatically
        # This method exists for consistency with the interface
        return 0
