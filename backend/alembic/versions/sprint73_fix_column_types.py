"""Fix column type mismatches in bidding tables.

- bidding_analyses.valor_estimado: VARCHAR(50) -> DECIMAL(15,2)
- bidding_opportunities.orgao_cnpj: VARCHAR(14) -> VARCHAR(18)
- bidding_assessments: ADD raw_assessment JSONB

Revision ID: sprint73_fix_column_types
Revises: sprint72_fix_bidding_schema
Create Date: 2026-03-12

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "sprint73_fix_column_types"
down_revision = "sprint72_fix_bidding_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. bidding_analyses.valor_estimado: VARCHAR(50) -> DECIMAL(15,2)
    op.alter_column(
        "bidding_analyses",
        "valor_estimado",
        type_=sa.Numeric(15, 2),
        postgresql_using="CASE WHEN valor_estimado ~ '^[0-9.]+$' THEN valor_estimado::numeric(15,2) ELSE NULL END",
    )

    # 2. bidding_opportunities.orgao_cnpj: VARCHAR(14) -> VARCHAR(18)
    op.alter_column(
        "bidding_opportunities",
        "orgao_cnpj",
        type_=sa.String(18),
    )

    # 3. bidding_assessments: ADD raw_assessment JSONB
    op.add_column(
        "bidding_assessments",
        sa.Column("raw_assessment", postgresql.JSONB, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("bidding_assessments", "raw_assessment")
    op.alter_column("bidding_opportunities", "orgao_cnpj", type_=sa.String(14))
    op.alter_column("bidding_analyses", "valor_estimado", type_=sa.String(50))
