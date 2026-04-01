"""Modelo DashboardWidget - Widgets individuais de dashboard."""

import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from .dashboard_config import DashboardConfig


class WidgetType(StrEnum):
    """Tipo de widget."""

    # Gráficos
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    DONUT_CHART = "donut_chart"
    AREA_CHART = "area_chart"
    STACKED_BAR = "stacked_bar"
    SCATTER_PLOT = "scatter_plot"
    HEATMAP = "heatmap"
    GAUGE = "gauge"
    SPARKLINE = "sparkline"

    # KPIs e métricas
    KPI_CARD = "kpi_card"
    STAT_CARD = "stat_card"
    PROGRESS_BAR = "progress_bar"
    TREND_INDICATOR = "trend_indicator"

    # Tabelas e listas
    DATA_TABLE = "data_table"
    RANKING_LIST = "ranking_list"
    TIMELINE = "timeline"

    # Mapas e geo
    MAP = "map"
    GEOFENCE_MAP = "geofence_map"

    # Texto e mídia
    TEXT_BLOCK = "text_block"
    MARKDOWN = "markdown"
    IMAGE = "image"
    IFRAME = "iframe"

    # Interativos
    FILTER_PANEL = "filter_panel"
    DATE_PICKER = "date_picker"
    DROPDOWN = "dropdown"


class DataSource(StrEnum):
    """Fonte de dados do widget."""

    TIME_ENTRIES = "time_entries"
    CHECKINS = "checkins"
    EMPLOYEES = "employees"
    DEPARTMENTS = "departments"
    OVERTIME = "overtime"
    ABSENCES = "absences"
    BANK_HOURS = "bank_hours"
    REP_EVENTS = "rep_events"
    GEOFENCE_LOGS = "geofence_logs"
    CUSTOM_QUERY = "custom_query"
    EXTERNAL_API = "external_api"


class AggregationType(StrEnum):
    """Tipo de agregação."""

    COUNT = "count"
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    PERCENTILE = "percentile"
    DISTINCT = "distinct"
    RATE = "rate"
    TREND = "trend"


class DashboardWidget(Base):
    """Modelo de widget de dashboard."""

    __tablename__ = "dashboard_widgets"

    # Identificação
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    dashboard_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dashboard_configs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Informações básicas
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    subtitle: Mapped[str | None] = mapped_column(String(200))
    widget_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    # Posição no grid
    grid_x: Mapped[int] = mapped_column(Integer, default=0)
    grid_y: Mapped[int] = mapped_column(Integer, default=0)
    grid_width: Mapped[int] = mapped_column(Integer, default=4)
    grid_height: Mapped[int] = mapped_column(Integer, default=3)

    # Fonte de dados
    data_source: Mapped[str] = mapped_column(
        String(30),
        default=DataSource.TIME_ENTRIES.value,
    )
    aggregation: Mapped[str] = mapped_column(
        String(20),
        default=AggregationType.COUNT.value,
    )
    group_by: Mapped[str | None] = mapped_column(String(50))
    order_by: Mapped[str | None] = mapped_column(String(50))
    limit: Mapped[int | None] = mapped_column(Integer)

    # Query customizada
    custom_query: Mapped[str | None] = mapped_column(Text)
    query_params: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    # Filtros
    filters: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    date_range: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    inherit_dashboard_filters: Mapped[bool] = mapped_column(Boolean, default=True)

    # Configuração visual
    chart_config: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    colors: Mapped[list | None] = mapped_column(JSONB, default=list)
    show_legend: Mapped[bool] = mapped_column(Boolean, default=True)
    show_labels: Mapped[bool] = mapped_column(Boolean, default=True)
    show_grid: Mapped[bool] = mapped_column(Boolean, default=True)

    # KPI específico
    kpi_metric: Mapped[str | None] = mapped_column(String(50))
    kpi_target: Mapped[float | None] = mapped_column(Integer)  # Float stored as int*100
    kpi_unit: Mapped[str | None] = mapped_column(String(20))
    kpi_format: Mapped[str | None] = mapped_column(String(30))
    show_comparison: Mapped[bool] = mapped_column(Boolean, default=True)
    comparison_period: Mapped[str | None] = mapped_column(String(30))

    # Thresholds e alertas
    thresholds: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    alert_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    alert_conditions: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    # Atualização
    refresh_interval: Mapped[str | None] = mapped_column(String(20))
    cache_duration_seconds: Mapped[int] = mapped_column(Integer, default=300)
    last_refreshed_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Interatividade
    is_interactive: Mapped[bool] = mapped_column(Boolean, default=True)
    click_action: Mapped[str | None] = mapped_column(String(30))
    drill_down_config: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    # Estado
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True)
    is_collapsed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_loading: Mapped[bool] = mapped_column(Boolean, default=False)

    # Metadados
    settings: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    # Auditoria
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relacionamentos
    dashboard: Mapped["DashboardConfig"] = relationship(
        "DashboardConfig",
        back_populates="widgets",
    )

    # Índices
    __table_args__ = (
        Index("ix_dashboard_widgets_dashboard", "dashboard_id"),
        Index("ix_dashboard_widgets_type", "widget_type"),
        Index("ix_dashboard_widgets_data_source", "data_source"),
    )

    @property
    def grid_position(self) -> dict:
        """Retorna posição no grid."""
        return {
            "x": self.grid_x,
            "y": self.grid_y,
            "w": self.grid_width,
            "h": self.grid_height,
        }

    @property
    def needs_refresh(self) -> bool:
        """Verifica se precisa atualizar cache."""
        if not self.last_refreshed_at:
            return True
        elapsed = (datetime.utcnow() - self.last_refreshed_at).total_seconds()
        return elapsed > self.cache_duration_seconds

    def update_position(self, x: int, y: int, width: int, height: int) -> None:
        """Atualiza posição no grid."""
        self.grid_x = x
        self.grid_y = y
        self.grid_width = width
        self.grid_height = height

    def mark_refreshed(self) -> None:
        """Marca como atualizado."""
        self.last_refreshed_at = datetime.utcnow()
        self.is_loading = False

    def get_threshold_status(self, value: float) -> str:
        """Retorna status baseado em thresholds."""
        if not self.thresholds:
            return "normal"

        critical = self.thresholds.get("critical")
        warning = self.thresholds.get("warning")
        good = self.thresholds.get("good")

        if critical and value >= critical:
            return "critical"
        if warning and value >= warning:
            return "warning"
        if good and value >= good:
            return "good"
        return "normal"

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "title": self.title,
            "widget_type": self.widget_type,
            "data_source": self.data_source,
            "position": self.grid_position,
            "is_visible": self.is_visible,
            "needs_refresh": self.needs_refresh,
        }
