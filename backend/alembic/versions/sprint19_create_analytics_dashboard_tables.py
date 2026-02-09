"""Sprint 19: Create Analytics Dashboard tables.

Revision ID: sprint19_analytics_dashboard
Revises: sprint18_mobile_time_clock
Create Date: 2025-12-31

Tabelas:
- dashboard_configs: Configurações de dashboards customizáveis
- dashboard_widgets: Widgets de visualização (gráficos, KPIs, tabelas)
- kpi_definitions: Definições de KPIs com fórmulas e thresholds
- analytics_cache: Cache de métricas computadas
- scheduled_reports: Relatórios agendados com entrega automática
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "sprint19_analytics_dashboard"
down_revision: str | None = "sprint18_mobile_time_clock"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Cria tabelas do módulo Analytics Dashboard."""

    # ==================== DASHBOARD_CONFIGS ====================
    op.create_table(
        "dashboard_configs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("condominio_id", UUID(as_uuid=True), nullable=True),
        sa.Column("owner_id", UUID(as_uuid=True), nullable=True),
        # Identificação
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("slug", sa.String(100), nullable=True),
        # Tipo e visibilidade
        sa.Column("dashboard_type", sa.String(50), nullable=False, server_default="custom"),
        sa.Column("visibility", sa.String(50), nullable=False, server_default="private"),
        # Layout e aparência
        sa.Column("layout_config", JSONB, nullable=True),
        sa.Column("theme", sa.String(50), nullable=True, server_default="light"),
        sa.Column("grid_columns", sa.Integer, nullable=True, server_default="12"),
        sa.Column("row_height", sa.Integer, nullable=True, server_default="100"),
        # Refresh
        sa.Column("auto_refresh", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("refresh_interval", sa.String(50), nullable=True, server_default="5min"),
        # Período padrão
        sa.Column("default_period", sa.String(50), nullable=True, server_default="30d"),
        sa.Column("default_filters", JSONB, nullable=True),
        # Compartilhamento
        sa.Column("is_shared", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("shared_with", JSONB, nullable=True),
        sa.Column("is_template", sa.Boolean, nullable=False, server_default="false"),
        # Flags
        sa.Column("is_default", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_system", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_favorite", sa.Boolean, nullable=False, server_default="false"),
        # Métricas
        sa.Column("view_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_viewed_at", sa.DateTime(timezone=True), nullable=True),
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Índices para dashboard_configs
    op.create_index("ix_dashboard_configs_condominio", "dashboard_configs", ["condominio_id"])
    op.create_index("ix_dashboard_configs_owner", "dashboard_configs", ["owner_id"])
    op.create_index("ix_dashboard_configs_type", "dashboard_configs", ["dashboard_type"])
    op.create_index("ix_dashboard_configs_visibility", "dashboard_configs", ["visibility"])
    op.create_index("ix_dashboard_configs_slug", "dashboard_configs", ["slug"])
    op.create_index("ix_dashboard_configs_default", "dashboard_configs", ["condominio_id", "is_default"])

    # ==================== DASHBOARD_WIDGETS ====================
    op.create_table(
        "dashboard_widgets",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "dashboard_id",
            UUID(as_uuid=True),
            sa.ForeignKey("dashboard_configs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Identificação
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        # Tipo e dados
        sa.Column("widget_type", sa.String(50), nullable=False),
        sa.Column("data_source", sa.String(100), nullable=True),
        sa.Column("aggregation_type", sa.String(50), nullable=True, server_default="count"),
        # Posição no grid
        sa.Column("position_x", sa.Integer, nullable=False, server_default="0"),
        sa.Column("position_y", sa.Integer, nullable=False, server_default="0"),
        sa.Column("width", sa.Integer, nullable=False, server_default="4"),
        sa.Column("height", sa.Integer, nullable=False, server_default="3"),
        sa.Column("min_width", sa.Integer, nullable=True, server_default="2"),
        sa.Column("min_height", sa.Integer, nullable=True, server_default="2"),
        # Configurações de visualização
        sa.Column("chart_config", JSONB, nullable=True),
        sa.Column("display_config", JSONB, nullable=True),
        sa.Column("colors", JSONB, nullable=True),
        # Configurações de KPI
        sa.Column("kpi_code", sa.String(100), nullable=True),
        sa.Column("kpi_format", sa.String(50), nullable=True),
        sa.Column("show_trend", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("show_comparison", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("comparison_period", sa.String(50), nullable=True),
        # Thresholds visuais
        sa.Column("thresholds", JSONB, nullable=True),
        # Filtros e query
        sa.Column("filters", JSONB, nullable=True),
        sa.Column("query_config", JSONB, nullable=True),
        sa.Column("date_field", sa.String(100), nullable=True),
        sa.Column("group_by", sa.String(100), nullable=True),
        # Refresh
        sa.Column("refresh_interval", sa.Integer, nullable=True),
        sa.Column("last_refreshed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cache_ttl", sa.Integer, nullable=True, server_default="300"),
        # Ordenação
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        # Status
        sa.Column("is_visible", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("is_expanded", sa.Boolean, nullable=False, server_default="false"),
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Índices para dashboard_widgets
    op.create_index("ix_dashboard_widgets_dashboard", "dashboard_widgets", ["dashboard_id"])
    op.create_index("ix_dashboard_widgets_type", "dashboard_widgets", ["widget_type"])
    op.create_index("ix_dashboard_widgets_kpi", "dashboard_widgets", ["kpi_code"])
    op.create_index("ix_dashboard_widgets_sort", "dashboard_widgets", ["dashboard_id", "sort_order"])

    # ==================== KPI_DEFINITIONS ====================
    op.create_table(
        "kpi_definitions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("condominio_id", UUID(as_uuid=True), nullable=True),
        # Identificação
        sa.Column("code", sa.String(100), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        # Categoria e tipo
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("unit", sa.String(50), nullable=False, server_default="number"),
        sa.Column("direction", sa.String(20), nullable=False, server_default="up"),
        # Fórmula e cálculo
        sa.Column("formula", sa.Text, nullable=True),
        sa.Column("formula_description", sa.Text, nullable=True),
        sa.Column("data_sources", JSONB, nullable=True),
        sa.Column("calculation_frequency", sa.String(50), nullable=True, server_default="daily"),
        # Meta e thresholds
        sa.Column("target_value", sa.Numeric(15, 4), nullable=True),
        sa.Column("min_value", sa.Numeric(15, 4), nullable=True),
        sa.Column("max_value", sa.Numeric(15, 4), nullable=True),
        sa.Column("threshold_warning", sa.Numeric(15, 4), nullable=True),
        sa.Column("threshold_critical", sa.Numeric(15, 4), nullable=True),
        # Formatação
        sa.Column("decimal_places", sa.Integer, nullable=True, server_default="2"),
        sa.Column("prefix", sa.String(20), nullable=True),
        sa.Column("suffix", sa.String(20), nullable=True),
        # Comparação
        sa.Column("comparison_enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("comparison_period", sa.String(50), nullable=True, server_default="previous_period"),
        # Flags
        sa.Column("is_system", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_featured", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        # Cache
        sa.Column("cache_ttl", sa.Integer, nullable=True, server_default="3600"),
        # Metadados
        sa.Column("tags", JSONB, nullable=True),
        sa.Column("metadata", JSONB, nullable=True),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Índices para kpi_definitions
    op.create_index("ix_kpi_definitions_condominio", "kpi_definitions", ["condominio_id"])
    op.create_index("ix_kpi_definitions_code", "kpi_definitions", ["code"])
    op.create_index("ix_kpi_definitions_category", "kpi_definitions", ["category"])
    op.create_index("ix_kpi_definitions_system", "kpi_definitions", ["is_system"])
    op.create_index("ix_kpi_definitions_featured", "kpi_definitions", ["is_featured"])
    op.create_unique_index("uq_kpi_definitions_code_condo", "kpi_definitions", ["code", "condominio_id"])

    # ==================== ANALYTICS_CACHE ====================
    op.create_table(
        "analytics_cache",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("condominio_id", UUID(as_uuid=True), nullable=True),
        # Identificação
        sa.Column("cache_key", sa.String(500), nullable=False, unique=True),
        sa.Column("cache_type", sa.String(50), nullable=False),
        # Dados
        sa.Column("data", JSONB, nullable=False),
        sa.Column("compressed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("data_size", sa.Integer, nullable=True),
        # Metadados de cálculo
        sa.Column("query_params", JSONB, nullable=True),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=True),
        # Validade
        sa.Column("ttl_seconds", sa.Integer, nullable=False, server_default="3600"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        # Status
        sa.Column("status", sa.String(50), nullable=False, server_default="valid"),
        sa.Column("invalidated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("invalidation_reason", sa.String(200), nullable=True),
        # Métricas
        sa.Column("hit_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_hit_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("computation_time_ms", sa.Integer, nullable=True),
        # Dependências
        sa.Column("depends_on", JSONB, nullable=True),
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Índices para analytics_cache
    op.create_index("ix_analytics_cache_key", "analytics_cache", ["cache_key"])
    op.create_index("ix_analytics_cache_type", "analytics_cache", ["cache_type"])
    op.create_index("ix_analytics_cache_condominio", "analytics_cache", ["condominio_id"])
    op.create_index("ix_analytics_cache_expires", "analytics_cache", ["expires_at"])
    op.create_index("ix_analytics_cache_status", "analytics_cache", ["status"])

    # ==================== SCHEDULED_REPORTS ====================
    op.create_table(
        "scheduled_reports",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("condominio_id", UUID(as_uuid=True), nullable=True),
        sa.Column("owner_id", UUID(as_uuid=True), nullable=True),
        # Identificação
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        # Tipo e formato
        sa.Column("report_type", sa.String(100), nullable=False),
        sa.Column("output_format", sa.String(50), nullable=False, server_default="pdf"),
        # Agendamento
        sa.Column("schedule_frequency", sa.String(50), nullable=False, server_default="monthly"),
        sa.Column("schedule_config", JSONB, nullable=True),
        sa.Column("timezone", sa.String(50), nullable=True, server_default="America/Sao_Paulo"),
        sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=True),
        # Período do relatório
        sa.Column("report_period", sa.String(50), nullable=True, server_default="previous_month"),
        sa.Column("custom_period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("custom_period_end", sa.DateTime(timezone=True), nullable=True),
        # Filtros e parâmetros
        sa.Column("filters", JSONB, nullable=True),
        sa.Column("parameters", JSONB, nullable=True),
        sa.Column("included_sections", JSONB, nullable=True),
        # Entrega
        sa.Column("delivery_method", sa.String(50), nullable=False, server_default="email"),
        sa.Column("delivery_config", JSONB, nullable=True),
        sa.Column("recipients", JSONB, nullable=True),
        # Status
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("paused_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paused_reason", sa.String(200), nullable=True),
        # Execução
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_status", sa.String(50), nullable=True),
        sa.Column("last_error", sa.Text, nullable=True),
        sa.Column("last_file_path", sa.String(500), nullable=True),
        sa.Column("last_file_size", sa.Integer, nullable=True),
        # Métricas
        sa.Column("run_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("success_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("failure_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("avg_generation_time_ms", sa.Integer, nullable=True),
        # Retenção
        sa.Column("retention_days", sa.Integer, nullable=True, server_default="90"),
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Índices para scheduled_reports
    op.create_index("ix_scheduled_reports_condominio", "scheduled_reports", ["condominio_id"])
    op.create_index("ix_scheduled_reports_owner", "scheduled_reports", ["owner_id"])
    op.create_index("ix_scheduled_reports_type", "scheduled_reports", ["report_type"])
    op.create_index("ix_scheduled_reports_status", "scheduled_reports", ["status"])
    op.create_index("ix_scheduled_reports_next_run", "scheduled_reports", ["next_run_at"])
    op.create_index("ix_scheduled_reports_frequency", "scheduled_reports", ["schedule_frequency"])

    # ==================== REPORT_EXECUTIONS (histórico) ====================
    op.create_table(
        "report_executions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "report_id", UUID(as_uuid=True), sa.ForeignKey("scheduled_reports.id", ondelete="CASCADE"), nullable=False
        ),
        # Período coberto
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=True),
        # Execução
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Integer, nullable=True),
        # Status
        sa.Column("status", sa.String(50), nullable=False, server_default="running"),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("error_traceback", sa.Text, nullable=True),
        # Arquivo gerado
        sa.Column("output_format", sa.String(50), nullable=True),
        sa.Column("file_path", sa.String(500), nullable=True),
        sa.Column("file_size", sa.Integer, nullable=True),
        sa.Column("file_checksum", sa.String(64), nullable=True),
        # Entrega
        sa.Column("delivery_status", sa.String(50), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivery_error", sa.Text, nullable=True),
        sa.Column("recipients_notified", JSONB, nullable=True),
        # Métricas
        sa.Column("records_processed", sa.Integer, nullable=True),
        sa.Column("pages_generated", sa.Integer, nullable=True),
        # Metadados
        sa.Column("execution_params", JSONB, nullable=True),
        sa.Column("triggered_by", sa.String(100), nullable=True),
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Índices para report_executions
    op.create_index("ix_report_executions_report", "report_executions", ["report_id"])
    op.create_index("ix_report_executions_status", "report_executions", ["status"])
    op.create_index("ix_report_executions_started", "report_executions", ["started_at"])


def downgrade() -> None:
    """Remove tabelas do módulo Analytics Dashboard."""

    # Remover tabelas em ordem reversa (dependências)
    op.drop_table("report_executions")
    op.drop_table("scheduled_reports")
    op.drop_table("analytics_cache")
    op.drop_table("kpi_definitions")
    op.drop_table("dashboard_widgets")
    op.drop_table("dashboard_configs")
