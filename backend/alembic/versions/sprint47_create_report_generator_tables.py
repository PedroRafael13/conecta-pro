"""Sprint 47: Create report generator tables

Revision ID: sprint47_report_gen
Revises: sprint46_sentiment
Create Date: 2026-01-05

Cria tabelas para o módulo AI Report Generator:
- ai_reports: Relatórios gerados
- ai_report_templates: Templates de relatório
- ai_report_schedules: Agendamentos
- ai_report_executions: Histórico de execuções
- ai_report_sections: Seções dos relatórios
- ai_report_widgets: Widgets/componentes visuais
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, ENUM

# revision identifiers
revision = 'sprint47_report_gen'
down_revision = 'sprint46_sentiment'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============== ENUMS ==============

    # Report Type Enum
    report_type_enum = postgresql.ENUM(
        'dashboard', 'summary', 'detailed', 'analytical', 'comparative',
        'financial', 'sales', 'hr', 'operations', 'inventory', 'customer',
        'kpi', 'forecast', 'anomaly', 'trend', 'audit', 'compliance',
        'performance', 'custom', 'ad_hoc',
        name='report_type_enum',
        create_type=False
    )
    report_type_enum.create(op.get_bind(), checkfirst=True)

    # Report Status Enum
    report_status_enum = postgresql.ENUM(
        'draft', 'generating', 'completed', 'failed', 'archived', 'expired',
        name='report_status_enum',
        create_type=False
    )
    report_status_enum.create(op.get_bind(), checkfirst=True)

    # Report Priority Enum
    report_priority_enum = postgresql.ENUM(
        'low', 'normal', 'high', 'critical',
        name='report_priority_enum',
        create_type=False
    )
    report_priority_enum.create(op.get_bind(), checkfirst=True)

    # Template Category Enum
    template_category_enum = postgresql.ENUM(
        'financial', 'sales', 'hr', 'operations', 'inventory', 'customer',
        'marketing', 'executive', 'operational', 'analytical', 'compliance',
        'audit', 'general', 'custom',
        name='template_category_enum',
        create_type=False
    )
    template_category_enum.create(op.get_bind(), checkfirst=True)

    # Template Status Enum
    template_status_enum = postgresql.ENUM(
        'draft', 'active', 'inactive', 'deprecated', 'archived',
        name='template_status_enum',
        create_type=False
    )
    template_status_enum.create(op.get_bind(), checkfirst=True)

    # Schedule Frequency Enum
    schedule_frequency_enum = postgresql.ENUM(
        'once', 'hourly', 'daily', 'weekly', 'biweekly', 'monthly',
        'quarterly', 'yearly', 'custom',
        name='schedule_frequency_enum',
        create_type=False
    )
    schedule_frequency_enum.create(op.get_bind(), checkfirst=True)

    # Schedule Status Enum
    schedule_status_enum = postgresql.ENUM(
        'active', 'paused', 'completed', 'failed', 'expired', 'cancelled',
        name='schedule_status_enum',
        create_type=False
    )
    schedule_status_enum.create(op.get_bind(), checkfirst=True)

    # Execution Status Enum
    execution_status_enum = postgresql.ENUM(
        'pending', 'queued', 'running', 'collecting_data', 'processing',
        'generating_insights', 'rendering', 'exporting', 'delivering',
        'completed', 'failed', 'cancelled', 'timeout',
        name='execution_status_enum',
        create_type=False
    )
    execution_status_enum.create(op.get_bind(), checkfirst=True)

    # Execution Trigger Enum
    execution_trigger_enum = postgresql.ENUM(
        'manual', 'scheduled', 'api', 'webhook', 'event', 'retry',
        name='execution_trigger_enum',
        create_type=False
    )
    execution_trigger_enum.create(op.get_bind(), checkfirst=True)

    # Section Type Enum
    section_type_enum = postgresql.ENUM(
        'header', 'footer', 'cover', 'table_of_contents', 'summary',
        'text', 'table', 'chart', 'image', 'metric', 'kpi',
        'trend', 'comparison', 'breakdown', 'ranking', 'heatmap',
        'insight', 'recommendation', 'anomaly', 'forecast',
        'dashboard', 'grid', 'tabs', 'accordion',
        'divider', 'spacer', 'page_break', 'custom',
        name='section_type_enum',
        create_type=False
    )
    section_type_enum.create(op.get_bind(), checkfirst=True)

    # Section Layout Enum
    section_layout_enum = postgresql.ENUM(
        'full_width', 'half_width', 'third_width', 'two_thirds', 'quarter', 'custom',
        name='section_layout_enum',
        create_type=False
    )
    section_layout_enum.create(op.get_bind(), checkfirst=True)

    # Widget Type Enum
    widget_type_enum = postgresql.ENUM(
        'bar_chart', 'line_chart', 'pie_chart', 'donut_chart', 'area_chart',
        'stacked_bar', 'grouped_bar', 'combo_chart', 'scatter_plot', 'bubble_chart',
        'waterfall', 'funnel', 'gauge', 'radar', 'treemap', 'sankey',
        'kpi_card', 'metric_card', 'progress_bar', 'sparkline', 'trend_indicator',
        'data_table', 'pivot_table', 'comparison_table', 'ranking_table',
        'geo_map', 'heatmap', 'choropleth',
        'text_box', 'rich_text', 'insight_box', 'alert_box',
        'image', 'iframe', 'custom',
        name='widget_type_enum',
        create_type=False
    )
    widget_type_enum.create(op.get_bind(), checkfirst=True)

    # Widget Size Enum
    widget_size_enum = postgresql.ENUM(
        'small', 'medium', 'large', 'full', 'custom',
        name='widget_size_enum',
        create_type=False
    )
    widget_size_enum.create(op.get_bind(), checkfirst=True)

    # ============== TABLES ==============

    # ai_report_templates
    op.create_table(
        'ai_report_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('code', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('category', postgresql.ENUM('financial', 'sales', 'hr', 'operations', 'inventory', 'customer', 'marketing', 'executive', 'operational', 'analytical', 'compliance', 'audit', 'general', 'custom', name='template_category_enum', create_type=False), nullable=False),
        sa.Column('subcategory', sa.String(100), nullable=True),
        sa.Column('tags', postgresql.JSONB, default=[]),
        sa.Column('status', postgresql.ENUM('draft', 'active', 'inactive', 'deprecated', 'archived', name='template_status_enum', create_type=False), nullable=False, default='draft'),
        sa.Column('data_sources', postgresql.JSONB, default=[]),
        sa.Column('primary_source', sa.String(100), nullable=True),
        sa.Column('queries', postgresql.JSONB, default={}),
        sa.Column('joins', postgresql.JSONB, default=[]),
        sa.Column('parameters', postgresql.JSONB, default=[]),
        sa.Column('required_parameters', postgresql.JSONB, default=[]),
        sa.Column('default_values', postgresql.JSONB, default={}),
        sa.Column('default_filters', postgresql.JSONB, default={}),
        sa.Column('available_filters', postgresql.JSONB, default=[]),
        sa.Column('layout', postgresql.JSONB, default={}),
        sa.Column('sections_config', postgresql.JSONB, default=[]),
        sa.Column('header_config', postgresql.JSONB, default={}),
        sa.Column('footer_config', postgresql.JSONB, default={}),
        sa.Column('widgets_config', postgresql.JSONB, default=[]),
        sa.Column('charts_config', postgresql.JSONB, default=[]),
        sa.Column('tables_config', postgresql.JSONB, default=[]),
        sa.Column('metrics_config', postgresql.JSONB, default=[]),
        sa.Column('kpis_config', postgresql.JSONB, default=[]),
        sa.Column('calculations', postgresql.JSONB, default=[]),
        sa.Column('ai_insights_enabled', sa.Boolean, default=True),
        sa.Column('insight_types', postgresql.JSONB, default=[]),
        sa.Column('anomaly_detection_enabled', sa.Boolean, default=True),
        sa.Column('trend_analysis_enabled', sa.Boolean, default=True),
        sa.Column('recommendations_enabled', sa.Boolean, default=True),
        sa.Column('supported_formats', postgresql.JSONB, default=['pdf', 'excel', 'csv']),
        sa.Column('default_format', sa.String(20), default='pdf'),
        sa.Column('pdf_config', postgresql.JSONB, default={}),
        sa.Column('excel_config', postgresql.JSONB, default={}),
        sa.Column('logo_url', sa.String(500), nullable=True),
        sa.Column('brand_colors', postgresql.JSONB, default={}),
        sa.Column('custom_css', sa.Text, nullable=True),
        sa.Column('font_family', sa.String(100), default='Arial'),
        sa.Column('default_schedule', postgresql.JSONB, default={}),
        sa.Column('scheduling_enabled', sa.Boolean, default=True),
        sa.Column('default_recipients', postgresql.JSONB, default=[]),
        sa.Column('email_subject_template', sa.String(500), nullable=True),
        sa.Column('email_body_template', sa.Text, nullable=True),
        sa.Column('is_public', sa.Boolean, default=False),
        sa.Column('is_system', sa.Boolean, default=False),
        sa.Column('allowed_roles', postgresql.JSONB, default=[]),
        sa.Column('allowed_organizations', postgresql.JSONB, default=[]),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('usage_count', sa.Integer, default=0),
        sa.Column('last_used_at', sa.DateTime, nullable=True),
        sa.Column('average_generation_time_ms', sa.Integer, default=0),
        sa.Column('version', sa.Integer, default=1),
        sa.Column('parent_template_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('changelog', postgresql.JSONB, default=[]),
        sa.Column('validation_rules', postgresql.JSONB, default=[]),
        sa.Column('is_validated', sa.Boolean, default=False),
        sa.Column('validation_errors', postgresql.JSONB, default=[]),
        sa.Column('extra_metadata', postgresql.JSONB, default={}),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('published_at', sa.DateTime, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('deleted_at', sa.DateTime, nullable=True),
    )

    # ai_report_executions (precisa vir antes de ai_reports)
    op.create_table(
        'ai_report_executions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('execution_number', sa.Integer, nullable=False),
        sa.Column('report_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_report_templates.id'), nullable=True),
        sa.Column('schedule_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', postgresql.ENUM('pending', 'queued', 'running', 'collecting_data', 'processing', 'generating_insights', 'rendering', 'exporting', 'delivering', 'completed', 'failed', 'cancelled', 'timeout', name='execution_status_enum', create_type=False), nullable=False, default='pending'),
        sa.Column('progress', sa.Float, default=0.0),
        sa.Column('current_step', sa.String(100), nullable=True),
        sa.Column('trigger', postgresql.ENUM('manual', 'scheduled', 'api', 'webhook', 'event', 'retry', name='execution_trigger_enum', create_type=False), nullable=False, default='manual'),
        sa.Column('triggered_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('parameters', postgresql.JSONB, default={}),
        sa.Column('filters', postgresql.JSONB, default={}),
        sa.Column('period_start', sa.DateTime, nullable=True),
        sa.Column('period_end', sa.DateTime, nullable=True),
        sa.Column('requested_formats', postgresql.JSONB, default=['pdf']),
        sa.Column('generated_formats', postgresql.JSONB, default=[]),
        sa.Column('queued_at', sa.DateTime, nullable=True),
        sa.Column('started_at', sa.DateTime, nullable=True),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        sa.Column('failed_at', sa.DateTime, nullable=True),
        sa.Column('queue_time_ms', sa.Integer, default=0),
        sa.Column('data_collection_time_ms', sa.Integer, default=0),
        sa.Column('processing_time_ms', sa.Integer, default=0),
        sa.Column('insight_generation_time_ms', sa.Integer, default=0),
        sa.Column('rendering_time_ms', sa.Integer, default=0),
        sa.Column('export_time_ms', sa.Integer, default=0),
        sa.Column('delivery_time_ms', sa.Integer, default=0),
        sa.Column('total_time_ms', sa.Integer, default=0),
        sa.Column('records_processed', sa.Integer, default=0),
        sa.Column('data_sources_queried', sa.Integer, default=0),
        sa.Column('queries_executed', sa.Integer, default=0),
        sa.Column('cache_hits', sa.Integer, default=0),
        sa.Column('cache_misses', sa.Integer, default=0),
        sa.Column('insights_generated', sa.Integer, default=0),
        sa.Column('anomalies_detected', sa.Integer, default=0),
        sa.Column('recommendations_generated', sa.Integer, default=0),
        sa.Column('pages_generated', sa.Integer, default=0),
        sa.Column('charts_generated', sa.Integer, default=0),
        sa.Column('tables_generated', sa.Integer, default=0),
        sa.Column('file_size_bytes', sa.Integer, default=0),
        sa.Column('output_files', postgresql.JSONB, default=[]),
        sa.Column('storage_paths', postgresql.JSONB, default={}),
        sa.Column('delivery_status', postgresql.JSONB, default={}),
        sa.Column('delivered_to', postgresql.JSONB, default=[]),
        sa.Column('delivery_errors', postgresql.JSONB, default=[]),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('error_code', sa.String(50), nullable=True),
        sa.Column('error_details', postgresql.JSONB, default={}),
        sa.Column('stack_trace', sa.Text, nullable=True),
        sa.Column('retry_count', sa.Integer, default=0),
        sa.Column('max_retries', sa.Integer, default=3),
        sa.Column('retry_after', sa.DateTime, nullable=True),
        sa.Column('parent_execution_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('execution_logs', postgresql.JSONB, default=[]),
        sa.Column('debug_info', postgresql.JSONB, default={}),
        sa.Column('memory_used_mb', sa.Float, default=0.0),
        sa.Column('cpu_time_seconds', sa.Float, default=0.0),
        sa.Column('worker_id', sa.String(100), nullable=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('extra_metadata', postgresql.JSONB, default={}),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )

    # ai_reports
    op.create_table(
        'ai_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('code', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('report_type', postgresql.ENUM('dashboard', 'summary', 'detailed', 'analytical', 'comparative', 'financial', 'sales', 'hr', 'operations', 'inventory', 'customer', 'kpi', 'forecast', 'anomaly', 'trend', 'audit', 'compliance', 'performance', 'custom', 'ad_hoc', name='report_type_enum', create_type=False), nullable=False, default='summary'),
        sa.Column('category', sa.String(100), nullable=True, index=True),
        sa.Column('tags', postgresql.JSONB, default=[]),
        sa.Column('status', postgresql.ENUM('draft', 'generating', 'completed', 'failed', 'archived', 'expired', name='report_status_enum', create_type=False), nullable=False, default='draft'),
        sa.Column('priority', postgresql.ENUM('low', 'normal', 'high', 'critical', name='report_priority_enum', create_type=False), nullable=False, default='normal'),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_report_templates.id'), nullable=True),
        sa.Column('period_start', sa.DateTime, nullable=True),
        sa.Column('period_end', sa.DateTime, nullable=True),
        sa.Column('period_type', sa.String(50), nullable=True),
        sa.Column('filters', postgresql.JSONB, default={}),
        sa.Column('parameters', postgresql.JSONB, default={}),
        sa.Column('data', postgresql.JSONB, default={}),
        sa.Column('summary', postgresql.JSONB, default={}),
        sa.Column('metrics', postgresql.JSONB, default={}),
        sa.Column('insights', postgresql.JSONB, default=[]),
        sa.Column('recommendations', postgresql.JSONB, default=[]),
        sa.Column('anomalies', postgresql.JSONB, default=[]),
        sa.Column('trends', postgresql.JSONB, default=[]),
        sa.Column('charts', postgresql.JSONB, default=[]),
        sa.Column('tables', postgresql.JSONB, default=[]),
        sa.Column('data_quality_score', sa.Float, default=0.0),
        sa.Column('completeness_score', sa.Float, default=0.0),
        sa.Column('accuracy_score', sa.Float, default=0.0),
        sa.Column('exported_formats', postgresql.JSONB, default=[]),
        sa.Column('file_paths', postgresql.JSONB, default={}),
        sa.Column('file_size_bytes', sa.Integer, default=0),
        sa.Column('recipients', postgresql.JSONB, default=[]),
        sa.Column('sent_at', sa.DateTime, nullable=True),
        sa.Column('sent_count', sa.Integer, default=0),
        sa.Column('view_count', sa.Integer, default=0),
        sa.Column('download_count', sa.Integer, default=0),
        sa.Column('last_viewed_at', sa.DateTime, nullable=True),
        sa.Column('last_downloaded_at', sa.DateTime, nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_public', sa.Boolean, default=False),
        sa.Column('allowed_roles', postgresql.JSONB, default=[]),
        sa.Column('allowed_users', postgresql.JSONB, default=[]),
        sa.Column('execution_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_report_executions.id'), nullable=True),
        sa.Column('generation_time_ms', sa.Integer, default=0),
        sa.Column('expires_at', sa.DateTime, nullable=True),
        sa.Column('retention_days', sa.Integer, default=90),
        sa.Column('version', sa.Integer, default=1),
        sa.Column('extra_metadata', postgresql.JSONB, default={}),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('generated_at', sa.DateTime, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('deleted_at', sa.DateTime, nullable=True),
    )

    # ai_report_schedules
    op.create_table(
        'ai_report_schedules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_report_templates.id'), nullable=False),
        sa.Column('status', postgresql.ENUM('active', 'paused', 'completed', 'failed', 'expired', 'cancelled', name='schedule_status_enum', create_type=False), nullable=False, default='active'),
        sa.Column('frequency', postgresql.ENUM('once', 'hourly', 'daily', 'weekly', 'biweekly', 'monthly', 'quarterly', 'yearly', 'custom', name='schedule_frequency_enum', create_type=False), nullable=False, default='daily'),
        sa.Column('cron_expression', sa.String(100), nullable=True),
        sa.Column('run_time', sa.Time, nullable=True),
        sa.Column('timezone', sa.String(50), default='America/Sao_Paulo'),
        sa.Column('days_of_week', postgresql.JSONB, default=[]),
        sa.Column('days_of_month', postgresql.JSONB, default=[]),
        sa.Column('months', postgresql.JSONB, default=[]),
        sa.Column('period_type', sa.String(50), nullable=True),
        sa.Column('period_offset', sa.Integer, default=0),
        sa.Column('custom_period_start', sa.String(100), nullable=True),
        sa.Column('custom_period_end', sa.String(100), nullable=True),
        sa.Column('parameters', postgresql.JSONB, default={}),
        sa.Column('filters', postgresql.JSONB, default={}),
        sa.Column('dynamic_parameters', postgresql.JSONB, default={}),
        sa.Column('output_formats', postgresql.JSONB, default=['pdf']),
        sa.Column('primary_format', sa.String(20), default='pdf'),
        sa.Column('delivery_methods', postgresql.JSONB, default=['email']),
        sa.Column('email_recipients', postgresql.JSONB, default=[]),
        sa.Column('email_cc', postgresql.JSONB, default=[]),
        sa.Column('email_bcc', postgresql.JSONB, default=[]),
        sa.Column('email_subject', sa.String(500), nullable=True),
        sa.Column('email_body', sa.Text, nullable=True),
        sa.Column('attach_report', sa.Boolean, default=True),
        sa.Column('include_summary_in_body', sa.Boolean, default=True),
        sa.Column('webhook_url', sa.String(500), nullable=True),
        sa.Column('webhook_headers', postgresql.JSONB, default={}),
        sa.Column('webhook_method', sa.String(10), default='POST'),
        sa.Column('storage_path', sa.String(500), nullable=True),
        sa.Column('filename_template', sa.String(255), default='{report_name}_{date}'),
        sa.Column('overwrite_existing', sa.Boolean, default=False),
        sa.Column('slack_channel', sa.String(100), nullable=True),
        sa.Column('slack_webhook', sa.String(500), nullable=True),
        sa.Column('teams_webhook', sa.String(500), nullable=True),
        sa.Column('next_run_at', sa.DateTime, nullable=True),
        sa.Column('last_run_at', sa.DateTime, nullable=True),
        sa.Column('last_success_at', sa.DateTime, nullable=True),
        sa.Column('last_failure_at', sa.DateTime, nullable=True),
        sa.Column('total_runs', sa.Integer, default=0),
        sa.Column('successful_runs', sa.Integer, default=0),
        sa.Column('failed_runs', sa.Integer, default=0),
        sa.Column('consecutive_failures', sa.Integer, default=0),
        sa.Column('max_runs', sa.Integer, nullable=True),
        sa.Column('max_consecutive_failures', sa.Integer, default=3),
        sa.Column('retry_on_failure', sa.Boolean, default=True),
        sa.Column('retry_attempts', sa.Integer, default=3),
        sa.Column('retry_delay_minutes', sa.Integer, default=15),
        sa.Column('start_date', sa.DateTime, nullable=True),
        sa.Column('end_date', sa.DateTime, nullable=True),
        sa.Column('expires_at', sa.DateTime, nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('notify_on_success', sa.Boolean, default=False),
        sa.Column('notify_on_failure', sa.Boolean, default=True),
        sa.Column('notification_recipients', postgresql.JSONB, default=[]),
        sa.Column('extra_metadata', postgresql.JSONB, default={}),
        sa.Column('tags', postgresql.JSONB, default=[]),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('deleted_at', sa.DateTime, nullable=True),
    )

    # Adiciona FK de schedule_id em ai_report_executions
    op.create_foreign_key(
        'fk_execution_schedule',
        'ai_report_executions',
        'ai_report_schedules',
        ['schedule_id'],
        ['id']
    )

    # ai_report_sections
    op.create_table(
        'ai_report_sections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('code', sa.String(100), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('report_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_reports.id'), nullable=True),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_report_templates.id'), nullable=True),
        sa.Column('parent_section_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_report_sections.id'), nullable=True),
        sa.Column('section_type', postgresql.ENUM('header', 'footer', 'cover', 'table_of_contents', 'summary', 'text', 'table', 'chart', 'image', 'metric', 'kpi', 'trend', 'comparison', 'breakdown', 'ranking', 'heatmap', 'insight', 'recommendation', 'anomaly', 'forecast', 'dashboard', 'grid', 'tabs', 'accordion', 'divider', 'spacer', 'page_break', 'custom', name='section_type_enum', create_type=False), nullable=False, default='text'),
        sa.Column('layout', postgresql.ENUM('full_width', 'half_width', 'third_width', 'two_thirds', 'quarter', 'custom', name='section_layout_enum', create_type=False), nullable=False, default='full_width'),
        sa.Column('order', sa.Integer, default=0),
        sa.Column('level', sa.Integer, default=0),
        sa.Column('page_number', sa.Integer, nullable=True),
        sa.Column('data_source', sa.String(100), nullable=True),
        sa.Column('query', sa.Text, nullable=True),
        sa.Column('filters', postgresql.JSONB, default={}),
        sa.Column('parameters', postgresql.JSONB, default={}),
        sa.Column('aggregations', postgresql.JSONB, default=[]),
        sa.Column('groupings', postgresql.JSONB, default=[]),
        sa.Column('sortings', postgresql.JSONB, default=[]),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('subtitle', sa.String(500), nullable=True),
        sa.Column('content', sa.Text, nullable=True),
        sa.Column('content_template', sa.Text, nullable=True),
        sa.Column('rendered_content', sa.Text, nullable=True),
        sa.Column('data', postgresql.JSONB, default={}),
        sa.Column('computed_values', postgresql.JSONB, default={}),
        sa.Column('styles', postgresql.JSONB, default={}),
        sa.Column('css_classes', postgresql.JSONB, default=[]),
        sa.Column('background_color', sa.String(20), nullable=True),
        sa.Column('border', postgresql.JSONB, default={}),
        sa.Column('padding', postgresql.JSONB, default={}),
        sa.Column('margin', postgresql.JSONB, default={}),
        sa.Column('width', sa.String(50), nullable=True),
        sa.Column('height', sa.String(50), nullable=True),
        sa.Column('min_height', sa.String(50), nullable=True),
        sa.Column('max_height', sa.String(50), nullable=True),
        sa.Column('chart_type', sa.String(50), nullable=True),
        sa.Column('chart_config', postgresql.JSONB, default={}),
        sa.Column('chart_data', postgresql.JSONB, default={}),
        sa.Column('table_columns', postgresql.JSONB, default=[]),
        sa.Column('table_config', postgresql.JSONB, default={}),
        sa.Column('table_data', postgresql.JSONB, default=[]),
        sa.Column('show_totals', sa.Boolean, default=False),
        sa.Column('show_pagination', sa.Boolean, default=False),
        sa.Column('metric_value', sa.String(100), nullable=True),
        sa.Column('metric_label', sa.String(255), nullable=True),
        sa.Column('metric_unit', sa.String(50), nullable=True),
        sa.Column('metric_trend', sa.String(20), nullable=True),
        sa.Column('metric_change', sa.Float, nullable=True),
        sa.Column('metric_target', sa.Float, nullable=True),
        sa.Column('metric_format', sa.String(50), nullable=True),
        sa.Column('insight_type', sa.String(50), nullable=True),
        sa.Column('insight_severity', sa.String(20), nullable=True),
        sa.Column('insight_data', postgresql.JSONB, default={}),
        sa.Column('visibility_condition', sa.Text, nullable=True),
        sa.Column('is_visible', sa.Boolean, default=True),
        sa.Column('show_if_empty', sa.Boolean, default=False),
        sa.Column('is_interactive', sa.Boolean, default=False),
        sa.Column('drill_down_config', postgresql.JSONB, default={}),
        sa.Column('click_action', postgresql.JSONB, default={}),
        sa.Column('extra_metadata', postgresql.JSONB, default={}),
        sa.Column('tags', postgresql.JSONB, default=[]),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
    )

    # ai_report_widgets
    op.create_table(
        'ai_report_widgets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('code', sa.String(100), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_report_templates.id'), nullable=True),
        sa.Column('section_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_report_sections.id'), nullable=True),
        sa.Column('widget_type', postgresql.ENUM('bar_chart', 'line_chart', 'pie_chart', 'donut_chart', 'area_chart', 'stacked_bar', 'grouped_bar', 'combo_chart', 'scatter_plot', 'bubble_chart', 'waterfall', 'funnel', 'gauge', 'radar', 'treemap', 'sankey', 'kpi_card', 'metric_card', 'progress_bar', 'sparkline', 'trend_indicator', 'data_table', 'pivot_table', 'comparison_table', 'ranking_table', 'geo_map', 'heatmap', 'choropleth', 'text_box', 'rich_text', 'insight_box', 'alert_box', 'image', 'iframe', 'custom', name='widget_type_enum', create_type=False), nullable=False, default='bar_chart'),
        sa.Column('order', sa.Integer, default=0),
        sa.Column('row', sa.Integer, default=0),
        sa.Column('col', sa.Integer, default=0),
        sa.Column('row_span', sa.Integer, default=1),
        sa.Column('col_span', sa.Integer, default=1),
        sa.Column('size', postgresql.ENUM('small', 'medium', 'large', 'full', 'custom', name='widget_size_enum', create_type=False), default='medium'),
        sa.Column('width', sa.String(50), nullable=True),
        sa.Column('height', sa.String(50), nullable=True),
        sa.Column('min_width', sa.String(50), nullable=True),
        sa.Column('min_height', sa.String(50), nullable=True),
        sa.Column('max_width', sa.String(50), nullable=True),
        sa.Column('max_height', sa.String(50), nullable=True),
        sa.Column('data_source', sa.String(100), nullable=True),
        sa.Column('query', sa.Text, nullable=True),
        sa.Column('query_params', postgresql.JSONB, default={}),
        sa.Column('filters', postgresql.JSONB, default={}),
        sa.Column('aggregation', sa.String(50), nullable=True),
        sa.Column('group_by', postgresql.JSONB, default=[]),
        sa.Column('order_by', postgresql.JSONB, default=[]),
        sa.Column('limit', sa.Integer, nullable=True),
        sa.Column('data_mapping', postgresql.JSONB, default={}),
        sa.Column('value_field', sa.String(100), nullable=True),
        sa.Column('label_field', sa.String(100), nullable=True),
        sa.Column('category_field', sa.String(100), nullable=True),
        sa.Column('series_field', sa.String(100), nullable=True),
        sa.Column('data', postgresql.JSONB, default={}),
        sa.Column('computed_data', postgresql.JSONB, default={}),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('subtitle', sa.String(500), nullable=True),
        sa.Column('show_title', sa.Boolean, default=True),
        sa.Column('show_legend', sa.Boolean, default=True),
        sa.Column('legend_position', sa.String(20), default='bottom'),
        sa.Column('colors', postgresql.JSONB, default=[]),
        sa.Column('color_scheme', sa.String(50), nullable=True),
        sa.Column('background_color', sa.String(20), nullable=True),
        sa.Column('x_axis_config', postgresql.JSONB, default={}),
        sa.Column('y_axis_config', postgresql.JSONB, default={}),
        sa.Column('secondary_y_axis', postgresql.JSONB, default={}),
        sa.Column('number_format', sa.String(50), nullable=True),
        sa.Column('date_format', sa.String(50), nullable=True),
        sa.Column('currency', sa.String(10), nullable=True),
        sa.Column('decimal_places', sa.Integer, default=2),
        sa.Column('show_values', sa.Boolean, default=True),
        sa.Column('value_position', sa.String(20), default='inside'),
        sa.Column('show_tooltip', sa.Boolean, default=True),
        sa.Column('tooltip_template', sa.Text, nullable=True),
        sa.Column('enable_animation', sa.Boolean, default=True),
        sa.Column('animation_duration', sa.Integer, default=500),
        sa.Column('is_interactive', sa.Boolean, default=True),
        sa.Column('enable_zoom', sa.Boolean, default=False),
        sa.Column('enable_drill_down', sa.Boolean, default=False),
        sa.Column('drill_down_config', postgresql.JSONB, default={}),
        sa.Column('click_action', postgresql.JSONB, default={}),
        sa.Column('responsive', sa.Boolean, default=True),
        sa.Column('mobile_config', postgresql.JSONB, default={}),
        sa.Column('thresholds', postgresql.JSONB, default=[]),
        sa.Column('alert_rules', postgresql.JSONB, default=[]),
        sa.Column('highlight_conditions', postgresql.JSONB, default=[]),
        sa.Column('kpi_value', sa.String(100), nullable=True),
        sa.Column('kpi_label', sa.String(255), nullable=True),
        sa.Column('kpi_unit', sa.String(50), nullable=True),
        sa.Column('kpi_trend', sa.String(20), nullable=True),
        sa.Column('kpi_change', sa.Float, nullable=True),
        sa.Column('kpi_change_period', sa.String(50), nullable=True),
        sa.Column('kpi_target', sa.Float, nullable=True),
        sa.Column('kpi_status', sa.String(20), nullable=True),
        sa.Column('comparison_enabled', sa.Boolean, default=False),
        sa.Column('comparison_type', sa.String(50), nullable=True),
        sa.Column('comparison_value', sa.Float, nullable=True),
        sa.Column('comparison_label', sa.String(100), nullable=True),
        sa.Column('styles', postgresql.JSONB, default={}),
        sa.Column('css_classes', postgresql.JSONB, default=[]),
        sa.Column('custom_css', sa.Text, nullable=True),
        sa.Column('visibility_condition', sa.Text, nullable=True),
        sa.Column('is_visible', sa.Boolean, default=True),
        sa.Column('cache_enabled', sa.Boolean, default=True),
        sa.Column('cache_ttl_seconds', sa.Integer, default=300),
        sa.Column('last_cached_at', sa.DateTime, nullable=True),
        sa.Column('is_system', sa.Boolean, default=False),
        sa.Column('is_reusable', sa.Boolean, default=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('extra_metadata', postgresql.JSONB, default={}),
        sa.Column('tags', postgresql.JSONB, default=[]),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
    )

    # ============== INDEXES ==============

    # Indexes para ai_reports
    op.create_index('ix_reports_type_status', 'ai_reports', ['report_type', 'status'])
    op.create_index('ix_reports_template', 'ai_reports', ['template_id'])
    op.create_index('ix_reports_created_by', 'ai_reports', ['created_by'])
    op.create_index('ix_reports_generated_at', 'ai_reports', ['generated_at'])

    # Indexes para ai_report_templates
    op.create_index('ix_templates_category_status', 'ai_report_templates', ['category', 'status'])
    op.create_index('ix_templates_is_system', 'ai_report_templates', ['is_system'])

    # Indexes para ai_report_schedules
    op.create_index('ix_schedules_status_next_run', 'ai_report_schedules', ['status', 'next_run_at'])
    op.create_index('ix_schedules_template', 'ai_report_schedules', ['template_id'])

    # Indexes para ai_report_executions
    op.create_index('ix_executions_status', 'ai_report_executions', ['status'])
    op.create_index('ix_executions_schedule', 'ai_report_executions', ['schedule_id'])
    op.create_index('ix_executions_created_at', 'ai_report_executions', ['created_at'])

    # Indexes para ai_report_sections
    op.create_index('ix_sections_report', 'ai_report_sections', ['report_id'])
    op.create_index('ix_sections_template', 'ai_report_sections', ['template_id'])
    op.create_index('ix_sections_order', 'ai_report_sections', ['report_id', 'order'])

    # Indexes para ai_report_widgets
    op.create_index('ix_widgets_template', 'ai_report_widgets', ['template_id'])
    op.create_index('ix_widgets_section', 'ai_report_widgets', ['section_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_widgets_section', table_name='ai_report_widgets')
    op.drop_index('ix_widgets_template', table_name='ai_report_widgets')
    op.drop_index('ix_sections_order', table_name='ai_report_sections')
    op.drop_index('ix_sections_template', table_name='ai_report_sections')
    op.drop_index('ix_sections_report', table_name='ai_report_sections')
    op.drop_index('ix_executions_created_at', table_name='ai_report_executions')
    op.drop_index('ix_executions_schedule', table_name='ai_report_executions')
    op.drop_index('ix_executions_status', table_name='ai_report_executions')
    op.drop_index('ix_schedules_template', table_name='ai_report_schedules')
    op.drop_index('ix_schedules_status_next_run', table_name='ai_report_schedules')
    op.drop_index('ix_templates_is_system', table_name='ai_report_templates')
    op.drop_index('ix_templates_category_status', table_name='ai_report_templates')
    op.drop_index('ix_reports_generated_at', table_name='ai_reports')
    op.drop_index('ix_reports_created_by', table_name='ai_reports')
    op.drop_index('ix_reports_template', table_name='ai_reports')
    op.drop_index('ix_reports_type_status', table_name='ai_reports')

    # Drop FK
    op.drop_constraint('fk_execution_schedule', 'ai_report_executions', type_='foreignkey')

    # Drop tables
    op.drop_table('ai_report_widgets')
    op.drop_table('ai_report_sections')
    op.drop_table('ai_report_schedules')
    op.drop_table('ai_reports')
    op.drop_table('ai_report_executions')
    op.drop_table('ai_report_templates')

    # Drop enums
    op.execute("DROP TYPE IF EXISTS widget_size_enum")
    op.execute("DROP TYPE IF EXISTS widget_type_enum")
    op.execute("DROP TYPE IF EXISTS section_layout_enum")
    op.execute("DROP TYPE IF EXISTS section_type_enum")
    op.execute("DROP TYPE IF EXISTS execution_trigger_enum")
    op.execute("DROP TYPE IF EXISTS execution_status_enum")
    op.execute("DROP TYPE IF EXISTS schedule_status_enum")
    op.execute("DROP TYPE IF EXISTS schedule_frequency_enum")
    op.execute("DROP TYPE IF EXISTS template_status_enum")
    op.execute("DROP TYPE IF EXISTS template_category_enum")
    op.execute("DROP TYPE IF EXISTS report_priority_enum")
    op.execute("DROP TYPE IF EXISTS report_status_enum")
    op.execute("DROP TYPE IF EXISTS report_type_enum")
