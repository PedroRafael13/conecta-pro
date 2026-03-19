"""sprint75: Create GP Ponto Eletronico and SST tables

Revision ID: sprint75_gp_ponto_sst
Revises: sprint74_ged_client_portal_tables
Create Date: 2026-03-13
"""

import sqlalchemy as sa

from alembic import op

revision = "sprint75_gp_ponto_sst"
down_revision = "sprint74_ged_client_portal"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Ponto - Batidas
    op.create_table(
        "gp_clock_punches",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("punch_id", sa.String(36), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("punch_type", sa.String(20), nullable=False),
        sa.Column("punch_timestamp", sa.DateTime(), nullable=False),
        sa.Column("server_timestamp", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="normal"),
        sa.Column("facial_match", sa.Boolean(), nullable=True),
        sa.Column("facial_confidence", sa.Float(), nullable=True),
        sa.Column("facial_liveness", sa.Boolean(), nullable=True),
        sa.Column("foto_capturada_url", sa.String(500), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("accuracy", sa.Float(), nullable=True),
        sa.Column("dentro_geofence", sa.Boolean(), nullable=True),
        sa.Column("distancia_posto_metros", sa.Float(), nullable=True),
        sa.Column("device_type", sa.String(20), nullable=False, server_default="web"),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("is_offline", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("synced_at", sa.DateTime(), nullable=True),
        sa.Column("sync_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("posto_id", sa.Integer(), nullable=True),
        sa.Column("posto_nome", sa.String(255), nullable=True),
        sa.Column("justification_id", sa.String(36), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_by", sa.String(36), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("punch_id"),
    )
    op.create_index("ix_gp_punch_employee_date", "gp_clock_punches", ["employee_id", "punch_timestamp"])
    op.create_index("ix_gp_punch_offline", "gp_clock_punches", ["is_offline", "synced_at"])
    op.create_index("ix_gp_punch_id", "gp_clock_punches", ["punch_id"])

    # Ponto - Justificativas
    op.create_table(
        "gp_justifications",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("justification_id", sa.String(36), nullable=False),
        sa.Column("punch_id", sa.String(36), nullable=True),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("justification_type", sa.String(20), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("category", sa.String(30), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pendente"),
        sa.Column("attachments", sa.JSON(), nullable=True),
        sa.Column("reviewed_by", sa.String(36), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.Column("review_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("justification_id"),
    )
    op.create_index("ix_gp_justification_employee", "gp_justifications", ["employee_id"])
    op.create_index("ix_gp_justification_status", "gp_justifications", ["status", "employee_id"])

    # Ponto - Fechamento Mensal
    op.create_table(
        "gp_monthly_closings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("total_horas_trabalhadas", sa.Float(), server_default="0"),
        sa.Column("total_horas_extras_50", sa.Float(), server_default="0"),
        sa.Column("total_horas_extras_100", sa.Float(), server_default="0"),
        sa.Column("total_horas_noturnas", sa.Float(), server_default="0"),
        sa.Column("total_faltas", sa.Integer(), server_default="0"),
        sa.Column("total_atrasos_minutos", sa.Float(), server_default="0"),
        sa.Column("total_dias_trabalhados", sa.Integer(), server_default="0"),
        sa.Column("fechado", sa.Boolean(), server_default="false"),
        sa.Column("fechado_por", sa.String(36), nullable=True),
        sa.Column("fechado_em", sa.DateTime(), nullable=True),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_gp_closing_employee", "gp_monthly_closings", ["employee_id", "year", "month"])

    # SST - ASOs
    op.create_table(
        "gp_asos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("aso_id", sa.String(36), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="agendado"),
        sa.Column("data_agendamento", sa.Date(), nullable=True),
        sa.Column("data_realizacao", sa.Date(), nullable=True),
        sa.Column("data_validade", sa.Date(), nullable=True),
        sa.Column("clinica", sa.String(255), nullable=True),
        sa.Column("medico", sa.String(255), nullable=True),
        sa.Column("crm", sa.String(20), nullable=True),
        sa.Column("apto", sa.Boolean(), nullable=True),
        sa.Column("restricoes", sa.JSON(), nullable=True),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("documento_url", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("aso_id"),
    )
    op.create_index("ix_gp_aso_employee", "gp_asos", ["employee_id"])

    # SST - EPIs
    op.create_table(
        "gp_epi_deliveries",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("delivery_id", sa.String(36), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("epi_nome", sa.String(255), nullable=False),
        sa.Column("epi_ca", sa.String(20), nullable=True),
        sa.Column("quantidade", sa.Integer(), server_default="1"),
        sa.Column("nr", sa.String(10), server_default="NR-6"),
        sa.Column("data_entrega", sa.Date(), nullable=False),
        sa.Column("data_validade", sa.Date(), nullable=True),
        sa.Column("data_devolucao", sa.Date(), nullable=True),
        sa.Column("motivo_devolucao", sa.Text(), nullable=True),
        sa.Column("assinatura_funcionario", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("delivery_id"),
    )
    op.create_index("ix_gp_epi_employee", "gp_epi_deliveries", ["employee_id"])

    # SST - CATs
    op.create_table(
        "gp_cats",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cat_id", sa.String(36), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("tipo_acidente", sa.String(50), nullable=False),
        sa.Column("data_acidente", sa.Date(), nullable=False),
        sa.Column("hora_acidente", sa.String(5), nullable=True),
        sa.Column("local", sa.String(255), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column("gravidade", sa.String(20), server_default="leve"),
        sa.Column("parte_corpo", sa.String(100), nullable=True),
        sa.Column("agente_causador", sa.String(255), nullable=True),
        sa.Column("testemunhas", sa.JSON(), nullable=True),
        sa.Column("afastamento", sa.Integer(), server_default="0"),
        sa.Column("numero_cat_inss", sa.String(20), nullable=True),
        sa.Column("status", sa.String(20), server_default="aberta"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cat_id"),
    )
    op.create_index("ix_gp_cat_employee", "gp_cats", ["employee_id"])

    # SST - Riscos
    op.create_table(
        "gp_risks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("risk_id", sa.String(36), nullable=False),
        sa.Column("posto_id", sa.Integer(), nullable=False),
        sa.Column("categoria", sa.String(20), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column("nivel", sa.String(20), server_default="medio"),
        sa.Column("fonte_geradora", sa.String(255), nullable=True),
        sa.Column("medidas_controle", sa.JSON(), nullable=True),
        sa.Column("epi_recomendado", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(20), server_default="identificado"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("risk_id"),
    )
    op.create_index("ix_gp_risk_posto", "gp_risks", ["posto_id"])

    # Audit Log GP
    op.create_table(
        "gp_audit_logs",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("entity", sa.String(100), nullable=False),
        sa.Column("entity_id", sa.String(36), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("source_module", sa.String(50), nullable=False),
        sa.Column("actor_user_id", sa.String(36), nullable=False),
        sa.Column("actor_user_name", sa.String(255), nullable=False),
        sa.Column("actor_user_role", sa.String(50), nullable=False),
        sa.Column("actor_user_module", sa.String(50), nullable=False),
        sa.Column("context_ip", sa.String(45), nullable=True),
        sa.Column("context_user_agent", sa.Text(), nullable=True),
        sa.Column("context_device_type", sa.String(20), nullable=True),
        sa.Column("context_session_id", sa.String(36), nullable=True),
        sa.Column("context_geolocation", sa.JSON(), nullable=True),
        sa.Column("related_funcionario_id", sa.String(36), nullable=True),
        sa.Column("related_documento_id", sa.String(36), nullable=True),
        sa.Column("changes", sa.JSON(), nullable=True),
        sa.Column("affected_modules", sa.JSON(), nullable=True),
        sa.Column("extra_data", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_gp_audit_timestamp", "gp_audit_logs", ["timestamp", "action"])
    op.create_index("ix_gp_audit_actor", "gp_audit_logs", ["actor_user_id", "entity"])


def downgrade() -> None:
    op.drop_table("gp_audit_logs")
    op.drop_table("gp_risks")
    op.drop_table("gp_cats")
    op.drop_table("gp_epi_deliveries")
    op.drop_table("gp_asos")
    op.drop_table("gp_monthly_closings")
    op.drop_table("gp_justifications")
    op.drop_table("gp_clock_punches")
