"""Schemas Pydantic para DashboardWidget."""

from datetime import datetime
from typing import Optional, List, Any
from uuid import UUID

from pydantic import BaseModel, Field

from modules.hr.analytics_dashboard.models import (
    WidgetType,
    DataSource,
    AggregationType,
)


class WidgetPosition(BaseModel):
    """Schema para posição do widget no grid."""

    x: int = Field(default=0, ge=0)
    y: int = Field(default=0, ge=0)
    w: int = Field(default=4, ge=1, le=12, alias="width")
    h: int = Field(default=3, ge=1, le=12, alias="height")


class WidgetThreshold(BaseModel):
    """Schema para thresholds do widget."""

    critical: Optional[float] = None
    warning: Optional[float] = None
    good: Optional[float] = None
    excellent: Optional[float] = None


class WidgetChartConfig(BaseModel):
    """Schema para configuração de gráfico."""

    show_legend: bool = True
    show_labels: bool = True
    show_grid: bool = True
    show_tooltip: bool = True
    animation: bool = True
    stacked: bool = False
    curved: bool = False
    fill: bool = False


class DashboardWidgetBase(BaseModel):
    """Schema base para widget."""

    title: str = Field(..., min_length=1, max_length=100)
    subtitle: Optional[str] = Field(None, max_length=200)
    widget_type: WidgetType


class DashboardWidgetCreate(DashboardWidgetBase):
    """Schema para criação de widget."""

    # Posição
    grid_x: int = Field(default=0, ge=0)
    grid_y: int = Field(default=0, ge=0)
    grid_width: int = Field(default=4, ge=1, le=12)
    grid_height: int = Field(default=3, ge=1, le=12)

    # Fonte de dados
    data_source: DataSource = DataSource.TIME_ENTRIES
    aggregation: AggregationType = AggregationType.COUNT
    group_by: Optional[str] = None
    order_by: Optional[str] = None
    limit: Optional[int] = Field(None, ge=1, le=1000)

    # Query customizada
    custom_query: Optional[str] = None
    query_params: Optional[dict] = None

    # Filtros
    filters: Optional[dict] = None
    date_range: Optional[dict] = None
    inherit_dashboard_filters: bool = True

    # Configuração visual
    chart_config: Optional[dict] = None
    colors: Optional[List[str]] = None

    # KPI específico
    kpi_metric: Optional[str] = None
    kpi_target: Optional[float] = None
    kpi_unit: Optional[str] = None
    kpi_format: Optional[str] = None
    show_comparison: bool = True
    comparison_period: Optional[str] = None

    # Thresholds
    thresholds: Optional[dict] = None
    alert_enabled: bool = False
    alert_conditions: Optional[dict] = None

    # Atualização
    refresh_interval: Optional[str] = None
    cache_duration_seconds: int = Field(default=300, ge=0, le=86400)

    # Interatividade
    is_interactive: bool = True
    click_action: Optional[str] = None
    drill_down_config: Optional[dict] = None

    settings: Optional[dict] = None


class DashboardWidgetUpdate(BaseModel):
    """Schema para atualização de widget."""

    title: Optional[str] = Field(None, min_length=1, max_length=100)
    subtitle: Optional[str] = Field(None, max_length=200)
    widget_type: Optional[WidgetType] = None

    grid_x: Optional[int] = Field(None, ge=0)
    grid_y: Optional[int] = Field(None, ge=0)
    grid_width: Optional[int] = Field(None, ge=1, le=12)
    grid_height: Optional[int] = Field(None, ge=1, le=12)

    data_source: Optional[DataSource] = None
    aggregation: Optional[AggregationType] = None
    group_by: Optional[str] = None
    order_by: Optional[str] = None
    limit: Optional[int] = Field(None, ge=1, le=1000)

    filters: Optional[dict] = None
    date_range: Optional[dict] = None

    chart_config: Optional[dict] = None
    colors: Optional[List[str]] = None

    kpi_metric: Optional[str] = None
    kpi_target: Optional[float] = None
    show_comparison: Optional[bool] = None

    thresholds: Optional[dict] = None
    alert_enabled: Optional[bool] = None

    is_visible: Optional[bool] = None
    is_collapsed: Optional[bool] = None

    settings: Optional[dict] = None


class WidgetPositionUpdate(BaseModel):
    """Schema para atualização de posição."""

    widget_id: UUID
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    width: int = Field(ge=1, le=12)
    height: int = Field(ge=1, le=12)


class WidgetBatchPositionUpdate(BaseModel):
    """Schema para atualização em lote de posições."""

    positions: List[WidgetPositionUpdate]


class DashboardWidgetResponse(DashboardWidgetBase):
    """Schema de resposta de widget."""

    id: UUID
    dashboard_id: UUID

    grid_x: int
    grid_y: int
    grid_width: int
    grid_height: int

    data_source: str
    aggregation: str
    group_by: Optional[str] = None

    filters: Optional[dict] = None
    date_range: Optional[dict] = None
    inherit_dashboard_filters: bool

    chart_config: Optional[dict] = None
    colors: Optional[List[str]] = None

    kpi_metric: Optional[str] = None
    kpi_target: Optional[float] = None
    kpi_unit: Optional[str] = None
    show_comparison: bool

    thresholds: Optional[dict] = None
    alert_enabled: bool

    cache_duration_seconds: int
    last_refreshed_at: Optional[datetime] = None

    is_visible: bool
    is_collapsed: bool
    is_interactive: bool

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WidgetDataRequest(BaseModel):
    """Schema para requisição de dados do widget."""

    widget_id: UUID
    filters: Optional[dict] = None
    date_range: Optional[dict] = None
    force_refresh: bool = False


class WidgetDataResponse(BaseModel):
    """Schema para resposta de dados do widget."""

    widget_id: UUID
    data: Any
    metadata: Optional[dict] = None
    computed_at: datetime
    from_cache: bool
    cache_expires_at: Optional[datetime] = None


class WidgetPreviewRequest(BaseModel):
    """Schema para preview de widget."""

    widget_type: WidgetType
    data_source: DataSource
    aggregation: AggregationType = AggregationType.COUNT
    group_by: Optional[str] = None
    filters: Optional[dict] = None
    date_range: Optional[dict] = None
    limit: int = Field(default=10, ge=1, le=100)
