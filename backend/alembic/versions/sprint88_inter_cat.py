"""inter_transaction_categorias

Revision ID: sprint88_inter_cat
Revises: sprint87_d7_payments
Create Date: 2026-05-05
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "sprint88_inter_cat"
down_revision = "sprint87_d7_payments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "inter_transaction_categorias",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
        ),
        sa.Column(
            "transaction_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("inter_transactions.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("categoria", sa.String(50), nullable=False),
        sa.Column("document_type", sa.String(50), nullable=True),
        sa.Column("observacao", sa.Text(), nullable=True),
        sa.Column("incluir_no_kit", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("sugerido_por_ia", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("confianca_sugestao", sa.Float(), nullable=True),
        sa.Column(
            "categorizado_por",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "categorizado_em",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_inter_cat_transaction",
        "inter_transaction_categorias",
        ["transaction_id"],
    )
    op.create_index(
        "ix_inter_cat_categoria",
        "inter_transaction_categorias",
        ["categoria"],
    )
    op.create_index(
        "ix_inter_cat_incluir_kit",
        "inter_transaction_categorias",
        ["incluir_no_kit"],
    )


def downgrade() -> None:
    op.drop_table("inter_transaction_categorias")
