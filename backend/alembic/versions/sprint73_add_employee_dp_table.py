"""Add employee_dp table — Dados trabalhistas estendidos (80 campos CLT).

Tabela complementar ao employees (operacional) com documentação trabalhista,
dados bancários, adicionais, benefícios, sindicato, eSocial e FGTS.

Revision ID: sprint73_employee_dp
Revises: sprint72_people_management
Create Date: 2026-03-12
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "sprint73_employee_dp"
down_revision = "sprint72_people_management"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "employee_dp",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("employee_id", postgresql.UUID(as_uuid=False), nullable=False, unique=True),
        # --- DOCUMENTACAO TRABALHISTA ---
        sa.Column("ctps_numero", sa.String(20), nullable=True),
        sa.Column("ctps_serie", sa.String(10), nullable=True),
        sa.Column("ctps_uf", sa.String(2), nullable=True),
        sa.Column("ctps_data_emissao", sa.Date, nullable=True),
        sa.Column("pis_pasep", sa.String(15), nullable=True, unique=True),
        sa.Column("nit", sa.String(15), nullable=True),
        sa.Column("titulo_eleitor", sa.String(15), nullable=True),
        sa.Column("titulo_zona", sa.String(5), nullable=True),
        sa.Column("titulo_secao", sa.String(5), nullable=True),
        sa.Column("certificado_reservista", sa.String(15), nullable=True),
        sa.Column("cnh_numero", sa.String(15), nullable=True),
        sa.Column("cnh_categoria", sa.String(3), nullable=True),
        sa.Column("cnh_validade", sa.Date, nullable=True),
        # --- DADOS PESSOAIS COMPLEMENTARES ---
        sa.Column("nome_mae", sa.String(200), nullable=True),
        sa.Column("nome_pai", sa.String(200), nullable=True),
        sa.Column("estado_civil", sa.String(20), nullable=True),
        sa.Column("grau_instrucao", sa.String(50), nullable=True),
        sa.Column("nacionalidade", sa.String(50), server_default="Brasileira"),
        sa.Column("naturalidade_cidade", sa.String(100), nullable=True),
        sa.Column("naturalidade_uf", sa.String(2), nullable=True),
        sa.Column("raca_cor", sa.String(20), nullable=True),
        sa.Column("deficiencia", sa.Boolean, server_default="false"),
        sa.Column("tipo_deficiencia", sa.String(100), nullable=True),
        # --- CONTRATO / JORNADA ---
        sa.Column("data_admissao", sa.Date, nullable=True),
        sa.Column("data_demissao", sa.Date, nullable=True),
        sa.Column("tipo_contrato", sa.String(30), server_default="indeterminado"),
        sa.Column("jornada_tipo", sa.String(30), server_default="44h_semanais"),
        sa.Column("carga_horaria_semanal", sa.Integer, server_default="44"),
        sa.Column("carga_horaria_mensal", sa.Integer, server_default="220"),
        sa.Column("horario_entrada", sa.String(5), nullable=True),
        sa.Column("horario_saida", sa.String(5), nullable=True),
        sa.Column("horario_intervalo_inicio", sa.String(5), nullable=True),
        sa.Column("horario_intervalo_fim", sa.String(5), nullable=True),
        # --- REMUNERACAO ---
        sa.Column("salario_base", sa.Numeric(12, 2), nullable=True),
        sa.Column("salario_familia", sa.Boolean, server_default="false"),
        sa.Column("quantidade_dependentes_sf", sa.Integer, server_default="0"),
        # --- ADICIONAIS LEGAIS ---
        sa.Column("adicional_periculosidade", sa.Boolean, server_default="false"),
        sa.Column("percentual_periculosidade", sa.Numeric(5, 2), server_default="30"),
        sa.Column("grau_insalubridade", sa.String(10), server_default="nenhum"),
        sa.Column("adicional_noturno", sa.Boolean, server_default="false"),
        sa.Column("percentual_noturno", sa.Numeric(5, 2), server_default="20"),
        sa.Column("adicional_transferencia", sa.Boolean, server_default="false"),
        # --- BENEFICIOS ---
        sa.Column("vale_transporte", sa.Boolean, server_default="true"),
        sa.Column("vale_refeicao", sa.Boolean, server_default="false"),
        sa.Column("valor_vale_refeicao", sa.Numeric(10, 2), nullable=True),
        sa.Column("vale_alimentacao", sa.Boolean, server_default="false"),
        sa.Column("valor_vale_alimentacao", sa.Numeric(10, 2), nullable=True),
        sa.Column("plano_saude", sa.Boolean, server_default="false"),
        sa.Column("plano_odontologico", sa.Boolean, server_default="false"),
        sa.Column("seguro_vida", sa.Boolean, server_default="false"),
        # --- SINDICATO ---
        sa.Column("sindicato_nome", sa.String(200), nullable=True),
        sa.Column("sindicato_cnpj", sa.String(18), nullable=True),
        sa.Column("contribuicao_sindical", sa.Boolean, server_default="false"),
        sa.Column("data_base_categoria", sa.String(5), nullable=True),
        # --- DADOS BANCARIOS ---
        sa.Column("banco_codigo", sa.String(5), nullable=True),
        sa.Column("banco_nome", sa.String(100), nullable=True),
        sa.Column("agencia", sa.String(10), nullable=True),
        sa.Column("agencia_digito", sa.String(2), nullable=True),
        sa.Column("conta", sa.String(15), nullable=True),
        sa.Column("conta_digito", sa.String(2), nullable=True),
        sa.Column("tipo_conta", sa.String(20), server_default="corrente"),
        sa.Column("chave_pix", sa.String(100), nullable=True),
        # --- DEPENDENTES ---
        sa.Column("dependentes", postgresql.JSONB, nullable=True),
        # --- eSocial ---
        sa.Column("matricula_esocial", sa.String(30), nullable=True, unique=True),
        sa.Column("categoria_trabalhador", sa.String(5), server_default="101"),
        sa.Column("cod_cbo", sa.String(10), nullable=True),
        # --- FERIAS / AFASTAMENTO ---
        sa.Column("periodo_aquisitivo_inicio", sa.Date, nullable=True),
        sa.Column("ferias_vencidas", sa.Boolean, server_default="false"),
        sa.Column("afastamento_atual", sa.String(50), nullable=True),
        sa.Column("data_retorno_previsto", sa.Date, nullable=True),
        # --- FGTS ---
        sa.Column("optante_fgts", sa.Boolean, server_default="true"),
        sa.Column("data_opcao_fgts", sa.Date, nullable=True),
        sa.Column("conta_fgts", sa.String(30), nullable=True),
        sa.Column("saldo_fgts_estimado", sa.Numeric(14, 2), nullable=True),
        # --- METADATA ---
        sa.Column("observacoes", sa.Text, nullable=True),
        sa.Column("dados_extras", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_index("ix_employee_dp_employee_id", "employee_dp", ["employee_id"])


def downgrade():
    op.drop_index("ix_employee_dp_employee_id", table_name="employee_dp")
    op.drop_table("employee_dp")
