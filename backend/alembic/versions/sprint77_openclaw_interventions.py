"""OpenClaw interventions table

Revision ID: sprint77_openclaw_interventions
Revises: sprint76_rh_structs
Create Date: 2026-03-20
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

from alembic import op

revision = "sprint77_openclaw_interventions"
down_revision = "6ce4dc2d4186"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "openclaw_interventions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("alert_name", sa.String(200), nullable=False, index=True),
        sa.Column("alert_fingerprint", sa.String(64), nullable=False, server_default=""),
        sa.Column(
            "severity",
            sa.Enum("info", "warning", "critical", name="interventionseverity"),
            nullable=False,
            server_default="warning",
        ),
        sa.Column(
            "status",
            sa.Enum(
                "received",
                "diagnosing",
                "acting",
                "resolved",
                "failed",
                "escalated",
                name="interventionstatus",
            ),
            nullable=False,
            server_default="received",
        ),
        sa.Column("diagnosis", sa.Text, nullable=True),
        sa.Column("actions_taken", JSONB, nullable=True),
        sa.Column("resolution", sa.Text, nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("response_time_seconds", sa.Integer, nullable=True),
        sa.Column("raw_payload", JSONB, nullable=True),
        sa.Column("telegram_sent", sa.Boolean, server_default="false"),
        sa.Column("telegram_message_id", sa.String(50), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
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
    )
    op.create_index("ix_openclaw_interventions_created", "openclaw_interventions", ["created_at"])
    op.create_index("ix_openclaw_interventions_status", "openclaw_interventions", ["status"])


def downgrade() -> None:
    op.drop_table("openclaw_interventions")
    op.execute("DROP TYPE IF EXISTS interventionseverity")
    op.execute("DROP TYPE IF EXISTS interventionstatus")
