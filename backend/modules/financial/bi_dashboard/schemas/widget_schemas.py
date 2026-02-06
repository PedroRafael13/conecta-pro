"""Schemas de Widget de Dashboard Financeiro."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from modules.financial.bi_dashboard.models.dashboard_widget import (
    WidgetType,
    WidgetSize,
    ChartType,
    DataSource,
)


class WidgetBase(BaseModel):
    """Schema base de Widget."""

    titulo: str = Field(..., min_length=1, max_length=200)
    subtitulo: Optional[str] = Field(None, max_length=500)
    descricao: Optional[str] = Field(None, max_length=2000)
    tipo: WidgetType = Field(default=WidgetType.KPI_CARD)
    tamanho: WidgetSize = Field(default=WidgetSize.MEDIUM)
    chart_type: Optional[ChartType] = None
    data_source: DataSource = Field(default=DataSource.CASH_FLOW)


class WidgetPosition(BaseModel):
    """Posicao do widget no grid."""

    x: int = Field(default=0, ge=0)
    y: int = Field(default=0, ge=0)
    w: int = Field(default=1, ge=1, le=12)
    h: int = Field(default=1, ge=1, le=8)


class WidgetDataConfig(BaseModel):
    """Configuracao de dados do widget."""

    metric_field: Optional[str] = Field(None, max_length=100)
    dimension_field: Optional[str] = Field(None, max_length=100)
    time_field: str = Field(default="created_at", max_length=100)
    aggregation: str = Field(default="sum", max_length=50)
    group_by: list = Field(default_factory=list)
    sort_by: Optional[str] = Field(None, max_length=100)
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
    limit: int = Field(default=10, ge=1, le=1000)
    filters: dict = Field(default_factory=dict)
    date_range_days: int = Field(default=30, ge=1, le=365)


class WidgetStyleConfig(BaseModel):
    """Configuracao de estilo do widget."""

    colors: list = Field(default_factory=list)
    background_color: Optional[str] = Field(None, max_length=20)
    border_color: Optional[str] = Field(None, max_length=20)
    text_color: Optional[str] = Field(None, max_length=20)
    icon: Optional[str] = Field(None, max_length=100)
    value_format: str = Field(default="currency", max_length=50)
    decimal_places: int = Field(default=2, ge=0, le=8)
    show_percentage: bool = Field(default=False)
    show_trend: bool = Field(default=True)
    show_comparison: bool = Field(default=False)
    show_legend: bool = Field(default=True)


class WidgetThresholds(BaseModel):
    """Thresholds do widget para alertas."""

    warning: Optional[Decimal] = None
    critical: Optional[Decimal] = None
    success: Optional[Decimal] = None
    invert_colors: bool = Field(default=False)


class WidgetCreate(WidgetBase):
    """Schema para criar Widget."""

    codigo: str = Field(..., min_length=1, max_length=50)
    dashboard_id: UUID
    position: WidgetPosition = Field(default_factory=WidgetPosition)
    data_config: WidgetDataConfig = Field(default_factory=WidgetDataConfig)
    style_config: WidgetStyleConfig = Field(default_factory=WidgetStyleConfig)
    thresholds: WidgetThresholds = Field(default_factory=WidgetThresholds)
    custom_query: Optional[str] = None
    query_params: dict = Field(default_factory=dict)
    comparison_enabled: bool = Field(default=False)
    comparison_period: Optional[str] = None
    is_clickable: bool = Field(default=True)
    click_action: Optional[str] = None
    drill_down_enabled: bool = Field(default=False)
    drill_down_config: dict = Field(default_factory=dict)
    cache_ttl_seconds: int = Field(default=300, ge=0, le=86400)


class WidgetUpdate(BaseModel):
    """Schema para atualizar Widget."""

    titulo: Optional[str] = Field(None, min_length=1, max_length=200)
    subtitulo: Optional[str] = Field(None, max_length=500)
    descricao: Optional[str] = Field(None, max_length=2000)
    tipo: Optional[WidgetType] = None
    tamanho: Optional[WidgetSize] = None
    chart_type: Optional[ChartType] = None
    data_source: Optional[DataSource] = None
    position: Optional[WidgetPosition] = None
    data_config: Optional[WidgetDataConfig] = None
    style_config: Optional[WidgetStyleConfig] = None
    thresholds: Optional[WidgetThresholds] = None
    custom_query: Optional[str] = None
    query_params: Optional[dict] = None
    comparison_enabled: Optional[bool] = None
    comparison_period: Optional[str] = None
    is_visible: Optional[bool] = None
    is_clickable: Optional[bool] = None
    click_action: Optional[str] = None
    drill_down_enabled: Optional[bool] = None
    drill_down_config: Optional[dict] = None
    cache_ttl_seconds: Optional[int] = Field(None, ge=0, le=86400)


class WidgetResponse(WidgetBase):
    """Schema de resposta de Widget."""

    id: UUID
    dashboard_id: UUID
    condominio_id: UUID
    codigo: str
    position_x: int
    position_y: int
    width: int
    height: int
    order: int
    custom_query: Optional[str] = None
    query_params: dict = Field(default_factory=dict)
    metric_field: Optional[str] = None
    dimension_field: Optional[str] = None
    time_field: str = "created_at"
    aggregation: str = "sum"
    group_by: list = Field(default_factory=list)
    filters: dict = Field(default_factory=dict)
    date_range_days: int = 30
    comparison_enabled: bool = False
    comparison_period: Optional[str] = None
    value_format: str = "currency"
    decimal_places: int = 2
    show_percentage: bool = False
    show_trend: bool = True
    show_legend: bool = True
    colors: list = Field(default_factory=list)
    icon: Optional[str] = None
    threshold_warning: Optional[Decimal] = None
    threshold_critical: Optional[Decimal] = None
    threshold_success: Optional[Decimal] = None
    is_visible: bool = True
    is_clickable: bool = True
    drill_down_enabled: bool = False
    is_loading: bool = False
    last_error: Optional[str] = None
    last_updated_at: Optional[datetime] = None
    cache_ttl_seconds: int = 300
    is_chart: bool = False
    is_kpi: bool = True
    needs_refresh: bool = False
    grid_position: dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class WidgetData(BaseModel):
    """Dados carregados do widget."""

    widget_id: UUID
    data: Any
    value: Optional[Decimal] = None
    previous_value: Optional[Decimal] = None
    change_percent: Optional[Decimal] = None
    trend: Optional[str] = None
    labels: list = Field(default_factory=list)
    series: list = Field(default_factory=list)
    table_data: list = Field(default_factory=list)
    total_rows: int = 0
    color: Optional[str] = None
    alert_level: Optional[str] = None
    loaded_at: datetime
    cached: bool = False
    ttl_remaining: int = 0


class WidgetFilters(BaseModel):
    """Filtros para busca de Widgets."""

    dashboard_id: Optional[UUID] = None
    tipo: Optional[WidgetType] = None
    data_source: Optional[DataSource] = None
    is_visible: Optional[bool] = None
    search: Optional[str] = Field(None, max_length=200)


class WidgetBulkUpdate(BaseModel):
    """Atualizacao em lote de widgets."""

    widgets: list[dict] = Field(..., min_length=1)


class WidgetClone(BaseModel):
    """Schema para clonar widget."""

    target_dashboard_id: UUID
    new_codigo: Optional[str] = Field(None, max_length=50)
    new_titulo: Optional[str] = Field(None, max_length=200)
