"""Schemas Pydantic para DashboardWidget."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from modules.hr.analytics_dashboard.models import (
    AggregationType,
    DataSource,
    WidgetType,
)


class WidgetPosition(BaseModel):
    """Schema para posição do widget no grid."""

    x: int = Field(default=0, ge=0)
    y: int = Field(default=0, ge=0)
    w: int = Field(default=4, ge=1, le=12, alias="width")
    h: int = Field(default=3, ge=1, le=12, alias="height")


class WidgetThreshold(BaseModel):
    """Schema para thresholds do widget."""

    critical: float | None = None
    warning: float | None = None
    good: float | None = None
    excellent: float | None = None


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
    subtitle: str | None = Field(None, max_length=200)
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
    group_by: str | None = None
    order_by: str | None = None
    limit: int | None = Field(None, ge=1, le=1000)

    # Query customizada
    custom_query: str | None = None
    query_params: dict | None = None

    # Filtros
    filters: dict | None = None
    date_range: dict | None = None
    inherit_dashboard_filters: bool = True

    # Configuração visual
    chart_config: dict | None = None
    colors: list[str] | None = None

    # KPI específico
    kpi_metric: str | None = None
    kpi_target: float | None = None
    kpi_unit: str | None = None
    kpi_format: str | None = None
    show_comparison: bool = True
    comparison_period: str | None = None

    # Thresholds
    thresholds: dict | None = None
    alert_enabled: bool = False
    alert_conditions: dict | None = None

    # Atualização
    refresh_interval: str | None = None
    cache_duration_seconds: int = Field(default=300, ge=0, le=86400)

    # Interatividade
    is_interactive: bool = True
    click_action: str | None = None
    drill_down_config: dict | None = None

    settings: dict | None = None


class DashboardWidgetUpdate(BaseModel):
    """Schema para atualização de widget."""

    title: str | None = Field(None, min_length=1, max_length=100)
    subtitle: str | None = Field(None, max_length=200)
    widget_type: WidgetType | None = None

    grid_x: int | None = Field(None, ge=0)
    grid_y: int | None = Field(None, ge=0)
    grid_width: int | None = Field(None, ge=1, le=12)
    grid_height: int | None = Field(None, ge=1, le=12)

    data_source: DataSource | None = None
    aggregation: AggregationType | None = None
    group_by: str | None = None
    order_by: str | None = None
    limit: int | None = Field(None, ge=1, le=1000)

    filters: dict | None = None
    date_range: dict | None = None

    chart_config: dict | None = None
    colors: list[str] | None = None

    kpi_metric: str | None = None
    kpi_target: float | None = None
    show_comparison: bool | None = None

    thresholds: dict | None = None
    alert_enabled: bool | None = None

    is_visible: bool | None = None
    is_collapsed: bool | None = None

    settings: dict | None = None


class WidgetPositionUpdate(BaseModel):
    """Schema para atualização de posição."""

    widget_id: UUID
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    width: int = Field(ge=1, le=12)
    height: int = Field(ge=1, le=12)


class WidgetBatchPositionUpdate(BaseModel):
    """Schema para atualização em lote de posições."""

    positions: list[WidgetPositionUpdate]


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
    group_by: str | None = None

    filters: dict | None = None
    date_range: dict | None = None
    inherit_dashboard_filters: bool

    chart_config: dict | None = None
    colors: list[str] | None = None

    kpi_metric: str | None = None
    kpi_target: float | None = None
    kpi_unit: str | None = None
    show_comparison: bool

    thresholds: dict | None = None
    alert_enabled: bool

    cache_duration_seconds: int
    last_refreshed_at: datetime | None = None

    is_visible: bool
    is_collapsed: bool
    is_interactive: bool

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WidgetDataRequest(BaseModel):
    """Schema para requisição de dados do widget."""

    widget_id: UUID
    filters: dict | None = None
    date_range: dict | None = None
    force_refresh: bool = False


class WidgetDataResponse(BaseModel):
    """Schema para resposta de dados do widget."""

    widget_id: UUID
    data: Any
    metadata: dict | None = None
    computed_at: datetime
    from_cache: bool
    cache_expires_at: datetime | None = None


class WidgetPreviewRequest(BaseModel):
    """Schema para preview de widget."""

    widget_type: WidgetType
    data_source: DataSource
    aggregation: AggregationType = AggregationType.COUNT
    group_by: str | None = None
    filters: dict | None = None
    date_range: dict | None = None
    limit: int = Field(default=10, ge=1, le=100)
