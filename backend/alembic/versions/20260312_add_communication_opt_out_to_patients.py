"""add communication_opt_out column to patients

Revision ID: d5e6f7a8b9c0
Revises: c4d5e6f7a8b9
Create Date: 2026-03-12 10:00:00.000000+00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "d5e6f7a8b9c0"
down_revision: Union[str, None] = "c4d5e6f7a8b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "patients",
        sa.Column(
            "communication_opt_out",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment='Opt-out flags: {"sms": true, "email": true}',
        ),
    )


def downgrade() -> None:
    op.drop_column("patients", "communication_opt_out")
