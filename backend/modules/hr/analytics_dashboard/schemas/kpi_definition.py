"""Schemas Pydantic para KPIDefinition."""

from datetime import datetime
from typing import Optional, List, Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from modules.hr.analytics_dashboard.models import (
    KPICategory,
    KPIUnit,
    KPIDirection,
    KPIFrequency,
)


class KPIDefinitionBase(BaseModel):
    """Schema base para KPI."""

    code: str = Field(..., min_length=1, max_length=50, pattern="^[A-Z_]+$")
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category: KPICategory = KPICategory.ATTENDANCE


class KPIDefinitionCreate(KPIDefinitionBase):
    """Schema para criação de KPI."""

    # Unidade e formato
    unit: KPIUnit = KPIUnit.PERCENTAGE
    decimal_places: int = Field(default=2, ge=0, le=6)
    format_pattern: Optional[str] = None
    prefix: Optional[str] = Field(None, max_length=10)
    suffix: Optional[str] = Field(None, max_length=10)

    # Direção e metas
    direction: KPIDirection = KPIDirection.UP
    target_value: Optional[float] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None

    # Thresholds
    threshold_critical: Optional[float] = None
    threshold_warning: Optional[float] = None
    threshold_good: Optional[float] = None
    threshold_excellent: Optional[float] = None

    # Cálculo
    calculation_formula: Optional[str] = None
    calculation_query: Optional[str] = None
    calculation_params: Optional[dict] = None
    frequency: KPIFrequency = KPIFrequency.DAILY

    # Comparações
    enable_comparison: bool = True
    comparison_periods: Optional[List[str]] = None

    # Benchmark
    industry_benchmark: Optional[float] = None
    benchmark_source: Optional[str] = None

    # Alertas
    alert_enabled: bool = False
    alert_recipients: Optional[List[str]] = None
    alert_conditions: Optional[dict] = None

    # Visualização
    default_chart_type: str = "line_chart"
    color_scheme: Optional[dict] = None
    icon: Optional[str] = None

    # Drill-down
    drill_down_enabled: bool = True
    drill_down_dimensions: Optional[List[str]] = None

    tags: Optional[List[str]] = None
    settings: Optional[dict] = None

    is_featured: bool = False

    @field_validator("code")
    @classmethod
    def uppercase_code(cls, v):
        """Garante código em maiúsculas."""
        return v.upper() if v else v


class KPIDefinitionUpdate(BaseModel):
    """Schema para atualização de KPI."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category: Optional[KPICategory] = None

    unit: Optional[KPIUnit] = None
    decimal_places: Optional[int] = Field(None, ge=0, le=6)
    prefix: Optional[str] = Field(None, max_length=10)
    suffix: Optional[str] = Field(None, max_length=10)

    direction: Optional[KPIDirection] = None
    target_value: Optional[float] = None

    threshold_critical: Optional[float] = None
    threshold_warning: Optional[float] = None
    threshold_good: Optional[float] = None
    threshold_excellent: Optional[float] = None

    frequency: Optional[KPIFrequency] = None

    industry_benchmark: Optional[float] = None

    alert_enabled: Optional[bool] = None
    alert_recipients: Optional[List[str]] = None

    default_chart_type: Optional[str] = None
    icon: Optional[str] = None

    is_featured: Optional[bool] = None
    tags: Optional[List[str]] = None
    settings: Optional[dict] = None


class KPIDefinitionResponse(KPIDefinitionBase):
    """Schema de resposta de KPI."""

    id: UUID
    condominio_id: Optional[UUID] = None

    unit: str
    decimal_places: int
    prefix: Optional[str] = None
    suffix: Optional[str] = None

    direction: str
    target_value: Optional[float] = None

    threshold_critical: Optional[float] = None
    threshold_warning: Optional[float] = None
    threshold_good: Optional[float] = None
    threshold_excellent: Optional[float] = None

    frequency: str
    enable_comparison: bool

    industry_benchmark: Optional[float] = None

    default_chart_type: str
    icon: Optional[str] = None

    drill_down_enabled: bool

    is_featured: bool
    is_system: bool
    sort_order: int

    tags: Optional[List[str]] = None

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KPIValueRequest(BaseModel):
    """Schema para requisição de valor de KPI."""

    kpi_code: str
    condominio_id: UUID
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    filters: Optional[dict] = None
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

    target_value: Optional[float] = None
    target_percentage: Optional[float] = None

    trend: Optional[KPITrend] = None
    comparisons: Optional[List[KPIComparison]] = None

    period_start: datetime
    period_end: datetime

    computed_at: datetime
    from_cache: bool


class KPIDashboardResponse(BaseModel):
    """Schema para dashboard de KPIs."""

    kpis: List[KPIValueResponse]
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
    filters: Optional[dict] = None


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
    data_points: List[KPIHistoryPoint]
    statistics: dict  # min, max, avg, trend


class KPIAlertConfig(BaseModel):
    """Schema para configuração de alerta de KPI."""

    kpi_code: str
    enabled: bool = True
    condition: str = Field(..., pattern="^(above|below|equals|change)$")
    threshold: float
    comparison_value: Optional[float] = None  # Para condition=change (%)
    recipients: List[str]
    channels: List[str] = ["email"]  # email, push, webhook
    cooldown_minutes: int = Field(default=60, ge=5, le=1440)
