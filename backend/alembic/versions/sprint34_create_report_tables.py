"""Sprint 34 - Create Report Tables

Revision ID: sprint34_reports
Revises: sprint33_audit
Create Date: 2024-01-01 00:00:00.000000

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "sprint34_reports"
down_revision = "sprint33_audit"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ==================== report_templates ====================
    op.create_table(
        "report_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("codigo", sa.String(50), nullable=False, unique=True),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("report_type", sa.String(50), nullable=False),
        sa.Column("default_format", sa.String(20), nullable=False),
        sa.Column("supported_formats", postgresql.JSONB(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, default=1),
        sa.Column("layout_config", postgresql.JSONB(), nullable=True),
        sa.Column("header_config", postgresql.JSONB(), nullable=True),
        sa.Column("footer_config", postgresql.JSONB(), nullable=True),
        sa.Column("sections", postgresql.JSONB(), nullable=True),
        sa.Column("charts", postgresql.JSONB(), nullable=True),
        sa.Column("parameters", postgresql.JSONB(), nullable=True),
        sa.Column("data_sources", postgresql.JSONB(), nullable=True),
        sa.Column("filters", postgresql.JSONB(), nullable=True),
        sa.Column("sorting", postgresql.JSONB(), nullable=True),
        sa.Column("grouping", postgresql.JSONB(), nullable=True),
        sa.Column("totals_config", postgresql.JSONB(), nullable=True),
        sa.Column("style_config", postgresql.JSONB(), nullable=True),
        sa.Column("visibility", sa.String(20), nullable=False),
        sa.Column("allowed_roles", postgresql.JSONB(), nullable=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("usage_count", sa.Integer(), nullable=False, default=0),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tags", postgresql.JSONB(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_report_templates_codigo", "report_templates", ["codigo"])
    op.create_index("ix_report_templates_category", "report_templates", ["category"])
    op.create_index("ix_report_templates_status", "report_templates", ["status"])
    op.create_index("ix_report_templates_visibility", "report_templates", ["visibility"])
    op.create_index("ix_report_templates_owner_id", "report_templates", ["owner_id"])

    # ==================== report_schedules ====================
    op.create_table(
        "report_schedules",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("codigo", sa.String(50), nullable=False, unique=True),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("frequency", sa.String(20), nullable=False),
        sa.Column("cron_expression", sa.String(100), nullable=True),
        sa.Column("timezone", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_execution", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_execution", sa.DateTime(timezone=True), nullable=True),
        sa.Column("execution_count", sa.Integer(), nullable=False, default=0),
        sa.Column("success_count", sa.Integer(), nullable=False, default=0),
        sa.Column("failure_count", sa.Integer(), nullable=False, default=0),
        sa.Column("consecutive_failures", sa.Integer(), nullable=False, default=0),
        sa.Column("max_retries", sa.Integer(), nullable=False, default=3),
        sa.Column("retry_delay_minutes", sa.Integer(), nullable=False, default=15),
        sa.Column("parameters", postgresql.JSONB(), nullable=True),
        sa.Column("filters", postgresql.JSONB(), nullable=True),
        sa.Column("output_format", sa.String(20), nullable=False),
        sa.Column("delivery_method", sa.String(20), nullable=False),
        sa.Column("recipients", postgresql.JSONB(), nullable=True),
        sa.Column("cc_recipients", postgresql.JSONB(), nullable=True),
        sa.Column("email_subject", sa.String(500), nullable=True),
        sa.Column("email_body", sa.Text(), nullable=True),
        sa.Column("storage_path", sa.String(500), nullable=True),
        sa.Column("webhook_url", sa.String(500), nullable=True),
        sa.Column("notification_config", postgresql.JSONB(), nullable=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("tags", postgresql.JSONB(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["template_id"], ["report_templates.id"]),
    )
    op.create_index("ix_report_schedules_codigo", "report_schedules", ["codigo"])
    op.create_index("ix_report_schedules_template_id", "report_schedules", ["template_id"])
    op.create_index("ix_report_schedules_status", "report_schedules", ["status"])
    op.create_index("ix_report_schedules_frequency", "report_schedules", ["frequency"])
    op.create_index("ix_report_schedules_next_execution", "report_schedules", ["next_execution"])
    op.create_index("ix_report_schedules_owner_id", "report_schedules", ["owner_id"])

    # ==================== report_exports ====================
    op.create_table(
        "report_exports",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("export_id", sa.String(50), nullable=False, unique=True),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("schedule_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("trigger", sa.String(20), nullable=False),
        sa.Column("format", sa.String(20), nullable=False),
        sa.Column("parameters", postgresql.JSONB(), nullable=True),
        sa.Column("filters", postgresql.JSONB(), nullable=True),
        sa.Column("file_name", sa.String(500), nullable=True),
        sa.Column("file_path", sa.String(1000), nullable=True),
        sa.Column("file_size", sa.BigInteger(), nullable=True),
        sa.Column("file_hash", sa.String(64), nullable=True),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column("row_count", sa.Integer(), nullable=True),
        sa.Column("page_count", sa.Integer(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("processing_time_ms", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("error_details", postgresql.JSONB(), nullable=True),
        sa.Column("download_url", sa.String(1000), nullable=True),
        sa.Column("download_token", sa.String(100), nullable=True),
        sa.Column("download_count", sa.Integer(), nullable=False, default=0),
        sa.Column("last_downloaded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivered", sa.Boolean(), nullable=False, default=False),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivery_method", sa.String(20), nullable=True),
        sa.Column("delivery_details", postgresql.JSONB(), nullable=True),
        sa.Column("requested_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["template_id"], ["report_templates.id"]),
        sa.ForeignKeyConstraint(["schedule_id"], ["report_schedules.id"]),
    )
    op.create_index("ix_report_exports_export_id", "report_exports", ["export_id"])
    op.create_index("ix_report_exports_template_id", "report_exports", ["template_id"])
    op.create_index("ix_report_exports_schedule_id", "report_exports", ["schedule_id"])
    op.create_index("ix_report_exports_status", "report_exports", ["status"])
    op.create_index("ix_report_exports_trigger", "report_exports", ["trigger"])
    op.create_index("ix_report_exports_requested_by", "report_exports", ["requested_by"])
    op.create_index("ix_report_exports_expires_at", "report_exports", ["expires_at"])
    op.create_index("ix_report_exports_download_token", "report_exports", ["download_token"])

    # ==================== executive_kpis ====================
    op.create_table(
        "executive_kpis",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("codigo", sa.String(50), nullable=False, unique=True),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("kpi_type", sa.String(50), nullable=False),
        sa.Column("direction", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("precision", sa.Integer(), nullable=False, default=2),
        sa.Column("current_value", sa.Numeric(20, 4), nullable=True),
        sa.Column("previous_value", sa.Numeric(20, 4), nullable=True),
        sa.Column("target_value", sa.Numeric(20, 4), nullable=True),
        sa.Column("min_value", sa.Numeric(20, 4), nullable=True),
        sa.Column("max_value", sa.Numeric(20, 4), nullable=True),
        sa.Column("baseline_value", sa.Numeric(20, 4), nullable=True),
        sa.Column("variance", sa.Numeric(10, 4), nullable=True),
        sa.Column("variance_percentage", sa.Numeric(10, 4), nullable=True),
        sa.Column("trend", sa.String(20), nullable=True),
        sa.Column("trend_percentage", sa.Numeric(10, 4), nullable=True),
        sa.Column("alert_level", sa.String(20), nullable=False),
        sa.Column("threshold_critical", sa.Numeric(20, 4), nullable=True),
        sa.Column("threshold_warning", sa.Numeric(20, 4), nullable=True),
        sa.Column("threshold_target", sa.Numeric(20, 4), nullable=True),
        sa.Column("threshold_excellent", sa.Numeric(20, 4), nullable=True),
        sa.Column("aggregation_period", sa.String(20), nullable=False),
        sa.Column("calculation_formula", sa.Text(), nullable=True),
        sa.Column("data_source", sa.String(200), nullable=True),
        sa.Column("data_query", sa.Text(), nullable=True),
        sa.Column("last_calculated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_calculation_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("calculation_frequency_minutes", sa.Integer(), nullable=False, default=60),
        sa.Column("history", postgresql.JSONB(), nullable=True),
        sa.Column("history_retention_days", sa.Integer(), nullable=False, default=365),
        sa.Column("display_order", sa.Integer(), nullable=False, default=0),
        sa.Column("visibility", sa.String(20), nullable=False),
        sa.Column("allowed_roles", postgresql.JSONB(), nullable=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("dashboard_config", postgresql.JSONB(), nullable=True),
        sa.Column("chart_type", sa.String(20), nullable=True),
        sa.Column("tags", postgresql.JSONB(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_executive_kpis_codigo", "executive_kpis", ["codigo"])
    op.create_index("ix_executive_kpis_category", "executive_kpis", ["category"])
    op.create_index("ix_executive_kpis_kpi_type", "executive_kpis", ["kpi_type"])
    op.create_index("ix_executive_kpis_status", "executive_kpis", ["status"])
    op.create_index("ix_executive_kpis_alert_level", "executive_kpis", ["alert_level"])
    op.create_index("ix_executive_kpis_visibility", "executive_kpis", ["visibility"])
    op.create_index("ix_executive_kpis_owner_id", "executive_kpis", ["owner_id"])
    op.create_index("ix_executive_kpis_display_order", "executive_kpis", ["display_order"])

    # ==================== benchmarks ====================
    op.create_table(
        "benchmarks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("codigo", sa.String(50), nullable=False, unique=True),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("benchmark_type", sa.String(50), nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("industry", sa.String(100), nullable=True),
        sa.Column("segment", sa.String(100), nullable=True),
        sa.Column("region", sa.String(100), nullable=True),
        sa.Column("company_size", sa.String(50), nullable=True),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("precision", sa.Integer(), nullable=False, default=2),
        sa.Column("reference_value", sa.Numeric(20, 4), nullable=True),
        sa.Column("reference_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reference_period", sa.String(50), nullable=True),
        sa.Column("min_value", sa.Numeric(20, 4), nullable=True),
        sa.Column("max_value", sa.Numeric(20, 4), nullable=True),
        sa.Column("median_value", sa.Numeric(20, 4), nullable=True),
        sa.Column("mean_value", sa.Numeric(20, 4), nullable=True),
        sa.Column("std_deviation", sa.Numeric(20, 4), nullable=True),
        sa.Column("percentile_25", sa.Numeric(20, 4), nullable=True),
        sa.Column("percentile_50", sa.Numeric(20, 4), nullable=True),
        sa.Column("percentile_75", sa.Numeric(20, 4), nullable=True),
        sa.Column("percentile_90", sa.Numeric(20, 4), nullable=True),
        sa.Column("sample_size", sa.Integer(), nullable=True),
        sa.Column("company_value", sa.Numeric(20, 4), nullable=True),
        sa.Column("company_value_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("comparison_result", sa.String(20), nullable=True),
        sa.Column("percentile_rank", sa.Numeric(10, 4), nullable=True),
        sa.Column("gap_to_benchmark", sa.Numeric(20, 4), nullable=True),
        sa.Column("gap_percentage", sa.Numeric(10, 4), nullable=True),
        sa.Column("target_value", sa.Numeric(20, 4), nullable=True),
        sa.Column("target_percentile", sa.Integer(), nullable=True),
        sa.Column("target_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("history", postgresql.JSONB(), nullable=True),
        sa.Column("data_source_url", sa.String(500), nullable=True),
        sa.Column("data_source_name", sa.String(200), nullable=True),
        sa.Column("last_updated_from_source", sa.DateTime(timezone=True), nullable=True),
        sa.Column("update_frequency", sa.String(50), nullable=True),
        sa.Column("next_update", sa.DateTime(timezone=True), nullable=True),
        sa.Column("kpi_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("visibility", sa.String(20), nullable=False),
        sa.Column("allowed_roles", postgresql.JSONB(), nullable=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("tags", postgresql.JSONB(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["kpi_id"], ["executive_kpis.id"]),
    )
    op.create_index("ix_benchmarks_codigo", "benchmarks", ["codigo"])
    op.create_index("ix_benchmarks_category", "benchmarks", ["category"])
    op.create_index("ix_benchmarks_benchmark_type", "benchmarks", ["benchmark_type"])
    op.create_index("ix_benchmarks_source", "benchmarks", ["source"])
    op.create_index("ix_benchmarks_status", "benchmarks", ["status"])
    op.create_index("ix_benchmarks_industry", "benchmarks", ["industry"])
    op.create_index("ix_benchmarks_kpi_id", "benchmarks", ["kpi_id"])
    op.create_index("ix_benchmarks_visibility", "benchmarks", ["visibility"])
    op.create_index("ix_benchmarks_owner_id", "benchmarks", ["owner_id"])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table("benchmarks")
    op.drop_table("executive_kpis")
    op.drop_table("report_exports")
    op.drop_table("report_schedules")
    op.drop_table("report_templates")
