"""add chat_analysis table

Revision ID: a1b2c3d4e5f6
Revises: 8b3c5e7f9a12
Create Date: 2026-02-10

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "8b3c5e7f9a12"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "chat_analyses",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("conversation_id", sa.UUID(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="pending",
            comment="pending | processing | completed | failed",
        ),
        sa.Column(
            "error_message", sa.Text(), nullable=True, comment="Error details if analysis failed"
        ),
        sa.Column(
            "analyzed_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="When analysis completed",
        ),
        sa.Column(
            "analysis_model",
            sa.String(length=100),
            nullable=True,
            comment="LLM model used for analysis",
        ),
        sa.Column(
            "analysis_tokens", sa.Integer(), nullable=True, comment="Tokens consumed by analysis"
        ),
        sa.Column(
            "sentiment",
            sa.String(length=20),
            nullable=True,
            comment="positive | neutral | negative",
        ),
        sa.Column(
            "sentiment_score", sa.Float(), nullable=True, comment="Score from -1.0 to 1.0"
        ),
        sa.Column(
            "resolution_status",
            sa.String(length=20),
            nullable=True,
            comment="resolved | unresolved | partial | escalated",
        ),
        sa.Column(
            "user_satisfaction",
            sa.String(length=20),
            nullable=True,
            comment="satisfied | neutral | dissatisfied",
        ),
        sa.Column(
            "primary_topic",
            sa.String(length=100),
            nullable=True,
            comment="Main topic category",
        ),
        sa.Column(
            "topics",
            sa.dialects.postgresql.JSONB(),
            nullable=True,
            comment="All topics discussed",
        ),
        sa.Column(
            "entities",
            sa.dialects.postgresql.JSONB(),
            nullable=True,
            comment="Pet names, species, medications, etc.",
        ),
        sa.Column(
            "key_points",
            sa.dialects.postgresql.JSONB(),
            nullable=True,
            comment="Summary bullet points",
        ),
        sa.Column(
            "suggested_followup", sa.Text(), nullable=True, comment="Suggested next action"
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
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("conversation_id"),
    )
    op.create_index("ix_chat_analyses_conversation_id", "chat_analyses", ["conversation_id"])
    op.create_index("ix_chat_analyses_sentiment", "chat_analyses", ["sentiment"])
    op.create_index("ix_chat_analyses_resolution", "chat_analyses", ["resolution_status"])
    op.create_index("ix_chat_analyses_topic", "chat_analyses", ["primary_topic"])
    op.create_index("ix_chat_analyses_status", "chat_analyses", ["status"])


def downgrade() -> None:
    op.drop_index("ix_chat_analyses_status", table_name="chat_analyses")
    op.drop_index("ix_chat_analyses_topic", table_name="chat_analyses")
    op.drop_index("ix_chat_analyses_resolution", table_name="chat_analyses")
    op.drop_index("ix_chat_analyses_sentiment", table_name="chat_analyses")
    op.drop_index("ix_chat_analyses_conversation_id", table_name="chat_analyses")
    op.drop_table("chat_analyses")
