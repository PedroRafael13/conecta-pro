"""Create monitoring tables for Early Warning System.

Revision ID: ews001
Revises: a1b2c3d4e5f6
Create Date: 2026-01-06

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ews001"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Criar enum types
    alert_level = postgresql.ENUM(
        "green", "yellow", "orange", "red",
        name="alertlevel",
        create_type=False,
    )
    alert_level.create(op.get_bind(), checkfirst=True)

    alert_status = postgresql.ENUM(
        "active", "acknowledged", "resolved", "escalated", "suppressed",
        name="alertstatus",
        create_type=False,
    )
    alert_status.create(op.get_bind(), checkfirst=True)

    threshold_type = postgresql.ENUM(
        "upper", "lower", "range",
        name="thresholdtype",
        create_type=False,
    )
    threshold_type.create(op.get_bind(), checkfirst=True)

    # Tabela de thresholds
    op.create_table(
        "monitoring_thresholds",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("metric_name", sa.String(100), nullable=False),
        sa.Column("display_name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(50), nullable=False, server_default="general"),
        sa.Column(
            "threshold_type",
            postgresql.ENUM("upper", "lower", "range", name="thresholdtype", create_type=False),
            nullable=False,
            server_default="upper",
        ),
        sa.Column("yellow_threshold", sa.Float(), nullable=False),
        sa.Column("orange_threshold", sa.Float(), nullable=False),
        sa.Column("red_threshold", sa.Float(), nullable=False),
        sa.Column("yellow_lower", sa.Float(), nullable=True),
        sa.Column("orange_lower", sa.Float(), nullable=True),
        sa.Column("red_lower", sa.Float(), nullable=True),
        sa.Column("unit", sa.String(20), nullable=False, server_default=""),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("cooldown_seconds", sa.Integer(), nullable=False, server_default="300"),
        sa.Column("consecutive_breaches", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("notify_channels", postgresql.JSONB(), nullable=True),
        sa.Column("tags", postgresql.JSONB(), nullable=True),
        sa.Column("last_alert_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_value", sa.Float(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("metric_name"),
    )

    op.create_index(
        "ix_monitoring_thresholds_metric_name",
        "monitoring_thresholds",
        ["metric_name"],
    )
    op.create_index(
        "ix_monitoring_thresholds_category",
        "monitoring_thresholds",
        ["category"],
    )

    # Tabela de alertas
    op.create_table(
        "monitoring_alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("metric_name", sa.String(100), nullable=False),
        sa.Column("source", sa.String(100), nullable=False, server_default="system"),
        sa.Column(
            "level",
            postgresql.ENUM("green", "yellow", "orange", "red", name="alertlevel", create_type=False),
            nullable=False,
            server_default="yellow",
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "active", "acknowledged", "resolved", "escalated", "suppressed",
                name="alertstatus",
                create_type=False,
            ),
            nullable=False,
            server_default="active",
        ),
        sa.Column("current_value", sa.Float(), nullable=False),
        sa.Column("threshold_value", sa.Float(), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("details", postgresql.JSONB(), nullable=True),
        sa.Column(
            "triggered_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("acknowledged_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("resolved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("resolution_notes", sa.Text(), nullable=True),
        sa.Column("threshold_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["threshold_id"],
            ["monitoring_thresholds.id"],
            ondelete="SET NULL",
        ),
    )

    op.create_index(
        "ix_monitoring_alerts_metric_name",
        "monitoring_alerts",
        ["metric_name"],
    )
    op.create_index(
        "ix_monitoring_alerts_level",
        "monitoring_alerts",
        ["level"],
    )
    op.create_index(
        "ix_monitoring_alerts_status",
        "monitoring_alerts",
        ["status"],
    )
    op.create_index(
        "ix_monitoring_alerts_triggered_at",
        "monitoring_alerts",
        ["triggered_at"],
    )


def downgrade() -> None:
    op.drop_table("monitoring_alerts")
    op.drop_table("monitoring_thresholds")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS alertlevel")
    op.execute("DROP TYPE IF EXISTS alertstatus")
    op.execute("DROP TYPE IF EXISTS thresholdtype")
