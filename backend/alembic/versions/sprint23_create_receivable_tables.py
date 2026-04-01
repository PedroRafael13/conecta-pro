"""Sprint 23: Cria tabelas de Contas a Receber.

Revision ID: sprint23_receivable
Revises: sprint22_payable
Create Date: 2024-12-31

Tabelas criadas:
- receivable_categories: Categorias de receitas
- customers: Clientes/Devedores
- receivable_accounts: Contas a receber
- receivable_installments: Parcelas
- receivable_payments: Recebimentos
- billing_rules: Regras de cobranca automatica
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers
revision = "sprint23_receivable"
down_revision = "sprint22_payable"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Cria tabelas de Contas a Receber."""

    # =========================================================================
    # Tabela: receivable_categories
    # Categorias de receitas (taxa condominial, reservas, multas, etc.)
    # =========================================================================
    op.create_table(
        "receivable_categories",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "condominio_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            index=True,
        ),
        # Hierarquia
        sa.Column(
            "parent_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        # Identificacao
        sa.Column("code", sa.String(20), nullable=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        # Tipo
        sa.Column(
            "category_type",
            sa.String(30),
            nullable=False,
            server_default="taxa_condominial",
        ),
        # Configuracao de juros e multa
        sa.Column(
            "default_interest_rate",
            sa.Numeric(5, 2),
            server_default="1.00",
        ),
        sa.Column(
            "default_penalty_rate",
            sa.Numeric(5, 2),
            server_default="2.00",
        ),
        sa.Column("grace_days", sa.Integer, server_default="0"),
        # Contabilidade
        sa.Column("accounting_code", sa.String(20), nullable=True),
        sa.Column("cost_center", sa.String(50), nullable=True),
        # Status
        sa.Column("is_active", sa.Boolean, server_default="true"),
        # Auditoria
        sa.Column("created_at", sa.DateTime, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime, server_default=sa.text("now()")),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        # FK
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["receivable_categories.id"],
            name="fk_receivable_categories_parent",
        ),
    )

    # Indices
    op.create_index(
        "ix_receivable_categories_parent",
        "receivable_categories",
        ["parent_id"],
    )
    op.create_index(
        "ix_receivable_categories_code",
        "receivable_categories",
        ["condominio_id", "code"],
        unique=True,
        postgresql_where=sa.text("code IS NOT NULL"),
    )

    # =========================================================================
    # Tabela: customers
    # Clientes/Devedores (moradores, proprietarios, etc.)
    # =========================================================================
    op.create_table(
        "customers",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "condominio_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            index=True,
        ),
        # Vinculos
        sa.Column(
            "morador_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
            index=True,
        ),
        sa.Column(
            "unidade_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
            index=True,
        ),
        # Identificacao
        sa.Column("cpf_cnpj", sa.String(18), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        # Tipo e status
        sa.Column(
            "customer_type",
            sa.String(20),
            nullable=False,
            server_default="morador",
        ),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="ativo",
        ),
        # Contato
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("mobile", sa.String(20), nullable=True),
        # Endereco de cobranca
        sa.Column("billing_address_street", sa.String(255), nullable=True),
        sa.Column("billing_address_number", sa.String(20), nullable=True),
        sa.Column("billing_address_complement", sa.String(100), nullable=True),
        sa.Column("billing_address_neighborhood", sa.String(100), nullable=True),
        sa.Column("billing_address_city", sa.String(100), nullable=True),
        sa.Column("billing_address_state", sa.String(2), nullable=True),
        sa.Column("billing_address_zip", sa.String(10), nullable=True),
        # Divida
        sa.Column("total_debt", sa.Numeric(15, 2), server_default="0"),
        sa.Column("overdue_debt", sa.Numeric(15, 2), server_default="0"),
        # Preferencias
        sa.Column("preferred_payment_method", sa.String(20), nullable=True),
        sa.Column("auto_debit_enabled", sa.Boolean, server_default="false"),
        sa.Column("email_notifications", sa.Boolean, server_default="true"),
        sa.Column("sms_notifications", sa.Boolean, server_default="false"),
        sa.Column("whatsapp_notifications", sa.Boolean, server_default="false"),
        # Observacoes
        sa.Column("notes", sa.Text, nullable=True),
        # Auditoria
        sa.Column("created_at", sa.DateTime, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime, server_default=sa.text("now()")),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Indices
    op.create_index(
        "ix_customers_cpf_cnpj",
        "customers",
        ["condominio_id", "cpf_cnpj"],
        unique=True,
    )
    op.create_index(
        "ix_customers_debt",
        "customers",
        ["condominio_id", "total_debt"],
        postgresql_where=sa.text("total_debt > 0"),
    )

    # =========================================================================
    # Tabela: receivable_accounts
    # Contas a receber
    # =========================================================================
    op.create_table(
        "receivable_accounts",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "condominio_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            index=True,
        ),
        # Relacionamentos
        sa.Column(
            "customer_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "unidade_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "category_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        # Identificacao
        sa.Column("document_number", sa.String(50), nullable=True),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("reference_month", sa.String(7), nullable=True),
        # Valores
        sa.Column("gross_value", sa.Numeric(15, 2), nullable=False),
        sa.Column("discount_value", sa.Numeric(15, 2), server_default="0"),
        sa.Column("addition_value", sa.Numeric(15, 2), server_default="0"),
        sa.Column("net_value", sa.Numeric(15, 2), nullable=False),
        sa.Column("paid_value", sa.Numeric(15, 2), server_default="0"),
        # Juros e multa
        sa.Column("interest_rate", sa.Numeric(5, 2), server_default="1.00"),
        sa.Column("penalty_rate", sa.Numeric(5, 2), server_default="2.00"),
        sa.Column("interest_value", sa.Numeric(15, 2), server_default="0"),
        sa.Column("penalty_value", sa.Numeric(15, 2), server_default="0"),
        # Datas
        sa.Column("issue_date", sa.Date, nullable=False),
        sa.Column("due_date", sa.Date, nullable=False, index=True),
        sa.Column("payment_date", sa.Date, nullable=True),
        sa.Column("competence_date", sa.Date, nullable=True),
        # Status
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="pendente",
            index=True,
        ),
        # Parcelamento
        sa.Column("total_installments", sa.Integer, server_default="1"),
        sa.Column("current_installment", sa.Integer, server_default="1"),
        # Boleto
        sa.Column("boleto_number", sa.String(50), nullable=True),
        sa.Column("boleto_barcode", sa.String(50), nullable=True),
        sa.Column("boleto_line", sa.String(60), nullable=True),
        sa.Column("boleto_url", sa.String(500), nullable=True),
        sa.Column("boleto_generated_at", sa.DateTime, nullable=True),
        # PIX
        sa.Column("pix_qrcode", sa.Text, nullable=True),
        sa.Column("pix_key", sa.String(100), nullable=True),
        sa.Column("pix_txid", sa.String(50), nullable=True),
        sa.Column("pix_generated_at", sa.DateTime, nullable=True),
        # Protesto
        sa.Column("protest_date", sa.Date, nullable=True),
        sa.Column("protest_number", sa.String(50), nullable=True),
        sa.Column("protested_by", postgresql.UUID(as_uuid=True), nullable=True),
        # Baixa
        sa.Column("write_off_date", sa.Date, nullable=True),
        sa.Column("write_off_reason", sa.Text, nullable=True),
        sa.Column("written_off_by", postgresql.UUID(as_uuid=True), nullable=True),
        # Recorrencia
        sa.Column("is_recurring", sa.Boolean, server_default="false"),
        sa.Column("recurring_day", sa.Integer, nullable=True),
        sa.Column("recurring_frequency", sa.String(20), nullable=True),
        sa.Column(
            "parent_account_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        # Observacoes
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("internal_notes", sa.Text, nullable=True),
        # Metadados
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        # Auditoria
        sa.Column("created_at", sa.DateTime, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime, server_default=sa.text("now()")),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("deleted_by", postgresql.UUID(as_uuid=True), nullable=True),
        # FKs
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["customers.id"],
            name="fk_receivable_accounts_customer",
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["receivable_categories.id"],
            name="fk_receivable_accounts_category",
        ),
        sa.ForeignKeyConstraint(
            ["parent_account_id"],
            ["receivable_accounts.id"],
            name="fk_receivable_accounts_parent",
        ),
    )

    # Indices
    op.create_index(
        "ix_receivable_accounts_customer",
        "receivable_accounts",
        ["customer_id"],
    )
    op.create_index(
        "ix_receivable_accounts_unidade",
        "receivable_accounts",
        ["unidade_id"],
    )
    op.create_index(
        "ix_receivable_accounts_category",
        "receivable_accounts",
        ["category_id"],
    )
    op.create_index(
        "ix_receivable_accounts_document",
        "receivable_accounts",
        ["condominio_id", "document_number"],
        unique=True,
        postgresql_where=sa.text("document_number IS NOT NULL"),
    )
    op.create_index(
        "ix_receivable_accounts_overdue",
        "receivable_accounts",
        ["condominio_id", "due_date"],
        postgresql_where=sa.text("status = 'vencida'"),
    )

    # =========================================================================
    # Tabela: receivable_installments
    # Parcelas das contas a receber
    # =========================================================================
    op.create_table(
        "receivable_installments",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "receivable_account_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        # Identificacao
        sa.Column("installment_number", sa.Integer, nullable=False),
        # Valores
        sa.Column("original_value", sa.Numeric(15, 2), nullable=False),
        sa.Column("discount_value", sa.Numeric(15, 2), server_default="0"),
        sa.Column("addition_value", sa.Numeric(15, 2), server_default="0"),
        sa.Column("current_value", sa.Numeric(15, 2), nullable=False),
        sa.Column("paid_value", sa.Numeric(15, 2), server_default="0"),
        # Juros e multa
        sa.Column("interest_rate", sa.Numeric(5, 2), server_default="1.00"),
        sa.Column("penalty_rate", sa.Numeric(5, 2), server_default="2.00"),
        sa.Column("interest_value", sa.Numeric(15, 2), server_default="0"),
        sa.Column("penalty_value", sa.Numeric(15, 2), server_default="0"),
        # Datas
        sa.Column("due_date", sa.Date, nullable=False, index=True),
        sa.Column("original_due_date", sa.Date, nullable=True),
        sa.Column("payment_date", sa.Date, nullable=True),
        # Status
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="pendente",
            index=True,
        ),
        # Boleto
        sa.Column("boleto_number", sa.String(50), nullable=True),
        sa.Column("boleto_barcode", sa.String(50), nullable=True),
        sa.Column("boleto_line", sa.String(60), nullable=True),
        sa.Column("boleto_url", sa.String(500), nullable=True),
        sa.Column("boleto_generated_at", sa.DateTime, nullable=True),
        # PIX
        sa.Column("pix_qrcode", sa.Text, nullable=True),
        sa.Column("pix_key", sa.String(100), nullable=True),
        sa.Column("pix_txid", sa.String(50), nullable=True),
        sa.Column("pix_generated_at", sa.DateTime, nullable=True),
        # Cobranca
        sa.Column("collection_attempts", sa.Integer, server_default="0"),
        sa.Column("last_collection_date", sa.DateTime, nullable=True),
        sa.Column("notifications_sent", postgresql.JSONB, nullable=True),
        # Renegociacao
        sa.Column("renegotiated_at", sa.DateTime, nullable=True),
        sa.Column("renegotiation_reason", sa.Text, nullable=True),
        # Observacoes
        sa.Column("notes", sa.Text, nullable=True),
        # Auditoria
        sa.Column("created_at", sa.DateTime, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime, server_default=sa.text("now()")),
        # FK
        sa.ForeignKeyConstraint(
            ["receivable_account_id"],
            ["receivable_accounts.id"],
            name="fk_receivable_installments_account",
            ondelete="CASCADE",
        ),
    )

    # Indices
    op.create_index(
        "ix_receivable_installments_account",
        "receivable_installments",
        ["receivable_account_id"],
    )
    op.create_index(
        "ix_receivable_installments_pending",
        "receivable_installments",
        ["due_date"],
        postgresql_where=sa.text("status IN ('pendente', 'vencida')"),
    )

    # =========================================================================
    # Tabela: receivable_payments
    # Recebimentos
    # =========================================================================
    op.create_table(
        "receivable_payments",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "installment_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "payment_method_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "bank_account_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        # Valores
        sa.Column("paid_value", sa.Numeric(15, 2), nullable=False),
        sa.Column("discount_value", sa.Numeric(15, 2), server_default="0"),
        sa.Column("interest_value", sa.Numeric(15, 2), server_default="0"),
        sa.Column("penalty_value", sa.Numeric(15, 2), server_default="0"),
        sa.Column("fee_value", sa.Numeric(15, 2), server_default="0"),
        # Datas
        sa.Column("payment_date", sa.Date, nullable=False),
        sa.Column("credit_date", sa.Date, nullable=True),
        # Status e origem
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="confirmado",
        ),
        sa.Column(
            "payment_origin",
            sa.String(20),
            nullable=False,
            server_default="manual",
        ),
        # Identificacao do pagamento
        sa.Column("transaction_id", sa.String(100), nullable=True),
        sa.Column("authentication_code", sa.String(100), nullable=True),
        sa.Column("nsu", sa.String(50), nullable=True),
        # Conciliacao
        sa.Column("is_reconciled", sa.Boolean, server_default="false"),
        sa.Column("reconciled_at", sa.DateTime, nullable=True),
        sa.Column("reconciled_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reconciliation_notes", sa.Text, nullable=True),
        # Estorno
        sa.Column("reversed_at", sa.DateTime, nullable=True),
        sa.Column("reversed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reversal_reason", sa.Text, nullable=True),
        # Observacoes
        sa.Column("notes", sa.Text, nullable=True),
        # Metadados
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        # Auditoria
        sa.Column("created_at", sa.DateTime, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime, server_default=sa.text("now()")),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        # FK
        sa.ForeignKeyConstraint(
            ["installment_id"],
            ["receivable_installments.id"],
            name="fk_receivable_payments_installment",
        ),
        sa.ForeignKeyConstraint(
            ["payment_method_id"],
            ["payment_methods.id"],
            name="fk_receivable_payments_method",
        ),
    )

    # Indices
    op.create_index(
        "ix_receivable_payments_installment",
        "receivable_payments",
        ["installment_id"],
    )
    op.create_index(
        "ix_receivable_payments_date",
        "receivable_payments",
        ["payment_date"],
    )
    op.create_index(
        "ix_receivable_payments_pending_reconciliation",
        "receivable_payments",
        ["is_reconciled"],
        postgresql_where=sa.text("is_reconciled = false AND status = 'confirmado'"),
    )

    # =========================================================================
    # Tabela: billing_rules
    # Regras de cobranca automatica
    # =========================================================================
    op.create_table(
        "billing_rules",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "condominio_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "category_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        # Identificacao
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        # Tipo e frequencia
        sa.Column(
            "billing_type",
            sa.String(30),
            nullable=False,
            server_default="taxa_condominial",
        ),
        sa.Column(
            "frequency",
            sa.String(20),
            nullable=False,
            server_default="mensal",
        ),
        # Valores
        sa.Column("base_value", sa.Numeric(15, 2), nullable=False),
        sa.Column("calculation_type", sa.String(20), server_default="fixo"),
        sa.Column("calculation_formula", sa.Text, nullable=True),
        # Configuracao de geracao
        sa.Column("due_day", sa.Integer, nullable=False, server_default="10"),
        sa.Column("generation_day", sa.Integer, nullable=False, server_default="1"),
        sa.Column("days_before_due", sa.Integer, server_default="5"),
        # Juros e multa
        sa.Column("interest_rate", sa.Numeric(5, 2), server_default="1.00"),
        sa.Column("penalty_rate", sa.Numeric(5, 2), server_default="2.00"),
        sa.Column("grace_days", sa.Integer, server_default="0"),
        # Notificacoes
        sa.Column("notification_types", postgresql.ARRAY(sa.String(20)), nullable=True),
        sa.Column("notify_days_before", postgresql.ARRAY(sa.Integer), nullable=True),
        sa.Column("notify_on_overdue", sa.Boolean, server_default="true"),
        # Geracao automatica
        sa.Column("auto_generate_boleto", sa.Boolean, server_default="true"),
        sa.Column("auto_generate_pix", sa.Boolean, server_default="true"),
        # Escopo
        sa.Column("apply_to_all_units", sa.Boolean, server_default="true"),
        sa.Column("apply_to_units", postgresql.ARRAY(postgresql.UUID), nullable=True),
        sa.Column("exclude_units", postgresql.ARRAY(postgresql.UUID), nullable=True),
        # Periodo
        sa.Column("start_date", sa.Date, nullable=True),
        sa.Column("end_date", sa.Date, nullable=True),
        # Status
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="ativa",
        ),
        # Controle de execucao
        sa.Column("last_generation_date", sa.Date, nullable=True),
        sa.Column("next_generation_date", sa.Date, nullable=True),
        sa.Column("total_generated", sa.Integer, server_default="0"),
        # Observacoes
        sa.Column("notes", sa.Text, nullable=True),
        # Auditoria
        sa.Column("created_at", sa.DateTime, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime, server_default=sa.text("now()")),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("deleted_by", postgresql.UUID(as_uuid=True), nullable=True),
        # FK
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["receivable_categories.id"],
            name="fk_billing_rules_category",
        ),
    )

    # Indices
    op.create_index(
        "ix_billing_rules_category",
        "billing_rules",
        ["category_id"],
    )
    op.create_index(
        "ix_billing_rules_active",
        "billing_rules",
        ["condominio_id", "status"],
        postgresql_where=sa.text("status = 'ativa'"),
    )
    op.create_index(
        "ix_billing_rules_next_gen",
        "billing_rules",
        ["next_generation_date"],
        postgresql_where=sa.text("status = 'ativa'"),
    )


def downgrade() -> None:
    """Remove tabelas de Contas a Receber."""

    # Remove tabelas na ordem inversa
    op.drop_table("billing_rules")
    op.drop_table("receivable_payments")
    op.drop_table("receivable_installments")
    op.drop_table("receivable_accounts")
    op.drop_table("customers")
    op.drop_table("receivable_categories")
