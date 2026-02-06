"""Sprint 36: Fix Float columns to Numeric for monetary values.

Revision ID: sprint36_fix_float_numeric
Revises: sprint35_config
Create Date: 2026-01-05

REGRA 6 - DECIMAL PARA DINHEIRO:
Corrige violações de Float para valores monetários em todo o sistema CRM.
Converte colunas Float para Numeric(15, 2) para precisão financeira.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

# revision identifiers, used by Alembic (pylint: disable=invalid-name).
revision: str = "sprint36_fix_float_numeric"
down_revision: Union[str, None] = "sprint35_config"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None  # pylint: disable=invalid-name


def table_exists(table_name: str) -> bool:
    """Verifica se uma tabela existe no banco."""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    """Converter colunas Float para Numeric em tabelas CRM.

    Tabelas afetadas:
    - crm_leads: expected_value
    - crm_opportunities: value
    - crm_proposals: subtotal, discount_value, taxes, total
    - crm_proposal_items: quantity, unit_price, discount_percent, total
    - crm_commission_rules: base_value, min_value, max_value, min_sale_value, max_sale_value
    - crm_commissions: sale_value, sale_margin, commission_rate, base_commission,
                       adjustments, final_commission
    - crm_commission_summaries: total_sales, total_commissions, total_paid,
                                total_pending, sales_target, bonus_earned
    - crm_commission_payments: amount
    """

    # ==================== CRM_LEADS ====================
    if table_exists("crm_leads"):
        op.alter_column(
            "crm_leads",
            "expected_value",
            type_=sa.Numeric(15, 2),
            existing_type=sa.Float(),
            postgresql_using="expected_value::numeric(15,2)",
        )

    # ==================== CRM_OPPORTUNITIES ====================
    if table_exists("crm_opportunities"):
        op.alter_column(
            "crm_opportunities",
            "value",
            type_=sa.Numeric(15, 2),
            existing_type=sa.Float(),
            postgresql_using="value::numeric(15,2)",
        )

    # ==================== CRM_PROPOSALS ====================
    if table_exists("crm_proposals"):
        for column in ["subtotal", "discount_value", "taxes", "total"]:
            op.alter_column(
                "crm_proposals",
                column,
                type_=sa.Numeric(15, 2),
                existing_type=sa.Float(),
                postgresql_using=f"{column}::numeric(15,2)",
            )

    # ==================== CRM_PROPOSAL_ITEMS ====================
    if table_exists("crm_proposal_items"):
        op.alter_column(
            "crm_proposal_items",
            "quantity",
            type_=sa.Numeric(10, 4),
            existing_type=sa.Float(),
            postgresql_using="quantity::numeric(10,4)",
        )

        op.alter_column(
            "crm_proposal_items",
            "unit_price",
            type_=sa.Numeric(15, 2),
            existing_type=sa.Float(),
            postgresql_using="unit_price::numeric(15,2)",
        )

        op.alter_column(
            "crm_proposal_items",
            "discount_percent",
            type_=sa.Numeric(5, 2),
            existing_type=sa.Float(),
            postgresql_using="discount_percent::numeric(5,2)",
        )

        op.alter_column(
            "crm_proposal_items",
            "total",
            type_=sa.Numeric(15, 2),
            existing_type=sa.Float(),
            postgresql_using="total::numeric(15,2)",
        )

    # ==================== CRM_COMMISSION_RULES ====================
    if table_exists("crm_commission_rules"):
        for column in ["base_value", "min_value", "max_value", "min_sale_value", "max_sale_value"]:
            op.alter_column(
                "crm_commission_rules",
                column,
                type_=sa.Numeric(15, 2),
                existing_type=sa.Float(),
                postgresql_using=f"{column}::numeric(15,2)",
            )

    # ==================== CRM_COMMISSIONS ====================
    if table_exists("crm_commissions"):
        for column in [
            "sale_value",
            "sale_margin",
            "commission_rate",
            "base_commission",
            "adjustments",
            "final_commission",
        ]:
            op.alter_column(
                "crm_commissions",
                column,
                type_=sa.Numeric(15, 2),
                existing_type=sa.Float(),
                postgresql_using=f"{column}::numeric(15,2)",
            )

    # ==================== CRM_COMMISSION_SUMMARIES ====================
    if table_exists("crm_commission_summaries"):
        for column in [
            "total_sales",
            "total_commissions",
            "total_paid",
            "total_pending",
            "sales_target",
            "bonus_earned",
        ]:
            op.alter_column(
                "crm_commission_summaries",
                column,
                type_=sa.Numeric(15, 2),
                existing_type=sa.Float(),
                postgresql_using=f"{column}::numeric(15,2)",
            )

    # ==================== CRM_COMMISSION_PAYMENTS ====================
    if table_exists("crm_commission_payments"):
        op.alter_column(
            "crm_commission_payments",
            "amount",
            type_=sa.Numeric(15, 2),
            existing_type=sa.Float(),
            postgresql_using="amount::numeric(15,2)",
        )


def downgrade() -> None:
    """Reverter colunas Numeric para Float.

    AVISO: Esta operação pode causar perda de precisão!
    """

    # CRM_LEADS
    if table_exists("crm_leads"):
        op.alter_column(
            "crm_leads",
            "expected_value",
            type_=sa.Float(),
            existing_type=sa.Numeric(15, 2),
            postgresql_using="expected_value::double precision",
        )

    # CRM_OPPORTUNITIES
    if table_exists("crm_opportunities"):
        op.alter_column(
            "crm_opportunities",
            "value",
            type_=sa.Float(),
            existing_type=sa.Numeric(15, 2),
            postgresql_using="value::double precision",
        )

    # CRM_PROPOSALS
    if table_exists("crm_proposals"):
        for column in ["subtotal", "discount_value", "taxes", "total"]:
            op.alter_column(
                "crm_proposals",
                column,
                type_=sa.Float(),
                existing_type=sa.Numeric(15, 2),
                postgresql_using=f"{column}::double precision",
            )

    # CRM_PROPOSAL_ITEMS
    if table_exists("crm_proposal_items"):
        for column in ["quantity", "unit_price", "discount_percent", "total"]:
            op.alter_column(
                "crm_proposal_items",
                column,
                type_=sa.Float(),
                existing_type=(
                    sa.Numeric(10, 4)
                    if column == "quantity"
                    else (sa.Numeric(5, 2) if column == "discount_percent" else sa.Numeric(15, 2))
                ),
                postgresql_using=f"{column}::double precision",
            )

    # CRM_COMMISSION_RULES
    if table_exists("crm_commission_rules"):
        for column in ["base_value", "min_value", "max_value", "min_sale_value", "max_sale_value"]:
            op.alter_column(
                "crm_commission_rules",
                column,
                type_=sa.Float(),
                existing_type=sa.Numeric(15, 2),
                postgresql_using=f"{column}::double precision",
            )

    # CRM_COMMISSIONS
    if table_exists("crm_commissions"):
        for column in [
            "sale_value",
            "sale_margin",
            "commission_rate",
            "base_commission",
            "adjustments",
            "final_commission",
        ]:
            op.alter_column(
                "crm_commissions",
                column,
                type_=sa.Float(),
                existing_type=sa.Numeric(15, 2),
                postgresql_using=f"{column}::double precision",
            )

    # CRM_COMMISSION_SUMMARIES
    if table_exists("crm_commission_summaries"):
        for column in [
            "total_sales",
            "total_commissions",
            "total_paid",
            "total_pending",
            "sales_target",
            "bonus_earned",
        ]:
            op.alter_column(
                "crm_commission_summaries",
                column,
                type_=sa.Float(),
                existing_type=sa.Numeric(15, 2),
                postgresql_using=f"{column}::double precision",
            )

    # CRM_COMMISSION_PAYMENTS
    if table_exists("crm_commission_payments"):
        op.alter_column(
            "crm_commission_payments",
            "amount",
            type_=sa.Float(),
            existing_type=sa.Numeric(15, 2),
            postgresql_using="amount::double precision",
        )
