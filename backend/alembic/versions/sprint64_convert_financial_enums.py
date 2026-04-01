"""Convert enum columns to VARCHAR in bank_accounts, bank_transactions, bank_reconciliations, fin_accounting_*.

Revision ID: sprint64_convert_financial_enums
Revises: sprint63_convert_warehouse_enums
Create Date: 2026-03-09

"""

from alembic import op

revision = "sprint64_convert_financial_enums"
down_revision = "sprint63_convert_warehouse_enums"
branch_labels = None
depends_on = None


def _alter_if_enum(table: str, column: str, length: int = 30) -> None:
    """Converts column to VARCHAR only if it is currently an enum type."""
    op.execute(f"""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = '{table}'
                AND column_name = '{column}'
                AND udt_name NOT IN ('varchar', 'text', 'character varying', 'bpchar')
            ) THEN
                ALTER TABLE {table} ALTER COLUMN {column} TYPE VARCHAR({length}) USING {column}::text;
            END IF;
        END$$
    """)


def upgrade() -> None:
    # bank_accounts
    _alter_if_enum("bank_accounts", "account_type", 30)
    _alter_if_enum("bank_accounts", "status", 30)
    _alter_if_enum("bank_accounts", "pix_key_type", 30)

    # bank_reconciliations
    _alter_if_enum("bank_reconciliations", "period_type", 30)
    _alter_if_enum("bank_reconciliations", "status", 30)

    # bank_transactions
    _alter_if_enum("bank_transactions", "transaction_type", 30)
    _alter_if_enum("bank_transactions", "status", 30)
    _alter_if_enum("bank_transactions", "reconciliation_status", 30)
    _alter_if_enum("bank_transactions", "category", 50)
    _alter_if_enum("bank_transactions", "origin", 30)

    # fin_accounting_accounts
    _alter_if_enum("fin_accounting_accounts", "account_type", 30)
    _alter_if_enum("fin_accounting_accounts", "nature", 30)
    _alter_if_enum("fin_accounting_accounts", "classification", 30)
    _alter_if_enum("fin_accounting_accounts", "status", 30)
    _alter_if_enum("fin_accounting_accounts", "sped_nature", 30)

    # fin_accounting_periods
    _alter_if_enum("fin_accounting_periods", "period_type", 30)
    _alter_if_enum("fin_accounting_periods", "status", 30)
    _alter_if_enum("fin_accounting_periods", "closing_type", 30)


def downgrade() -> None:
    pass
