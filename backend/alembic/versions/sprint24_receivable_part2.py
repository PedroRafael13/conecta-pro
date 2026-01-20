"""Sprint 24 - Contas a Receber Parte 2

Adiciona recursos avancados de contas a receber:
- Campos adicionais para receivable_accounts (prioridade, centro de custo, etc)
- Campos adicionais para customers (trade_name, bloqueio, limite credito)
- Campos adicionais para installments (condominio_id, boleto_expires_at)
- Campos adicionais para payments (origem, comprovante, dados bancarios)
- Tabela payment_agreements para acordos de pagamento
- Tabela collection_actions para historico de cobranca

Revision ID: sprint24_receivable_p2
Revises: sprint23_receivable
Create Date: 2026-01-07

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, ENUM

# revision identifiers, used by Alembic.
revision: str = "sprint24_receivable_p2"
down_revision: Union[str, None] = "sprint23_receivable"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Aplica migração - Contas a Receber Parte 2."""

    # =========================================================================
    # 1. Adicionar campos em customers
    # =========================================================================
    op.add_column(
        "customers",
        sa.Column("trade_name", sa.String(200), nullable=True),
    )
    op.add_column(
        "customers",
        sa.Column("email_secondary", sa.String(200), nullable=True),
    )
    op.add_column(
        "customers",
        sa.Column("phone_secondary", sa.String(20), nullable=True),
    )
    op.add_column(
        "customers",
        sa.Column("whatsapp", sa.String(20), nullable=True),
    )
    op.add_column(
        "customers",
        sa.Column("credit_limit", sa.Numeric(15, 2), server_default="0"),
    )
    op.add_column(
        "customers",
        sa.Column("billing_email", sa.String(200), nullable=True),
    )
    op.add_column(
        "customers",
        sa.Column("billing_day", sa.Integer(), nullable=True),
    )
    op.add_column(
        "customers",
        sa.Column("auto_billing", sa.Boolean(), server_default="true"),
    )
    op.add_column(
        "customers",
        sa.Column("is_blocked", sa.Boolean(), server_default="false"),
    )
    op.add_column(
        "customers",
        sa.Column("blocked_reason", sa.Text(), nullable=True),
    )
    op.add_column(
        "customers",
        sa.Column("blocked_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "customers",
        sa.Column("blocked_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "customers",
        sa.Column("extra_data", postgresql.JSONB(), server_default="{}"),
    )
    op.add_column(
        "customers",
        sa.Column("ativo", sa.Boolean(), server_default="true"),
    )

    # =========================================================================
    # 2. Adicionar campos em receivable_accounts
    # =========================================================================
    op.add_column(
        "receivable_accounts",
        sa.Column("code", sa.String(30), nullable=True),
    )
    op.add_column(
        "receivable_accounts",
        sa.Column("receivable_type", sa.String(20), server_default="avulsa"),
    )
    op.add_column(
        "receivable_accounts",
        sa.Column("priority", sa.String(20), server_default="media"),
    )
    op.add_column(
        "receivable_accounts",
        sa.Column("morador_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "receivable_accounts",
        sa.Column("grace_days", sa.Integer(), server_default="0"),
    )
    op.add_column(
        "receivable_accounts",
        sa.Column("entry_date", sa.Date(), nullable=True),
    )
    op.add_column(
        "receivable_accounts",
        sa.Column("remaining_value", sa.Numeric(15, 2), nullable=True),
    )
    op.add_column(
        "receivable_accounts",
        sa.Column("boleto_digitable_line", sa.String(100), nullable=True),
    )
    op.add_column(
        "receivable_accounts",
        sa.Column("pix_copy_paste", sa.String(500), nullable=True),
    )
    op.add_column(
        "receivable_accounts",
        sa.Column("cost_center", sa.String(50), nullable=True),
    )
    op.add_column(
        "receivable_accounts",
        sa.Column("collection_attempts", sa.Integer(), server_default="0"),
    )
    op.add_column(
        "receivable_accounts",
        sa.Column("last_collection_date", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "receivable_accounts",
        sa.Column("next_collection_date", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "receivable_accounts",
        sa.Column("collection_notes", sa.Text(), nullable=True),
    )
    op.add_column(
        "receivable_accounts",
        sa.Column("is_protested", sa.Boolean(), server_default="false"),
    )
    op.add_column(
        "receivable_accounts",
        sa.Column("protested_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "receivable_accounts",
        sa.Column("is_in_agreement", sa.Boolean(), server_default="false"),
    )
    op.add_column(
        "receivable_accounts",
        sa.Column("agreement_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "receivable_accounts",
        sa.Column("is_written_off", sa.Boolean(), server_default="false"),
    )
    op.add_column(
        "receivable_accounts",
        sa.Column("written_off_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "receivable_accounts",
        sa.Column("recurrence_type", sa.String(20), nullable=True),
    )
    op.add_column(
        "receivable_accounts",
        sa.Column("recurrence_end_date", sa.Date(), nullable=True),
    )
    op.add_column(
        "receivable_accounts",
        sa.Column("attachments", postgresql.JSONB(), server_default="[]"),
    )
    op.add_column(
        "receivable_accounts",
        sa.Column("tags", postgresql.JSONB(), server_default="[]"),
    )
    op.add_column(
        "receivable_accounts",
        sa.Column("ativo", sa.Boolean(), server_default="true"),
    )

    # Indices adicionais
    op.create_index(
        "ix_receivable_accounts_code",
        "receivable_accounts",
        ["condominio_id", "code"],
        postgresql_where=sa.text("code IS NOT NULL"),
    )
    op.create_index(
        "ix_receivable_accounts_morador",
        "receivable_accounts",
        ["morador_id"],
    )
    op.create_index(
        "ix_receivable_accounts_agreement",
        "receivable_accounts",
        ["agreement_id"],
        postgresql_where=sa.text("agreement_id IS NOT NULL"),
    )

    # =========================================================================
    # 3. Adicionar campos em receivable_installments
    # =========================================================================
    op.add_column(
        "receivable_installments",
        sa.Column(
            "condominio_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )
    op.add_column(
        "receivable_installments",
        sa.Column("total_installments", sa.Integer(), nullable=True),
    )
    op.add_column(
        "receivable_installments",
        sa.Column("boleto_expires_at", sa.Date(), nullable=True),
    )
    op.add_column(
        "receivable_installments",
        sa.Column("pix_expires_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "receivable_installments",
        sa.Column("last_collection_method", sa.String(30), nullable=True),
    )
    op.add_column(
        "receivable_installments",
        sa.Column("is_renegotiated", sa.Boolean(), server_default="false"),
    )
    op.add_column(
        "receivable_installments",
        sa.Column(
            "renegotiated_from_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )
    op.add_column(
        "receivable_installments",
        sa.Column("ativo", sa.Boolean(), server_default="true"),
    )

    # Indice adicional
    op.create_index(
        "ix_receivable_installments_condominio",
        "receivable_installments",
        ["condominio_id"],
    )

    # =========================================================================
    # 4. Adicionar campos em receivable_payments
    # =========================================================================
    op.add_column(
        "receivable_payments",
        sa.Column(
            "condominio_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )
    op.add_column(
        "receivable_payments",
        sa.Column("code", sa.String(30), nullable=True),
    )
    op.add_column(
        "receivable_payments",
        sa.Column("origin", sa.String(30), server_default="manual"),
    )
    op.add_column(
        "receivable_payments",
        sa.Column("net_value", sa.Numeric(15, 2), nullable=True),
    )
    op.add_column(
        "receivable_payments",
        sa.Column("processing_date", sa.Date(), nullable=True),
    )
    op.add_column(
        "receivable_payments",
        sa.Column("confirmation_date", sa.Date(), nullable=True),
    )
    op.add_column(
        "receivable_payments",
        sa.Column("payment_method_name", sa.String(100), nullable=True),
    )
    op.add_column(
        "receivable_payments",
        sa.Column("bank_account_name", sa.String(100), nullable=True),
    )
    op.add_column(
        "receivable_payments",
        sa.Column("receipt_number", sa.String(50), nullable=True),
    )
    op.add_column(
        "receivable_payments",
        sa.Column("receipt_url", sa.String(500), nullable=True),
    )
    op.add_column(
        "receivable_payments",
        sa.Column("bank_transaction_id", sa.String(100), nullable=True),
    )
    op.add_column(
        "receivable_payments",
        sa.Column("bank_return_code", sa.String(20), nullable=True),
    )
    op.add_column(
        "receivable_payments",
        sa.Column("bank_return_message", sa.String(500), nullable=True),
    )
    # Dados de boleto pago
    op.add_column(
        "receivable_payments",
        sa.Column("boleto_nosso_numero", sa.String(50), nullable=True),
    )
    op.add_column(
        "receivable_payments",
        sa.Column("boleto_payment_date", sa.Date(), nullable=True),
    )
    op.add_column(
        "receivable_payments",
        sa.Column("boleto_payment_value", sa.Numeric(15, 2), nullable=True),
    )
    # Dados de PIX
    op.add_column(
        "receivable_payments",
        sa.Column("pix_txid", sa.String(100), nullable=True),
    )
    op.add_column(
        "receivable_payments",
        sa.Column("pix_end_to_end_id", sa.String(100), nullable=True),
    )
    # Dados de cheque
    op.add_column(
        "receivable_payments",
        sa.Column("cheque_number", sa.String(20), nullable=True),
    )
    op.add_column(
        "receivable_payments",
        sa.Column("cheque_bank", sa.String(10), nullable=True),
    )
    op.add_column(
        "receivable_payments",
        sa.Column("cheque_agency", sa.String(10), nullable=True),
    )
    op.add_column(
        "receivable_payments",
        sa.Column("cheque_account", sa.String(20), nullable=True),
    )
    op.add_column(
        "receivable_payments",
        sa.Column("cheque_date", sa.Date(), nullable=True),
    )
    # Estorno
    op.add_column(
        "receivable_payments",
        sa.Column("is_reversed", sa.Boolean(), server_default="false"),
    )
    op.add_column(
        "receivable_payments",
        sa.Column("reversal_receipt", sa.String(500), nullable=True),
    )
    # Extra
    op.add_column(
        "receivable_payments",
        sa.Column("extra_data", postgresql.JSONB(), server_default="{}"),
    )
    op.add_column(
        "receivable_payments",
        sa.Column("ativo", sa.Boolean(), server_default="true"),
    )

    # Indices
    op.create_index(
        "ix_receivable_payments_condominio",
        "receivable_payments",
        ["condominio_id"],
    )
    op.create_index(
        "ix_receivable_payments_origin",
        "receivable_payments",
        ["origin"],
    )

    # =========================================================================
    # 5. Tabela payment_agreements - Acordos de pagamento
    # =========================================================================
    op.create_table(
        "payment_agreements",
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
            "customer_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        # Identificacao
        sa.Column("code", sa.String(30), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        # Valores originais
        sa.Column("original_total", sa.Numeric(15, 2), nullable=False),
        sa.Column("original_principal", sa.Numeric(15, 2), nullable=False),
        sa.Column("original_interest", sa.Numeric(15, 2), server_default="0"),
        sa.Column("original_penalty", sa.Numeric(15, 2), server_default="0"),
        # Valores negociados
        sa.Column("discount_percent", sa.Numeric(5, 2), server_default="0"),
        sa.Column("discount_value", sa.Numeric(15, 2), server_default="0"),
        sa.Column("negotiated_total", sa.Numeric(15, 2), nullable=False),
        # Parcelamento
        sa.Column("total_installments", sa.Integer(), nullable=False),
        sa.Column("installment_value", sa.Numeric(15, 2), nullable=False),
        sa.Column("first_due_date", sa.Date(), nullable=False),
        sa.Column("due_day", sa.Integer(), nullable=True),
        # Juros e multa do acordo
        sa.Column("agreement_interest_rate", sa.Numeric(5, 2), server_default="0"),
        sa.Column("agreement_penalty_rate", sa.Numeric(5, 2), server_default="2"),
        # Status
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="ativo",
        ),
        # Contas incluidas
        sa.Column(
            "included_accounts",
            postgresql.ARRAY(postgresql.UUID(as_uuid=True)),
            nullable=True,
        ),
        # Pagamentos
        sa.Column("paid_installments", sa.Integer(), server_default="0"),
        sa.Column("paid_value", sa.Numeric(15, 2), server_default="0"),
        sa.Column("remaining_value", sa.Numeric(15, 2), nullable=True),
        # Quebra do acordo
        sa.Column("is_broken", sa.Boolean(), server_default="false"),
        sa.Column("broken_at", sa.DateTime(), nullable=True),
        sa.Column("broken_reason", sa.Text(), nullable=True),
        sa.Column("broken_by", postgresql.UUID(as_uuid=True), nullable=True),
        # Datas
        sa.Column("signed_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        # Documento
        sa.Column("document_url", sa.String(500), nullable=True),
        sa.Column("signature_url", sa.String(500), nullable=True),
        # Observacoes
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("internal_notes", sa.Text(), nullable=True),
        # Auditoria
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        # FK
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["customers.id"],
            name="fk_payment_agreements_customer",
        ),
    )

    # Indices
    op.create_index(
        "ix_payment_agreements_customer",
        "payment_agreements",
        ["customer_id"],
    )
    op.create_index(
        "ix_payment_agreements_status",
        "payment_agreements",
        ["status"],
    )
    op.create_index(
        "ix_payment_agreements_active",
        "payment_agreements",
        ["condominio_id", "status"],
        postgresql_where=sa.text("status = 'ativo'"),
    )

    # =========================================================================
    # 6. Tabela collection_actions - Historico de acoes de cobranca
    # =========================================================================
    op.create_table(
        "collection_actions",
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
            "customer_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "receivable_account_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "installment_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        # Tipo de acao
        sa.Column(
            "action_type",
            sa.String(30),
            nullable=False,
        ),  # email, sms, whatsapp, ligacao, carta, protesto, negativacao
        # Detalhes da acao
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("contact_info", sa.String(200), nullable=True),  # email/telefone
        sa.Column("message_template", sa.String(100), nullable=True),
        sa.Column("message_content", sa.Text(), nullable=True),
        # Status
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="enviado",
        ),  # enviado, entregue, lido, respondido, falhou
        # Resultado
        sa.Column("result", sa.String(50), nullable=True),  # sucesso, sem_resposta, prometeu_pagar, etc
        sa.Column("result_notes", sa.Text(), nullable=True),
        # Rastreamento
        sa.Column("external_id", sa.String(100), nullable=True),  # ID do SMS, email, etc
        sa.Column("delivered_at", sa.DateTime(), nullable=True),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.Column("responded_at", sa.DateTime(), nullable=True),
        # Proxima acao
        sa.Column("next_action_date", sa.DateTime(), nullable=True),
        sa.Column("next_action_type", sa.String(30), nullable=True),
        # Auditoria
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        # FKs
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["customers.id"],
            name="fk_collection_actions_customer",
        ),
        sa.ForeignKeyConstraint(
            ["receivable_account_id"],
            ["receivable_accounts.id"],
            name="fk_collection_actions_account",
        ),
        sa.ForeignKeyConstraint(
            ["installment_id"],
            ["receivable_installments.id"],
            name="fk_collection_actions_installment",
        ),
    )

    # Indices
    op.create_index(
        "ix_collection_actions_customer",
        "collection_actions",
        ["customer_id"],
    )
    op.create_index(
        "ix_collection_actions_account",
        "collection_actions",
        ["receivable_account_id"],
    )
    op.create_index(
        "ix_collection_actions_type",
        "collection_actions",
        ["action_type"],
    )
    op.create_index(
        "ix_collection_actions_date",
        "collection_actions",
        ["created_at"],
    )

    # =========================================================================
    # 7. Adicionar campos em receivable_categories
    # =========================================================================
    op.add_column(
        "receivable_categories",
        sa.Column("display_order", sa.Integer(), server_default="0"),
    )
    op.add_column(
        "receivable_categories",
        sa.Column("ativo", sa.Boolean(), server_default="true"),
    )


def downgrade() -> None:
    """Reverte migração."""

    # Remove tabelas novas
    op.drop_table("collection_actions")
    op.drop_table("payment_agreements")

    # Remove campos de receivable_categories
    op.drop_column("receivable_categories", "ativo")
    op.drop_column("receivable_categories", "display_order")

    # Remove indices de receivable_payments
    op.drop_index("ix_receivable_payments_origin", table_name="receivable_payments")
    op.drop_index("ix_receivable_payments_condominio", table_name="receivable_payments")

    # Remove campos de receivable_payments
    op.drop_column("receivable_payments", "ativo")
    op.drop_column("receivable_payments", "extra_data")
    op.drop_column("receivable_payments", "reversal_receipt")
    op.drop_column("receivable_payments", "is_reversed")
    op.drop_column("receivable_payments", "cheque_date")
    op.drop_column("receivable_payments", "cheque_account")
    op.drop_column("receivable_payments", "cheque_agency")
    op.drop_column("receivable_payments", "cheque_bank")
    op.drop_column("receivable_payments", "cheque_number")
    op.drop_column("receivable_payments", "pix_end_to_end_id")
    op.drop_column("receivable_payments", "pix_txid")
    op.drop_column("receivable_payments", "boleto_payment_value")
    op.drop_column("receivable_payments", "boleto_payment_date")
    op.drop_column("receivable_payments", "boleto_nosso_numero")
    op.drop_column("receivable_payments", "bank_return_message")
    op.drop_column("receivable_payments", "bank_return_code")
    op.drop_column("receivable_payments", "bank_transaction_id")
    op.drop_column("receivable_payments", "receipt_url")
    op.drop_column("receivable_payments", "receipt_number")
    op.drop_column("receivable_payments", "bank_account_name")
    op.drop_column("receivable_payments", "payment_method_name")
    op.drop_column("receivable_payments", "confirmation_date")
    op.drop_column("receivable_payments", "processing_date")
    op.drop_column("receivable_payments", "net_value")
    op.drop_column("receivable_payments", "origin")
    op.drop_column("receivable_payments", "code")
    op.drop_column("receivable_payments", "condominio_id")

    # Remove indice de receivable_installments
    op.drop_index("ix_receivable_installments_condominio", table_name="receivable_installments")

    # Remove campos de receivable_installments
    op.drop_column("receivable_installments", "ativo")
    op.drop_column("receivable_installments", "renegotiated_from_id")
    op.drop_column("receivable_installments", "is_renegotiated")
    op.drop_column("receivable_installments", "last_collection_method")
    op.drop_column("receivable_installments", "pix_expires_at")
    op.drop_column("receivable_installments", "boleto_expires_at")
    op.drop_column("receivable_installments", "total_installments")
    op.drop_column("receivable_installments", "condominio_id")

    # Remove indices de receivable_accounts
    op.drop_index("ix_receivable_accounts_agreement", table_name="receivable_accounts")
    op.drop_index("ix_receivable_accounts_morador", table_name="receivable_accounts")
    op.drop_index("ix_receivable_accounts_code", table_name="receivable_accounts")

    # Remove campos de receivable_accounts
    op.drop_column("receivable_accounts", "ativo")
    op.drop_column("receivable_accounts", "tags")
    op.drop_column("receivable_accounts", "attachments")
    op.drop_column("receivable_accounts", "recurrence_end_date")
    op.drop_column("receivable_accounts", "recurrence_type")
    op.drop_column("receivable_accounts", "written_off_at")
    op.drop_column("receivable_accounts", "is_written_off")
    op.drop_column("receivable_accounts", "agreement_id")
    op.drop_column("receivable_accounts", "is_in_agreement")
    op.drop_column("receivable_accounts", "protested_at")
    op.drop_column("receivable_accounts", "is_protested")
    op.drop_column("receivable_accounts", "collection_notes")
    op.drop_column("receivable_accounts", "next_collection_date")
    op.drop_column("receivable_accounts", "last_collection_date")
    op.drop_column("receivable_accounts", "collection_attempts")
    op.drop_column("receivable_accounts", "cost_center")
    op.drop_column("receivable_accounts", "pix_copy_paste")
    op.drop_column("receivable_accounts", "boleto_digitable_line")
    op.drop_column("receivable_accounts", "remaining_value")
    op.drop_column("receivable_accounts", "entry_date")
    op.drop_column("receivable_accounts", "grace_days")
    op.drop_column("receivable_accounts", "morador_id")
    op.drop_column("receivable_accounts", "priority")
    op.drop_column("receivable_accounts", "receivable_type")
    op.drop_column("receivable_accounts", "code")

    # Remove campos de customers
    op.drop_column("customers", "ativo")
    op.drop_column("customers", "extra_data")
    op.drop_column("customers", "blocked_by")
    op.drop_column("customers", "blocked_at")
    op.drop_column("customers", "blocked_reason")
    op.drop_column("customers", "is_blocked")
    op.drop_column("customers", "auto_billing")
    op.drop_column("customers", "billing_day")
    op.drop_column("customers", "billing_email")
    op.drop_column("customers", "credit_limit")
    op.drop_column("customers", "whatsapp")
    op.drop_column("customers", "phone_secondary")
    op.drop_column("customers", "email_secondary")
    op.drop_column("customers", "trade_name")
