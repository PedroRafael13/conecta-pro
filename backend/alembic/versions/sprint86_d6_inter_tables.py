"""D6: inter_transactions, inter_cobrancas, inter_pix_recebidos, inter_conciliacao_folha

Revision ID: sprint86_d6_inter_tables
Revises: sprint85_d5_4_coleta_logs_certidoes
Create Date: 2026-04-30
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "sprint86_d6_inter_tables"
down_revision = "sprint85_d5_4_certidoes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── inter_transactions (D6.1) ─────────────────────────────────────────
    op.create_table(
        "inter_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("data_lancamento", sa.Date, nullable=False),
        sa.Column("data_inclusao", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tipo_operacao", sa.String(2), nullable=False),  # 'C' ou 'D'
        sa.Column("tipo_transacao", sa.String(50), nullable=True),  # PIX, BOLETO, TED...
        sa.Column("valor", sa.Numeric(15, 2), nullable=False),
        sa.Column("titulo", sa.String(255), nullable=True),
        sa.Column("descricao", sa.Text, nullable=True),
        sa.Column("detalhes_pagador", postgresql.JSONB, nullable=True),
        sa.Column("detalhes_destinatario", postgresql.JSONB, nullable=True),
        sa.Column("raw_payload", postgresql.JSONB, nullable=True),
        sa.Column("matched_conciliacao_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_inter_transactions_data_lancamento", "inter_transactions", ["data_lancamento"])
    op.create_index("ix_inter_transactions_tipo_operacao", "inter_transactions", ["tipo_operacao"])
    op.create_unique_constraint(
        "uq_inter_transactions_dedup",
        "inter_transactions",
        ["data_lancamento", "tipo_operacao", "valor", "descricao"],
    )

    # ── inter_cobrancas (D6.3) ────────────────────────────────────────────
    op.create_table(
        "inter_cobrancas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("cobranca_id_inter", sa.String(255), unique=True, nullable=True),
        sa.Column("seu_numero", sa.String(15), unique=True, nullable=True),
        sa.Column("valor", sa.Numeric(15, 2), nullable=False),
        sa.Column("vencimento", sa.Date, nullable=False),
        sa.Column("pagador", postgresql.JSONB, nullable=True),
        sa.Column("status", sa.String(30), nullable=True),  # RECEBIDO, A_RECEBER...
        sa.Column("url_boleto", sa.Text, nullable=True),
        sa.Column("pix_copia_cola", sa.Text, nullable=True),
        sa.Column("barcode", sa.Text, nullable=True),
        sa.Column("linha_digitavel", sa.Text, nullable=True),
        sa.Column("descricao", sa.Text, nullable=True),
        sa.Column("raw_payload", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_inter_cobrancas_status", "inter_cobrancas", ["status"])
    op.create_index("ix_inter_cobrancas_vencimento", "inter_cobrancas", ["vencimento"])

    # ── inter_pix_recebidos (D6.4) ────────────────────────────────────────
    op.create_table(
        "inter_pix_recebidos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("end_to_end_id", sa.String(32), unique=True, nullable=False),
        sa.Column("txid", sa.String(35), nullable=True),
        sa.Column("valor", sa.Numeric(15, 2), nullable=False),
        sa.Column("pagador", postgresql.JSONB, nullable=True),
        sa.Column("data_horario", sa.DateTime(timezone=True), nullable=True),
        sa.Column("inter_transaction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("cobranca_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("raw_payload", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_inter_pix_recebidos_data", "inter_pix_recebidos", ["data_horario"])

    # ── inter_conciliacao_folha (D6.2) ────────────────────────────────────
    op.create_table(
        "inter_conciliacao_folha",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("competencia", sa.String(7), nullable=False),  # '2026-04'
        sa.Column("valor_liquido", sa.Numeric(15, 2), nullable=True),
        sa.Column("data_prevista", sa.Date, nullable=True),
        sa.Column("data_paga", sa.Date, nullable=True),
        sa.Column("inter_transaction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "status", sa.String(20), nullable=False, server_default="previsto"
        ),  # previsto|pago|em_conciliacao|divergente
        sa.Column("match_tipo", sa.String(10), nullable=True),  # forte|medio|fraco
        sa.Column("observacoes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_inter_conciliacao_competencia", "inter_conciliacao_folha", ["competencia"])
    op.create_index("ix_inter_conciliacao_employee", "inter_conciliacao_folha", ["employee_id"])
    op.create_index("ix_inter_conciliacao_status", "inter_conciliacao_folha", ["status"])


def downgrade() -> None:
    op.drop_table("inter_conciliacao_folha")
    op.drop_table("inter_pix_recebidos")
    op.drop_table("inter_cobrancas")
    op.drop_table("inter_transactions")
