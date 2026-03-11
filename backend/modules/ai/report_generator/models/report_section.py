"""
ReportSection Model - Seções do relatório.

Define seções/blocos que compõem um relatório.
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


class SectionTypeEnum(StrEnum):
    """Tipos de seção."""

    # Estruturais
    HEADER = "header"
    FOOTER = "footer"
    COVER = "cover"
    TABLE_OF_CONTENTS = "table_of_contents"
    SUMMARY = "summary"

    # Conteúdo
    TEXT = "text"
    TABLE = "table"
    CHART = "chart"
    IMAGE = "image"
    METRIC = "metric"
    KPI = "kpi"

    # Análises
    TREND = "trend"
    COMPARISON = "comparison"
    BREAKDOWN = "breakdown"
    RANKING = "ranking"
    HEATMAP = "heatmap"

    # IA
    INSIGHT = "insight"
    RECOMMENDATION = "recommendation"
    ANOMALY = "anomaly"
    FORECAST = "forecast"

    # Compostos
    DASHBOARD = "dashboard"
    GRID = "grid"
    TABS = "tabs"
    ACCORDION = "accordion"

    # Outros
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


class ReportSection(Base):
    """Model de seção de relatório."""

    __tablename__ = "ai_report_sections"

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # noqa: A003
    code = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Relacionamentos
    report_id = Column(UUID(as_uuid=True), ForeignKey("ai_reports.id"), nullable=True)
    report = relationship("Report", back_populates="sections")
    template_id = Column(UUID(as_uuid=True), ForeignKey("ai_report_templates.id"), nullable=True)
    template = relationship("AIReportTemplate", back_populates="sections")
    parent_section_id = Column(UUID(as_uuid=True), ForeignKey("ai_report_sections.id"), nullable=True)

    # Tipo e layout
    section_type = Column(
        SQLEnum(SectionTypeEnum, name="section_type_enum"), nullable=False, default=SectionTypeEnum.TEXT
    )
    layout = Column(
        SQLEnum(SectionLayoutEnum, name="section_layout_enum"), nullable=False, default=SectionLayoutEnum.FULL_WIDTH
    )

    # Ordenação
    order = Column(Integer, default=0)
    level = Column(Integer, default=0)  # Para hierarquia (0=root)
    page_number = Column(Integer, nullable=True)

    # Configuração de dados
    data_source = Column(String(100), nullable=True)
    query = Column(Text, nullable=True)
    filters = Column(JSONB, default=dict)
    parameters = Column(JSONB, default=dict)
    aggregations = Column(JSONB, default=list)
    groupings = Column(JSONB, default=list)
    sortings = Column(JSONB, default=list)

    # Conteúdo
    title = Column(String(255), nullable=True)
    subtitle = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)  # Texto, markdown
    content_template = Column(Text, nullable=True)  # Template com variáveis

    # Dados renderizados
    rendered_content = Column(Text, nullable=True)
    data = Column(JSONB, default=dict)
    computed_values = Column(JSONB, default=dict)

    # Configuração visual
    styles = Column(JSONB, default=dict)
    css_classes = Column(JSONB, default=list)
    background_color = Column(String(20), nullable=True)
    border = Column(JSONB, default=dict)
    padding = Column(JSONB, default=dict)
    margin = Column(JSONB, default=dict)

    # Dimensões
    width = Column(String(50), nullable=True)
    height = Column(String(50), nullable=True)
    min_height = Column(String(50), nullable=True)
    max_height = Column(String(50), nullable=True)

    # Chart config (para tipo CHART)
    chart_type = Column(String(50), nullable=True)  # bar, line, pie, etc.
    chart_config = Column(JSONB, default=dict)
    chart_data = Column(JSONB, default=dict)

    # Table config (para tipo TABLE)
    table_columns = Column(JSONB, default=list)
    table_config = Column(JSONB, default=dict)
    table_data = Column(JSONB, default=list)
    show_totals = Column(Boolean, default=False)
    show_pagination = Column(Boolean, default=False)

    # Metric/KPI config
    metric_value = Column(String(100), nullable=True)
    metric_label = Column(String(255), nullable=True)
    metric_unit = Column(String(50), nullable=True)
    metric_trend = Column(String(20), nullable=True)  # up, down, stable
    metric_change = Column(Float, nullable=True)
    metric_target = Column(Float, nullable=True)
    metric_format = Column(String(50), nullable=True)

    # Insight config (para tipo INSIGHT)
    insight_type = Column(String(50), nullable=True)
    insight_severity = Column(String(20), nullable=True)
    insight_data = Column(JSONB, default=dict)

    # Condicional
    visibility_condition = Column(Text, nullable=True)  # Expressão para visibilidade
    is_visible = Column(Boolean, default=True)
    show_if_empty = Column(Boolean, default=False)

    # Interatividade
    is_interactive = Column(Boolean, default=False)
    drill_down_config = Column(JSONB, default=dict)
    click_action = Column(JSONB, default=dict)

    # Metadados
    extra_metadata = Column(JSONB, default=dict)
    tags = Column(JSONB, default=list)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Soft delete
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    widgets = relationship("ReportWidget", back_populates="section")
    children = relationship(
        "ReportSection",
        backref="parent",
        remote_side=[id],  # noqa: A003
        cascade="all, delete-orphan",
        single_parent=True,
    )

    def __repr__(self) -> str:
        return f"<ReportSection(id={self.id}, code={self.code}, type={self.section_type})>"

    @property
    def has_data(self) -> bool:
        """Verifica se a seção tem dados."""
        if self.section_type == SectionTypeEnum.TABLE:
            return bool(self.table_data)
        if self.section_type == SectionTypeEnum.CHART:
            return bool(self.chart_data)
        return bool(self.data)

    @property
    def is_empty(self) -> bool:
        """Verifica se a seção está vazia."""
        return not self.has_data and not self.content and not self.rendered_content

    @property
    def children_count(self) -> int:
        """Número de seções filhas."""
        return len(self.children) if self.children else 0

    def set_chart_data(self, chart_type: str, data: dict[str, Any], config: dict[str, Any] = None) -> None:
        """Configura dados do gráfico."""
        self.section_type = SectionTypeEnum.CHART
        self.chart_type = chart_type
        self.chart_data = data
        if config:
            self.chart_config = config

    def set_table_data(
        self, columns: list[dict[str, Any]], data: list[dict[str, Any]], config: dict[str, Any] = None
    ) -> None:
        """Configura dados da tabela."""
        self.section_type = SectionTypeEnum.TABLE
        self.table_columns = columns
        self.table_data = data
        if config:
            self.table_config = config

    def set_metric(
        self,
        value: Any,
        label: str,
        unit: str = None,
        trend: str = None,
        change: float = None,
        target: float = None,
        format_str: str = None,
    ) -> None:
        """Configura métrica/KPI."""
        self.section_type = SectionTypeEnum.METRIC
        self.metric_value = str(value)
        self.metric_label = label
        self.metric_unit = unit
        self.metric_trend = trend
        self.metric_change = change
        self.metric_target = target
        self.metric_format = format_str

    def set_insight(self, insight_type: str, content: str, severity: str = "info", data: dict[str, Any] = None) -> None:
        """Configura insight."""
        self.section_type = SectionTypeEnum.INSIGHT
        self.insight_type = insight_type
        self.content = content
        self.insight_severity = severity
        if data:
            self.insight_data = data

    def render_template(self, context: dict[str, Any]) -> str:
        """Renderiza template com contexto."""
        if not self.content_template:
            return self.content or ""

        rendered = self.content_template
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            rendered = rendered.replace(placeholder, str(value))

        self.rendered_content = rendered
        return rendered

    def evaluate_visibility(self, context: dict[str, Any]) -> bool:
        """Avalia condição de visibilidade."""
        if not self.visibility_condition:
            return True

        try:
            # Avaliação segura da condição
            return eval(self.visibility_condition, {"__builtins__": {}}, context)  # noqa: S307  # nosec B307
        except Exception:
            return True

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "code": self.code,
            "name": self.name,
            "section_type": self.section_type.value,
            "layout": self.layout.value,
            "order": self.order,
            "level": self.level,
            "title": self.title,
            "subtitle": self.subtitle,
            "is_visible": self.is_visible,
            "has_data": self.has_data,
            "children_count": self.children_count,
        }

    def to_render_dict(self) -> dict[str, Any]:
        """Converte para dicionário de renderização."""
        base = self.to_dict()
        base.update(
            {
                "content": self.rendered_content or self.content,
                "data": self.data,
                "styles": self.styles,
                "chart_type": self.chart_type,
                "chart_config": self.chart_config,
                "chart_data": self.chart_data,
                "table_columns": self.table_columns,
                "table_config": self.table_config,
                "table_data": self.table_data,
                "metric_value": self.metric_value,
                "metric_label": self.metric_label,
                "metric_unit": self.metric_unit,
                "metric_trend": self.metric_trend,
                "metric_change": self.metric_change,
            }
        )
        return base
