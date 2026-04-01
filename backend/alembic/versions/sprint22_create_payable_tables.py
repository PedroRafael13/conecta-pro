"""Sprint 22: Cria tabelas de Contas a Pagar.

Revision ID: sprint22_payable
Revises: sprint21_001_employee_portal_tables
Create Date: 2024-12-31

Tabelas criadas:
- suppliers: Fornecedores
- payment_methods: Formas de pagamento
- payable_categories: Categorias de despesas
- payable_accounts: Contas a pagar
- payable_installments: Parcelas
- payable_payments: Pagamentos
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers
revision = "sprint22_payable"
down_revision = "sprint21_001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Cria tabelas de Contas a Pagar."""

    # =========================================================================
    # Tabela: suppliers
    # Cadastro de fornecedores
    # =========================================================================
    op.create_table(
        "suppliers",
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
        # Identificação
        sa.Column("cpf_cnpj", sa.String(18), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("trade_name", sa.String(200), nullable=True),
        # Tipo e categoria
        sa.Column(
            "supplier_type",
            sa.String(20),
            nullable=False,
            server_default="pessoa_juridica",
        ),
        sa.Column("category", sa.String(50), nullable=True),
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
        sa.Column("contact_name", sa.String(100), nullable=True),
        sa.Column("website", sa.String(255), nullable=True),
        # Endereço
        sa.Column("address_street", sa.String(255), nullable=True),
        sa.Column("address_number", sa.String(20), nullable=True),
        sa.Column("address_complement", sa.String(100), nullable=True),
        sa.Column("address_neighborhood", sa.String(100), nullable=True),
        sa.Column("address_city", sa.String(100), nullable=True),
        sa.Column("address_state", sa.String(2), nullable=True),
        sa.Column("address_zip", sa.String(10), nullable=True),
        # Dados bancários
        sa.Column("bank_code", sa.String(10), nullable=True),
        sa.Column("bank_name", sa.String(100), nullable=True),
        sa.Column("bank_agency", sa.String(10), nullable=True),
        sa.Column("bank_agency_digit", sa.String(2), nullable=True),
        sa.Column("bank_account", sa.String(20), nullable=True),
        sa.Column("bank_account_digit", sa.String(2), nullable=True),
        sa.Column("bank_account_type", sa.String(20), nullable=True),
        # PIX
        sa.Column("pix_key", sa.String(100), nullable=True),
        sa.Column("pix_key_type", sa.String(20), nullable=True),
        # Documentos fiscais
        sa.Column("state_registration", sa.String(20), nullable=True),
        sa.Column("municipal_registration", sa.String(20), nullable=True),
        # Retenções
        sa.Column("withhold_iss", sa.Boolean, server_default="false"),
        sa.Column("withhold_ir", sa.Boolean, server_default="false"),
        sa.Column("withhold_pis", sa.Boolean, server_default="false"),
        sa.Column("withhold_cofins", sa.Boolean, server_default="false"),
        sa.Column("withhold_csll", sa.Boolean, server_default="false"),
        sa.Column("withhold_inss", sa.Boolean, server_default="false"),
        sa.Column("iss_rate", sa.Numeric(5, 2), nullable=True),
        # Condições de pagamento
        sa.Column(
            "payment_terms",
            sa.String(20),
            server_default="a_vista",
        ),
        sa.Column("payment_day", sa.Integer, nullable=True),
        # Qualificação
        sa.Column("is_qualified", sa.Boolean, server_default="false"),
        sa.Column("qualification_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "qualified_by",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        # Bloqueio
        sa.Column("is_blocked", sa.Boolean, server_default="false"),
        sa.Column("block_reason", sa.Text, nullable=True),
        sa.Column("block_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "blocked_by",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        # Notas e tags
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String), nullable=True),
        # Auditoria
        sa.Column("ativo", sa.Boolean, server_default="true"),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Índices
    op.create_index(
        "ix_suppliers_cpf_cnpj_condo",
        "suppliers",
        ["cpf_cnpj", "condominio_id"],
        unique=True,
    )
    op.create_index("ix_suppliers_name", "suppliers", ["name"])
    op.create_index("ix_suppliers_status", "suppliers", ["status"])

    # =========================================================================
    # Tabela: payment_methods
    # Formas de pagamento
    # =========================================================================
    op.create_table(
        "payment_methods",
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
        sa.Column("code", sa.String(20), nullable=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        # Tipo e status
        sa.Column(
            "payment_type",
            sa.String(30),
            nullable=False,
            server_default="boleto",
        ),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="ativo",
        ),
        # Requisitos
        sa.Column("requires_bank_account", sa.Boolean, server_default="false"),
        sa.Column("requires_authorization", sa.Boolean, server_default="false"),
        sa.Column("requires_document", sa.Boolean, server_default="false"),
        # Conta bancária associada
        sa.Column(
            "bank_account_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        # Prazos e limites
        sa.Column("days_to_process", sa.Integer, server_default="0"),
        sa.Column("min_value", sa.Numeric(15, 2), nullable=True),
        sa.Column("max_value", sa.Numeric(15, 2), nullable=True),
        sa.Column("daily_limit", sa.Numeric(15, 2), nullable=True),
        # Taxas
        sa.Column("fee_percentage", sa.Numeric(5, 4), nullable=True),
        sa.Column("fee_fixed", sa.Numeric(10, 2), nullable=True),
        # Configurações extras
        sa.Column("settings", postgresql.JSONB, server_default="{}"),
        # Exibição
        sa.Column("display_order", sa.Integer, server_default="0"),
        sa.Column("icon", sa.String(50), nullable=True),
        sa.Column("color", sa.String(20), nullable=True),
        sa.Column("is_default", sa.Boolean, server_default="false"),
        # Auditoria
        sa.Column("ativo", sa.Boolean, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # =========================================================================
    # Tabela: payable_categories
    # Plano de contas - Categorias hierárquicas
    # =========================================================================
    op.create_table(
        "payable_categories",
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
        # Identificação
        sa.Column("code", sa.String(20), nullable=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        # Tipo e natureza
        sa.Column(
            "category_type",
            sa.String(20),
            nullable=False,
            server_default="despesa",
        ),
        sa.Column("nature", sa.String(30), nullable=True),
        # Hierarquia
        sa.Column(
            "parent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("payable_categories.id"),
            nullable=True,
        ),
        sa.Column("path", sa.String(500), nullable=True),
        sa.Column("depth", sa.Integer, server_default="0"),
        sa.Column("full_name", sa.String(500), nullable=True),
        # Flags
        sa.Column("allows_children", sa.Boolean, server_default="true"),
        sa.Column("requires_cost_center", sa.Boolean, server_default="false"),
        sa.Column("requires_project", sa.Boolean, server_default="false"),
        # Contabilidade
        sa.Column("accounting_code", sa.String(20), nullable=True),
        sa.Column("cost_center_default", sa.String(50), nullable=True),
        # Orçamento
        sa.Column("budget_monthly", sa.Numeric(15, 2), nullable=True),
        sa.Column("budget_yearly", sa.Numeric(15, 2), nullable=True),
        sa.Column("alert_percentage", sa.Integer, server_default="80"),
        # Exibição
        sa.Column("icon", sa.String(50), nullable=True),
        sa.Column("color", sa.String(20), nullable=True),
        sa.Column("display_order", sa.Integer, server_default="0"),
        # Flags
        sa.Column("is_system", sa.Boolean, server_default="false"),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        # Auditoria
        sa.Column("ativo", sa.Boolean, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index(
        "ix_payable_categories_code_condo",
        "payable_categories",
        ["code", "condominio_id"],
        unique=True,
    )
    op.create_index("ix_payable_categories_parent", "payable_categories", ["parent_id"])

    # =========================================================================
    # Tabela: payable_accounts
    # Contas a pagar (principal)
    # =========================================================================
    op.create_table(
        "payable_accounts",
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
        # Código interno
        sa.Column("code", sa.String(30), nullable=True),
        # Relacionamentos
        sa.Column(
            "supplier_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("suppliers.id"),
            nullable=True,
            index=True,
        ),
        sa.Column(
            "category_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("payable_categories.id"),
            nullable=True,
            index=True,
        ),
        sa.Column(
            "payment_method_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("payment_methods.id"),
            nullable=True,
        ),
        # Descrição
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("document_number", sa.String(50), nullable=True),
        sa.Column("document_type", sa.String(30), nullable=True),
        # Valores
        sa.Column("gross_value", sa.Numeric(15, 2), nullable=False),
        sa.Column("discount", sa.Numeric(15, 2), server_default="0"),
        sa.Column("interest", sa.Numeric(15, 2), server_default="0"),
        sa.Column("penalty", sa.Numeric(15, 2), server_default="0"),
        sa.Column("net_value", sa.Numeric(15, 2), nullable=False),
        # Retenções
        sa.Column("withholding_iss", sa.Numeric(15, 2), server_default="0"),
        sa.Column("withholding_ir", sa.Numeric(15, 2), server_default="0"),
        sa.Column("withholding_pis", sa.Numeric(15, 2), server_default="0"),
        sa.Column("withholding_cofins", sa.Numeric(15, 2), server_default="0"),
        sa.Column("withholding_csll", sa.Numeric(15, 2), server_default="0"),
        sa.Column("withholding_inss", sa.Numeric(15, 2), server_default="0"),
        sa.Column("total_withholdings", sa.Numeric(15, 2), server_default="0"),
        # Datas
        sa.Column("issue_date", sa.Date, nullable=False),
        sa.Column("due_date", sa.Date, nullable=False, index=True),
        sa.Column("competence_date", sa.Date, nullable=True),
        # Parcelamento
        sa.Column("installments", sa.Integer, server_default="1"),
        sa.Column("current_installment", sa.Integer, server_default="1"),
        # Status
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="pendente",
        ),
        sa.Column(
            "payable_type",
            sa.String(20),
            server_default="normal",
        ),
        sa.Column(
            "priority",
            sa.String(20),
            server_default="normal",
        ),
        # Recorrência
        sa.Column("is_recurring", sa.Boolean, server_default="false"),
        sa.Column("recurrence_type", sa.String(20), nullable=True),
        sa.Column(
            "parent_recurrence_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        # Aprovação
        sa.Column("requires_approval", sa.Boolean, server_default="false"),
        sa.Column(
            "approved_by",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        # Agendamento
        sa.Column("scheduled_date", sa.Date, nullable=True),
        sa.Column(
            "scheduled_by",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        # Pagamento
        sa.Column("paid_amount", sa.Numeric(15, 2), server_default="0"),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        # Centro de custo e projeto
        sa.Column("cost_center", sa.String(50), nullable=True),
        sa.Column("project", sa.String(100), nullable=True),
        # Notas e anexos
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("attachments", postgresql.JSONB, nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String), nullable=True),
        # Cancelamento
        sa.Column(
            "cancelled_by",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancel_reason", sa.Text, nullable=True),
        # Auditoria
        sa.Column("ativo", sa.Boolean, server_default="true"),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Índices
    op.create_index("ix_payable_accounts_status", "payable_accounts", ["status"])
    op.create_index(
        "ix_payable_accounts_condo_due",
        "payable_accounts",
        ["condominio_id", "due_date"],
    )

    # =========================================================================
    # Tabela: payable_installments
    # Parcelas de contas a pagar
    # =========================================================================
    op.create_table(
        "payable_installments",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "payable_account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("payable_accounts.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        # Número da parcela
        sa.Column("installment_number", sa.Integer, nullable=False),
        sa.Column("description", sa.String(200), nullable=True),
        # Valores
        sa.Column("original_value", sa.Numeric(15, 2), nullable=False),
        sa.Column("discount", sa.Numeric(15, 2), server_default="0"),
        sa.Column("interest", sa.Numeric(15, 2), server_default="0"),
        sa.Column("penalty", sa.Numeric(15, 2), server_default="0"),
        sa.Column("current_value", sa.Numeric(15, 2), nullable=False),
        # Pagamento
        sa.Column("paid_amount", sa.Numeric(15, 2), server_default="0"),
        sa.Column("payment_date", sa.Date, nullable=True),
        # Datas
        sa.Column("due_date", sa.Date, nullable=False, index=True),
        # Status
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="pendente",
        ),
        # Código de barras / PIX
        sa.Column("barcode", sa.String(60), nullable=True),
        sa.Column("barcode_digitable", sa.String(60), nullable=True),
        sa.Column("pix_qrcode", sa.Text, nullable=True),
        sa.Column("pix_copy_paste", sa.Text, nullable=True),
        # Taxas por atraso
        sa.Column("interest_rate_daily", sa.Numeric(8, 6), nullable=True),
        sa.Column("penalty_rate", sa.Numeric(5, 2), nullable=True),
        # Renegociação
        sa.Column("is_renegotiated", sa.Boolean, server_default="false"),
        sa.Column("original_due_date", sa.Date, nullable=True),
        sa.Column("renegotiation_reason", sa.Text, nullable=True),
        # Notas
        sa.Column("notes", sa.Text, nullable=True),
        # Auditoria
        sa.Column("ativo", sa.Boolean, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index(
        "ix_payable_installments_status",
        "payable_installments",
        ["status"],
    )

    # =========================================================================
    # Tabela: payable_payments
    # Pagamentos realizados
    # =========================================================================
    op.create_table(
        "payable_payments",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "installment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("payable_installments.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "payment_method_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("payment_methods.id"),
            nullable=True,
        ),
        # Valores
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("discount_applied", sa.Numeric(15, 2), server_default="0"),
        sa.Column("interest_applied", sa.Numeric(15, 2), server_default="0"),
        sa.Column("penalty_applied", sa.Numeric(15, 2), server_default="0"),
        sa.Column("fees", sa.Numeric(15, 2), server_default="0"),
        sa.Column("net_amount", sa.Numeric(15, 2), nullable=False),
        # Datas
        sa.Column("payment_date", sa.Date, nullable=False),
        sa.Column("effective_date", sa.Date, nullable=True),
        # Status
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="pendente",
        ),
        sa.Column(
            "origin",
            sa.String(20),
            server_default="manual",
        ),
        # Dados bancários da transação
        sa.Column("bank_account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("bank_transaction_id", sa.String(100), nullable=True),
        sa.Column("bank_authentication", sa.String(100), nullable=True),
        sa.Column("bank_receipt", sa.Text, nullable=True),
        # Comprovante
        sa.Column("receipt_number", sa.String(50), nullable=True),
        sa.Column("receipt_file", sa.String(500), nullable=True),
        # Reconciliação
        sa.Column("is_reconciled", sa.Boolean, server_default="false"),
        sa.Column("reconciled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reconciled_by", postgresql.UUID(as_uuid=True), nullable=True),
        # Estorno
        sa.Column("is_reversed", sa.Boolean, server_default="false"),
        sa.Column("reversed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reversed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reverse_reason", sa.Text, nullable=True),
        sa.Column("reverse_payment_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Notas
        sa.Column("notes", sa.Text, nullable=True),
        # Auditoria
        sa.Column("ativo", sa.Boolean, server_default="true"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("ix_payable_payments_status", "payable_payments", ["status"])
    op.create_index(
        "ix_payable_payments_date",
        "payable_payments",
        ["payment_date"],
    )


def downgrade() -> None:
    """Remove tabelas de Contas a Pagar."""
    op.drop_table("payable_payments")
    op.drop_table("payable_installments")
    op.drop_table("payable_accounts")
    op.drop_table("payable_categories")
    op.drop_table("payment_methods")
    op.drop_table("suppliers")
