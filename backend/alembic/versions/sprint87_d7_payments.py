"""D7 — inter_payments + inter_payment_otp + inter_payment_audit + função limite diário.

Revision ID: sprint87_d7_payments
Revises: sprint86_d6_inter_addendum
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

from alembic import op

revision = "sprint87_d7_payments"
down_revision = "sprint86_d6_inter_addendum"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── inter_payments ────────────────────────────────────────────────────────
    op.create_table(
        "inter_payments",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("payment_type", sa.String(20), nullable=False),
        sa.Column("destinatario", JSONB, nullable=False),
        sa.Column("valor", sa.Numeric(15, 2), nullable=False),
        sa.Column("data_pagamento", sa.Date, nullable=False),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="preparado",
        ),
        sa.Column("prepared_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("approved_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approval_otp_used", sa.String(6), nullable=True),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("cancel_reason", sa.Text, nullable=True),
        sa.Column("inter_payment_id", sa.String(255), nullable=True),
        sa.Column("inter_response", JSONB, nullable=True),
        sa.Column("inter_transaction_id", UUID(as_uuid=True), sa.ForeignKey("inter_transactions.id"), nullable=True),
        sa.Column("observacoes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("valor > 0", name="ck_inter_payments_valor_positivo"),
        sa.CheckConstraint(
            "status IN ('preparado','aprovado','executado','confirmado','cancelado','erro')",
            name="ck_inter_payments_status",
        ),
    )
    op.create_index("idx_inter_payments_status", "inter_payments", ["status"])
    op.create_index("idx_inter_payments_type", "inter_payments", ["payment_type"])
    op.create_index("idx_inter_payments_data", "inter_payments", ["data_pagamento"])

    # ── inter_payment_otp ─────────────────────────────────────────────────────
    op.create_table(
        "inter_payment_otp",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column(
            "payment_id", UUID(as_uuid=True), sa.ForeignKey("inter_payments.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("code", sa.String(6), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used", sa.Boolean, server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_inter_payment_otp_payment_id", "inter_payment_otp", ["payment_id"])

    # ── inter_payment_audit ───────────────────────────────────────────────────
    op.create_table(
        "inter_payment_audit",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column(
            "payment_id", UUID(as_uuid=True), sa.ForeignKey("inter_payments.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("status_from", sa.String(20), nullable=True),
        sa.Column("status_to", sa.String(20), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("motivo", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_inter_payment_audit_payment_id", "inter_payment_audit", ["payment_id"])

    # ── função SQL limite diário ──────────────────────────────────────────────
    op.execute("""
        CREATE OR REPLACE FUNCTION get_limite_diario_consumido()
        RETURNS NUMERIC AS $$
            SELECT COALESCE(SUM(valor), 0)
            FROM inter_payments
            WHERE status IN ('aprovado','executado','confirmado')
            AND DATE(approved_at) = CURRENT_DATE;
        $$ LANGUAGE SQL;
    """)


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS get_limite_diario_consumido()")
    op.drop_table("inter_payment_audit")
    op.drop_table("inter_payment_otp")
    op.drop_table("inter_payments")
