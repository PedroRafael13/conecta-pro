"""sprint80: add condominio_id to payable_installments

Revision ID: sprint80_payable_inst_cond
Revises: sprint79_justification_employee_uuid
Create Date: 2026-04-01

Causa: PayableInstallment model tem coluna condominio_id mas tabela não tinha.
SQLAlchemy incluía a coluna no SELECT causando UndefinedColumnError 500.
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "sprint80_payable_inst_cond"
down_revision = "sprint79_justification_employee_uuid"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "payable_installments",
        sa.Column(
            "condominio_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("condominios.id"),
            nullable=True,
            index=True,
        ),
    )

    # Backfill a partir de payable_accounts
    op.execute("""
        UPDATE payable_installments pi
        SET condominio_id = pa.condominio_id
        FROM payable_accounts pa
        WHERE pi.payable_account_id = pa.id
        AND pi.condominio_id IS NULL
    """)

    op.create_index(
        "ix_payable_installments_condominio_id",
        "payable_installments",
        ["condominio_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_payable_installments_condominio_id", "payable_installments")
    op.drop_column("payable_installments", "condominio_id")
