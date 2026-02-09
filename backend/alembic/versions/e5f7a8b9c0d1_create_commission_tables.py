"""create_commission_tables

Revision ID: e5f7a8b9c0d1
Revises: d32dc56bebba
Create Date: 2025-12-30 05:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e5f7a8b9c0d1"
down_revision: str | None = "d32dc56bebba"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Tabela de regras de comissão
    op.create_table(
        "commission_rules",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("commission_type", sa.String(length=20), nullable=False),
        sa.Column("base_value", sa.Float(), nullable=False),
        sa.Column("min_value", sa.Float(), nullable=True),
        sa.Column("max_value", sa.Float(), nullable=True),
        sa.Column("progressive_scale", sa.Text(), nullable=True),
        sa.Column("trigger", sa.String(length=20), nullable=False),
        sa.Column("trigger_delay_days", sa.Integer(), nullable=False),
        sa.Column("applies_to_all", sa.Boolean(), nullable=False),
        sa.Column("product_categories", sa.Text(), nullable=True),
        sa.Column("service_types", sa.Text(), nullable=True),
        sa.Column("min_sale_value", sa.Float(), nullable=True),
        sa.Column("max_sale_value", sa.Float(), nullable=True),
        sa.Column("valid_from", sa.Date(), nullable=False),
        sa.Column("valid_until", sa.Date(), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("created_by_id", sa.UUID(as_uuid=False), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_commission_rules_name"), "commission_rules", ["name"], unique=False)

    # Tabela de associação vendedor-regra
    op.create_table(
        "seller_commission_rules",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("seller_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("rule_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("custom_base_value", sa.Float(), nullable=True),
        sa.Column("valid_from", sa.Date(), nullable=False),
        sa.Column("valid_until", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["seller_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["rule_id"], ["commission_rules.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_seller_commission_rules_seller_id"), "seller_commission_rules", ["seller_id"], unique=False
    )
    op.create_index(op.f("ix_seller_commission_rules_rule_id"), "seller_commission_rules", ["rule_id"], unique=False)

    # Tabela principal de comissões
    op.create_table(
        "commissions",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("reference_number", sa.String(length=50), nullable=False),
        sa.Column("seller_id", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("proposal_id", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("rule_id", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("sale_value", sa.Float(), nullable=False),
        sa.Column("sale_margin", sa.Float(), nullable=False),
        sa.Column("commission_type", sa.String(length=20), nullable=False),
        sa.Column("commission_rate", sa.Float(), nullable=False),
        sa.Column("base_commission", sa.Float(), nullable=False),
        sa.Column("adjustments", sa.Float(), nullable=False),
        sa.Column("final_commission", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("trigger", sa.String(length=20), nullable=False),
        sa.Column("trigger_date", sa.Date(), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("paid_date", sa.Date(), nullable=True),
        sa.Column("period_start", sa.Date(), nullable=True),
        sa.Column("period_end", sa.Date(), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("created_by_id", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("approved_by_id", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["seller_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["proposal_id"], ["proposals.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["rule_id"], ["commission_rules.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["approved_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_commissions_reference_number"), "commissions", ["reference_number"], unique=True)
    op.create_index(op.f("ix_commissions_seller_id"), "commissions", ["seller_id"], unique=False)
    op.create_index(op.f("ix_commissions_proposal_id"), "commissions", ["proposal_id"], unique=False)
    op.create_index(op.f("ix_commissions_status"), "commissions", ["status"], unique=False)

    # Tabela de pagamentos de comissão
    op.create_table(
        "commission_payments",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("commission_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("payment_method", sa.String(length=20), nullable=False),
        sa.Column("payment_date", sa.Date(), nullable=False),
        sa.Column("payment_reference", sa.String(length=100), nullable=True),
        sa.Column("bank_account", sa.String(length=50), nullable=True),
        sa.Column("transaction_id", sa.String(length=100), nullable=True),
        sa.Column("is_confirmed", sa.Boolean(), nullable=False),
        sa.Column("confirmed_at", sa.DateTime(), nullable=True),
        sa.Column("confirmed_by_id", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("created_by_id", sa.UUID(as_uuid=False), nullable=True),
        sa.ForeignKeyConstraint(["commission_id"], ["commissions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["confirmed_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_commission_payments_commission_id"), "commission_payments", ["commission_id"], unique=False
    )

    # Tabela de resumo mensal de comissões
    op.create_table(
        "commission_summaries",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("seller_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("total_sales", sa.Float(), nullable=False),
        sa.Column("total_sales_count", sa.Integer(), nullable=False),
        sa.Column("total_commissions", sa.Float(), nullable=False),
        sa.Column("total_paid", sa.Float(), nullable=False),
        sa.Column("total_pending", sa.Float(), nullable=False),
        sa.Column("sales_target", sa.Float(), nullable=True),
        sa.Column("target_percentage", sa.Float(), nullable=True),
        sa.Column("bonus_earned", sa.Float(), nullable=False),
        sa.Column("is_closed", sa.Boolean(), nullable=False),
        sa.Column("closed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["seller_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_commission_summaries_seller_id"), "commission_summaries", ["seller_id"], unique=False)
    op.create_index(
        "ix_commission_summaries_period", "commission_summaries", ["seller_id", "year", "month"], unique=True
    )


def downgrade() -> None:
    op.drop_index("ix_commission_summaries_period", table_name="commission_summaries")
    op.drop_index(op.f("ix_commission_summaries_seller_id"), table_name="commission_summaries")
    op.drop_table("commission_summaries")

    op.drop_index(op.f("ix_commission_payments_commission_id"), table_name="commission_payments")
    op.drop_table("commission_payments")

    op.drop_index(op.f("ix_commissions_status"), table_name="commissions")
    op.drop_index(op.f("ix_commissions_proposal_id"), table_name="commissions")
    op.drop_index(op.f("ix_commissions_seller_id"), table_name="commissions")
    op.drop_index(op.f("ix_commissions_reference_number"), table_name="commissions")
    op.drop_table("commissions")

    op.drop_index(op.f("ix_seller_commission_rules_rule_id"), table_name="seller_commission_rules")
    op.drop_index(op.f("ix_seller_commission_rules_seller_id"), table_name="seller_commission_rules")
    op.drop_table("seller_commission_rules")

    op.drop_index(op.f("ix_commission_rules_name"), table_name="commission_rules")
    op.drop_table("commission_rules")
