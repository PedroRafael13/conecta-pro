"""Sprint 29 - Create costing (ABC) tables.

Revision ID: sprint29_costing
Revises: sprint28_fiscal
Create Date: 2025-01-20 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "sprint29_costing"
down_revision: str | None = "sprint28_fiscal"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Cria tabelas de Custeio ABC."""

    # ===========================================
    # COST DRIVERS - Direcionadores de Custo
    # ===========================================
    op.create_table(
        "cost_drivers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("condominios.id"), nullable=False),
        sa.Column("codigo", sa.String(50), nullable=False),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("descricao", sa.Text, nullable=True),
        sa.Column("tipo", sa.String(50), nullable=False),  # RESOURCE, ACTIVITY
        sa.Column("categoria", sa.String(50), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, default="ACTIVE"),
        sa.Column("unidade_medida", sa.String(30), nullable=True),
        # Capacidade
        sa.Column("capacidade_pratica", sa.Numeric(18, 4), nullable=True),
        sa.Column("quantidade_usada", sa.Numeric(18, 4), nullable=True),
        # Custos
        sa.Column("custo_total", sa.Numeric(18, 2), nullable=False, default=0),
        sa.Column("custo_unitario", sa.Numeric(18, 6), nullable=True),
        # Período
        sa.Column("periodo_inicio", sa.Date, nullable=True),
        sa.Column("periodo_fim", sa.Date, nullable=True),
        # Metadata
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("observacoes", sa.Text, nullable=True),
        # Auditoria
        sa.Column("ativo", sa.Boolean, nullable=False, default=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_cost_drivers_condominio", "cost_drivers", ["condominio_id"])
    op.create_index("ix_cost_drivers_codigo", "cost_drivers", ["codigo"])
    op.create_index("ix_cost_drivers_tipo", "cost_drivers", ["tipo"])
    op.create_index("ix_cost_drivers_status", "cost_drivers", ["status"])
    op.create_unique_constraint("uq_cost_drivers_codigo_condo", "cost_drivers", ["condominio_id", "codigo"])

    # ===========================================
    # COST ACTIVITIES - Atividades
    # ===========================================
    op.create_table(
        "cost_activities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("condominios.id"), nullable=False),
        sa.Column("codigo", sa.String(50), nullable=False),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("descricao", sa.Text, nullable=True),
        sa.Column("tipo", sa.String(50), nullable=True),
        sa.Column("nivel", sa.String(30), nullable=True),  # UNIT, BATCH, PRODUCT, FACILITY
        sa.Column("status", sa.String(20), nullable=False, default="ACTIVE"),
        # Valor agregado
        sa.Column("tipo_valor_agregado", sa.String(30), nullable=True),  # VALUE_ADDED, NON_VALUE_ADDED, BUSINESS_VALUE
        # Driver
        sa.Column("driver_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cost_drivers.id"), nullable=True),
        # Custos
        sa.Column("custo_direto", sa.Numeric(18, 2), nullable=False, default=0),
        # Capacidade
        sa.Column("capacidade_pratica", sa.Numeric(18, 4), nullable=True),
        sa.Column("capacidade_usada", sa.Numeric(18, 4), nullable=True),
        # Output
        sa.Column("output_unidade", sa.String(50), nullable=True),
        sa.Column("output_quantidade", sa.Numeric(18, 4), nullable=True),
        # Centro de custo
        sa.Column("centro_custo_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Hierarquia
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cost_activities.id"), nullable=True),
        # Metadata
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("observacoes", sa.Text, nullable=True),
        # Auditoria
        sa.Column("ativo", sa.Boolean, nullable=False, default=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_cost_activities_condominio", "cost_activities", ["condominio_id"])
    op.create_index("ix_cost_activities_codigo", "cost_activities", ["codigo"])
    op.create_index("ix_cost_activities_nivel", "cost_activities", ["nivel"])
    op.create_index("ix_cost_activities_status", "cost_activities", ["status"])
    op.create_index("ix_cost_activities_driver", "cost_activities", ["driver_id"])
    op.create_unique_constraint("uq_cost_activities_codigo_condo", "cost_activities", ["condominio_id", "codigo"])

    # ===========================================
    # COST POOLS - Pools de Custo
    # ===========================================
    op.create_table(
        "cost_pools",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("condominios.id"), nullable=False),
        sa.Column("codigo", sa.String(50), nullable=False),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("descricao", sa.Text, nullable=True),
        sa.Column("tipo", sa.String(50), nullable=False),  # OVERHEAD, LABOR, EQUIPMENT, etc.
        sa.Column("status", sa.String(20), nullable=False, default="ACTIVE"),
        # Valores
        sa.Column("valor_total", sa.Numeric(18, 2), nullable=False, default=0),
        sa.Column("valor_alocado", sa.Numeric(18, 2), nullable=False, default=0),
        # Driver e base de alocação
        sa.Column("driver_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cost_drivers.id"), nullable=True),
        sa.Column("base_alocacao", sa.String(30), nullable=True),  # DRIVER, PERCENTAGE, EQUAL, etc.
        # Hierarquia
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cost_pools.id"), nullable=True),
        # Período
        sa.Column("periodo_inicio", sa.Date, nullable=True),
        sa.Column("periodo_fim", sa.Date, nullable=True),
        # Metadata
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("observacoes", sa.Text, nullable=True),
        # Auditoria
        sa.Column("ativo", sa.Boolean, nullable=False, default=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_cost_pools_condominio", "cost_pools", ["condominio_id"])
    op.create_index("ix_cost_pools_codigo", "cost_pools", ["codigo"])
    op.create_index("ix_cost_pools_tipo", "cost_pools", ["tipo"])
    op.create_index("ix_cost_pools_status", "cost_pools", ["status"])
    op.create_unique_constraint("uq_cost_pools_codigo_condo", "cost_pools", ["condominio_id", "codigo"])

    # ===========================================
    # COST OBJECTS - Objetos de Custo
    # ===========================================
    op.create_table(
        "cost_objects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("condominios.id"), nullable=False),
        sa.Column("codigo", sa.String(50), nullable=False),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("descricao", sa.Text, nullable=True),
        sa.Column("tipo", sa.String(50), nullable=False),  # PRODUCT, SERVICE, CUSTOMER, PROJECT, CONTRACT
        # Custos
        sa.Column("custo_direto", sa.Numeric(18, 2), nullable=False, default=0),
        sa.Column("custo_indireto", sa.Numeric(18, 2), nullable=False, default=0),
        sa.Column("custo_fixo", sa.Numeric(18, 2), nullable=False, default=0),
        sa.Column("custo_variavel", sa.Numeric(18, 2), nullable=False, default=0),
        # Receita
        sa.Column("receita", sa.Numeric(18, 2), nullable=False, default=0),
        # Quantidade
        sa.Column("quantidade", sa.Numeric(18, 4), nullable=True),
        sa.Column("unidade", sa.String(30), nullable=True),
        # Relacionamentos
        sa.Column("cliente_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("contrato_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("projeto_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Período
        sa.Column("periodo_inicio", sa.Date, nullable=True),
        sa.Column("periodo_fim", sa.Date, nullable=True),
        # Metadata
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("observacoes", sa.Text, nullable=True),
        # Auditoria
        sa.Column("ativo", sa.Boolean, nullable=False, default=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_cost_objects_condominio", "cost_objects", ["condominio_id"])
    op.create_index("ix_cost_objects_codigo", "cost_objects", ["codigo"])
    op.create_index("ix_cost_objects_tipo", "cost_objects", ["tipo"])
    op.create_index("ix_cost_objects_cliente", "cost_objects", ["cliente_id"])
    op.create_index("ix_cost_objects_contrato", "cost_objects", ["contrato_id"])
    op.create_unique_constraint("uq_cost_objects_codigo_condo", "cost_objects", ["condominio_id", "codigo"])

    # ===========================================
    # COST ALLOCATIONS - Alocações
    # ===========================================
    op.create_table(
        "cost_allocations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("condominios.id"), nullable=False),
        sa.Column("codigo", sa.String(100), nullable=False),
        sa.Column("descricao", sa.Text, nullable=True),
        # Tipo e método
        sa.Column("tipo", sa.String(50), nullable=False),  # POOL_TO_ACTIVITY, ACTIVITY_TO_OBJECT, DIRECT, RECIPROCAL
        sa.Column("metodo", sa.String(30), nullable=True),  # DRIVER_BASED, PERCENTAGE, PROPORTIONAL, EQUAL, STEP_DOWN
        # Origem
        sa.Column("origem_tipo", sa.String(30), nullable=False),
        sa.Column("origem_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Destino
        sa.Column("destino_tipo", sa.String(30), nullable=False),
        sa.Column("destino_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Valores
        sa.Column("valor_alocado", sa.Numeric(18, 2), nullable=False),
        sa.Column("percentual_alocado", sa.Numeric(8, 4), nullable=True),
        # Driver
        sa.Column("driver_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cost_drivers.id"), nullable=True),
        sa.Column("driver_quantidade", sa.Numeric(18, 4), nullable=True),
        sa.Column("taxa_driver", sa.Numeric(18, 6), nullable=True),
        # Período
        sa.Column("data_alocacao", sa.Date, nullable=False),
        sa.Column("periodo_inicio", sa.Date, nullable=True),
        sa.Column("periodo_fim", sa.Date, nullable=True),
        # Status e workflow
        sa.Column("status", sa.String(20), nullable=False, default="PENDING"),
        sa.Column("aprovado_por", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("aprovado_em", sa.DateTime, nullable=True),
        sa.Column("executado_por", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("executado_em", sa.DateTime, nullable=True),
        # Reversão
        sa.Column("revertido_por", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("revertido_em", sa.DateTime, nullable=True),
        sa.Column("motivo_reversao", sa.Text, nullable=True),
        sa.Column(
            "alocacao_referencia_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cost_allocations.id"), nullable=True
        ),
        # Metadata
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("observacoes", sa.Text, nullable=True),
        # Auditoria
        sa.Column("criado_por", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("ativo", sa.Boolean, nullable=False, default=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_cost_allocations_condominio", "cost_allocations", ["condominio_id"])
    op.create_index("ix_cost_allocations_codigo", "cost_allocations", ["codigo"])
    op.create_index("ix_cost_allocations_tipo", "cost_allocations", ["tipo"])
    op.create_index("ix_cost_allocations_status", "cost_allocations", ["status"])
    op.create_index("ix_cost_allocations_origem", "cost_allocations", ["origem_tipo", "origem_id"])
    op.create_index("ix_cost_allocations_destino", "cost_allocations", ["destino_tipo", "destino_id"])
    op.create_index("ix_cost_allocations_data", "cost_allocations", ["data_alocacao"])
    op.create_index("ix_cost_allocations_driver", "cost_allocations", ["driver_id"])

    # ===========================================
    # COST ANALYSES - Análises
    # ===========================================
    op.create_table(
        "cost_analyses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("condominios.id"), nullable=False),
        sa.Column("codigo", sa.String(100), nullable=False),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("descricao", sa.Text, nullable=True),
        sa.Column(
            "tipo", sa.String(50), nullable=False
        ),  # ABC_COSTING, PROFITABILITY, VARIANCE, BREAK_EVEN, TREND, FORECAST
        sa.Column("status", sa.String(20), nullable=False, default="PENDING"),
        # Período
        sa.Column("periodo_inicio", sa.Date, nullable=True),
        sa.Column("periodo_fim", sa.Date, nullable=True),
        # Parâmetros e resultados
        sa.Column("parametros", postgresql.JSONB, nullable=True),
        sa.Column("resultados", postgresql.JSONB, nullable=True),
        sa.Column("insights", postgresql.JSONB, nullable=True),
        sa.Column("recomendacoes", postgresql.JSONB, nullable=True),
        # Execução
        sa.Column("executado_por", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("executado_em", sa.DateTime, nullable=True),
        sa.Column("tempo_execucao_ms", sa.Integer, nullable=True),
        # Metadata
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("observacoes", sa.Text, nullable=True),
        # Auditoria
        sa.Column("ativo", sa.Boolean, nullable=False, default=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_cost_analyses_condominio", "cost_analyses", ["condominio_id"])
    op.create_index("ix_cost_analyses_codigo", "cost_analyses", ["codigo"])
    op.create_index("ix_cost_analyses_tipo", "cost_analyses", ["tipo"])
    op.create_index("ix_cost_analyses_status", "cost_analyses", ["status"])
    op.create_index("ix_cost_analyses_periodo", "cost_analyses", ["periodo_inicio", "periodo_fim"])


def downgrade() -> None:
    """Remove tabelas de Custeio ABC."""
    op.drop_table("cost_analyses")
    op.drop_table("cost_allocations")
    op.drop_table("cost_objects")
    op.drop_table("cost_pools")
    op.drop_table("cost_activities")
    op.drop_table("cost_drivers")
