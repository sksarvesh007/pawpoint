"""fix column types for uuid fields

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-17

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6a7"
down_revision: str | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Change patient_id_matched from VARCHAR(36) to UUID
    op.alter_column(
        "call_logs",
        "patient_id_matched",
        existing_type=sa.String(36),
        type_=postgresql.UUID(as_uuid=True),
        existing_nullable=True,
        postgresql_using="patient_id_matched::uuid",
    )

    # Change reviewed_by_user_id from VARCHAR(36) to UUID
    op.alter_column(
        "call_logs",
        "reviewed_by_user_id",
        existing_type=sa.String(36),
        type_=postgresql.UUID(as_uuid=True),
        existing_nullable=True,
        postgresql_using="reviewed_by_user_id::uuid",
    )


def downgrade() -> None:
    # Revert reviewed_by_user_id back to VARCHAR(36)
    op.alter_column(
        "call_logs",
        "reviewed_by_user_id",
        existing_type=postgresql.UUID(as_uuid=True),
        type_=sa.String(36),
        existing_nullable=True,
        postgresql_using="reviewed_by_user_id::text",
    )

    # Revert patient_id_matched back to VARCHAR(36)
    op.alter_column(
        "call_logs",
        "patient_id_matched",
        existing_type=postgresql.UUID(as_uuid=True),
        type_=sa.String(36),
        existing_nullable=True,
        postgresql_using="patient_id_matched::text",
    )
