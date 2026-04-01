"""
ReportWidget Model - Widgets/componentes visuais.

Widgets reutilizáveis para compor relatórios (gráficos, KPIs, etc.).
"""

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.database import Base


class WidgetTypeEnum(StrEnum):
    """Tipos de widget."""

    # Gráficos básicos
    BAR_CHART = "bar_chart"
    LINE_CHART = "line_chart"
    PIE_CHART = "pie_chart"
    DONUT_CHART = "donut_chart"
    AREA_CHART = "area_chart"

    # Gráficos avançados
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

    # KPIs
    KPI_CARD = "kpi_card"
    METRIC_CARD = "metric_card"
    PROGRESS_BAR = "progress_bar"
    SPARKLINE = "sparkline"
    TREND_INDICATOR = "trend_indicator"

    # Tabelas
    DATA_TABLE = "data_table"
    PIVOT_TABLE = "pivot_table"
    COMPARISON_TABLE = "comparison_table"
    RANKING_TABLE = "ranking_table"

    # Mapas
    GEO_MAP = "geo_map"
    HEATMAP = "heatmap"
    CHOROPLETH = "choropleth"

    # Texto
    TEXT_BOX = "text_box"
    RICH_TEXT = "rich_text"
    INSIGHT_BOX = "insight_box"
    ALERT_BOX = "alert_box"

    # Outros
    IMAGE = "image"
    IFRAME = "iframe"
    CUSTOM = "custom"


class WidgetSizeEnum(StrEnum):
    """Tamanhos predefinidos."""

    SMALL = "small"  # 1/4 width
    MEDIUM = "medium"  # 1/2 width
    LARGE = "large"  # 3/4 width
    FULL = "full"  # full width
    CUSTOM = "custom"


class ReportWidget(Base):
    """Model de widget de relatório."""

    __tablename__ = "ai_report_widgets"

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Relacionamentos
    template_id = Column(UUID(as_uuid=True), ForeignKey("ai_report_templates.id"), nullable=True)
    template = relationship("AIReportTemplate", back_populates="widgets")
    section_id = Column(UUID(as_uuid=True), ForeignKey("ai_report_sections.id"), nullable=True)
    section = relationship("ReportSection", back_populates="widgets")

    # Tipo
    widget_type = Column(
        SQLEnum(WidgetTypeEnum, name="widget_type_enum"), nullable=False, default=WidgetTypeEnum.BAR_CHART
    )

    # Posição e tamanho
    order = Column(Integer, default=0)
    row = Column(Integer, default=0)
    col = Column(Integer, default=0)
    row_span = Column(Integer, default=1)
    col_span = Column(Integer, default=1)
    size = Column(SQLEnum(WidgetSizeEnum, name="widget_size_enum"), default=WidgetSizeEnum.MEDIUM)

    # Dimensões customizadas
    width = Column(String(50), nullable=True)
    height = Column(String(50), nullable=True)
    min_width = Column(String(50), nullable=True)
    min_height = Column(String(50), nullable=True)
    max_width = Column(String(50), nullable=True)
    max_height = Column(String(50), nullable=True)

    # Configuração de dados
    data_source = Column(String(100), nullable=True)
    query = Column(Text, nullable=True)
    query_params = Column(JSONB, default=dict)
    filters = Column(JSONB, default=dict)
    aggregation = Column(String(50), nullable=True)  # sum, avg, count, etc.
    group_by = Column(JSONB, default=list)
    order_by = Column(JSONB, default=list)
    limit = Column(Integer, nullable=True)

    # Mapeamento de dados
    data_mapping = Column(JSONB, default=dict)  # x, y, series, etc.
    value_field = Column(String(100), nullable=True)
    label_field = Column(String(100), nullable=True)
    category_field = Column(String(100), nullable=True)
    series_field = Column(String(100), nullable=True)

    # Dados renderizados
    data = Column(JSONB, default=dict)
    computed_data = Column(JSONB, default=dict)

    # Configuração visual
    title = Column(String(255), nullable=True)
    subtitle = Column(String(500), nullable=True)
    show_title = Column(Boolean, default=True)
    show_legend = Column(Boolean, default=True)
    legend_position = Column(String(20), default="bottom")

    # Cores
    colors = Column(JSONB, default=list)
    color_scheme = Column(String(50), nullable=True)
    background_color = Column(String(20), nullable=True)

    # Eixos (para gráficos)
    x_axis_config = Column(JSONB, default=dict)
    y_axis_config = Column(JSONB, default=dict)
    secondary_y_axis = Column(JSONB, default=dict)

    # Formatação
    number_format = Column(String(50), nullable=True)
    date_format = Column(String(50), nullable=True)
    currency = Column(String(10), nullable=True)
    decimal_places = Column(Integer, default=2)
    show_values = Column(Boolean, default=True)
    value_position = Column(String(20), default="inside")

    # Tooltips
    show_tooltip = Column(Boolean, default=True)
    tooltip_template = Column(Text, nullable=True)

    # Animações
    enable_animation = Column(Boolean, default=True)
    animation_duration = Column(Integer, default=500)

    # Interatividade
    is_interactive = Column(Boolean, default=True)
    enable_zoom = Column(Boolean, default=False)
    enable_drill_down = Column(Boolean, default=False)
    drill_down_config = Column(JSONB, default=dict)
    click_action = Column(JSONB, default=dict)

    # Responsividade
    responsive = Column(Boolean, default=True)
    mobile_config = Column(JSONB, default=dict)

    # Thresholds e alertas
    thresholds = Column(JSONB, default=list)
    alert_rules = Column(JSONB, default=list)
    highlight_conditions = Column(JSONB, default=list)

    # KPI específico
    kpi_value = Column(String(100), nullable=True)
    kpi_label = Column(String(255), nullable=True)
    kpi_unit = Column(String(50), nullable=True)
    kpi_trend = Column(String(20), nullable=True)
    kpi_change = Column(Float, nullable=True)
    kpi_change_period = Column(String(50), nullable=True)
    kpi_target = Column(Float, nullable=True)
    kpi_status = Column(String(20), nullable=True)  # good, warning, critical

    # Comparação
    comparison_enabled = Column(Boolean, default=False)
    comparison_type = Column(String(50), nullable=True)  # previous_period, target, benchmark
    comparison_value = Column(Float, nullable=True)
    comparison_label = Column(String(100), nullable=True)

    # Estilos
    styles = Column(JSONB, default=dict)
    css_classes = Column(JSONB, default=list)
    custom_css = Column(Text, nullable=True)

    # Condicional
    visibility_condition = Column(Text, nullable=True)
    is_visible = Column(Boolean, default=True)

    # Cache
    cache_enabled = Column(Boolean, default=True)
    cache_ttl_seconds = Column(Integer, default=300)
    last_cached_at = Column(DateTime, nullable=True)

    # Biblioteca/sistema
    is_system = Column(Boolean, default=False)
    is_reusable = Column(Boolean, default=True)

    # Ownership
    created_by = Column(UUID(as_uuid=True), nullable=True)
    organization_id = Column(UUID(as_uuid=True), nullable=True)

    # Metadados
    extra_metadata = Column(JSONB, default=dict)
    tags = Column(JSONB, default=list)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Soft delete
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<ReportWidget(id={self.id}, code={self.code}, type={self.widget_type})>"

    @property
    def has_data(self) -> bool:
        """Verifica se o widget tem dados."""
        return bool(self.data or self.computed_data)

    @property
    def needs_refresh(self) -> bool:
        """Verifica se precisa atualizar dados."""
        if not self.cache_enabled:
            return True
        if not self.last_cached_at:
            return True
        elapsed = (datetime.utcnow() - self.last_cached_at).total_seconds()
        return elapsed > self.cache_ttl_seconds

    def set_data(self, data: dict[str, Any]) -> None:
        """Define dados do widget."""
        self.data = data
        self.last_cached_at = datetime.utcnow()

    def set_kpi(
        self,
        value: Any,
        label: str,
        unit: str = None,
        trend: str = None,
        change: float = None,
        target: float = None,
        status: str = None,
    ) -> None:
        """Configura KPI."""
        self.widget_type = WidgetTypeEnum.KPI_CARD
        self.kpi_value = str(value)
        self.kpi_label = label
        self.kpi_unit = unit
        self.kpi_trend = trend
        self.kpi_change = change
        self.kpi_target = target
        self.kpi_status = status or self._calculate_status(value, target)

    def _calculate_status(self, value: Any, target: float) -> str:
        """Calcula status baseado no valor e target."""
        if target is None:
            return "neutral"
        try:
            val = float(value)
            if val >= target:
                return "good"
            elif val >= target * 0.8:
                return "warning"
            else:
                return "critical"
        except (ValueError, TypeError):
            return "neutral"

    def set_chart_config(
        self, chart_type: str, x_field: str, y_field: str, series_field: str = None, colors: list[str] = None
    ) -> None:
        """Configura gráfico."""
        type_map = {
            "bar": WidgetTypeEnum.BAR_CHART,
            "line": WidgetTypeEnum.LINE_CHART,
            "pie": WidgetTypeEnum.PIE_CHART,
            "donut": WidgetTypeEnum.DONUT_CHART,
            "area": WidgetTypeEnum.AREA_CHART,
            "scatter": WidgetTypeEnum.SCATTER_PLOT,
            "gauge": WidgetTypeEnum.GAUGE,
            "funnel": WidgetTypeEnum.FUNNEL,
        }
        self.widget_type = type_map.get(chart_type, WidgetTypeEnum.BAR_CHART)
        self.data_mapping = {
            "x": x_field,
            "y": y_field,
            "series": series_field,
        }
        if colors:
            self.colors = colors

    def add_threshold(self, value: float, color: str, label: str = None, operator: str = "gte") -> None:
        """Adiciona threshold."""
        if not self.thresholds:
            self.thresholds = []
        self.thresholds.append(
            {
                "value": value,
                "color": color,
                "label": label,
                "operator": operator,
            }
        )

    def add_highlight_condition(self, condition: str, style: dict[str, Any], label: str = None) -> None:
        """Adiciona condição de destaque."""
        if not self.highlight_conditions:
            self.highlight_conditions = []
        self.highlight_conditions.append(
            {
                "condition": condition,
                "style": style,
                "label": label,
            }
        )

    def clone(self, new_code: str) -> "ReportWidget":
        """Cria cópia do widget."""
        return ReportWidget(
            code=new_code,
            name=f"{self.name} (Cópia)",
            description=self.description,
            widget_type=self.widget_type,
            size=self.size,
            data_source=self.data_source,
            query=self.query,
            data_mapping=self.data_mapping.copy() if self.data_mapping else {},
            title=self.title,
            show_title=self.show_title,
            colors=self.colors.copy() if self.colors else [],
            x_axis_config=self.x_axis_config.copy() if self.x_axis_config else {},
            y_axis_config=self.y_axis_config.copy() if self.y_axis_config else {},
            styles=self.styles.copy() if self.styles else {},
            is_reusable=True,
        )

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "code": self.code,
            "name": self.name,
            "widget_type": self.widget_type.value,
            "size": self.size.value,
            "title": self.title,
            "has_data": self.has_data,
            "is_visible": self.is_visible,
        }

    def to_render_dict(self) -> dict[str, Any]:
        """Converte para dicionário de renderização."""
        return {
            "id": str(self.id),
            "code": self.code,
            "widget_type": self.widget_type.value,
            "title": self.title,
            "subtitle": self.subtitle,
            "data": self.data,
            "data_mapping": self.data_mapping,
            "colors": self.colors,
            "show_legend": self.show_legend,
            "legend_position": self.legend_position,
            "x_axis_config": self.x_axis_config,
            "y_axis_config": self.y_axis_config,
            "number_format": self.number_format,
            "show_values": self.show_values,
            "thresholds": self.thresholds,
            "kpi_value": self.kpi_value,
            "kpi_label": self.kpi_label,
            "kpi_unit": self.kpi_unit,
            "kpi_trend": self.kpi_trend,
            "kpi_change": self.kpi_change,
            "kpi_target": self.kpi_target,
            "kpi_status": self.kpi_status,
            "styles": self.styles,
            "width": self.width,
            "height": self.height,
        }
