"""Schemas Pydantic para KPIDefinition."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from modules.hr.analytics_dashboard.models import (
    KPICategory,
    KPIDirection,
    KPIFrequency,
    KPIUnit,
)


class KPIDefinitionBase(BaseModel):
    """Schema base para KPI."""

    code: str = Field(..., min_length=1, max_length=50, pattern="^[A-Z_]+$")
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    category: KPICategory = KPICategory.ATTENDANCE


class KPIDefinitionCreate(KPIDefinitionBase):
    """Schema para criação de KPI."""

    # Unidade e formato
    unit: KPIUnit = KPIUnit.PERCENTAGE
    decimal_places: int = Field(default=2, ge=0, le=6)
    format_pattern: str | None = None
    prefix: str | None = Field(None, max_length=10)
    suffix: str | None = Field(None, max_length=10)

    # Direção e metas
    direction: KPIDirection = KPIDirection.UP
    target_value: float | None = None
    min_value: float | None = None
    max_value: float | None = None

    # Thresholds
    threshold_critical: float | None = None
    threshold_warning: float | None = None
    threshold_good: float | None = None
    threshold_excellent: float | None = None

    # Cálculo
    calculation_formula: str | None = None
    calculation_query: str | None = None
    calculation_params: dict | None = None
    frequency: KPIFrequency = KPIFrequency.DAILY

    # Comparações
    enable_comparison: bool = True
    comparison_periods: list[str] | None = None

    # Benchmark
    industry_benchmark: float | None = None
    benchmark_source: str | None = None

    # Alertas
    alert_enabled: bool = False
    alert_recipients: list[str] | None = None
    alert_conditions: dict | None = None

    # Visualização
    default_chart_type: str = "line_chart"
    color_scheme: dict | None = None
    icon: str | None = None

    # Drill-down
    drill_down_enabled: bool = True
    drill_down_dimensions: list[str] | None = None

    tags: list[str] | None = None
    settings: dict | None = None

    is_featured: bool = False

    @field_validator("code")
    @classmethod
    def uppercase_code(cls, v):
        """Garante código em maiúsculas."""
        return v.upper() if v else v


class KPIDefinitionUpdate(BaseModel):
    """Schema para atualização de KPI."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    category: KPICategory | None = None

    unit: KPIUnit | None = None
    decimal_places: int | None = Field(None, ge=0, le=6)
    prefix: str | None = Field(None, max_length=10)
    suffix: str | None = Field(None, max_length=10)

    direction: KPIDirection | None = None
    target_value: float | None = None

    threshold_critical: float | None = None
    threshold_warning: float | None = None
    threshold_good: float | None = None
    threshold_excellent: float | None = None

    frequency: KPIFrequency | None = None

    industry_benchmark: float | None = None

    alert_enabled: bool | None = None
    alert_recipients: list[str] | None = None

    default_chart_type: str | None = None
    icon: str | None = None

    is_featured: bool | None = None
    tags: list[str] | None = None
    settings: dict | None = None


class KPIDefinitionResponse(KPIDefinitionBase):
    """Schema de resposta de KPI."""

    id: UUID
    condominio_id: UUID | None = None

    unit: str
    decimal_places: int
    prefix: str | None = None
    suffix: str | None = None

    direction: str
    target_value: float | None = None

    threshold_critical: float | None = None
    threshold_warning: float | None = None
    threshold_good: float | None = None
    threshold_excellent: float | None = None

    frequency: str
    enable_comparison: bool

    industry_benchmark: float | None = None

    default_chart_type: str
    icon: str | None = None

    drill_down_enabled: bool

    is_featured: bool
    is_system: bool
    sort_order: int

    tags: list[str] | None = None

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KPIValueRequest(BaseModel):
    """Schema para requisição de valor de KPI."""

    kpi_code: str
    condominio_id: UUID
    period_start: datetime | None = None
    period_end: datetime | None = None
    filters: dict | None = None
    include_comparison: bool = True
    include_trend: bool = True


class KPITrend(BaseModel):
    """Schema para tendência de KPI."""

    direction: str  # up, down, neutral
    percentage: float
    is_positive: bool


class KPIComparison(BaseModel):
    """Schema para comparação de KPI."""

    period: str
    value: float
    trend: KPITrend


class KPIValueResponse(BaseModel):
    """Schema de resposta de valor de KPI."""

    kpi_code: str
    kpi_name: str
    category: str
    unit: str

    current_value: float
    formatted_value: str
    status: str  # excellent, good, warning, critical, neutral

    target_value: float | None = None
    target_percentage: float | None = None

    trend: KPITrend | None = None
    comparisons: list[KPIComparison] | None = None

    period_start: datetime
    period_end: datetime

    computed_at: datetime
    from_cache: bool


class KPIDashboardResponse(BaseModel):
    """Schema para dashboard de KPIs."""

    kpis: list[KPIValueResponse]
    period_start: datetime
    period_end: datetime
    condominio_id: UUID
    computed_at: datetime


class KPIHistoryRequest(BaseModel):
    """Schema para requisição de histórico de KPI."""

    kpi_code: str
    condominio_id: UUID
    granularity: str = Field(default="daily", pattern="^(hourly|daily|weekly|monthly)$")
    period_start: datetime
    period_end: datetime
    filters: dict | None = None


class KPIHistoryPoint(BaseModel):
    """Schema para ponto no histórico."""

    timestamp: datetime
    value: float
    status: str


class KPIHistoryResponse(BaseModel):
    """Schema de resposta de histórico de KPI."""

    kpi_code: str
    kpi_name: str
    granularity: str
    data_points: list[KPIHistoryPoint]
    statistics: dict  # min, max, avg, trend


class KPIAlertConfig(BaseModel):
    """Schema para configuração de alerta de KPI."""

    kpi_code: str
    enabled: bool = True
    condition: str = Field(..., pattern="^(above|below|equals|change)$")
    threshold: float
    comparison_value: float | None = None  # Para condition=change (%)
    recipients: list[str]
    channels: list[str] = ["email"]  # email, push, webhook
    cooldown_minutes: int = Field(default=60, ge=5, le=1440)
