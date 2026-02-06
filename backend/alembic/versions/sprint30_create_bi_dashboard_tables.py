"""Sprint 30: Create BI Dashboard tables.

Revision ID: sprint30_bi_dashboard
Revises: sprint29_costing
Create Date: 2025-01-20 10:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "sprint30_bi_dashboard"
down_revision: Union[str, None] = "sprint29_costing"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create BI Dashboard tables."""
    # Enum types
    op.execute("""
        CREATE TYPE dashboard_type AS ENUM (
            'executive', 'operational', 'analytical', 'tactical', 'custom'
        )
    """)
    op.execute("""
        CREATE TYPE dashboard_status AS ENUM (
            'draft', 'published', 'archived'
        )
    """)
    op.execute("""
        CREATE TYPE dashboard_layout AS ENUM (
            'grid', 'freeform', 'fixed', 'responsive'
        )
    """)
    op.execute("""
        CREATE TYPE refresh_interval AS ENUM (
            'realtime', 'minute_1', 'minute_5', 'minute_15',
            'minute_30', 'hour_1', 'hour_6', 'hour_12', 'day_1', 'manual'
        )
    """)
    op.execute("""
        CREATE TYPE widget_type AS ENUM (
            'card', 'chart', 'table', 'gauge', 'map',
            'list', 'text', 'image', 'kpi', 'filter', 'custom'
        )
    """)
    op.execute("""
        CREATE TYPE widget_size AS ENUM (
            'small', 'medium', 'large', 'xlarge', 'full'
        )
    """)
    op.execute("""
        CREATE TYPE chart_type AS ENUM (
            'line', 'bar', 'pie', 'donut', 'area', 'scatter',
            'bubble', 'heatmap', 'treemap', 'funnel', 'radar',
            'waterfall', 'candlestick', 'gauge', 'sparkline', 'combo'
        )
    """)
    op.execute("""
        CREATE TYPE data_source AS ENUM (
            'cash_flow', 'accounts_payable', 'accounts_receivable',
            'bank_accounts', 'purchases', 'inventory', 'accounting',
            'fiscal', 'costing', 'budget', 'custom_query', 'external_api'
        )
    """)
    op.execute("""
        CREATE TYPE kpi_category AS ENUM (
            'liquidity', 'profitability', 'efficiency', 'leverage',
            'activity', 'growth', 'cash_flow', 'budget', 'custom'
        )
    """)
    op.execute("""
        CREATE TYPE kpi_frequency AS ENUM (
            'daily', 'weekly', 'biweekly', 'monthly',
            'quarterly', 'semiannual', 'annual'
        )
    """)
    op.execute("""
        CREATE TYPE kpi_status AS ENUM (
            'active', 'inactive', 'calculating', 'error'
        )
    """)
    op.execute("""
        CREATE TYPE kpi_trend AS ENUM (
            'up', 'down', 'stable', 'volatile'
        )
    """)
    op.execute("""
        CREATE TYPE alert_level AS ENUM (
            'none', 'info', 'warning', 'critical'
        )
    """)
    op.execute("""
        CREATE TYPE report_type AS ENUM (
            'dashboard_snapshot', 'kpi_report', 'financial_summary',
            'custom_report', 'variance_report', 'trend_report',
            'forecast_report', 'comparison_report'
        )
    """)
    op.execute("""
        CREATE TYPE report_format AS ENUM (
            'pdf', 'excel', 'csv', 'json', 'html'
        )
    """)
    op.execute("""
        CREATE TYPE report_frequency AS ENUM (
            'once', 'daily', 'weekly', 'biweekly', 'monthly',
            'quarterly', 'semiannual', 'annual'
        )
    """)
    op.execute("""
        CREATE TYPE report_status AS ENUM (
            'active', 'paused', 'cancelled', 'completed'
        )
    """)
    op.execute("""
        CREATE TYPE delivery_method AS ENUM (
            'email', 'webhook', 'storage', 'notification'
        )
    """)
    op.execute("""
        CREATE TYPE cache_status AS ENUM (
            'valid', 'expired', 'invalidated', 'refreshing'
        )
    """)
    op.execute("""
        CREATE TYPE cache_type AS ENUM (
            'widget_data', 'kpi_value', 'report_data',
            'aggregation', 'forecast', 'analytics'
        )
    """)

    # financial_dashboards table
    op.create_table(
        "financial_dashboards",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("descricao", sa.Text, nullable=True),
        sa.Column("tipo", postgresql.ENUM(
            "executive", "operational", "analytical", "tactical", "custom",
            name="dashboard_type", create_type=False
        ), nullable=False, server_default="custom"),
        sa.Column("status", postgresql.ENUM(
            "draft", "published", "archived",
            name="dashboard_status", create_type=False
        ), nullable=False, server_default="draft"),
        sa.Column("layout", postgresql.ENUM(
            "grid", "freeform", "fixed", "responsive",
            name="dashboard_layout", create_type=False
        ), nullable=False, server_default="grid"),
        sa.Column("refresh_interval", postgresql.ENUM(
            "realtime", "minute_1", "minute_5", "minute_15",
            "minute_30", "hour_1", "hour_6", "hour_12", "day_1", "manual",
            name="refresh_interval", create_type=False
        ), nullable=False, server_default="minute_5"),
        sa.Column("configuracoes", postgresql.JSONB, nullable=True),
        sa.Column("filtros_globais", postgresql.JSONB, nullable=True),
        sa.Column("permissoes", postgresql.JSONB, nullable=True),
        sa.Column("tema", sa.String(50), nullable=True),
        sa.Column("icone", sa.String(100), nullable=True),
        sa.Column("ordem", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_favorito", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_padrao", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_publico", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("visualizacoes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("ultima_visualizacao", sa.DateTime, nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("published_at", sa.DateTime, nullable=True),
        sa.Column("published_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index(
        "ix_financial_dashboards_condominio_id",
        "financial_dashboards",
        ["condominio_id"],
    )
    op.create_index(
        "ix_financial_dashboards_status",
        "financial_dashboards",
        ["status"],
    )
    op.create_index(
        "ix_financial_dashboards_tipo",
        "financial_dashboards",
        ["tipo"],
    )

    # financial_widgets table
    op.create_table(
        "financial_widgets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "dashboard_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("financial_dashboards.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("titulo", sa.String(200), nullable=False),
        sa.Column("descricao", sa.Text, nullable=True),
        sa.Column("tipo", postgresql.ENUM(
            "card", "chart", "table", "gauge", "map",
            "list", "text", "image", "kpi", "filter", "custom",
            name="widget_type", create_type=False
        ), nullable=False, server_default="card"),
        sa.Column("tamanho", postgresql.ENUM(
            "small", "medium", "large", "xlarge", "full",
            name="widget_size", create_type=False
        ), nullable=False, server_default="medium"),
        sa.Column("posicao_x", sa.Integer, nullable=False, server_default="0"),
        sa.Column("posicao_y", sa.Integer, nullable=False, server_default="0"),
        sa.Column("largura", sa.Integer, nullable=False, server_default="4"),
        sa.Column("altura", sa.Integer, nullable=False, server_default="3"),
        sa.Column("tipo_grafico", postgresql.ENUM(
            "line", "bar", "pie", "donut", "area", "scatter",
            "bubble", "heatmap", "treemap", "funnel", "radar",
            "waterfall", "candlestick", "gauge", "sparkline", "combo",
            name="chart_type", create_type=False
        ), nullable=True),
        sa.Column("fonte_dados", postgresql.ENUM(
            "cash_flow", "accounts_payable", "accounts_receivable",
            "bank_accounts", "purchases", "inventory", "accounting",
            "fiscal", "costing", "budget", "custom_query", "external_api",
            name="data_source", create_type=False
        ), nullable=True),
        sa.Column("query_config", postgresql.JSONB, nullable=True),
        sa.Column("metricas", postgresql.JSONB, nullable=True),
        sa.Column("dimensoes", postgresql.JSONB, nullable=True),
        sa.Column("filtros", postgresql.JSONB, nullable=True),
        sa.Column("ordenacao", postgresql.JSONB, nullable=True),
        sa.Column("limite_registros", sa.Integer, nullable=True),
        sa.Column("agregacao", sa.String(50), nullable=True),
        sa.Column("periodo_dias", sa.Integer, nullable=True),
        sa.Column("comparar_periodo_anterior", sa.Boolean, server_default="false"),
        sa.Column("formatacao", postgresql.JSONB, nullable=True),
        sa.Column("cores", postgresql.JSONB, nullable=True),
        sa.Column("thresholds", postgresql.JSONB, nullable=True),
        sa.Column("opcoes_grafico", postgresql.JSONB, nullable=True),
        sa.Column("refresh_interval_segundos", sa.Integer, nullable=True),
        sa.Column("cache_ttl_segundos", sa.Integer, nullable=True),
        sa.Column("ultimo_refresh", sa.DateTime, nullable=True),
        sa.Column("ultimo_erro", sa.Text, nullable=True),
        sa.Column("is_visivel", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("is_interativo", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("ordem", sa.Integer, nullable=False, server_default="0"),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index(
        "ix_financial_widgets_dashboard_id",
        "financial_widgets",
        ["dashboard_id"],
    )
    op.create_index(
        "ix_financial_widgets_tipo",
        "financial_widgets",
        ["tipo"],
    )

    # financial_kpis table
    op.create_table(
        "financial_kpis",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("codigo", sa.String(50), nullable=False),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("descricao", sa.Text, nullable=True),
        sa.Column("categoria", postgresql.ENUM(
            "liquidity", "profitability", "efficiency", "leverage",
            "activity", "growth", "cash_flow", "budget", "custom",
            name="kpi_category", create_type=False
        ), nullable=False, server_default="custom"),
        sa.Column("formula", sa.Text, nullable=False),
        sa.Column("variaveis", postgresql.JSONB, nullable=True),
        sa.Column("unidade", sa.String(20), nullable=True),
        sa.Column("formato", sa.String(50), nullable=True),
        sa.Column("casas_decimais", sa.Integer, nullable=False, server_default="2"),
        sa.Column("frequencia", postgresql.ENUM(
            "daily", "weekly", "biweekly", "monthly",
            "quarterly", "semiannual", "annual",
            name="kpi_frequency", create_type=False
        ), nullable=False, server_default="monthly"),
        sa.Column("meta_valor", sa.Numeric(18, 4), nullable=True),
        sa.Column("meta_tipo", sa.String(20), nullable=True),
        sa.Column("threshold_warning", sa.Numeric(18, 4), nullable=True),
        sa.Column("threshold_critical", sa.Numeric(18, 4), nullable=True),
        sa.Column("threshold_success", sa.Numeric(18, 4), nullable=True),
        sa.Column("valor_atual", sa.Numeric(18, 4), nullable=True),
        sa.Column("valor_anterior", sa.Numeric(18, 4), nullable=True),
        sa.Column("variacao_percent", sa.Numeric(10, 4), nullable=True),
        sa.Column("status", postgresql.ENUM(
            "active", "inactive", "calculating", "error",
            name="kpi_status", create_type=False
        ), nullable=False, server_default="active"),
        sa.Column("tendencia", postgresql.ENUM(
            "up", "down", "stable", "volatile",
            name="kpi_trend", create_type=False
        ), nullable=True),
        sa.Column("alert_level", postgresql.ENUM(
            "none", "info", "warning", "critical",
            name="alert_level", create_type=False
        ), nullable=False, server_default="none"),
        sa.Column("historico", postgresql.JSONB, nullable=True),
        sa.Column("historico_max_registros", sa.Integer, server_default="365"),
        sa.Column("ultima_atualizacao", sa.DateTime, nullable=True),
        sa.Column("proximo_calculo", sa.DateTime, nullable=True),
        sa.Column("tempo_calculo_ms", sa.Integer, nullable=True),
        sa.Column("ultimo_erro", sa.Text, nullable=True),
        sa.Column("icone", sa.String(100), nullable=True),
        sa.Column("cor", sa.String(20), nullable=True),
        sa.Column("ordem", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_sistema", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index(
        "ix_financial_kpis_condominio_id",
        "financial_kpis",
        ["condominio_id"],
    )
    op.create_index(
        "ix_financial_kpis_codigo",
        "financial_kpis",
        ["codigo"],
    )
    op.create_index(
        "ix_financial_kpis_categoria",
        "financial_kpis",
        ["categoria"],
    )
    op.create_unique_constraint(
        "uq_financial_kpis_codigo_condominio",
        "financial_kpis",
        ["codigo", "condominio_id"],
    )

    # scheduled_reports table
    op.create_table(
        "scheduled_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("descricao", sa.Text, nullable=True),
        sa.Column("tipo", postgresql.ENUM(
            "dashboard_snapshot", "kpi_report", "financial_summary",
            "custom_report", "variance_report", "trend_report",
            "forecast_report", "comparison_report",
            name="report_type", create_type=False
        ), nullable=False, server_default="custom_report"),
        sa.Column("formato", postgresql.ENUM(
            "pdf", "excel", "csv", "json", "html",
            name="report_format", create_type=False
        ), nullable=False, server_default="pdf"),
        sa.Column("frequencia", postgresql.ENUM(
            "once", "daily", "weekly", "biweekly", "monthly",
            "quarterly", "semiannual", "annual",
            name="report_frequency", create_type=False
        ), nullable=False, server_default="monthly"),
        sa.Column("status", postgresql.ENUM(
            "active", "paused", "cancelled", "completed",
            name="report_status", create_type=False
        ), nullable=False, server_default="active"),
        sa.Column("dashboard_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("kpi_ids", postgresql.JSONB, nullable=True),
        sa.Column("configuracoes", postgresql.JSONB, nullable=True),
        sa.Column("filtros", postgresql.JSONB, nullable=True),
        sa.Column("periodo_inicio", sa.Date, nullable=True),
        sa.Column("periodo_fim", sa.Date, nullable=True),
        sa.Column("periodo_relativo_dias", sa.Integer, nullable=True),
        sa.Column("metodo_entrega", postgresql.ENUM(
            "email", "webhook", "storage", "notification",
            name="delivery_method", create_type=False
        ), nullable=False, server_default="email"),
        sa.Column("destinatarios_email", postgresql.JSONB, nullable=True),
        sa.Column("webhook_url", sa.String(500), nullable=True),
        sa.Column("storage_path", sa.String(500), nullable=True),
        sa.Column("template_id", sa.String(100), nullable=True),
        sa.Column("proxima_execucao", sa.DateTime, nullable=True),
        sa.Column("ultima_execucao", sa.DateTime, nullable=True),
        sa.Column("total_execucoes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("execucoes_sucesso", sa.Integer, nullable=False, server_default="0"),
        sa.Column("execucoes_falha", sa.Integer, nullable=False, server_default="0"),
        sa.Column("ultimo_erro", sa.Text, nullable=True),
        sa.Column("ultimo_arquivo", sa.String(500), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index(
        "ix_scheduled_reports_condominio_id",
        "scheduled_reports",
        ["condominio_id"],
    )
    op.create_index(
        "ix_scheduled_reports_status",
        "scheduled_reports",
        ["status"],
    )
    op.create_index(
        "ix_scheduled_reports_proxima_execucao",
        "scheduled_reports",
        ["proxima_execucao"],
    )

    # analytics_cache table
    op.create_table(
        "analytics_cache",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("cache_key", sa.String(255), nullable=False),
        sa.Column("cache_type", postgresql.ENUM(
            "widget_data", "kpi_value", "report_data",
            "aggregation", "forecast", "analytics",
            name="cache_type", create_type=False
        ), nullable=False),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("data", postgresql.JSONB, nullable=True),
        sa.Column("tamanho_bytes", sa.Integer, nullable=True),
        sa.Column("status", postgresql.ENUM(
            "valid", "expired", "invalidated", "refreshing",
            name="cache_status", create_type=False
        ), nullable=False, server_default="valid"),
        sa.Column("ttl_segundos", sa.Integer, nullable=False, server_default="300"),
        sa.Column("expira_em", sa.DateTime, nullable=True),
        sa.Column("hits", sa.Integer, nullable=False, server_default="0"),
        sa.Column("misses", sa.Integer, nullable=False, server_default="0"),
        sa.Column("ultimo_hit", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index(
        "ix_analytics_cache_cache_key",
        "analytics_cache",
        ["cache_key"],
        unique=True,
    )
    op.create_index(
        "ix_analytics_cache_cache_type",
        "analytics_cache",
        ["cache_type"],
    )
    op.create_index(
        "ix_analytics_cache_condominio_id",
        "analytics_cache",
        ["condominio_id"],
    )
    op.create_index(
        "ix_analytics_cache_expira_em",
        "analytics_cache",
        ["expira_em"],
    )


def downgrade() -> None:
    """Drop BI Dashboard tables."""
    op.drop_table("analytics_cache")
    op.drop_table("scheduled_reports")
    op.drop_table("financial_kpis")
    op.drop_table("financial_widgets")
    op.drop_table("financial_dashboards")

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS cache_type")
    op.execute("DROP TYPE IF EXISTS cache_status")
    op.execute("DROP TYPE IF EXISTS delivery_method")
    op.execute("DROP TYPE IF EXISTS report_status")
    op.execute("DROP TYPE IF EXISTS report_frequency")
    op.execute("DROP TYPE IF EXISTS report_format")
    op.execute("DROP TYPE IF EXISTS report_type")
    op.execute("DROP TYPE IF EXISTS alert_level")
    op.execute("DROP TYPE IF EXISTS kpi_trend")
    op.execute("DROP TYPE IF EXISTS kpi_status")
    op.execute("DROP TYPE IF EXISTS kpi_frequency")
    op.execute("DROP TYPE IF EXISTS kpi_category")
    op.execute("DROP TYPE IF EXISTS data_source")
    op.execute("DROP TYPE IF EXISTS chart_type")
    op.execute("DROP TYPE IF EXISTS widget_size")
    op.execute("DROP TYPE IF EXISTS widget_type")
    op.execute("DROP TYPE IF EXISTS refresh_interval")
    op.execute("DROP TYPE IF EXISTS dashboard_layout")
    op.execute("DROP TYPE IF EXISTS dashboard_status")
    op.execute("DROP TYPE IF EXISTS dashboard_type")
