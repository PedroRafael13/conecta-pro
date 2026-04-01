"""sprint80b: sync financial model columns missing from DB

Revision ID: sprint80b_fin_cols_sync
Revises: sprint80_payable_inst_cond
Create Date: 2026-04-01

Causa: Múltiplas tabelas financeiras tinham colunas definidas no SQLAlchemy model
mas ausentes no banco real, causando UndefinedColumnError 500 em:
  - financial/cashflow/projection
  - financial/bank-transactions
  - financial/bank-reconciliations

Tabelas corrigidas:
  - payable_installments: total_installments, discount_value, interest_value, etc.
  - bank_transactions: posting_date, value_date, external_id, counterparty_*, etc.
  - bank_reconciliations: condominio_id, system_*, bank_*, reconciled_count, etc.
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "sprint80b_fin_cols_sync"
down_revision = "sprint80_payable_inst_cond"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # === payable_installments ===
    op.add_column(
        "payable_installments",
        sa.Column("total_installments", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column(
        "payable_installments",
        sa.Column("discount_value", sa.Numeric(15, 2), nullable=True, server_default="0"),
    )
    op.add_column(
        "payable_installments",
        sa.Column("interest_value", sa.Numeric(15, 2), nullable=True, server_default="0"),
    )
    op.add_column(
        "payable_installments",
        sa.Column("penalty_value", sa.Numeric(15, 2), nullable=True, server_default="0"),
    )
    op.add_column(
        "payable_installments",
        sa.Column("addition_value", sa.Numeric(15, 2), nullable=True, server_default="0"),
    )
    op.add_column(
        "payable_installments",
        sa.Column("paid_value", sa.Numeric(15, 2), nullable=True, server_default="0"),
    )
    op.add_column(
        "payable_installments",
        sa.Column("interest_rate", sa.Numeric(8, 4), nullable=True, server_default="0"),
    )
    op.add_column(
        "payable_installments",
        sa.Column("payment_method_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "payable_installments",
        sa.Column("digitable_line", sa.String(100), nullable=True),
    )
    op.add_column(
        "payable_installments",
        sa.Column("boleto_url", sa.String(500), nullable=True),
    )
    op.add_column(
        "payable_installments",
        sa.Column("scheduled_payment_date", sa.Date(), nullable=True),
    )
    op.add_column(
        "payable_installments",
        sa.Column("scheduled_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "payable_installments",
        sa.Column("renegotiated_from_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # === bank_transactions ===
    op.add_column("bank_transactions", sa.Column("memo", sa.Text(), nullable=True))
    op.add_column("bank_transactions", sa.Column("posting_date", sa.Date(), nullable=True))
    op.add_column("bank_transactions", sa.Column("value_date", sa.Date(), nullable=True))
    op.add_column("bank_transactions", sa.Column("external_id", sa.String(100), nullable=True))
    op.add_column("bank_transactions", sa.Column("authentication", sa.String(100), nullable=True))
    op.add_column("bank_transactions", sa.Column("reference", sa.String(100), nullable=True))
    op.add_column("bank_transactions", sa.Column("source_type", sa.String(30), nullable=True))
    op.add_column(
        "bank_transactions",
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "bank_transactions",
        sa.Column("transfer_pair_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "bank_transactions",
        sa.Column("transfer_account_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "bank_transactions",
        sa.Column("reconciled_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column("bank_transactions", sa.Column("reconciliation_note", sa.Text(), nullable=True))
    op.add_column(
        "bank_transactions",
        sa.Column("counterparty_name", sa.String(150), nullable=True),
    )
    op.add_column(
        "bank_transactions",
        sa.Column("counterparty_document", sa.String(20), nullable=True),
    )
    op.add_column(
        "bank_transactions",
        sa.Column("counterparty_bank", sa.String(100), nullable=True),
    )
    op.add_column(
        "bank_transactions",
        sa.Column("counterparty_agency", sa.String(10), nullable=True),
    )
    op.add_column(
        "bank_transactions",
        sa.Column("counterparty_account", sa.String(20), nullable=True),
    )
    op.add_column("bank_transactions", sa.Column("pix_key", sa.String(100), nullable=True))
    op.add_column("bank_transactions", sa.Column("pix_end_to_end", sa.String(50), nullable=True))
    op.add_column("bank_transactions", sa.Column("barcode", sa.String(50), nullable=True))
    op.add_column("bank_transactions", sa.Column("boleto_number", sa.String(20), nullable=True))
    op.add_column("bank_transactions", sa.Column("imported_from", sa.String(50), nullable=True))
    op.add_column(
        "bank_transactions",
        sa.Column("import_batch_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "bank_transactions",
        sa.Column("raw_data", postgresql.JSONB(), nullable=True, server_default="{}"),
    )
    op.add_column(
        "bank_transactions",
        sa.Column("is_reversal", sa.Boolean(), nullable=True, server_default="false"),
    )
    op.add_column(
        "bank_transactions",
        sa.Column("reversed_transaction_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column("bank_transactions", sa.Column("reversal_reason", sa.Text(), nullable=True))
    op.add_column(
        "bank_transactions",
        sa.Column("attachments", postgresql.JSONB(), nullable=True, server_default="[]"),
    )
    op.add_column(
        "bank_transactions",
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # === bank_reconciliations ===
    op.add_column(
        "bank_reconciliations",
        sa.Column(
            "condominio_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("condominios.id"),
            nullable=True,
        ),
    )
    op.add_column("bank_reconciliations", sa.Column("reference", sa.String(50), nullable=True))
    op.add_column("bank_reconciliations", sa.Column("description", sa.Text(), nullable=True))
    op.add_column(
        "bank_reconciliations",
        sa.Column("system_opening_balance", sa.Numeric(15, 2), nullable=True, server_default="0"),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("system_closing_balance", sa.Numeric(15, 2), nullable=True),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("system_credits", sa.Numeric(15, 2), nullable=True, server_default="0"),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("system_debits", sa.Numeric(15, 2), nullable=True, server_default="0"),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("bank_opening_balance", sa.Numeric(15, 2), nullable=True),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("bank_closing_balance", sa.Numeric(15, 2), nullable=True),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("bank_credits", sa.Numeric(15, 2), nullable=True, server_default="0"),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("bank_debits", sa.Numeric(15, 2), nullable=True, server_default="0"),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("opening_difference", sa.Numeric(15, 2), nullable=True, server_default="0"),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("closing_difference", sa.Numeric(15, 2), nullable=True, server_default="0"),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("credits_difference", sa.Numeric(15, 2), nullable=True, server_default="0"),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("debits_difference", sa.Numeric(15, 2), nullable=True, server_default="0"),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("total_system_transactions", sa.Integer(), nullable=True, server_default="0"),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("total_bank_transactions", sa.Integer(), nullable=True, server_default="0"),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("reconciled_count", sa.Integer(), nullable=True, server_default="0"),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("pending_system_count", sa.Integer(), nullable=True, server_default="0"),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("pending_bank_count", sa.Integer(), nullable=True, server_default="0"),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("divergent_count", sa.Integer(), nullable=True, server_default="0"),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column(
            "reconciliation_progress",
            sa.Numeric(5, 2),
            nullable=True,
            server_default="0",
        ),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("auto_reconciled_count", sa.Integer(), nullable=True, server_default="0"),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("manual_reconciled_count", sa.Integer(), nullable=True, server_default="0"),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("statement_imported", sa.Boolean(), nullable=True, server_default="false"),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("statement_file_name", sa.String(255), nullable=True),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("statement_file_path", sa.String(500), nullable=True),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("statement_format", sa.String(20), nullable=True),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("statement_imported_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("statement_imported_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("started_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("reviewed_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("adjustments", postgresql.JSONB(), nullable=True, server_default="[]"),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("pending_items", postgresql.JSONB(), nullable=True, server_default="[]"),
    )
    op.add_column(
        "bank_reconciliations",
        sa.Column("divergent_items", postgresql.JSONB(), nullable=True, server_default="[]"),
    )
    op.add_column("bank_reconciliations", sa.Column("review_notes", sa.Text(), nullable=True))
    op.add_column(
        "bank_reconciliations",
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Register alembic version
    op.execute("INSERT INTO alembic_version (version_num) VALUES ('sprint80b_fin_cols_sync') ON CONFLICT DO NOTHING")


def downgrade() -> None:
    # payable_installments
    for col in [
        "total_installments",
        "discount_value",
        "interest_value",
        "penalty_value",
        "addition_value",
        "paid_value",
        "interest_rate",
        "payment_method_id",
        "digitable_line",
        "boleto_url",
        "scheduled_payment_date",
        "scheduled_by",
        "renegotiated_from_id",
    ]:
        op.drop_column("payable_installments", col)

    # bank_transactions
    for col in [
        "memo",
        "posting_date",
        "value_date",
        "external_id",
        "authentication",
        "reference",
        "source_type",
        "source_id",
        "transfer_pair_id",
        "transfer_account_id",
        "reconciled_by",
        "reconciliation_note",
        "counterparty_name",
        "counterparty_document",
        "counterparty_bank",
        "counterparty_agency",
        "counterparty_account",
        "pix_key",
        "pix_end_to_end",
        "barcode",
        "boleto_number",
        "imported_from",
        "import_batch_id",
        "raw_data",
        "is_reversal",
        "reversed_transaction_id",
        "reversal_reason",
        "attachments",
        "created_by",
    ]:
        op.drop_column("bank_transactions", col)

    # bank_reconciliations
    for col in [
        "condominio_id",
        "reference",
        "description",
        "system_opening_balance",
        "system_closing_balance",
        "system_credits",
        "system_debits",
        "bank_opening_balance",
        "bank_closing_balance",
        "bank_credits",
        "bank_debits",
        "opening_difference",
        "closing_difference",
        "credits_difference",
        "debits_difference",
        "total_system_transactions",
        "total_bank_transactions",
        "reconciled_count",
        "pending_system_count",
        "pending_bank_count",
        "divergent_count",
        "reconciliation_progress",
        "auto_reconciled_count",
        "manual_reconciled_count",
        "statement_imported",
        "statement_file_name",
        "statement_file_path",
        "statement_format",
        "statement_imported_at",
        "statement_imported_by",
        "started_by",
        "reviewed_by",
        "reviewed_at",
        "adjustments",
        "pending_items",
        "divergent_items",
        "review_notes",
        "created_by",
    ]:
        op.drop_column("bank_reconciliations", col)
