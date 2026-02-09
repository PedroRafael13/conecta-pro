"""
Report Generator Schemas.

Schemas Pydantic para validação de dados do módulo de relatórios.
"""

from datetime import datetime, time
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

# ============== ENUMS ==============


class ReportTypeEnum(StrEnum):
    """Tipos de relatório."""

    DASHBOARD = "dashboard"
    SUMMARY = "summary"
    DETAILED = "detailed"
    ANALYTICAL = "analytical"
    COMPARATIVE = "comparative"
    FINANCIAL = "financial"
    SALES = "sales"
    HR = "hr"
    OPERATIONS = "operations"
    INVENTORY = "inventory"
    CUSTOMER = "customer"
    KPI = "kpi"
    FORECAST = "forecast"
    ANOMALY = "anomaly"
    TREND = "trend"
    AUDIT = "audit"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"
    CUSTOM = "custom"
    AD_HOC = "ad_hoc"


class ReportStatusEnum(StrEnum):
    """Status do relatório."""

    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"
    EXPIRED = "expired"


class ReportFormatEnum(StrEnum):
    """Formatos de exportação."""

    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    HTML = "html"
    WORD = "word"
    POWERPOINT = "powerpoint"


class ReportPriorityEnum(StrEnum):
    """Prioridade do relatório."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class TemplateCategoryEnum(StrEnum):
    """Categorias de template."""

    FINANCIAL = "financial"
    SALES = "sales"
    HR = "hr"
    OPERATIONS = "operations"
    INVENTORY = "inventory"
    CUSTOMER = "customer"
    MARKETING = "marketing"
    EXECUTIVE = "executive"
    OPERATIONAL = "operational"
    ANALYTICAL = "analytical"
    COMPLIANCE = "compliance"
    AUDIT = "audit"
    GENERAL = "general"
    CUSTOM = "custom"


class TemplateStatusEnum(StrEnum):
    """Status do template."""

    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class DataSourceEnum(StrEnum):
    """Fontes de dados disponíveis."""

    LEADS = "leads"
    OPPORTUNITIES = "opportunities"
    CUSTOMERS = "customers"
    CONTRACTS = "contracts"
    INVOICES = "invoices"
    PAYMENTS = "payments"
    EXPENSES = "expenses"
    BUDGET = "budget"
    EMPLOYEES = "employees"
    ATTENDANCE = "attendance"
    PAYROLL = "payroll"
    RECRUITMENT = "recruitment"
    ORDERS = "orders"
    INVENTORY = "inventory"
    MAINTENANCE = "maintenance"
    EQUIPMENT = "equipment"
    PREDICTIONS = "predictions"
    ANOMALIES = "anomalies"
    SENTIMENT = "sentiment"
    FRAUD = "fraud"
    CUSTOM_QUERY = "custom_query"
    EXTERNAL_API = "external_api"


class ScheduleFrequencyEnum(StrEnum):
    """Frequência de agendamento."""

    ONCE = "once"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class ScheduleStatusEnum(StrEnum):
    """Status do agendamento."""

    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class DeliveryMethodEnum(StrEnum):
    """Método de entrega."""

    EMAIL = "email"
    SLACK = "slack"
    TEAMS = "teams"
    WEBHOOK = "webhook"
    STORAGE = "storage"
    FTP = "ftp"
    S3 = "s3"


class ExecutionStatusEnum(StrEnum):
    """Status da execução."""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COLLECTING_DATA = "collecting_data"
    PROCESSING = "processing"
    GENERATING_INSIGHTS = "generating_insights"
    RENDERING = "rendering"
    EXPORTING = "exporting"
    DELIVERING = "delivering"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class ExecutionTriggerEnum(StrEnum):
    """Gatilho da execução."""

    MANUAL = "manual"
    SCHEDULED = "scheduled"
    API = "api"
    WEBHOOK = "webhook"
    EVENT = "event"
    RETRY = "retry"


class SectionTypeEnum(StrEnum):
    """Tipos de seção."""

    HEADER = "header"
    FOOTER = "footer"
    COVER = "cover"
    TABLE_OF_CONTENTS = "table_of_contents"
    SUMMARY = "summary"
    TEXT = "text"
    TABLE = "table"
    CHART = "chart"
    IMAGE = "image"
    METRIC = "metric"
    KPI = "kpi"
    TREND = "trend"
    COMPARISON = "comparison"
    BREAKDOWN = "breakdown"
    RANKING = "ranking"
    HEATMAP = "heatmap"
    INSIGHT = "insight"
    RECOMMENDATION = "recommendation"
    ANOMALY = "anomaly"
    FORECAST = "forecast"
    DASHBOARD = "dashboard"
    GRID = "grid"
    TABS = "tabs"
    ACCORDION = "accordion"
    DIVIDER = "divider"
    SPACER = "spacer"
    PAGE_BREAK = "page_break"
    CUSTOM = "custom"


class SectionLayoutEnum(StrEnum):
    """Layout da seção."""

    FULL_WIDTH = "full_width"
    HALF_WIDTH = "half_width"
    THIRD_WIDTH = "third_width"
    TWO_THIRDS = "two_thirds"
    QUARTER = "quarter"
    CUSTOM = "custom"


class WidgetTypeEnum(StrEnum):
    """Tipos de widget."""

    BAR_CHART = "bar_chart"
    LINE_CHART = "line_chart"
    PIE_CHART = "pie_chart"
    DONUT_CHART = "donut_chart"
    AREA_CHART = "area_chart"
    STACKED_BAR = "stacked_bar"
    GROUPED_BAR = "grouped_bar"
    COMBO_CHART = "combo_chart"
    SCATTER_PLOT = "scatter_plot"
    BUBBLE_CHART = "bubble_chart"
    WATERFALL = "waterfall"
    FUNNEL = "funnel"
    GAUGE = "gauge"
    RADAR = "radar"
    TREEMAP = "treemap"
    SANKEY = "sankey"
    KPI_CARD = "kpi_card"
    METRIC_CARD = "metric_card"
    PROGRESS_BAR = "progress_bar"
    SPARKLINE = "sparkline"
    TREND_INDICATOR = "trend_indicator"
    DATA_TABLE = "data_table"
    PIVOT_TABLE = "pivot_table"
    COMPARISON_TABLE = "comparison_table"
    RANKING_TABLE = "ranking_table"
    GEO_MAP = "geo_map"
    HEATMAP = "heatmap"
    CHOROPLETH = "choropleth"
    TEXT_BOX = "text_box"
    RICH_TEXT = "rich_text"
    INSIGHT_BOX = "insight_box"
    ALERT_BOX = "alert_box"
    IMAGE = "image"
    IFRAME = "iframe"
    CUSTOM = "custom"


class WidgetSizeEnum(StrEnum):
    """Tamanhos predefinidos."""

    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    FULL = "full"
    CUSTOM = "custom"


# ============== BASE SCHEMAS ==============


class BaseSchema(BaseModel):
    """Schema base."""

    class Config:
        from_attributes = True
        populate_by_name = True


# ============== REPORT SCHEMAS ==============


class ReportCreate(BaseSchema):
    """Schema para criar relatório."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    report_type: ReportTypeEnum = ReportTypeEnum.SUMMARY
    category: str | None = Field(None, max_length=100)
    tags: list[str] | None = Field(default_factory=list)
    priority: ReportPriorityEnum = ReportPriorityEnum.NORMAL
    template_id: UUID | None = None
    period_start: datetime | None = None
    period_end: datetime | None = None
    period_type: str | None = None
    filters: dict[str, Any] | None = Field(default_factory=dict)
    parameters: dict[str, Any] | None = Field(default_factory=dict)
    recipients: list[str] | None = Field(default_factory=list)
    is_public: bool = False
    allowed_roles: list[str] | None = Field(default_factory=list)
    expires_at: datetime | None = None
    retention_days: int = Field(default=90, ge=1, le=3650)


class ReportUpdate(BaseSchema):
    """Schema para atualizar relatório."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    category: str | None = Field(None, max_length=100)
    tags: list[str] | None = None
    priority: ReportPriorityEnum | None = None
    status: ReportStatusEnum | None = None
    recipients: list[str] | None = None
    is_public: bool | None = None
    allowed_roles: list[str] | None = None
    expires_at: datetime | None = None


class ReportResponse(BaseSchema):
    """Schema de resposta de relatório."""

    id: UUID
    code: str
    name: str
    description: str | None
    report_type: ReportTypeEnum
    category: str | None
    tags: list[str]
    status: ReportStatusEnum
    priority: ReportPriorityEnum
    template_id: UUID | None
    period_start: datetime | None
    period_end: datetime | None
    period_type: str | None
    filters: dict[str, Any]
    parameters: dict[str, Any]
    summary: dict[str, Any]
    metrics: dict[str, Any]
    insights: list[dict[str, Any]]
    recommendations: list[dict[str, Any]]
    anomalies: list[dict[str, Any]]
    data_quality_score: float
    completeness_score: float
    accuracy_score: float
    exported_formats: list[str]
    file_paths: dict[str, str]
    recipients: list[str]
    sent_at: datetime | None
    view_count: int
    download_count: int
    last_viewed_at: datetime | None
    created_by: UUID | None
    organization_id: UUID | None
    is_public: bool
    generation_time_ms: int
    expires_at: datetime | None
    version: int
    created_at: datetime
    updated_at: datetime | None
    generated_at: datetime | None


class ReportSummary(BaseSchema):
    """Schema resumido de relatório."""

    id: UUID
    code: str
    name: str
    report_type: ReportTypeEnum
    status: ReportStatusEnum
    period_description: str | None
    insights_count: int
    has_anomalies: bool
    quality_score: float
    created_at: datetime
    generated_at: datetime | None


class ReportListResponse(BaseSchema):
    """Schema de lista de relatórios."""

    items: list[ReportSummary]
    total: int
    page: int
    size: int
    pages: int


class ReportFilter(BaseSchema):
    """Schema de filtro de relatórios."""

    report_type: ReportTypeEnum | None = None
    status: ReportStatusEnum | None = None
    category: str | None = None
    priority: ReportPriorityEnum | None = None
    template_id: UUID | None = None
    created_by: UUID | None = None
    period_start: datetime | None = None
    period_end: datetime | None = None
    tags: list[str] | None = None
    search: str | None = None


# ============== TEMPLATE SCHEMAS ==============


class TemplateParameter(BaseSchema):
    """Schema de parâmetro de template."""

    name: str
    label: str
    type: str  # string, number, date, boolean, select, multi_select
    required: bool = False
    default_value: Any | None = None
    options: list[dict[str, Any]] | None = None
    validation: dict[str, Any] | None = None
    description: str | None = None


class TemplateSectionConfig(BaseSchema):
    """Schema de configuração de seção."""

    code: str
    name: str
    section_type: SectionTypeEnum
    layout: SectionLayoutEnum = SectionLayoutEnum.FULL_WIDTH
    order: int = 0
    data_source: str | None = None
    query: str | None = None
    filters: dict[str, Any] | None = None
    title: str | None = None
    content_template: str | None = None
    chart_config: dict[str, Any] | None = None
    table_config: dict[str, Any] | None = None
    styles: dict[str, Any] | None = None
    is_visible: bool = True


class ReportTemplateCreate(BaseSchema):
    """Schema para criar template."""

    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    category: TemplateCategoryEnum = TemplateCategoryEnum.GENERAL
    subcategory: str | None = Field(None, max_length=100)
    tags: list[str] | None = Field(default_factory=list)
    data_sources: list[str] = Field(default_factory=list)
    primary_source: str | None = None
    queries: dict[str, str] | None = Field(default_factory=dict)
    parameters: list[TemplateParameter] | None = Field(default_factory=list)
    required_parameters: list[str] | None = Field(default_factory=list)
    default_values: dict[str, Any] | None = Field(default_factory=dict)
    default_filters: dict[str, Any] | None = Field(default_factory=dict)
    sections_config: list[TemplateSectionConfig] | None = Field(default_factory=list)
    widgets_config: list[dict[str, Any]] | None = Field(default_factory=list)
    metrics_config: list[dict[str, Any]] | None = Field(default_factory=list)
    ai_insights_enabled: bool = True
    anomaly_detection_enabled: bool = True
    trend_analysis_enabled: bool = True
    recommendations_enabled: bool = True
    supported_formats: list[str] = Field(default=["pdf", "excel", "csv"])
    default_format: str = "pdf"
    is_public: bool = False
    is_system: bool = False

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Valida código do template."""
        import re

        if not re.match(r"^[a-z][a-z0-9_]*$", v):
            raise ValueError("Código deve conter apenas letras minúsculas, números e underscore")
        return v


class ReportTemplateUpdate(BaseSchema):
    """Schema para atualizar template."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    category: TemplateCategoryEnum | None = None
    subcategory: str | None = Field(None, max_length=100)
    tags: list[str] | None = None
    status: TemplateStatusEnum | None = None
    data_sources: list[str] | None = None
    primary_source: str | None = None
    parameters: list[TemplateParameter] | None = None
    sections_config: list[TemplateSectionConfig] | None = None
    widgets_config: list[dict[str, Any]] | None = None
    ai_insights_enabled: bool | None = None
    supported_formats: list[str] | None = None
    is_public: bool | None = None


class ReportTemplateResponse(BaseSchema):
    """Schema de resposta de template."""

    id: UUID
    code: str
    name: str
    description: str | None
    category: TemplateCategoryEnum
    subcategory: str | None
    tags: list[str]
    status: TemplateStatusEnum
    data_sources: list[str]
    primary_source: str | None
    parameters: list[dict[str, Any]]
    required_parameters: list[str]
    default_values: dict[str, Any]
    sections_config: list[dict[str, Any]]
    widgets_config: list[dict[str, Any]]
    metrics_config: list[dict[str, Any]]
    ai_insights_enabled: bool
    anomaly_detection_enabled: bool
    trend_analysis_enabled: bool
    recommendations_enabled: bool
    supported_formats: list[str]
    default_format: str
    is_public: bool
    is_system: bool
    is_ready: bool
    usage_count: int
    last_used_at: datetime | None
    average_generation_time_ms: int
    version: int
    created_by: UUID | None
    organization_id: UUID | None
    created_at: datetime
    updated_at: datetime | None


class ReportTemplateListResponse(BaseSchema):
    """Schema de lista de templates."""

    items: list[ReportTemplateResponse]
    total: int
    page: int
    size: int
    pages: int


# ============== SCHEDULE SCHEMAS ==============


class ReportScheduleCreate(BaseSchema):
    """Schema para criar agendamento."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    template_id: UUID
    frequency: ScheduleFrequencyEnum = ScheduleFrequencyEnum.DAILY
    cron_expression: str | None = None
    run_time: time | None = None
    timezone: str = "America/Sao_Paulo"
    days_of_week: list[int] | None = None
    days_of_month: list[int] | None = None
    period_type: str | None = None
    parameters: dict[str, Any] | None = Field(default_factory=dict)
    filters: dict[str, Any] | None = Field(default_factory=dict)
    output_formats: list[str] = Field(default=["pdf"])
    delivery_methods: list[str] = Field(default=["email"])
    email_recipients: list[str] | None = Field(default_factory=list)
    email_subject: str | None = None
    email_body: str | None = None
    webhook_url: str | None = None
    slack_channel: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    max_runs: int | None = None
    notify_on_failure: bool = True


class ReportScheduleUpdate(BaseSchema):
    """Schema para atualizar agendamento."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    status: ScheduleStatusEnum | None = None
    frequency: ScheduleFrequencyEnum | None = None
    run_time: time | None = None
    parameters: dict[str, Any] | None = None
    filters: dict[str, Any] | None = None
    output_formats: list[str] | None = None
    email_recipients: list[str] | None = None
    email_subject: str | None = None
    end_date: datetime | None = None


class ReportScheduleResponse(BaseSchema):
    """Schema de resposta de agendamento."""

    id: UUID
    name: str
    description: str | None
    template_id: UUID
    status: ScheduleStatusEnum
    frequency: ScheduleFrequencyEnum
    cron_expression: str | None
    run_time: time | None
    timezone: str
    days_of_week: list[int]
    days_of_month: list[int]
    period_type: str | None
    parameters: dict[str, Any]
    filters: dict[str, Any]
    output_formats: list[str]
    delivery_methods: list[str]
    email_recipients: list[str]
    next_run_at: datetime | None
    last_run_at: datetime | None
    last_success_at: datetime | None
    last_failure_at: datetime | None
    total_runs: int
    successful_runs: int
    failed_runs: int
    success_rate: float
    start_date: datetime | None
    end_date: datetime | None
    created_by: UUID | None
    organization_id: UUID | None
    created_at: datetime
    updated_at: datetime | None


class ReportScheduleListResponse(BaseSchema):
    """Schema de lista de agendamentos."""

    items: list[ReportScheduleResponse]
    total: int
    page: int
    size: int
    pages: int


# ============== EXECUTION SCHEMAS ==============


class ExecutionMetrics(BaseSchema):
    """Schema de métricas de execução."""

    queue_time_ms: int
    data_collection_time_ms: int
    processing_time_ms: int
    insight_generation_time_ms: int
    rendering_time_ms: int
    export_time_ms: int
    delivery_time_ms: int
    total_time_ms: int
    records_processed: int
    queries_executed: int
    cache_hit_rate: float
    insights_generated: int
    anomalies_detected: int


class ReportExecutionResponse(BaseSchema):
    """Schema de resposta de execução."""

    id: UUID
    execution_number: int
    report_id: UUID | None
    template_id: UUID | None
    schedule_id: UUID | None
    status: ExecutionStatusEnum
    progress: float
    current_step: str | None
    trigger: ExecutionTriggerEnum
    triggered_by: UUID | None
    parameters: dict[str, Any]
    period_start: datetime | None
    period_end: datetime | None
    requested_formats: list[str]
    generated_formats: list[str]
    started_at: datetime | None
    completed_at: datetime | None
    failed_at: datetime | None
    metrics: ExecutionMetrics | None
    output_files: list[dict[str, Any]]
    delivery_status: dict[str, Any]
    error_message: str | None
    error_code: str | None
    retry_count: int
    can_retry: bool
    created_at: datetime


class ReportExecutionListResponse(BaseSchema):
    """Schema de lista de execuções."""

    items: list[ReportExecutionResponse]
    total: int
    page: int
    size: int
    pages: int


# ============== SECTION SCHEMAS ==============


class ReportSectionCreate(BaseSchema):
    """Schema para criar seção."""

    code: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    section_type: SectionTypeEnum
    layout: SectionLayoutEnum = SectionLayoutEnum.FULL_WIDTH
    order: int = 0
    data_source: str | None = None
    query: str | None = None
    filters: dict[str, Any] | None = None
    title: str | None = None
    content: str | None = None
    chart_type: str | None = None
    chart_config: dict[str, Any] | None = None
    table_columns: list[dict[str, Any]] | None = None
    table_config: dict[str, Any] | None = None
    styles: dict[str, Any] | None = None
    is_visible: bool = True


class ReportSectionUpdate(BaseSchema):
    """Schema para atualizar seção."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    section_type: SectionTypeEnum | None = None
    layout: SectionLayoutEnum | None = None
    order: int | None = None
    data_source: str | None = None
    query: str | None = None
    title: str | None = None
    content: str | None = None
    styles: dict[str, Any] | None = None
    is_visible: bool | None = None


class ReportSectionResponse(BaseSchema):
    """Schema de resposta de seção."""

    id: UUID
    code: str
    name: str
    description: str | None
    section_type: SectionTypeEnum
    layout: SectionLayoutEnum
    order: int
    level: int
    title: str | None
    subtitle: str | None
    content: str | None
    data: dict[str, Any]
    chart_type: str | None
    chart_data: dict[str, Any]
    table_columns: list[dict[str, Any]]
    table_data: list[dict[str, Any]]
    metric_value: str | None
    metric_label: str | None
    metric_trend: str | None
    metric_change: float | None
    is_visible: bool
    has_data: bool
    created_at: datetime


# ============== WIDGET SCHEMAS ==============


class ReportWidgetCreate(BaseSchema):
    """Schema para criar widget."""

    code: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    widget_type: WidgetTypeEnum
    size: WidgetSizeEnum = WidgetSizeEnum.MEDIUM
    data_source: str | None = None
    query: str | None = None
    data_mapping: dict[str, str] | None = None
    title: str | None = None
    colors: list[str] | None = None
    x_axis_config: dict[str, Any] | None = None
    y_axis_config: dict[str, Any] | None = None
    show_legend: bool = True
    show_values: bool = True
    thresholds: list[dict[str, Any]] | None = None
    styles: dict[str, Any] | None = None
    is_interactive: bool = True


class ReportWidgetUpdate(BaseSchema):
    """Schema para atualizar widget."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    widget_type: WidgetTypeEnum | None = None
    size: WidgetSizeEnum | None = None
    data_source: str | None = None
    title: str | None = None
    colors: list[str] | None = None
    show_legend: bool | None = None
    styles: dict[str, Any] | None = None
    is_visible: bool | None = None


class ReportWidgetResponse(BaseSchema):
    """Schema de resposta de widget."""

    id: UUID
    code: str
    name: str
    description: str | None
    widget_type: WidgetTypeEnum
    size: WidgetSizeEnum
    title: str | None
    data_source: str | None
    data: dict[str, Any]
    data_mapping: dict[str, str]
    colors: list[str]
    show_legend: bool
    show_values: bool
    thresholds: list[dict[str, Any]]
    kpi_value: str | None
    kpi_label: str | None
    kpi_unit: str | None
    kpi_trend: str | None
    kpi_change: float | None
    kpi_status: str | None
    has_data: bool
    is_visible: bool
    is_reusable: bool
    created_at: datetime


# ============== GENERATION SCHEMAS ==============


class GenerateReportRequest(BaseSchema):
    """Schema para solicitar geração de relatório."""

    template_id: UUID | None = None
    template_code: str | None = None
    name: str | None = None
    report_type: ReportTypeEnum | None = None
    period_start: datetime | None = None
    period_end: datetime | None = None
    period_type: str | None = None
    parameters: dict[str, Any] | None = Field(default_factory=dict)
    filters: dict[str, Any] | None = Field(default_factory=dict)
    output_formats: list[str] = Field(default=["pdf"])
    include_insights: bool = True
    include_recommendations: bool = True
    include_anomalies: bool = True
    priority: ReportPriorityEnum = ReportPriorityEnum.NORMAL
    async_generation: bool = False
    notify_on_completion: bool = False
    recipients: list[str] | None = None


class GenerateReportResponse(BaseSchema):
    """Schema de resposta de geração."""

    report_id: UUID
    execution_id: UUID
    status: ExecutionStatusEnum
    message: str
    estimated_time_seconds: int | None
    progress_url: str | None


# ============== EXPORT SCHEMAS ==============


class ExportReportRequest(BaseSchema):
    """Schema para exportar relatório."""

    report_id: UUID
    format: ReportFormatEnum
    include_charts: bool = True
    include_data: bool = True
    page_size: str | None = "A4"
    orientation: str | None = "portrait"
    include_header: bool = True
    include_footer: bool = True
    password: str | None = None


class ExportReportResponse(BaseSchema):
    """Schema de resposta de exportação."""

    report_id: UUID
    format: ReportFormatEnum
    file_path: str
    file_url: str | None
    file_size_bytes: int
    generated_at: datetime
    expires_at: datetime | None


# ============== DASHBOARD SCHEMAS ==============


class ReportDashboardResponse(BaseSchema):
    """Schema de dashboard de relatórios."""

    total_reports: int
    reports_by_status: dict[str, int]
    reports_by_type: dict[str, int]
    reports_this_month: int
    reports_trend: list[dict[str, Any]]
    average_generation_time_ms: int
    total_insights_generated: int
    total_anomalies_detected: int
    most_used_templates: list[dict[str, Any]]
    recent_reports: list[ReportSummary]
    scheduled_reports_count: int
    failed_schedules_count: int


class ReportStatsResponse(BaseSchema):
    """Schema de estatísticas de relatórios."""

    period: str
    total_generated: int
    total_exported: int
    total_delivered: int
    generation_success_rate: float
    delivery_success_rate: float
    average_generation_time_ms: int
    insights_per_report: float
    most_common_types: list[dict[str, int]]
    most_common_formats: list[dict[str, int]]
    busiest_hours: list[dict[str, int]]
