"""Create cashflow tables.

Revision ID: c8f5a3b2d1e0
Revises: d32dc56bebba
Create Date: 2025-12-31 10:00:00.000000

Sprint 24 - Fluxo de Caixa
- bank_accounts: Contas bancárias
- bank_transactions: Transações bancárias
- bank_reconciliations: Conciliações bancárias
- cashflow_entries: Entradas de fluxo de caixa
- cashflow_forecasts: Previsões de fluxo de caixa
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c8f5a3b2d1e0"
down_revision: str | None = "d32dc56bebba"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    # ==================== ENUMS ====================

    # Bank Account Enums
    op.execute(
        """
        CREATE TYPE bankaccounttype AS ENUM (
            'corrente', 'poupanca', 'aplicacao', 'investimento', 'caixa', 'digital'
        )
    """
    )
    op.execute(
        """
        CREATE TYPE bankaccountstatus AS ENUM (
            'ativa', 'inativa', 'suspensa', 'encerrada'
        )
    """
    )
    op.execute(
        """
        CREATE TYPE pixkeytype AS ENUM (
            'cpf', 'cnpj', 'email', 'telefone', 'aleatoria'
        )
    """
    )

    # Bank Transaction Enums
    op.execute(
        """
        CREATE TYPE transactiontype AS ENUM ('credito', 'debito')
    """
    )
    op.execute(
        """
        CREATE TYPE transactioncategory AS ENUM (
            'taxa_condominio', 'taxa_extra', 'multa', 'juros',
            'aluguel', 'reserva', 'outros_recebimentos',
            'manutencao', 'limpeza', 'seguranca', 'energia',
            'agua', 'gas', 'internet', 'telefone', 'salarios',
            'encargos', 'seguros', 'impostos', 'administrativo',
            'juridico', 'outros_pagamentos', 'transferencia', 'ajuste', 'outros'
        )
    """
    )
    op.execute(
        """
        CREATE TYPE transactionstatus AS ENUM (
            'pendente', 'efetivada', 'cancelada', 'estornada'
        )
    """
    )
    op.execute(
        """
        CREATE TYPE reconciliationstatus AS ENUM (
            'pendente', 'conciliado', 'divergente', 'ignorado'
        )
    """
    )
    op.execute(
        """
        CREATE TYPE transactionorigin AS ENUM (
            'manual', 'sistema', 'importacao', 'api', 'boleto', 'pix', 'debito_automatico'
        )
    """
    )

    # Bank Reconciliation Enums
    op.execute(
        """
        CREATE TYPE reconciliationperiodtype AS ENUM (
            'diario', 'semanal', 'quinzenal', 'mensal'
        )
    """
    )
    op.execute(
        """
        CREATE TYPE reconciliationstatus_recon AS ENUM (
            'pendente', 'em_andamento', 'concluida', 'cancelada'
        )
    """
    )

    # CashFlow Entry Enums
    op.execute(
        """
        CREATE TYPE cashflowentrytype AS ENUM ('entrada', 'saida')
    """
    )
    op.execute(
        """
        CREATE TYPE cashflowsourcetype AS ENUM (
            'conta_pagar', 'conta_receber', 'transferencia', 'manual', 'recorrente', 'previsao'
        )
    """
    )
    op.execute(
        """
        CREATE TYPE cashflowentrystatus AS ENUM (
            'previsto', 'confirmado', 'realizado', 'cancelado'
        )
    """
    )
    op.execute(
        """
        CREATE TYPE recurrencefrequency AS ENUM (
            'diaria', 'semanal', 'quinzenal', 'mensal', 'bimestral',
            'trimestral', 'semestral', 'anual'
        )
    """
    )

    # CashFlow Forecast Enums
    op.execute(
        """
        CREATE TYPE forecastperiodtype AS ENUM (
            'diario', 'semanal', 'quinzenal', 'mensal', 'trimestral', 'semestral', 'anual'
        )
    """
    )
    op.execute(
        """
        CREATE TYPE forecaststatus AS ENUM (
            'rascunho', 'ativo', 'revisado', 'encerrado', 'arquivado'
        )
    """
    )
    op.execute(
        """
        CREATE TYPE forecastconfidence AS ENUM (
            'muito_baixa', 'baixa', 'media', 'alta', 'muito_alta'
        )
    """
    )

    # ==================== TABLES ====================

    # bank_accounts
    op.create_table(
        "bank_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column(
            "account_type",
            sa.Enum(
                "corrente",
                "poupanca",
                "aplicacao",
                "investimento",
                "caixa",
                "digital",
                name="bankaccounttype",
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("ativa", "inativa", "suspensa", "encerrada", name="bankaccountstatus"),
            nullable=False,
            server_default="ativa",
        ),
        sa.Column("bank_code", sa.String(10), nullable=True),
        sa.Column("bank_name", sa.String(100), nullable=True),
        sa.Column("agency", sa.String(20), nullable=True),
        sa.Column("agency_digit", sa.String(5), nullable=True),
        sa.Column("account_number", sa.String(20), nullable=True),
        sa.Column("account_digit", sa.String(5), nullable=True),
        sa.Column("initial_balance", sa.Numeric(15, 2), nullable=False, server_default="0"),
        sa.Column("current_balance", sa.Numeric(15, 2), nullable=False, server_default="0"),
        sa.Column("blocked_balance", sa.Numeric(15, 2), nullable=False, server_default="0"),
        sa.Column("available_balance", sa.Numeric(15, 2), nullable=False, server_default="0"),
        sa.Column("overdraft_limit", sa.Numeric(15, 2), nullable=True),
        sa.Column("is_main", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("allows_payments", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("allows_receipts", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("allows_transfers", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("pix_enabled", sa.Boolean, nullable=False, server_default="false"),
        sa.Column(
            "pix_key_type",
            sa.Enum("cpf", "cnpj", "email", "telefone", "aleatoria", name="pixkeytype"),
            nullable=True,
        ),
        sa.Column("pix_key", sa.String(100), nullable=True),
        sa.Column("boleto_enabled", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("boleto_wallet", sa.String(10), nullable=True),
        sa.Column("boleto_agreement", sa.String(50), nullable=True),
        sa.Column("last_reconciled_balance", sa.Numeric(15, 2), nullable=True),
        sa.Column("last_reconciliation_date", sa.Date, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=True, onupdate=sa.func.now()),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_bank_accounts_condominio_id", "bank_accounts", ["condominio_id"])
    op.create_index("ix_bank_accounts_status", "bank_accounts", ["status"])
    op.create_index("ix_bank_accounts_is_main", "bank_accounts", ["is_main"])

    # bank_transactions
    op.create_table(
        "bank_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bank_account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "transaction_type",
            sa.Enum("credito", "debito", name="transactiontype"),
            nullable=False,
        ),
        sa.Column(
            "category",
            sa.Enum(
                "taxa_condominio",
                "taxa_extra",
                "multa",
                "juros",
                "aluguel",
                "reserva",
                "outros_recebimentos",
                "manutencao",
                "limpeza",
                "seguranca",
                "energia",
                "agua",
                "gas",
                "internet",
                "telefone",
                "salarios",
                "encargos",
                "seguros",
                "impostos",
                "administrativo",
                "juridico",
                "outros_pagamentos",
                "transferencia",
                "ajuste",
                "outros",
                name="transactioncategory",
            ),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("balance_before", sa.Numeric(15, 2), nullable=True),
        sa.Column("balance_after", sa.Numeric(15, 2), nullable=True),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("transaction_date", sa.Date, nullable=False),
        sa.Column("competence_date", sa.Date, nullable=True),
        sa.Column("document_number", sa.String(50), nullable=True),
        sa.Column(
            "status",
            sa.Enum("pendente", "efetivada", "cancelada", "estornada", name="transactionstatus"),
            nullable=False,
            server_default="pendente",
        ),
        sa.Column(
            "origin",
            sa.Enum(
                "manual",
                "sistema",
                "importacao",
                "api",
                "boleto",
                "pix",
                "debito_automatico",
                name="transactionorigin",
            ),
            nullable=False,
            server_default="manual",
        ),
        sa.Column(
            "reconciliation_status",
            sa.Enum("pendente", "conciliado", "divergente", "ignorado", name="reconciliationstatus"),
            nullable=False,
            server_default="pendente",
        ),
        sa.Column("reconciliation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reconciled_at", sa.Date, nullable=True),
        sa.Column("statement_reference", sa.String(100), nullable=True),
        sa.Column("payable_payment_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("receivable_payment_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("cashflow_entry_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("is_transfer", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("transfer_to_account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("transfer_from_account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=True, onupdate=sa.func.now()),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["bank_account_id"], ["bank_accounts.id"]),
        sa.ForeignKeyConstraint(["transfer_to_account_id"], ["bank_accounts.id"]),
        sa.ForeignKeyConstraint(["transfer_from_account_id"], ["bank_accounts.id"]),
    )
    op.create_index("ix_bank_transactions_bank_account_id", "bank_transactions", ["bank_account_id"])
    op.create_index("ix_bank_transactions_transaction_date", "bank_transactions", ["transaction_date"])
    op.create_index("ix_bank_transactions_status", "bank_transactions", ["status"])
    op.create_index(
        "ix_bank_transactions_reconciliation_status",
        "bank_transactions",
        ["reconciliation_status"],
    )

    # bank_reconciliations
    op.create_table(
        "bank_reconciliations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bank_account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "period_type",
            sa.Enum("diario", "semanal", "quinzenal", "mensal", name="reconciliationperiodtype"),
            nullable=False,
        ),
        sa.Column("period_start", sa.Date, nullable=False),
        sa.Column("period_end", sa.Date, nullable=False),
        sa.Column("opening_balance", sa.Numeric(15, 2), nullable=False),
        sa.Column("closing_balance", sa.Numeric(15, 2), nullable=True),
        sa.Column("statement_balance", sa.Numeric(15, 2), nullable=True),
        sa.Column("statement_date", sa.Date, nullable=True),
        sa.Column("difference", sa.Numeric(15, 2), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "pendente",
                "em_andamento",
                "concluida",
                "cancelada",
                name="reconciliationstatus_recon",
            ),
            nullable=False,
            server_default="pendente",
        ),
        sa.Column("total_credits", sa.Numeric(15, 2), nullable=False, server_default="0"),
        sa.Column("total_debits", sa.Numeric(15, 2), nullable=False, server_default="0"),
        sa.Column("total_adjustments", sa.Numeric(15, 2), nullable=False, server_default="0"),
        sa.Column("total_system_items", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_statement_items", sa.Integer, nullable=False, server_default="0"),
        sa.Column("items_reconciled", sa.Integer, nullable=False, server_default="0"),
        sa.Column("items_pending", sa.Integer, nullable=False, server_default="0"),
        sa.Column("statement_credits", sa.Numeric(15, 2), nullable=True),
        sa.Column("statement_debits", sa.Numeric(15, 2), nullable=True),
        sa.Column("progress_percentage", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("statement_source", sa.String(50), nullable=True),
        sa.Column("import_filename", sa.String(255), nullable=True),
        sa.Column("started_at", sa.DateTime, nullable=True),
        sa.Column("completed_at", sa.DateTime, nullable=True),
        sa.Column("completed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=True, onupdate=sa.func.now()),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["bank_account_id"], ["bank_accounts.id"]),
    )
    op.create_index("ix_bank_reconciliations_bank_account_id", "bank_reconciliations", ["bank_account_id"])
    op.create_index("ix_bank_reconciliations_period_start", "bank_reconciliations", ["period_start"])
    op.create_index("ix_bank_reconciliations_status", "bank_reconciliations", ["status"])

    # Add FK from bank_transactions to bank_reconciliations
    op.create_foreign_key(
        "fk_bank_transactions_reconciliation",
        "bank_transactions",
        "bank_reconciliations",
        ["reconciliation_id"],
        ["id"],
    )

    # cashflow_entries
    op.create_table(
        "cashflow_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bank_account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "entry_type",
            sa.Enum("entrada", "saida", name="cashflowentrytype"),
            nullable=False,
        ),
        sa.Column(
            "source_type",
            sa.Enum(
                "conta_pagar",
                "conta_receber",
                "transferencia",
                "manual",
                "recorrente",
                "previsao",
                name="cashflowsourcetype",
            ),
            nullable=False,
        ),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("expected_date", sa.Date, nullable=False),
        sa.Column("expected_amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("realized_date", sa.Date, nullable=True),
        sa.Column("realized_amount", sa.Numeric(15, 2), nullable=True),
        sa.Column(
            "status",
            sa.Enum("previsto", "confirmado", "realizado", "cancelado", name="cashflowentrystatus"),
            nullable=False,
            server_default="previsto",
        ),
        sa.Column("payable_account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("receivable_account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("is_recurring", sa.Boolean, nullable=False, server_default="false"),
        sa.Column(
            "recurrence_frequency",
            sa.Enum(
                "diaria",
                "semanal",
                "quinzenal",
                "mensal",
                "bimestral",
                "trimestral",
                "semestral",
                "anual",
                name="recurrencefrequency",
            ),
            nullable=True,
        ),
        sa.Column("recurrence_end_date", sa.Date, nullable=True),
        sa.Column("parent_entry_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("confidence_level", sa.Numeric(5, 2), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=True, onupdate=sa.func.now()),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["bank_account_id"], ["bank_accounts.id"]),
        sa.ForeignKeyConstraint(["parent_entry_id"], ["cashflow_entries.id"]),
    )
    op.create_index("ix_cashflow_entries_condominio_id", "cashflow_entries", ["condominio_id"])
    op.create_index("ix_cashflow_entries_expected_date", "cashflow_entries", ["expected_date"])
    op.create_index("ix_cashflow_entries_status", "cashflow_entries", ["status"])
    op.create_index("ix_cashflow_entries_entry_type", "cashflow_entries", ["entry_type"])

    # Add FK from bank_transactions to cashflow_entries
    op.create_foreign_key(
        "fk_bank_transactions_cashflow_entry",
        "bank_transactions",
        "cashflow_entries",
        ["cashflow_entry_id"],
        ["id"],
    )

    # cashflow_forecasts
    op.create_table(
        "cashflow_forecasts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column(
            "period_type",
            sa.Enum(
                "diario",
                "semanal",
                "quinzenal",
                "mensal",
                "trimestral",
                "semestral",
                "anual",
                name="forecastperiodtype",
            ),
            nullable=False,
        ),
        sa.Column("period_start", sa.Date, nullable=False),
        sa.Column("period_end", sa.Date, nullable=False),
        sa.Column(
            "status",
            sa.Enum("rascunho", "ativo", "revisado", "encerrado", "arquivado", name="forecaststatus"),
            nullable=False,
            server_default="rascunho",
        ),
        sa.Column(
            "confidence",
            sa.Enum("muito_baixa", "baixa", "media", "alta", "muito_alta", name="forecastconfidence"),
            nullable=False,
            server_default="media",
        ),
        sa.Column("expected_inflows", sa.Numeric(15, 2), nullable=False, server_default="0"),
        sa.Column("expected_outflows", sa.Numeric(15, 2), nullable=False, server_default="0"),
        sa.Column("expected_balance", sa.Numeric(15, 2), nullable=False, server_default="0"),
        sa.Column("actual_inflows", sa.Numeric(15, 2), nullable=True),
        sa.Column("actual_outflows", sa.Numeric(15, 2), nullable=True),
        sa.Column("actual_balance", sa.Numeric(15, 2), nullable=True),
        sa.Column("variance_inflows", sa.Numeric(15, 2), nullable=True),
        sa.Column("variance_outflows", sa.Numeric(15, 2), nullable=True),
        sa.Column("variance_balance", sa.Numeric(15, 2), nullable=True),
        sa.Column("variance_percentage", sa.Numeric(5, 2), nullable=True),
        sa.Column("pessimistic_balance", sa.Numeric(15, 2), nullable=True),
        sa.Column("optimistic_balance", sa.Numeric(15, 2), nullable=True),
        sa.Column("is_ai_generated", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("ai_model_version", sa.String(50), nullable=True),
        sa.Column("ai_accuracy_score", sa.Numeric(5, 4), nullable=True),
        sa.Column("risks", postgresql.JSONB, nullable=True),
        sa.Column("opportunities", postgresql.JSONB, nullable=True),
        sa.Column("alerts", postgresql.JSONB, nullable=True),
        sa.Column("assumptions", postgresql.JSONB, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=True, onupdate=sa.func.now()),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cashflow_forecasts_condominio_id", "cashflow_forecasts", ["condominio_id"])
    op.create_index("ix_cashflow_forecasts_period_start", "cashflow_forecasts", ["period_start"])
    op.create_index("ix_cashflow_forecasts_status", "cashflow_forecasts", ["status"])


def downgrade() -> None:
    """Downgrade database schema."""
    # Drop tables
    op.drop_table("cashflow_forecasts")
    op.drop_table("cashflow_entries")
    op.drop_table("bank_reconciliations")
    op.drop_table("bank_transactions")
    op.drop_table("bank_accounts")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS forecastconfidence")
    op.execute("DROP TYPE IF EXISTS forecaststatus")
    op.execute("DROP TYPE IF EXISTS forecastperiodtype")
    op.execute("DROP TYPE IF EXISTS recurrencefrequency")
    op.execute("DROP TYPE IF EXISTS cashflowentrystatus")
    op.execute("DROP TYPE IF EXISTS cashflowsourcetype")
    op.execute("DROP TYPE IF EXISTS cashflowentrytype")
    op.execute("DROP TYPE IF EXISTS reconciliationstatus_recon")
    op.execute("DROP TYPE IF EXISTS reconciliationperiodtype")
    op.execute("DROP TYPE IF EXISTS transactionorigin")
    op.execute("DROP TYPE IF EXISTS reconciliationstatus")
    op.execute("DROP TYPE IF EXISTS transactionstatus")
    op.execute("DROP TYPE IF EXISTS transactioncategory")
    op.execute("DROP TYPE IF EXISTS transactiontype")
    op.execute("DROP TYPE IF EXISTS pixkeytype")
    op.execute("DROP TYPE IF EXISTS bankaccountstatus")
    op.execute("DROP TYPE IF EXISTS bankaccounttype")
