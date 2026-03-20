"""add rh motivos desligamento onboarding absenteismo

Revision ID: sprint76_rh_structs
Revises: sprint75_gp_ponto_sst
Create Date: 2026-03-15
"""

import sqlalchemy as sa

from alembic import op

revision = "sprint76_rh_structs"
down_revision = "sprint75_gp_ponto_sst"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Colunas em employees
    op.add_column("employees", sa.Column("motivo_desligamento", sa.String(100), nullable=True))
    op.add_column("employees", sa.Column("data_desligamento", sa.Date(), nullable=True))
    op.add_column("employees", sa.Column("observacao_desligamento", sa.Text(), nullable=True))

    # Tabela motivos desligamento
    op.create_table(
        "rh_motivos_desligamento",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("codigo", sa.String(50), nullable=False, unique=True),
        sa.Column("descricao", sa.String(100), nullable=False),
        sa.Column("categoria", sa.String(50), nullable=False),
        sa.Column("gera_multa_fgts", sa.Boolean(), server_default="false"),
        sa.Column("requer_homologacao_sindicato", sa.Boolean(), server_default="false"),
        sa.Column("ativo", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
    )

    # Tabela onboarding templates
    op.create_table(
        "rh_onboarding_templates",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("cargo", sa.String(100), server_default="TODOS"),
        sa.Column("etapa", sa.Integer(), nullable=False),
        sa.Column("titulo", sa.String(100), nullable=False),
        sa.Column("descricao", sa.Text()),
        sa.Column("responsavel", sa.String(50), nullable=False),
        sa.Column("prazo_dias", sa.Integer(), nullable=False),
        sa.Column("obrigatorio", sa.Boolean(), server_default="true"),
        sa.Column("ativo", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
    )

    # Tabela onboarding checklist
    op.create_table(
        "rh_onboarding_checklist",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("employee_id", sa.dialects.postgresql.UUID(), nullable=False),
        sa.Column("template_id", sa.Integer(), sa.ForeignKey("rh_onboarding_templates.id"), nullable=False),
        sa.Column("etapa", sa.Integer(), nullable=False),
        sa.Column("titulo", sa.String(100), nullable=False),
        sa.Column("responsavel", sa.String(50), nullable=False),
        sa.Column("prazo_data", sa.Date(), nullable=False),
        sa.Column("concluido", sa.Boolean(), server_default="false"),
        sa.Column("data_conclusao", sa.Date()),
        sa.Column("observacao", sa.Text()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
    )

    # View alertas absenteismo
    op.execute("""
        CREATE OR REPLACE VIEW rh_alertas_absenteismo AS
        SELECT e.id as employee_id, e.nome as nome_colaborador, e.cargo,
               a.tipo as tipo_afastamento, a.data_inicio,
               a.data_fim_prevista as data_fim,
               CURRENT_DATE - a.data_inicio as dias_afastado,
               CASE WHEN CURRENT_DATE - a.data_inicio >= 15 AND (a.status != 'inss' OR a.status IS NULL) THEN 'INSS_PENDENTE'
                    WHEN a.ajuda_medicamento_ativa = TRUE AND a.data_fim_prevista IS NULL THEN 'AJUDA_MEDICAMENTO_ATIVA'
                    WHEN a.gera_estabilidade = TRUE THEN 'EM_ESTABILIDADE'
                    ELSE 'MONITORAR' END as status_alerta,
               a.ajuda_medicamento_ativa, a.ajuda_medicamento_valor,
               a.gera_estabilidade as estabilidade_ativa, a.estabilidade_ate as data_fim_estabilidade
        FROM sst_afastamentos a JOIN employees e ON e.id = a.employee_id
        WHERE a.data_fim_prevista IS NULL OR a.data_fim_prevista >= CURRENT_DATE
        ORDER BY a.data_inicio ASC
    """)


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS rh_alertas_absenteismo")
    op.drop_table("rh_onboarding_checklist")
    op.drop_table("rh_onboarding_templates")
    op.drop_table("rh_motivos_desligamento")
    op.drop_column("employees", "observacao_desligamento")
    op.drop_column("employees", "data_desligamento")
    op.drop_column("employees", "motivo_desligamento")
