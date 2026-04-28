"""D5.4: adiciona certidoes_atualizadas + alertas_disparados em ged_coleta_logs

Revision ID: sprint85_d5_4_coleta_logs_certidoes
Revises: sprint85_d4_coleta_automatica
Create Date: 2026-04-28
"""

import sqlalchemy as sa

from alembic import op

revision = "sprint85_d5_4_certidoes"
down_revision = "sprint85_d4_coleta_automatica"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ged_coleta_logs",
        sa.Column("certidoes_atualizadas", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "ged_coleta_logs",
        sa.Column("alertas_disparados", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("ged_coleta_logs", "alertas_disparados")
    op.drop_column("ged_coleta_logs", "certidoes_atualizadas")
