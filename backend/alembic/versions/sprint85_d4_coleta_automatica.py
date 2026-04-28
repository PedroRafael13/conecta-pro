"""D4: Coleta Automatica config + logs

Revision ID: sprint85_d4_coleta_automatica
Revises: 5ec309bea85c
Create Date: 2026-04-28

Tabelas:
  - ged_coleta_config: singleton (id=1) com enabled, cron_expr, timezone, last_run, last_status
  - ged_coleta_logs: historico de execucoes com stats por run
"""

import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

from alembic import op

revision = "sprint85_d4_coleta_automatica"
down_revision = "5ec309bea85c"  # pragma: allowlist secret
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ged_coleta_config",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("cron_expr", sa.String(50), nullable=False, server_default="0 6 21 * *"),
        sa.Column("timezone", sa.String(50), nullable=False, server_default="America/Manaus"),
        sa.Column("last_run", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_status", sa.String(20), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("updated_by", sa.String(255), nullable=True),
        sa.CheckConstraint("id = 1", name="ged_coleta_config_singleton"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.execute(
        """
        INSERT INTO ged_coleta_config (id, enabled, cron_expr, timezone)
        VALUES (1, TRUE, '0 6 21 * *', 'America/Manaus')
        """
    )

    op.create_table(
        "ged_coleta_logs",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            nullable=False,
            default=uuid.uuid4,
        ),
        sa.Column(
            "run_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("run_type", sa.String(10), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("sync_novos", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("kits_assembled", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("onvio_matched", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("erros", JSONB(), nullable=True),
        sa.Column("triggered_by", sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_ged_coleta_logs_run_at", "ged_coleta_logs", ["run_at"])


def downgrade() -> None:
    op.drop_index("ix_ged_coleta_logs_run_at", table_name="ged_coleta_logs")
    op.drop_table("ged_coleta_logs")
    op.drop_table("ged_coleta_config")
