"""Sprint 32 - Create diarists tables.

Revision ID: sprint32_diarists
Revises: sprint31_document_kits
Create Date: 2025-01-01 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "sprint32_diarists"
down_revision: str | None = "sprint31_document_kits"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create diarists tables."""
    # Enum types
    op.execute("""
        CREATE TYPE diarist_type AS ENUM (
            'LIMPEZA', 'FAXINA', 'PASSADEIRA', 'COZINHEIRA',
            'BABA', 'CUIDADORA', 'JARDINEIRO', 'MANUTENCAO', 'OUTROS'
        )
    """)

    op.execute("""
        CREATE TYPE diarist_status AS ENUM (
            'ATIVO', 'INATIVO', 'SUSPENSO', 'PENDENTE', 'BLOQUEADO'
        )
    """)

    op.execute("""
        CREATE TYPE document_type AS ENUM (
            'RG', 'CPF', 'COMPROVANTE_RESIDENCIA', 'ANTECEDENTES',
            'CTPS', 'CERTIFICADO', 'OUTROS'
        )
    """)

    op.execute("""
        CREATE TYPE assignment_type AS ENUM (
            'CONDOMINIO', 'UNIDADE', 'AREA_COMUM'
        )
    """)

    op.execute("""
        CREATE TYPE assignment_status AS ENUM (
            'ATIVO', 'PAUSADO', 'ENCERRADO', 'CANCELADO'
        )
    """)

    op.execute("""
        CREATE TYPE recurrence_type AS ENUM (
            'AVULSO', 'SEMANAL', 'QUINZENAL', 'MENSAL'
        )
    """)

    op.execute("""
        CREATE TYPE schedule_status AS ENUM (
            'AGENDADO', 'CONFIRMADO', 'EM_ANDAMENTO',
            'CONCLUIDO', 'CANCELADO', 'NAO_COMPARECEU'
        )
    """)

    op.execute("""
        CREATE TYPE payment_status AS ENUM (
            'PENDENTE', 'APROVADO', 'PAGO', 'CANCELADO', 'ESTORNADO'
        )
    """)

    op.execute("""
        CREATE TYPE payment_method AS ENUM (
            'PIX', 'TRANSFERENCIA', 'DINHEIRO', 'CHEQUE', 'BOLETO'
        )
    """)

    op.execute("""
        CREATE TYPE weekday AS ENUM (
            'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY',
            'FRIDAY', 'SATURDAY', 'SUNDAY'
        )
    """)

    # Table: diarists
    op.create_table(
        "diarists",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False, default=True),
        # Dados pessoais
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("cpf", sa.String(14), nullable=False, unique=True),
        sa.Column("rg", sa.String(20), nullable=True),
        sa.Column("data_nascimento", sa.Date(), nullable=True),
        sa.Column("telefone", sa.String(20), nullable=False),
        sa.Column("telefone_emergencia", sa.String(20), nullable=True),
        sa.Column("email", sa.String(200), nullable=True),
        sa.Column("foto_url", sa.String(500), nullable=True),
        # Endereço
        sa.Column("endereco", sa.String(300), nullable=True),
        sa.Column("cidade", sa.String(100), nullable=True),
        sa.Column("estado", sa.String(2), nullable=True),
        sa.Column("cep", sa.String(10), nullable=True),
        # Profissional
        sa.Column(
            "tipos_servico",
            postgresql.ARRAY(
                sa.Enum(
                    "LIMPEZA",
                    "FAXINA",
                    "PASSADEIRA",
                    "COZINHEIRA",
                    "BABA",
                    "CUIDADORA",
                    "JARDINEIRO",
                    "MANUTENCAO",
                    "OUTROS",
                    name="diarist_type_array",
                    create_type=False,
                )
            ),
            nullable=True,
        ),
        sa.Column("especialidades", postgresql.ARRAY(sa.String), nullable=True),
        sa.Column("experiencia_anos", sa.Integer(), nullable=True),
        sa.Column("referencias", postgresql.JSONB, nullable=True),
        sa.Column("documentos", postgresql.JSONB, nullable=True),
        # Disponibilidade
        sa.Column(
            "dias_disponiveis",
            postgresql.ARRAY(
                sa.Enum(
                    "MONDAY",
                    "TUESDAY",
                    "WEDNESDAY",
                    "THURSDAY",
                    "FRIDAY",
                    "SATURDAY",
                    "SUNDAY",
                    name="weekday_array",
                    create_type=False,
                )
            ),
            nullable=True,
        ),
        sa.Column("hora_inicio_disponivel", sa.Time(), nullable=True),
        sa.Column("hora_fim_disponivel", sa.Time(), nullable=True),
        sa.Column("aceita_hora_extra", sa.Boolean(), default=False),
        # Financeiro
        sa.Column("valor_hora", sa.Numeric(10, 2), nullable=True),
        sa.Column("valor_diaria", sa.Numeric(10, 2), nullable=True),
        sa.Column("valor_hora_extra", sa.Numeric(10, 2), nullable=True),
        sa.Column("banco", sa.String(100), nullable=True),
        sa.Column("agencia", sa.String(20), nullable=True),
        sa.Column("conta", sa.String(30), nullable=True),
        sa.Column("tipo_conta", sa.String(20), nullable=True),
        sa.Column("pix", sa.String(100), nullable=True),
        # Status e métricas
        sa.Column(
            "status",
            postgresql.ENUM(
                "ATIVO", "INATIVO", "SUSPENSO", "PENDENTE", "BLOQUEADO", name="diarist_status", create_type=False
            ),
            nullable=False,
            default="PENDENTE",
        ),
        sa.Column("avaliacao_media", sa.Numeric(3, 2), default=0),
        sa.Column("total_avaliacoes", sa.Integer(), default=0),
        sa.Column("total_servicos", sa.Integer(), default=0),
        sa.Column("valor_total_recebido", sa.Numeric(12, 2), default=0),
        # IA
        sa.Column("score_confiabilidade", sa.Numeric(5, 2), nullable=True),
        sa.Column("score_qualidade", sa.Numeric(5, 2), nullable=True),
        sa.Column("score_pontualidade", sa.Numeric(5, 2), nullable=True),
        sa.Column("ultima_analise_ia", sa.DateTime(), nullable=True),
        # Observações
        sa.Column("observacoes", sa.Text(), nullable=True),
    )

    op.create_index("ix_diarists_cpf", "diarists", ["cpf"])
    op.create_index("ix_diarists_status", "diarists", ["status"])
    op.create_index("ix_diarists_nome", "diarists", ["nome"])

    # Table: diarist_assignments
    op.create_table(
        "diarist_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False, default=True),
        sa.Column(
            "diarist_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("diarists.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("unidade_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "tipo",
            postgresql.ENUM("CONDOMINIO", "UNIDADE", "AREA_COMUM", name="assignment_type", create_type=False),
            nullable=False,
        ),
        sa.Column("descricao", sa.String(500), nullable=True),
        # Período
        sa.Column("data_inicio", sa.Date(), nullable=False),
        sa.Column("data_fim", sa.Date(), nullable=True),
        # Recorrência
        sa.Column(
            "recorrencia",
            postgresql.ENUM("AVULSO", "SEMANAL", "QUINZENAL", "MENSAL", name="recurrence_type", create_type=False),
            nullable=False,
            default="AVULSO",
        ),
        sa.Column(
            "dias_semana",
            postgresql.ARRAY(
                sa.Enum(
                    "MONDAY",
                    "TUESDAY",
                    "WEDNESDAY",
                    "THURSDAY",
                    "FRIDAY",
                    "SATURDAY",
                    "SUNDAY",
                    name="weekday_array2",
                    create_type=False,
                )
            ),
            nullable=True,
        ),
        sa.Column("hora_inicio", sa.Time(), nullable=True),
        sa.Column("hora_fim", sa.Time(), nullable=True),
        # Valores
        sa.Column("valor_acordado", sa.Numeric(10, 2), nullable=True),
        # Status
        sa.Column(
            "status",
            postgresql.ENUM("ATIVO", "PAUSADO", "ENCERRADO", "CANCELADO", name="assignment_status", create_type=False),
            nullable=False,
            default="ATIVO",
        ),
        sa.Column("observacoes", sa.Text(), nullable=True),
    )

    op.create_index("ix_diarist_assignments_diarist_id", "diarist_assignments", ["diarist_id"])
    op.create_index("ix_diarist_assignments_condominio_id", "diarist_assignments", ["condominio_id"])
    op.create_index("ix_diarist_assignments_status", "diarist_assignments", ["status"])

    # Table: diarist_schedules
    op.create_table(
        "diarist_schedules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False, default=True),
        sa.Column(
            "diarist_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("diarists.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "assignment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("diarist_assignments.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("unidade_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Data/hora planejada
        sa.Column("data_trabalho", sa.Date(), nullable=False),
        sa.Column("hora_inicio", sa.Time(), nullable=True),
        sa.Column("hora_fim", sa.Time(), nullable=True),
        # Check-in/Check-out real
        sa.Column("checkin_real", sa.DateTime(), nullable=True),
        sa.Column("checkout_real", sa.DateTime(), nullable=True),
        sa.Column("checkin_latitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("checkin_longitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("checkout_latitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("checkout_longitude", sa.Numeric(10, 7), nullable=True),
        # Valores
        sa.Column("valor_previsto", sa.Numeric(10, 2), nullable=True),
        sa.Column("valor_final", sa.Numeric(10, 2), nullable=True),
        # Status
        sa.Column(
            "status",
            postgresql.ENUM(
                "AGENDADO",
                "CONFIRMADO",
                "EM_ANDAMENTO",
                "CONCLUIDO",
                "CANCELADO",
                "NAO_COMPARECEU",
                name="schedule_status",
                create_type=False,
            ),
            nullable=False,
            default="AGENDADO",
        ),
        # Detalhes
        sa.Column("tarefas", postgresql.ARRAY(sa.String), nullable=True),
        sa.Column("observacoes", sa.Text(), nullable=True),
    )

    op.create_index("ix_diarist_schedules_diarist_id", "diarist_schedules", ["diarist_id"])
    op.create_index("ix_diarist_schedules_condominio_id", "diarist_schedules", ["condominio_id"])
    op.create_index("ix_diarist_schedules_data_trabalho", "diarist_schedules", ["data_trabalho"])
    op.create_index("ix_diarist_schedules_status", "diarist_schedules", ["status"])

    # Table: diarist_payments
    op.create_table(
        "diarist_payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False, default=True),
        sa.Column(
            "diarist_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("diarists.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Período
        sa.Column("data_referencia", sa.Date(), nullable=False),
        sa.Column("data_vencimento", sa.Date(), nullable=True),
        sa.Column("data_pagamento", sa.Date(), nullable=True),
        # Valores
        sa.Column("valor_bruto", sa.Numeric(10, 2), nullable=False),
        sa.Column("retencao_inss", sa.Numeric(10, 2), default=0),
        sa.Column("retencao_iss", sa.Numeric(10, 2), default=0),
        sa.Column("retencao_irrf", sa.Numeric(10, 2), default=0),
        sa.Column("outros_descontos", sa.Numeric(10, 2), default=0),
        sa.Column("valor_liquido", sa.Numeric(10, 2), nullable=False),
        # Pagamento
        sa.Column(
            "forma_pagamento",
            postgresql.ENUM(
                "PIX", "TRANSFERENCIA", "DINHEIRO", "CHEQUE", "BOLETO", name="payment_method", create_type=False
            ),
            nullable=True,
        ),
        sa.Column("comprovante_url", sa.String(500), nullable=True),
        # Status
        sa.Column(
            "status",
            postgresql.ENUM(
                "PENDENTE", "APROVADO", "PAGO", "CANCELADO", "ESTORNADO", name="payment_status", create_type=False
            ),
            nullable=False,
            default="PENDENTE",
        ),
        # Referências
        sa.Column("schedules_ids", postgresql.ARRAY(sa.String), nullable=True),
        sa.Column("descricao", sa.Text(), nullable=True),
    )

    op.create_index("ix_diarist_payments_diarist_id", "diarist_payments", ["diarist_id"])
    op.create_index("ix_diarist_payments_condominio_id", "diarist_payments", ["condominio_id"])
    op.create_index("ix_diarist_payments_status", "diarist_payments", ["status"])
    op.create_index("ix_diarist_payments_data_referencia", "diarist_payments", ["data_referencia"])

    # Table: diarist_evaluations
    op.create_table(
        "diarist_evaluations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False, default=True),
        sa.Column(
            "diarist_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("diarists.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "schedule_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("diarist_schedules.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("avaliador_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Notas (1-5)
        sa.Column("nota_geral", sa.Integer(), nullable=False),
        sa.Column("nota_pontualidade", sa.Integer(), nullable=True),
        sa.Column("nota_qualidade", sa.Integer(), nullable=True),
        sa.Column("nota_comportamento", sa.Integer(), nullable=True),
        sa.Column("nota_comunicacao", sa.Integer(), nullable=True),
        # Feedback
        sa.Column("comentario", sa.Text(), nullable=True),
        sa.Column("recomendaria", sa.Boolean(), default=True),
    )

    op.create_index("ix_diarist_evaluations_diarist_id", "diarist_evaluations", ["diarist_id"])
    op.create_index("ix_diarist_evaluations_schedule_id", "diarist_evaluations", ["schedule_id"])
    op.create_index("ix_diarist_evaluations_nota_geral", "diarist_evaluations", ["nota_geral"])


def downgrade() -> None:
    """Drop diarists tables."""
    op.drop_table("diarist_evaluations")
    op.drop_table("diarist_payments")
    op.drop_table("diarist_schedules")
    op.drop_table("diarist_assignments")
    op.drop_table("diarists")

    op.execute("DROP TYPE IF EXISTS weekday")
    op.execute("DROP TYPE IF EXISTS payment_method")
    op.execute("DROP TYPE IF EXISTS payment_status")
    op.execute("DROP TYPE IF EXISTS schedule_status")
    op.execute("DROP TYPE IF EXISTS recurrence_type")
    op.execute("DROP TYPE IF EXISTS assignment_status")
    op.execute("DROP TYPE IF EXISTS assignment_type")
    op.execute("DROP TYPE IF EXISTS document_type")
    op.execute("DROP TYPE IF EXISTS diarist_status")
    op.execute("DROP TYPE IF EXISTS diarist_type")
