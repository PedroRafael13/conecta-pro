"""Model de Widget de Dashboard Financeiro."""

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from core.models.base import Base


class WidgetType(StrEnum):
    """Tipo de widget."""

    KPI_CARD = "KPI_CARD"
    CHART = "CHART"
    TABLE = "TABLE"
    MAP = "MAP"
    GAUGE = "GAUGE"
    HEATMAP = "HEATMAP"
    FUNNEL = "FUNNEL"
    TREEMAP = "TREEMAP"
    CALENDAR = "CALENDAR"
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    IFRAME = "IFRAME"
    CUSTOM = "CUSTOM"


class WidgetSize(StrEnum):
    """Tamanho do widget."""

    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"
    EXTRA_LARGE = "EXTRA_LARGE"
    FULL_WIDTH = "FULL_WIDTH"


class ChartType(StrEnum):
    """Tipo de grafico."""

    LINE = "LINE"
    BAR = "BAR"
    BAR_HORIZONTAL = "BAR_HORIZONTAL"
    AREA = "AREA"
    PIE = "PIE"
    DONUT = "DONUT"
    SCATTER = "SCATTER"
    BUBBLE = "BUBBLE"
    RADAR = "RADAR"
    WATERFALL = "WATERFALL"
    CANDLESTICK = "CANDLESTICK"
    COMBO = "COMBO"
    STACKED_BAR = "STACKED_BAR"
    STACKED_AREA = "STACKED_AREA"


class DataSource(StrEnum):
    """Fonte de dados do widget."""

    ACCOUNTS_PAYABLE = "ACCOUNTS_PAYABLE"
    ACCOUNTS_RECEIVABLE = "ACCOUNTS_RECEIVABLE"
    CASH_FLOW = "CASH_FLOW"
    BANK_ACCOUNTS = "BANK_ACCOUNTS"
    PURCHASES = "PURCHASES"
    INVENTORY = "INVENTORY"
    ACCOUNTING = "ACCOUNTING"
    FISCAL = "FISCAL"
    COSTING = "COSTING"
    BUDGET = "BUDGET"
    CUSTOM_QUERY = "CUSTOM_QUERY"


class FinancialWidget(Base):
    """Widget de Dashboard Financeiro."""

    __tablename__ = "financial_widgets"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    dashboard_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("financial_dashboards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    condominio_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=False,
        index=True,
    )

    # Identificacao
    codigo = Column(String(50), nullable=False)
    titulo = Column(String(200), nullable=False)
    subtitulo = Column(String(500))
    descricao = Column(Text)

    # Tipo e Aparencia
    tipo = Column(
        SQLEnum(WidgetType, name="widget_type_enum"),
        default=WidgetType.KPI_CARD,
        nullable=False,
    )
    tamanho = Column(
        SQLEnum(WidgetSize, name="widget_size_enum"),
        default=WidgetSize.MEDIUM,
        nullable=False,
    )
    chart_type = Column(SQLEnum(ChartType, name="chart_type_enum"))

    # Posicionamento (Grid Layout)
    position_x = Column(Integer, default=0, nullable=False)
    position_y = Column(Integer, default=0, nullable=False)
    width = Column(Integer, default=1, nullable=False)
    height = Column(Integer, default=1, nullable=False)
    order = Column(Integer, default=0)

    # Fonte de Dados
    data_source = Column(
        SQLEnum(DataSource, name="data_source_enum"),
        default=DataSource.CASH_FLOW,
        nullable=False,
    )
    custom_query = Column(Text)
    query_params = Column(JSONB, default=dict)

    # Configuracao de Dados
    metric_field = Column(String(100))
    dimension_field = Column(String(100))
    time_field = Column(String(100), default="created_at")
    aggregation = Column(String(50), default="sum")
    group_by = Column(JSONB, default=list)
    sort_by = Column(String(100))
    sort_order = Column(String(10), default="desc")
    limit = Column(Integer, default=10)

    # Filtros
    filters = Column(JSONB, default=dict)
    date_range_days = Column(Integer, default=30)
    comparison_enabled = Column(Boolean, default=False)
    comparison_period = Column(String(50))

    # Formatacao
    value_format = Column(String(50), default="currency")
    decimal_places = Column(Integer, default=2)
    show_percentage = Column(Boolean, default=False)
    show_trend = Column(Boolean, default=True)
    show_comparison = Column(Boolean, default=False)
    show_legend = Column(Boolean, default=True)

    # Cores e Estilo
    colors = Column(JSONB, default=list)
    background_color = Column(String(20))
    border_color = Column(String(20))
    text_color = Column(String(20))
    icon = Column(String(100))

    # Thresholds e Alertas
    threshold_warning = Column(Numeric(20, 2))
    threshold_critical = Column(Numeric(20, 2))
    threshold_success = Column(Numeric(20, 2))
    invert_colors = Column(Boolean, default=False)

    # Interatividade
    is_clickable = Column(Boolean, default=True)
    click_action = Column(String(50))
    drill_down_enabled = Column(Boolean, default=False)
    drill_down_config = Column(JSONB, default=dict)

    # Estado
    is_visible = Column(Boolean, default=True, nullable=False)
    is_loading = Column(Boolean, default=False)
    last_error = Column(Text)
    last_updated_at = Column(DateTime)
    cache_ttl_seconds = Column(Integer, default=300)

    # Auditoria
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    dashboard = relationship("FinancialDashboard", back_populates="widgets")

    def __repr__(self) -> str:
        """Representacao do widget."""
        return f"<FinancialWidget {self.codigo}: {self.titulo}>"

    @property
    def is_chart(self) -> bool:
        """Verifica se widget eh um grafico."""
        return self.tipo == WidgetType.CHART

    @property
    def is_kpi(self) -> bool:
        """Verifica se widget eh um KPI card."""
        return self.tipo == WidgetType.KPI_CARD

    @property
    def needs_refresh(self) -> bool:
        """Verifica se widget precisa refresh."""
        if not self.last_updated_at:
            return True
        elapsed = (datetime.utcnow() - self.last_updated_at).total_seconds()
        return elapsed > self.cache_ttl_seconds

    @property
    def grid_position(self) -> dict:
        """Retorna posicao no grid."""
        return {
            "x": self.position_x,
            "y": self.position_y,
            "w": self.width,
            "h": self.height,
        }

    def move_to(self, x: int, y: int) -> None:
        """Move widget para nova posicao."""
        self.position_x = x
        self.position_y = y

    def resize(self, width: int, height: int) -> None:
        """Redimensiona widget."""
        self.width = width
        self.height = height

    def set_error(self, error: str) -> None:
        """Define erro no widget."""
        self.is_loading = False
        self.last_error = error

    def set_loaded(self) -> None:
        """Marca widget como carregado."""
        self.is_loading = False
        self.last_error = None
        self.last_updated_at = datetime.utcnow()

    def get_color_for_value(self, value: Decimal) -> str:
        """Retorna cor baseada nos thresholds."""
        if self.threshold_critical and value <= self.threshold_critical:
            return "#f44336" if not self.invert_colors else "#4caf50"
        if self.threshold_warning and value <= self.threshold_warning:
            return "#ff9800"
        if self.threshold_success and value >= self.threshold_success:
            return "#4caf50" if not self.invert_colors else "#f44336"
        return "#2196f3"
