"""add livekit fields to call_logs

Revision ID: 8b3c5e7f9a12
Revises: d04f74a5ecc8
Create Date: 2026-02-04

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8b3c5e7f9a12"
down_revision: str | None = "d04f74a5ecc8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create CallChannel enum type (if not exists)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE callchannel AS ENUM ('phone', 'web_voice');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Add LiveKit-specific columns to call_logs table (if not exist)
    op.execute("""
        ALTER TABLE call_logs
        ADD COLUMN IF NOT EXISTS livekit_room_name VARCHAR(100);
    """)
    op.execute("""
        ALTER TABLE call_logs
        ADD COLUMN IF NOT EXISTS livekit_participant_id VARCHAR(100);
    """)

    # Add channel column with default value (if not exists)
    op.execute("""
        ALTER TABLE call_logs
        ADD COLUMN IF NOT EXISTS channel callchannel NOT NULL DEFAULT 'phone';
    """)

    # Create indexes (if not exist)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_call_logs_livekit_room_name
        ON call_logs (livekit_room_name);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_call_logs_clinic_channel
        ON call_logs (clinic_id, channel);
    """)


def downgrade() -> None:
    # Drop indexes
    op.drop_index("ix_call_logs_clinic_channel", table_name="call_logs")
    op.drop_index("ix_call_logs_livekit_room_name", table_name="call_logs")

    # Drop columns
    op.drop_column("call_logs", "channel")
    op.drop_column("call_logs", "livekit_participant_id")
    op.drop_column("call_logs", "livekit_room_name")

    # Drop enum type
    op.execute("DROP TYPE callchannel")
