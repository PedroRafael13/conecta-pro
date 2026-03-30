"""CCT database tables with seed data — SINDECOMPRESTS/SINDICOND-AM 2026

Revision ID: sprint78_cct_db_001
Revises: sprint77_openclaw_memory
Create Date: 2026-03-30
"""

import uuid
from datetime import date

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "sprint78_cct_db_001"
down_revision = "sprint77_openclaw_memory"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # =========================================================================
    # 1. CRIAR TABELA: cct_convencoes
    # =========================================================================
    op.create_table(
        "cct_convencoes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("sindicato_trabalhadores", sa.String(200), nullable=False),
        sa.Column("sindicato_trabalhadores_cnpj", sa.String(20), nullable=True),
        sa.Column("sindicato_patronal", sa.String(200), nullable=False),
        sa.Column("sindicato_patronal_cnpj", sa.String(20), nullable=True),
        sa.Column("registro_mte", sa.String(50), nullable=True),
        sa.Column("data_inicio", sa.Date, nullable=False),
        sa.Column("data_fim", sa.Date, nullable=False),
        sa.Column("data_base", sa.String(5), nullable=True),
        sa.Column("municipio", sa.String(100), nullable=True),
        sa.Column("uf", sa.String(2), nullable=True),
        sa.Column("descricao", sa.Text, nullable=True),
        sa.Column("is_vigente", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # =========================================================================
    # 2. CRIAR TABELA: cct_cargos
    # =========================================================================
    op.create_table(
        "cct_cargos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "convencao_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cct_convencoes.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("cargo_nome", sa.String(200), nullable=False, index=True),
        sa.Column("piso_salarial", sa.Numeric(12, 2), nullable=False),
        sa.Column("adicional_tipo", sa.String(50), nullable=True),
        sa.Column(
            "adicional_noturno_percentual",
            sa.Numeric(5, 2),
            nullable=False,
            server_default="20.0",
        ),
        sa.Column(
            "adicional_periculosidade_percentual",
            sa.Numeric(5, 2),
            nullable=False,
            server_default="30.0",
        ),
        sa.Column(
            "adicional_insalubridade_percentual",
            sa.Numeric(5, 2),
            nullable=False,
            server_default="10.0",
        ),
        sa.Column(
            "horas_extras_percentual",
            sa.Numeric(5, 2),
            nullable=False,
            server_default="50.0",
        ),
        sa.Column(
            "horas_extras_noturnas_percentual",
            sa.Numeric(5, 2),
            nullable=False,
            server_default="100.0",
        ),
        sa.Column("jornada_semanal_horas", sa.Integer, nullable=False, server_default="44"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # =========================================================================
    # 3. CRIAR TABELA: cct_feriados
    # =========================================================================
    op.create_table(
        "cct_feriados",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "convencao_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cct_convencoes.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("data_feriado", sa.Date, nullable=False, index=True),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("tipo", sa.String(20), nullable=False),
        sa.Column("ano", sa.Integer, nullable=False, index=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # =========================================================================
    # 4. CRIAR TABELA: cct_beneficios
    # =========================================================================
    op.create_table(
        "cct_beneficios",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "convencao_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cct_convencoes.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("tipo_beneficio", sa.String(50), nullable=False, index=True),
        sa.Column("valor_minimo", sa.Numeric(10, 2), nullable=True),
        sa.Column("valor_empresa", sa.Numeric(10, 2), nullable=True),
        sa.Column("desconto_maximo_percentual", sa.Numeric(5, 2), nullable=True),
        sa.Column("desconto_percentual_sobre_salario", sa.Numeric(5, 2), nullable=True),
        sa.Column("obrigatorio", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("observacao", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # =========================================================================
    # 5. SEED DATA — CCT SINDECOMPRESTS/SINDICOND-AM 2026
    # =========================================================================
    convencao_id = uuid.UUID("00000000-cct0-0000-0000-202600000001")

    # 5.1 Convenção vigente
    op.bulk_insert(
        sa.table(
            "cct_convencoes",
            sa.column("id", postgresql.UUID(as_uuid=True)),
            sa.column("sindicato_trabalhadores", sa.String),
            sa.column("sindicato_trabalhadores_cnpj", sa.String),
            sa.column("sindicato_patronal", sa.String),
            sa.column("sindicato_patronal_cnpj", sa.String),
            sa.column("registro_mte", sa.String),
            sa.column("data_inicio", sa.Date),
            sa.column("data_fim", sa.Date),
            sa.column("data_base", sa.String),
            sa.column("municipio", sa.String),
            sa.column("uf", sa.String),
            sa.column("descricao", sa.Text),
            sa.column("is_vigente", sa.Boolean),
            sa.column("is_active", sa.Boolean),
        ),
        [
            {
                "id": convencao_id,
                "sindicato_trabalhadores": "SINDECOMPRESTS",
                "sindicato_trabalhadores_cnpj": "00.444.514/0001-36",
                "sindicato_patronal": "SINDICOND-AM",
                "sindicato_patronal_cnpj": "52.753.671/0001-27",
                "registro_mte": "AM000613/2025",
                "data_inicio": date(2026, 1, 1),
                "data_fim": date(2026, 12, 31),
                "data_base": "01/01",
                "municipio": "Manaus",
                "uf": "AM",
                "descricao": (
                    "Convenção Coletiva de Trabalho 2026 entre SINDECOMPRESTS (trabalhadores) "
                    "e SINDICOND-AM (empregadores). Reajuste: 7,1% no piso / 4,5% acima do piso. "
                    "Jornada predominante: 12x36. Escala 2x1 proibida (TAC MPT 11ª Região)."
                ),
                "is_vigente": True,
                "is_active": True,
            }
        ],
    )

    # 5.2 Cargos — tabela salarial CCT 2026 (50 cargos)
    cargos_seed = [
        # (cargo_nome, piso_salarial, adicional_tipo)
        ("ADMINISTRADOR (BACHAREL)", "5854.04", None),
        ("ADMINISTRADOR DE CONDOMINIOS (PODER HIERARQUICO)", "3340.27", None),
        ("AGENTE DE FISCALIZACAO", "1670.00", None),
        ("AJUDANTE DE MANUTENCAO", "1670.00", None),
        ("AJUDANTE DE PEDREIRO CONDOMINIAL", "1670.00", None),
        ("ANALISTA DE SISTEMA", "6639.18", None),
        ("ARTIFICE DE MANUTENCAO PREDIAL (ESPECIALIZADO NRS E ISO)", "2186.66", None),
        ("ARTIFICE NAO ESPECIALIZADO", "1742.52", None),
        ("ASCENSORISTA", "1670.00", None),
        ("ASSISTENTE ADMINISTRATIVO CONDOMINIOS EMPRESAS", "2157.76", None),
        ("AUXILIAR ADMINISTRATIVO NIVEL MEDIO", "1670.00", None),
        ("AUXILIAR ADMINISTRATIVO NIVEL TECNICO", "2917.70", None),
        ("AUX ADMINISTRATIVO", "1670.00", None),
        ("AUXILIAR DE BOMBEIRO HIDRAULICO", "1670.00", None),
        ("AUXILIAR DE CONTROLE DE PRAGA HAB A", "1670.00", "insalubridade_10"),
        ("AUXILIAR DE CONTROLE DE PRAGAS HAB B", "1670.00", "insalubridade_10"),
        ("AUXILIAR DE CONTROLE DE PRAGA HAB A+B", "1679.86", "insalubridade_10"),
        ("AUXILIAR DE MANUTENCAO", "1670.00", None),
        ("AUXILIAR DE MANUTENCAO CONDOMINIOS EMPRESAS", "2072.52", None),
        ("AUXILIAR DE SERVICOS DE REFRIGERACAO", "1673.50", None),
        ("BOMBEIRO HIDRAULICO", "2232.55", None),
        ("CARPINTEIROS E PEDREIROS CONDOMINIOS EMPRESAS", "2116.67", "adicional_10"),
        ("CONCIERGE", "1670.00", None),
        ("CONTROLADOR DE ACESSO", "1670.00", None),
        ("COPEIRO A", "1670.00", None),
        ("ELETRICISTA DE ALTA TENSAO", "2180.78", "periculosidade_30"),
        ("ELETRICISTA DE BAIXA TENSAO", "1670.00", "periculosidade_30"),
        ("ENCARREGADO DE ADMINISTRACAO", "3059.78", None),
        ("ENCARREGADO DE MANUTENCAO", "3059.78", None),
        ("ENCARREGADO DE OBRA", "3059.78", None),
        ("ENCARREGADO DE PATRIMONIO", "3059.78", None),
        ("ENCARREGADO DE SERVICOS GERAIS E SUPERVISOR", "2785.26", None),
        ("FISCAL DE PATIO", "1670.00", None),
        ("JARDINEIROS", "1670.00", None),
        ("LIDER DE JARDINAGEM", "1965.97", None),
        ("LIDER DE PORTARIA", "1787.53", None),
        ("LIDER DE SERVICOS GERAIS", "1965.97", None),
        ("MANUTENCAO DE CONDOMINIOS", "2785.26", None),
        ("MONITORADOR DE CFTV", "1670.00", None),
        ("MONITORADOR ELETRONICO", "1670.00", None),
        ("PINTOR CONDOMINIAL", "2118.19", None),
        ("PISCINEIRO", "1670.00", "insalubridade_10"),
        ("PORTEIROS AGENTE DE PORTARIA GUARDETE", "1670.00", None),
        ("RECEPCIONISTA DE CONDOMINIOS", "1670.00", None),
        ("SECRETARIA DE CONDOMINIOS EMPRESAS", "2785.26", None),
        ("SERVICOS GERAIS FAXINEIRO", "1670.00", None),
        ("SUPERVISOR DE CONDOMINIOS ORGANICO", "3340.27", None),
        ("TECNICO EM MANUTENCAO EM MAQUINAS E EQUIPAMENTOS", "1870.19", "periculosidade_30"),
        ("TECNICO EM SEGURANCA DO TRABALHO", "1947.12", None),
        ("TRATORISTA MARINA", "1776.68", None),
        ("VIGIA", "1670.00", "periculosidade_30"),
        ("ZELADOR RESIDENTE CONDOMINIOS", "2777.46", None),
    ]

    cargos_rows = [
        {
            "id": uuid.uuid4(),
            "convencao_id": convencao_id,
            "cargo_nome": cargo,
            "piso_salarial": piso,
            "adicional_tipo": adicional,
            "adicional_noturno_percentual": "20.0",
            "adicional_periculosidade_percentual": "30.0",
            "adicional_insalubridade_percentual": "10.0",
            "horas_extras_percentual": "50.0",
            "horas_extras_noturnas_percentual": "100.0",
            "jornada_semanal_horas": 44,
            "is_active": True,
        }
        for cargo, piso, adicional in cargos_seed
    ]

    op.bulk_insert(
        sa.table(
            "cct_cargos",
            sa.column("id", postgresql.UUID(as_uuid=True)),
            sa.column("convencao_id", postgresql.UUID(as_uuid=True)),
            sa.column("cargo_nome", sa.String),
            sa.column("piso_salarial", sa.Numeric),
            sa.column("adicional_tipo", sa.String),
            sa.column("adicional_noturno_percentual", sa.Numeric),
            sa.column("adicional_periculosidade_percentual", sa.Numeric),
            sa.column("adicional_insalubridade_percentual", sa.Numeric),
            sa.column("horas_extras_percentual", sa.Numeric),
            sa.column("horas_extras_noturnas_percentual", sa.Numeric),
            sa.column("jornada_semanal_horas", sa.Integer),
            sa.column("is_active", sa.Boolean),
        ),
        cargos_rows,
    )

    # 5.3 Feriados Manaus/AM 2026 (16 feriados)
    feriados_seed = [
        (date(2026, 1, 1), "Confraternizacao Universal", "nacional"),
        (date(2026, 2, 17), "Carnaval (terca-feira)", "nacional"),
        (date(2026, 2, 18), "Carnaval (quarta ate 12h)", "nacional"),
        (date(2026, 4, 3), "Sexta-feira Santa", "nacional"),
        (date(2026, 4, 21), "Tiradentes", "nacional"),
        (date(2026, 5, 1), "Dia do Trabalho", "nacional"),
        (date(2026, 6, 4), "Corpus Christi", "nacional"),
        (date(2026, 9, 5), "Elevacao do Amazonas a Categoria de Provincia", "estadual"),
        (date(2026, 9, 7), "Independencia do Brasil", "nacional"),
        (date(2026, 10, 12), "Nossa Senhora Aparecida", "nacional"),
        (date(2026, 10, 24), "Aniversario de Manaus", "municipal"),
        (date(2026, 11, 2), "Finados", "nacional"),
        (date(2026, 11, 15), "Proclamacao da Republica", "nacional"),
        (date(2026, 11, 20), "Consciencia Negra", "municipal"),
        (date(2026, 12, 8), "Nossa Senhora da Conceicao", "estadual"),
        (date(2026, 12, 25), "Natal", "nacional"),
    ]

    feriados_rows = [
        {
            "id": uuid.uuid4(),
            "convencao_id": convencao_id,
            "data_feriado": dt,
            "nome": nome,
            "tipo": tipo,
            "ano": 2026,
            "is_active": True,
        }
        for dt, nome, tipo in feriados_seed
    ]

    op.bulk_insert(
        sa.table(
            "cct_feriados",
            sa.column("id", postgresql.UUID(as_uuid=True)),
            sa.column("convencao_id", postgresql.UUID(as_uuid=True)),
            sa.column("data_feriado", sa.Date),
            sa.column("nome", sa.String),
            sa.column("tipo", sa.String),
            sa.column("ano", sa.Integer),
            sa.column("is_active", sa.Boolean),
        ),
        feriados_rows,
    )

    # 5.4 Benefícios CCT 2026
    beneficios_seed = [
        # (tipo, valor_minimo, valor_empresa, desc_max_pct, desc_pct_salario, obrigatorio, observacao)
        (
            "vale_transporte",
            None,
            None,
            None,
            "4.0",
            True,
            "Desconto 4% salario base. Pode ser substituido por auxilio-combustivel mesmo desconto.",
        ),
        (
            "vale_refeicao",
            "22.00",
            None,
            None,
            "1.0",
            True,
            "R$ 22,00/dia minimo. Desconto 1% salario base.",
        ),
        (
            "plano_odontologico",
            "18.00",
            "9.00",
            "9.00",
            None,
            True,
            "R$ 18,00/trabalhador. Empresa paga minimo R$ 9,00. Desconto max R$ 9,00.",
        ),
        (
            "seguro_vida",
            "6.00",
            "4.00",
            "2.00",
            None,
            True,
            "R$ 6,00 total. Empresa R$ 4,00. Desconto trabalhador ate R$ 2,00.",
        ),
        (
            "auxilio_funeral",
            "400.00",
            None,
            None,
            None,
            True,
            "R$ 400,00 (trabalhador, conjuge, dependentes).",
        ),
        (
            "ajuda_medicamento",
            "300.00",
            None,
            None,
            None,
            True,
            "Ate R$ 300,00/mes em caso de acidente de trabalho.",
        ),
        (
            "cesta_basica",
            "170.00",
            None,
            None,
            None,
            False,
            "R$ 120,00 a R$ 170,00 (nao incorpora salario). Opcional.",
        ),
        (
            "emprestimo_consignado",
            None,
            None,
            "30.0",
            None,
            False,
            "Teto 30% dos ganhos mensais. Opcional.",
        ),
    ]

    beneficios_rows = [
        {
            "id": uuid.uuid4(),
            "convencao_id": convencao_id,
            "tipo_beneficio": tipo,
            "valor_minimo": valor_min,
            "valor_empresa": valor_emp,
            "desconto_maximo_percentual": desc_max,
            "desconto_percentual_sobre_salario": desc_sal,
            "obrigatorio": obrig,
            "observacao": obs,
            "is_active": True,
        }
        for tipo, valor_min, valor_emp, desc_max, desc_sal, obrig, obs in beneficios_seed
    ]

    op.bulk_insert(
        sa.table(
            "cct_beneficios",
            sa.column("id", postgresql.UUID(as_uuid=True)),
            sa.column("convencao_id", postgresql.UUID(as_uuid=True)),
            sa.column("tipo_beneficio", sa.String),
            sa.column("valor_minimo", sa.Numeric),
            sa.column("valor_empresa", sa.Numeric),
            sa.column("desconto_maximo_percentual", sa.Numeric),
            sa.column("desconto_percentual_sobre_salario", sa.Numeric),
            sa.column("obrigatorio", sa.Boolean),
            sa.column("observacao", sa.Text),
            sa.column("is_active", sa.Boolean),
        ),
        beneficios_rows,
    )


def downgrade() -> None:
    op.drop_table("cct_beneficios")
    op.drop_table("cct_feriados")
    op.drop_table("cct_cargos")
    op.drop_table("cct_convencoes")
