"""Model de Definicao de KPI Financeiro."""

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

from core.models.base import Base


class KPICategory(StrEnum):
    """Categoria do KPI."""

    LIQUIDITY = "LIQUIDITY"
    PROFITABILITY = "PROFITABILITY"
    EFFICIENCY = "EFFICIENCY"
    SOLVENCY = "SOLVENCY"
    ACTIVITY = "ACTIVITY"
    CASH_FLOW = "CASH_FLOW"
    BUDGET = "BUDGET"
    COST = "COST"
    REVENUE = "REVENUE"
    CUSTOM = "CUSTOM"


class KPIFrequency(StrEnum):
    """Frequencia de calculo do KPI."""

    REAL_TIME = "REAL_TIME"
    HOURLY = "HOURLY"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    YEARLY = "YEARLY"


class KPIStatus(StrEnum):
    """Status do KPI."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DRAFT = "DRAFT"
    DEPRECATED = "DEPRECATED"


class KPITrend(StrEnum):
    """Tendencia do KPI."""

    UP = "UP"
    DOWN = "DOWN"
    STABLE = "STABLE"
    VOLATILE = "VOLATILE"


class AlertLevel(StrEnum):
    """Nivel de alerta do KPI."""

    NORMAL = "NORMAL"
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class FinancialKPI(Base):
    """Definicao de KPI Financeiro."""

    __tablename__ = "financial_kpis"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=False,
        index=True,
    )

    # Identificacao
    codigo = Column(String(50), nullable=False, unique=True, index=True)
    nome = Column(String(200), nullable=False)
    nome_curto = Column(String(50))
    descricao = Column(Text)

    # Classificacao
    categoria = Column(
        SQLEnum(KPICategory, name="kpi_category_enum"),
        default=KPICategory.CUSTOM,
        nullable=False,
    )
    status = Column(
        SQLEnum(KPIStatus, name="kpi_status_enum"),
        default=KPIStatus.ACTIVE,
        nullable=False,
    )
    frequencia = Column(
        SQLEnum(KPIFrequency, name="kpi_frequency_enum"),
        default=KPIFrequency.DAILY,
        nullable=False,
    )

    # Formula e Calculo
    formula = Column(Text, nullable=False)
    formula_descricao = Column(Text)
    variaveis = Column(JSONB, default=dict)
    data_sources = Column(JSONB, default=list)

    # Valor Atual
    valor_atual = Column(Numeric(20, 4), default=Decimal("0"))
    valor_anterior = Column(Numeric(20, 4))
    variacao_percentual = Column(Numeric(10, 2))
    trend = Column(SQLEnum(KPITrend, name="kpi_trend_enum"))
    ultimo_calculo_at = Column(DateTime)

    # Metas
    meta_valor = Column(Numeric(20, 4))
    meta_minimo = Column(Numeric(20, 4))
    meta_maximo = Column(Numeric(20, 4))
    meta_atingida = Column(Boolean, default=False)
    meta_percentual = Column(Numeric(10, 2))

    # Thresholds e Alertas
    threshold_warning_min = Column(Numeric(20, 4))
    threshold_warning_max = Column(Numeric(20, 4))
    threshold_critical_min = Column(Numeric(20, 4))
    threshold_critical_max = Column(Numeric(20, 4))
    alert_level = Column(
        SQLEnum(AlertLevel, name="alert_level_enum"),
        default=AlertLevel.NORMAL,
    )
    alert_message = Column(Text)
    alert_enabled = Column(Boolean, default=True)

    # Formatacao
    unidade = Column(String(20), default="R$")
    formato = Column(String(50), default="currency")
    casas_decimais = Column(Integer, default=2)
    is_percentage = Column(Boolean, default=False)
    is_inverted = Column(Boolean, default=False)

    # Visualizacao
    icon = Column(String(100))
    color = Column(String(20), default="#1976d2")
    show_in_summary = Column(Boolean, default=True)
    order = Column(Integer, default=0)

    # Historico
    historico_valores = Column(JSONB, default=list)
    historico_dias = Column(Integer, default=365)

    # Benchmark
    benchmark_valor = Column(Numeric(20, 4))
    benchmark_fonte = Column(String(200))
    benchmark_data = Column(DateTime)

    # Metadados
    tags = Column(JSONB, default=list)
    extra_metadata = Column(JSONB, default=dict)

    # Auditoria
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        """Representacao do KPI."""
        return f"<FinancialKPI {self.codigo}: {self.nome}>"

    @property
    def is_active(self) -> bool:
        """Verifica se KPI esta ativo."""
        return self.status == KPIStatus.ACTIVE

    @property
    def is_on_target(self) -> bool:
        """Verifica se KPI esta na meta."""
        if not self.meta_valor or not self.valor_atual:
            return False
        if self.is_inverted:
            return self.valor_atual <= self.meta_valor
        return self.valor_atual >= self.meta_valor

    @property
    def progress_to_target(self) -> Decimal:
        """Calcula progresso para meta (0-100%)."""
        if not self.meta_valor or self.meta_valor == 0:
            return Decimal("0")
        progress = (self.valor_atual / self.meta_valor) * 100
        return min(progress, Decimal("100"))

    @property
    def is_improving(self) -> bool:
        """Verifica se KPI esta melhorando."""
        if self.trend == KPITrend.UP:
            return not self.is_inverted
        if self.trend == KPITrend.DOWN:
            return self.is_inverted
        return False

    def update_value(self, new_value: Decimal) -> None:
        """Atualiza valor do KPI."""
        self.valor_anterior = self.valor_atual
        self.valor_atual = new_value
        self.ultimo_calculo_at = datetime.utcnow()

        # Calcula variacao
        if self.valor_anterior and self.valor_anterior != 0:
            variacao = ((new_value - self.valor_anterior) / self.valor_anterior) * 100
            self.variacao_percentual = variacao

            # Define trend
            if variacao > Decimal("2"):
                self.trend = KPITrend.UP
            elif variacao < Decimal("-2"):
                self.trend = KPITrend.DOWN
            else:
                self.trend = KPITrend.STABLE

        # Verifica meta
        if self.meta_valor:
            if self.is_inverted:
                self.meta_atingida = new_value <= self.meta_valor
            else:
                self.meta_atingida = new_value >= self.meta_valor
            if self.meta_valor != 0:
                self.meta_percentual = (new_value / self.meta_valor) * 100

        # Atualiza alerta
        self._update_alert_level()

    def _update_alert_level(self) -> None:
        """Atualiza nivel de alerta baseado nos thresholds."""
        if not self.valor_atual:
            self.alert_level = AlertLevel.NORMAL
            return

        value = self.valor_atual

        # Verifica critical
        if self.threshold_critical_min and value < self.threshold_critical_min:
            self.alert_level = AlertLevel.CRITICAL
            self.alert_message = f"Valor abaixo do limite critico ({self.threshold_critical_min})"
            return
        if self.threshold_critical_max and value > self.threshold_critical_max:
            self.alert_level = AlertLevel.CRITICAL
            self.alert_message = f"Valor acima do limite critico ({self.threshold_critical_max})"
            return

        # Verifica warning
        if self.threshold_warning_min and value < self.threshold_warning_min:
            self.alert_level = AlertLevel.WARNING
            self.alert_message = f"Valor abaixo do limite de atencao ({self.threshold_warning_min})"
            return
        if self.threshold_warning_max and value > self.threshold_warning_max:
            self.alert_level = AlertLevel.WARNING
            self.alert_message = f"Valor acima do limite de atencao ({self.threshold_warning_max})"
            return

        self.alert_level = AlertLevel.NORMAL
        self.alert_message = None

    def add_to_history(self, value: Decimal, date: datetime = None) -> None:
        """Adiciona valor ao historico."""
        if not self.historico_valores:
            self.historico_valores = []

        entry = {
            "value": float(value),
            "date": (date or datetime.utcnow()).isoformat(),
        }
        self.historico_valores.append(entry)

        # Limita tamanho do historico
        if len(self.historico_valores) > self.historico_dias:
            self.historico_valores = self.historico_valores[-self.historico_dias :]

    def format_value(self, value: Decimal = None) -> str:
        """Formata valor para exibicao."""
        val = value if value is not None else self.valor_atual
        if val is None:
            return "-"

        if self.is_percentage:
            return f"{val:.{self.casas_decimais}f}%"
        if self.formato == "currency":
            return f"{self.unidade} {val:,.{self.casas_decimais}f}"
        return f"{val:.{self.casas_decimais}f} {self.unidade}"
