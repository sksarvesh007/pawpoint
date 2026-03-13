"""Notification service for creating and managing staff notifications."""

import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, NotificationPriority, NotificationType

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for creating and managing staff notifications."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        clinic_id: UUID,
        type: NotificationType | str,
        priority: NotificationPriority | str,
        title: str,
        message: str,
        metadata: dict | None = None,
    ) -> Notification:
        """Create a new notification."""
        notification = Notification(
            clinic_id=clinic_id,
            type=NotificationType(type) if isinstance(type, str) else type,
            priority=NotificationPriority(priority)
            if isinstance(priority, str)
            else priority,
            title=title,
            message=message,
            metadata_json=metadata,
        )
        self.db.add(notification)
        await self.db.flush()
        return notification

    async def list(
        self,
        clinic_id: UUID,
        unread_only: bool = False,
        type_filter: str | None = None,
        priority_filter: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Notification], int]:
        """List notifications with filters and pagination.

        Returns:
            Tuple of (notifications, total_count)
        """
        conditions = [Notification.clinic_id == clinic_id]

        if unread_only:
            conditions.append(Notification.read_at.is_(None))

        if type_filter:
            conditions.append(Notification.type == type_filter)

        if priority_filter:
            conditions.append(Notification.priority == priority_filter)

        # Count total
        count_query = select(func.count()).select_from(
            select(Notification.id).where(and_(*conditions)).subquery()
        )
        total = (await self.db.execute(count_query)).scalar() or 0

        # Fetch page
        query = (
            select(Notification)
            .where(and_(*conditions))
            .order_by(Notification.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await self.db.execute(query)
        notifications = list(result.scalars().all())

        return notifications, total

    async def mark_read(self, notification_id: UUID) -> Notification | None:
        """Mark a notification as read."""
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()
        if notification and not notification.read_at:
            notification.read_at = datetime.now(UTC)
            await self.db.flush()
        return notification

    async def mark_resolved(
        self, notification_id: UUID, user_id: UUID
    ) -> Notification | None:
        """Mark a notification as resolved."""
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()
        if notification and not notification.resolved_at:
            notification.resolved_at = datetime.now(UTC)
            notification.resolved_by = user_id
            if not notification.read_at:
                notification.read_at = datetime.now(UTC)
            await self.db.flush()
        return notification

    async def unread_count(self, clinic_id: UUID) -> int:
        """Get count of unread notifications for badge display."""
        result = await self.db.execute(
            select(func.count()).where(
                and_(
                    Notification.clinic_id == clinic_id,
                    Notification.read_at.is_(None),
                )
            )
        )
        return result.scalar() or 0

    # --- Convenience methods for common notification types ---

    async def notify_emergency_call(
        self,
        clinic_id: UUID,
        call_log_id: UUID | None = None,
        caller_info: str | None = None,
    ) -> Notification:
        """Create an emergency call notification."""
        return await self.create(
            clinic_id=clinic_id,
            type=NotificationType.EMERGENCY_CALL,
            priority=NotificationPriority.URGENT,
            title="Emergency Call Received",
            message=f"An emergency call was received{' from ' + caller_info if caller_info else ''}. Immediate attention required.",
            metadata={"call_log_id": str(call_log_id)} if call_log_id else None,
        )

    async def notify_medication_request(
        self,
        clinic_id: UUID,
        request_data: dict,
    ) -> Notification:
        """Create a medication refill request notification."""
        pet_name = request_data.get("pet_name", "Unknown")
        medication = request_data.get("medication_name", "Unknown")
        caller = request_data.get("caller_name", "Unknown")
        urgency = request_data.get("urgency", "normal")
        priority = (
            NotificationPriority.HIGH
            if urgency == "urgent"
            else NotificationPriority.NORMAL
        )
        return await self.create(
            clinic_id=clinic_id,
            type=NotificationType.MEDICATION_REQUEST,
            priority=priority,
            title=f"Medication Refill: {medication} for {pet_name}",
            message=f"{caller} requested a refill of {medication} for {pet_name}. Callback: {request_data.get('callback_number', 'N/A')}",
            metadata=request_data,
        )

    async def notify_missed_transfer(
        self,
        clinic_id: UUID,
        call_log_id: UUID | None = None,
    ) -> Notification:
        """Create a missed transfer notification."""
        return await self.create(
            clinic_id=clinic_id,
            type=NotificationType.MISSED_TRANSFER,
            priority=NotificationPriority.HIGH,
            title="Missed Call Transfer",
            message="A call transfer was attempted but could not be completed. The caller may need a callback.",
            metadata={"call_log_id": str(call_log_id)} if call_log_id else None,
        )

    async def notify_failed_delivery(
        self,
        clinic_id: UUID,
        message_log_id: UUID | None = None,
        channel: str = "sms",
        recipient: str | None = None,
        error: str | None = None,
    ) -> Notification:
        """Create a failed message delivery notification."""
        msg = (
            f"A {channel} message to {recipient or 'a client'} could not be delivered."
        )
        if error:
            msg += f" Error: {error[:200]}"
        return await self.create(
            clinic_id=clinic_id,
            type=NotificationType.FAILED_DELIVERY,
            priority=NotificationPriority.NORMAL,
            title=f"Failed {channel.upper()} Delivery",
            message=msg,
            metadata={
                "message_log_id": str(message_log_id) if message_log_id else None,
                "channel": channel,
                "recipient": recipient,
            },
        )
