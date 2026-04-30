"""D6 addendum: matched_payroll_id, cliente_id, valor_bruto/descontos

Revision ID: sprint86_d6_inter_addendum
Revises: sprint86_d6_inter_tables
Create Date: 2026-04-30
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "sprint86_d6_inter_addendum"
down_revision = "sprint86_d6_inter_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Renomear matched_conciliacao_id → matched_payroll_id (spec D6.1.1)
    op.alter_column(
        "inter_transactions",
        "matched_conciliacao_id",
        new_column_name="matched_payroll_id",
    )

    # Adicionar cliente_id em inter_cobrancas (spec D6.3.1)
    op.add_column(
        "inter_cobrancas",
        sa.Column("cliente_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_inter_cobrancas_cliente", "inter_cobrancas", ["cliente_id"])

    # Adicionar valor_bruto e valor_descontos em inter_conciliacao_folha (spec D6.2.1)
    op.add_column(
        "inter_conciliacao_folha",
        sa.Column("valor_bruto", sa.Numeric(15, 2), nullable=True),
    )
    op.add_column(
        "inter_conciliacao_folha",
        sa.Column("valor_descontos", sa.Numeric(15, 2), nullable=True),
    )

    # Garantir UNIQUE(employee_id, competencia) em inter_conciliacao_folha
    try:
        op.create_unique_constraint(
            "uq_inter_conciliacao_employee_competencia",
            "inter_conciliacao_folha",
            ["employee_id", "competencia"],
        )
    except Exception:
        pass  # Pode já existir se aplicado manualmente


def downgrade() -> None:
    op.drop_constraint("uq_inter_conciliacao_employee_competencia", "inter_conciliacao_folha", type_="unique")
    op.drop_column("inter_conciliacao_folha", "valor_descontos")
    op.drop_column("inter_conciliacao_folha", "valor_bruto")
    op.drop_index("ix_inter_cobrancas_cliente", "inter_cobrancas")
    op.drop_column("inter_cobrancas", "cliente_id")
    op.alter_column(
        "inter_transactions",
        "matched_payroll_id",
        new_column_name="matched_conciliacao_id",
    )
