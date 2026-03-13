"""add message_logs, notifications tables and reminder_2h_sent_at column

Revision ID: c4d5e6f7a8b9
Revises: 82202603b7a7
Create Date: 2026-03-11 12:00:00.000000+00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "c4d5e6f7a8b9"
down_revision: Union[str, None] = "82202603b7a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- message_logs table ---
    op.create_table(
        "message_logs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("clinic_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "channel",
            sa.String(20),
            nullable=False,
            comment="sms or email",
        ),
        sa.Column(
            "recipient",
            sa.String(255),
            nullable=False,
            comment="Phone number or email address",
        ),
        sa.Column("subject", sa.String(255), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="sent",
            comment="sent, delivered, failed",
        ),
        sa.Column(
            "external_id",
            sa.String(255),
            nullable=True,
            comment="Twilio SID or SendGrid Message ID",
        ),
        sa.Column(
            "related_type",
            sa.String(50),
            nullable=True,
            comment="appointment_confirmation, reminder, clinic_info",
        ),
        sa.Column("related_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_message_logs_clinic_id", "message_logs", ["clinic_id"])
    op.create_index("ix_message_logs_id", "message_logs", ["id"])

    # --- notifications table ---
    notification_type = postgresql.ENUM(
        "emergency_call",
        "missed_transfer",
        "medication_request",
        "appointment_request",
        "callback_needed",
        "failed_delivery",
        "low_confidence_call",
        name="notificationtype",
        create_type=True,
    )
    notification_priority = postgresql.ENUM(
        "low",
        "normal",
        "high",
        "urgent",
        name="notificationpriority",
        create_type=True,
    )

    op.create_table(
        "notifications",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("clinic_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", notification_type, nullable=False),
        sa.Column(
            "priority",
            notification_priority,
            nullable=False,
            server_default="normal",
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Related entity info (call_log_id, patient_name, etc.)",
        ),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "resolved_by",
            postgresql.UUID(as_uuid=True),
            nullable=True,
            comment="User ID who resolved this notification",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_notifications_clinic_id", "notifications", ["clinic_id"])
    op.create_index("ix_notifications_type", "notifications", ["type"])
    op.create_index("ix_notifications_priority", "notifications", ["priority"])
    op.create_index("ix_notifications_id", "notifications", ["id"])

    # --- reminder_2h_sent_at on appointments ---
    op.add_column(
        "appointments",
        sa.Column("reminder_2h_sent_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("appointments", "reminder_2h_sent_at")

    op.drop_index("ix_notifications_id", table_name="notifications")
    op.drop_index("ix_notifications_priority", table_name="notifications")
    op.drop_index("ix_notifications_type", table_name="notifications")
    op.drop_index("ix_notifications_clinic_id", table_name="notifications")
    op.drop_table("notifications")

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS notificationpriority")
    op.execute("DROP TYPE IF EXISTS notificationtype")

    op.drop_index("ix_message_logs_id", table_name="message_logs")
    op.drop_index("ix_message_logs_clinic_id", table_name="message_logs")
    op.drop_table("message_logs")
