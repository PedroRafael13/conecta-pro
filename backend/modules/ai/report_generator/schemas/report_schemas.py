"""
Report Generator Schemas.

Schemas Pydantic para validação de dados do módulo de relatórios.
"""

from datetime import datetime, time
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ============== ENUMS ==============

class ReportTypeEnum(str, Enum):
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


class ReportStatusEnum(str, Enum):
    """Status do relatório."""
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"
    EXPIRED = "expired"


class ReportFormatEnum(str, Enum):
    """Formatos de exportação."""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    HTML = "html"
    WORD = "word"
    POWERPOINT = "powerpoint"


class ReportPriorityEnum(str, Enum):
    """Prioridade do relatório."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class TemplateCategoryEnum(str, Enum):
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


class TemplateStatusEnum(str, Enum):
    """Status do template."""
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class DataSourceEnum(str, Enum):
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


class ScheduleFrequencyEnum(str, Enum):
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


class ScheduleStatusEnum(str, Enum):
    """Status do agendamento."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class DeliveryMethodEnum(str, Enum):
    """Método de entrega."""
    EMAIL = "email"
    SLACK = "slack"
    TEAMS = "teams"
    WEBHOOK = "webhook"
    STORAGE = "storage"
    FTP = "ftp"
    S3 = "s3"


class ExecutionStatusEnum(str, Enum):
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


class ExecutionTriggerEnum(str, Enum):
    """Gatilho da execução."""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    API = "api"
    WEBHOOK = "webhook"
    EVENT = "event"
    RETRY = "retry"


class SectionTypeEnum(str, Enum):
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


class SectionLayoutEnum(str, Enum):
    """Layout da seção."""
    FULL_WIDTH = "full_width"
    HALF_WIDTH = "half_width"
    THIRD_WIDTH = "third_width"
    TWO_THIRDS = "two_thirds"
    QUARTER = "quarter"
    CUSTOM = "custom"


class WidgetTypeEnum(str, Enum):
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


class WidgetSizeEnum(str, Enum):
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
    description: Optional[str] = Field(None, max_length=2000)
    report_type: ReportTypeEnum = ReportTypeEnum.SUMMARY
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = Field(default_factory=list)
    priority: ReportPriorityEnum = ReportPriorityEnum.NORMAL
    template_id: Optional[UUID] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    period_type: Optional[str] = None
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    recipients: Optional[List[str]] = Field(default_factory=list)
    is_public: bool = False
    allowed_roles: Optional[List[str]] = Field(default_factory=list)
    expires_at: Optional[datetime] = None
    retention_days: int = Field(default=90, ge=1, le=3650)


class ReportUpdate(BaseSchema):
    """Schema para atualizar relatório."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    priority: Optional[ReportPriorityEnum] = None
    status: Optional[ReportStatusEnum] = None
    recipients: Optional[List[str]] = None
    is_public: Optional[bool] = None
    allowed_roles: Optional[List[str]] = None
    expires_at: Optional[datetime] = None


class ReportResponse(BaseSchema):
    """Schema de resposta de relatório."""
    id: UUID
    code: str
    name: str
    description: Optional[str]
    report_type: ReportTypeEnum
    category: Optional[str]
    tags: List[str]
    status: ReportStatusEnum
    priority: ReportPriorityEnum
    template_id: Optional[UUID]
    period_start: Optional[datetime]
    period_end: Optional[datetime]
    period_type: Optional[str]
    filters: Dict[str, Any]
    parameters: Dict[str, Any]
    summary: Dict[str, Any]
    metrics: Dict[str, Any]
    insights: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    anomalies: List[Dict[str, Any]]
    data_quality_score: float
    completeness_score: float
    accuracy_score: float
    exported_formats: List[str]
    file_paths: Dict[str, str]
    recipients: List[str]
    sent_at: Optional[datetime]
    view_count: int
    download_count: int
    last_viewed_at: Optional[datetime]
    created_by: Optional[UUID]
    organization_id: Optional[UUID]
    is_public: bool
    generation_time_ms: int
    expires_at: Optional[datetime]
    version: int
    created_at: datetime
    updated_at: Optional[datetime]
    generated_at: Optional[datetime]


class ReportSummary(BaseSchema):
    """Schema resumido de relatório."""
    id: UUID
    code: str
    name: str
    report_type: ReportTypeEnum
    status: ReportStatusEnum
    period_description: Optional[str]
    insights_count: int
    has_anomalies: bool
    quality_score: float
    created_at: datetime
    generated_at: Optional[datetime]


class ReportListResponse(BaseSchema):
    """Schema de lista de relatórios."""
    items: List[ReportSummary]
    total: int
    page: int
    size: int
    pages: int


class ReportFilter(BaseSchema):
    """Schema de filtro de relatórios."""
    report_type: Optional[ReportTypeEnum] = None
    status: Optional[ReportStatusEnum] = None
    category: Optional[str] = None
    priority: Optional[ReportPriorityEnum] = None
    template_id: Optional[UUID] = None
    created_by: Optional[UUID] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    tags: Optional[List[str]] = None
    search: Optional[str] = None


# ============== TEMPLATE SCHEMAS ==============

class TemplateParameter(BaseSchema):
    """Schema de parâmetro de template."""
    name: str
    label: str
    type: str  # string, number, date, boolean, select, multi_select
    required: bool = False
    default_value: Optional[Any] = None
    options: Optional[List[Dict[str, Any]]] = None
    validation: Optional[Dict[str, Any]] = None
    description: Optional[str] = None


class TemplateSectionConfig(BaseSchema):
    """Schema de configuração de seção."""
    code: str
    name: str
    section_type: SectionTypeEnum
    layout: SectionLayoutEnum = SectionLayoutEnum.FULL_WIDTH
    order: int = 0
    data_source: Optional[str] = None
    query: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    title: Optional[str] = None
    content_template: Optional[str] = None
    chart_config: Optional[Dict[str, Any]] = None
    table_config: Optional[Dict[str, Any]] = None
    styles: Optional[Dict[str, Any]] = None
    is_visible: bool = True


class ReportTemplateCreate(BaseSchema):
    """Schema para criar template."""
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    category: TemplateCategoryEnum = TemplateCategoryEnum.GENERAL
    subcategory: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = Field(default_factory=list)
    data_sources: List[str] = Field(default_factory=list)
    primary_source: Optional[str] = None
    queries: Optional[Dict[str, str]] = Field(default_factory=dict)
    parameters: Optional[List[TemplateParameter]] = Field(default_factory=list)
    required_parameters: Optional[List[str]] = Field(default_factory=list)
    default_values: Optional[Dict[str, Any]] = Field(default_factory=dict)
    default_filters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    sections_config: Optional[List[TemplateSectionConfig]] = Field(default_factory=list)
    widgets_config: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    metrics_config: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    ai_insights_enabled: bool = True
    anomaly_detection_enabled: bool = True
    trend_analysis_enabled: bool = True
    recommendations_enabled: bool = True
    supported_formats: List[str] = Field(default=["pdf", "excel", "csv"])
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
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[TemplateCategoryEnum] = None
    subcategory: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    status: Optional[TemplateStatusEnum] = None
    data_sources: Optional[List[str]] = None
    primary_source: Optional[str] = None
    parameters: Optional[List[TemplateParameter]] = None
    sections_config: Optional[List[TemplateSectionConfig]] = None
    widgets_config: Optional[List[Dict[str, Any]]] = None
    ai_insights_enabled: Optional[bool] = None
    supported_formats: Optional[List[str]] = None
    is_public: Optional[bool] = None


class ReportTemplateResponse(BaseSchema):
    """Schema de resposta de template."""
    id: UUID
    code: str
    name: str
    description: Optional[str]
    category: TemplateCategoryEnum
    subcategory: Optional[str]
    tags: List[str]
    status: TemplateStatusEnum
    data_sources: List[str]
    primary_source: Optional[str]
    parameters: List[Dict[str, Any]]
    required_parameters: List[str]
    default_values: Dict[str, Any]
    sections_config: List[Dict[str, Any]]
    widgets_config: List[Dict[str, Any]]
    metrics_config: List[Dict[str, Any]]
    ai_insights_enabled: bool
    anomaly_detection_enabled: bool
    trend_analysis_enabled: bool
    recommendations_enabled: bool
    supported_formats: List[str]
    default_format: str
    is_public: bool
    is_system: bool
    is_ready: bool
    usage_count: int
    last_used_at: Optional[datetime]
    average_generation_time_ms: int
    version: int
    created_by: Optional[UUID]
    organization_id: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime]


class ReportTemplateListResponse(BaseSchema):
    """Schema de lista de templates."""
    items: List[ReportTemplateResponse]
    total: int
    page: int
    size: int
    pages: int


# ============== SCHEDULE SCHEMAS ==============

class ReportScheduleCreate(BaseSchema):
    """Schema para criar agendamento."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    template_id: UUID
    frequency: ScheduleFrequencyEnum = ScheduleFrequencyEnum.DAILY
    cron_expression: Optional[str] = None
    run_time: Optional[time] = None
    timezone: str = "America/Sao_Paulo"
    days_of_week: Optional[List[int]] = None
    days_of_month: Optional[List[int]] = None
    period_type: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    output_formats: List[str] = Field(default=["pdf"])
    delivery_methods: List[str] = Field(default=["email"])
    email_recipients: Optional[List[str]] = Field(default_factory=list)
    email_subject: Optional[str] = None
    email_body: Optional[str] = None
    webhook_url: Optional[str] = None
    slack_channel: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_runs: Optional[int] = None
    notify_on_failure: bool = True


class ReportScheduleUpdate(BaseSchema):
    """Schema para atualizar agendamento."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[ScheduleStatusEnum] = None
    frequency: Optional[ScheduleFrequencyEnum] = None
    run_time: Optional[time] = None
    parameters: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    output_formats: Optional[List[str]] = None
    email_recipients: Optional[List[str]] = None
    email_subject: Optional[str] = None
    end_date: Optional[datetime] = None


class ReportScheduleResponse(BaseSchema):
    """Schema de resposta de agendamento."""
    id: UUID
    name: str
    description: Optional[str]
    template_id: UUID
    status: ScheduleStatusEnum
    frequency: ScheduleFrequencyEnum
    cron_expression: Optional[str]
    run_time: Optional[time]
    timezone: str
    days_of_week: List[int]
    days_of_month: List[int]
    period_type: Optional[str]
    parameters: Dict[str, Any]
    filters: Dict[str, Any]
    output_formats: List[str]
    delivery_methods: List[str]
    email_recipients: List[str]
    next_run_at: Optional[datetime]
    last_run_at: Optional[datetime]
    last_success_at: Optional[datetime]
    last_failure_at: Optional[datetime]
    total_runs: int
    successful_runs: int
    failed_runs: int
    success_rate: float
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_by: Optional[UUID]
    organization_id: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime]


class ReportScheduleListResponse(BaseSchema):
    """Schema de lista de agendamentos."""
    items: List[ReportScheduleResponse]
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
    report_id: Optional[UUID]
    template_id: Optional[UUID]
    schedule_id: Optional[UUID]
    status: ExecutionStatusEnum
    progress: float
    current_step: Optional[str]
    trigger: ExecutionTriggerEnum
    triggered_by: Optional[UUID]
    parameters: Dict[str, Any]
    period_start: Optional[datetime]
    period_end: Optional[datetime]
    requested_formats: List[str]
    generated_formats: List[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    failed_at: Optional[datetime]
    metrics: Optional[ExecutionMetrics]
    output_files: List[Dict[str, Any]]
    delivery_status: Dict[str, Any]
    error_message: Optional[str]
    error_code: Optional[str]
    retry_count: int
    can_retry: bool
    created_at: datetime


class ReportExecutionListResponse(BaseSchema):
    """Schema de lista de execuções."""
    items: List[ReportExecutionResponse]
    total: int
    page: int
    size: int
    pages: int


# ============== SECTION SCHEMAS ==============

class ReportSectionCreate(BaseSchema):
    """Schema para criar seção."""
    code: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    section_type: SectionTypeEnum
    layout: SectionLayoutEnum = SectionLayoutEnum.FULL_WIDTH
    order: int = 0
    data_source: Optional[str] = None
    query: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    title: Optional[str] = None
    content: Optional[str] = None
    chart_type: Optional[str] = None
    chart_config: Optional[Dict[str, Any]] = None
    table_columns: Optional[List[Dict[str, Any]]] = None
    table_config: Optional[Dict[str, Any]] = None
    styles: Optional[Dict[str, Any]] = None
    is_visible: bool = True


class ReportSectionUpdate(BaseSchema):
    """Schema para atualizar seção."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    section_type: Optional[SectionTypeEnum] = None
    layout: Optional[SectionLayoutEnum] = None
    order: Optional[int] = None
    data_source: Optional[str] = None
    query: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    styles: Optional[Dict[str, Any]] = None
    is_visible: Optional[bool] = None


class ReportSectionResponse(BaseSchema):
    """Schema de resposta de seção."""
    id: UUID
    code: str
    name: str
    description: Optional[str]
    section_type: SectionTypeEnum
    layout: SectionLayoutEnum
    order: int
    level: int
    title: Optional[str]
    subtitle: Optional[str]
    content: Optional[str]
    data: Dict[str, Any]
    chart_type: Optional[str]
    chart_data: Dict[str, Any]
    table_columns: List[Dict[str, Any]]
    table_data: List[Dict[str, Any]]
    metric_value: Optional[str]
    metric_label: Optional[str]
    metric_trend: Optional[str]
    metric_change: Optional[float]
    is_visible: bool
    has_data: bool
    created_at: datetime


# ============== WIDGET SCHEMAS ==============

class ReportWidgetCreate(BaseSchema):
    """Schema para criar widget."""
    code: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    widget_type: WidgetTypeEnum
    size: WidgetSizeEnum = WidgetSizeEnum.MEDIUM
    data_source: Optional[str] = None
    query: Optional[str] = None
    data_mapping: Optional[Dict[str, str]] = None
    title: Optional[str] = None
    colors: Optional[List[str]] = None
    x_axis_config: Optional[Dict[str, Any]] = None
    y_axis_config: Optional[Dict[str, Any]] = None
    show_legend: bool = True
    show_values: bool = True
    thresholds: Optional[List[Dict[str, Any]]] = None
    styles: Optional[Dict[str, Any]] = None
    is_interactive: bool = True


class ReportWidgetUpdate(BaseSchema):
    """Schema para atualizar widget."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    widget_type: Optional[WidgetTypeEnum] = None
    size: Optional[WidgetSizeEnum] = None
    data_source: Optional[str] = None
    title: Optional[str] = None
    colors: Optional[List[str]] = None
    show_legend: Optional[bool] = None
    styles: Optional[Dict[str, Any]] = None
    is_visible: Optional[bool] = None


class ReportWidgetResponse(BaseSchema):
    """Schema de resposta de widget."""
    id: UUID
    code: str
    name: str
    description: Optional[str]
    widget_type: WidgetTypeEnum
    size: WidgetSizeEnum
    title: Optional[str]
    data_source: Optional[str]
    data: Dict[str, Any]
    data_mapping: Dict[str, str]
    colors: List[str]
    show_legend: bool
    show_values: bool
    thresholds: List[Dict[str, Any]]
    kpi_value: Optional[str]
    kpi_label: Optional[str]
    kpi_unit: Optional[str]
    kpi_trend: Optional[str]
    kpi_change: Optional[float]
    kpi_status: Optional[str]
    has_data: bool
    is_visible: bool
    is_reusable: bool
    created_at: datetime


# ============== GENERATION SCHEMAS ==============

class GenerateReportRequest(BaseSchema):
    """Schema para solicitar geração de relatório."""
    template_id: Optional[UUID] = None
    template_code: Optional[str] = None
    name: Optional[str] = None
    report_type: Optional[ReportTypeEnum] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    period_type: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    output_formats: List[str] = Field(default=["pdf"])
    include_insights: bool = True
    include_recommendations: bool = True
    include_anomalies: bool = True
    priority: ReportPriorityEnum = ReportPriorityEnum.NORMAL
    async_generation: bool = False
    notify_on_completion: bool = False
    recipients: Optional[List[str]] = None


class GenerateReportResponse(BaseSchema):
    """Schema de resposta de geração."""
    report_id: UUID
    execution_id: UUID
    status: ExecutionStatusEnum
    message: str
    estimated_time_seconds: Optional[int]
    progress_url: Optional[str]


# ============== EXPORT SCHEMAS ==============

class ExportReportRequest(BaseSchema):
    """Schema para exportar relatório."""
    report_id: UUID
    format: ReportFormatEnum
    include_charts: bool = True
    include_data: bool = True
    page_size: Optional[str] = "A4"
    orientation: Optional[str] = "portrait"
    include_header: bool = True
    include_footer: bool = True
    password: Optional[str] = None


class ExportReportResponse(BaseSchema):
    """Schema de resposta de exportação."""
    report_id: UUID
    format: ReportFormatEnum
    file_path: str
    file_url: Optional[str]
    file_size_bytes: int
    generated_at: datetime
    expires_at: Optional[datetime]


# ============== DASHBOARD SCHEMAS ==============

class ReportDashboardResponse(BaseSchema):
    """Schema de dashboard de relatórios."""
    total_reports: int
    reports_by_status: Dict[str, int]
    reports_by_type: Dict[str, int]
    reports_this_month: int
    reports_trend: List[Dict[str, Any]]
    average_generation_time_ms: int
    total_insights_generated: int
    total_anomalies_detected: int
    most_used_templates: List[Dict[str, Any]]
    recent_reports: List[ReportSummary]
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
    most_common_types: List[Dict[str, int]]
    most_common_formats: List[Dict[str, int]]
    busiest_hours: List[Dict[str, int]]
