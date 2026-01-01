"""Cost Analysis model - Relatórios e Análises de Custo."""

import enum
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base


class AnalysisType(str, enum.Enum):
    """Tipo de análise."""

    ABC_COSTING = "ABC_COSTING"  # Custeio ABC
    PROFITABILITY = "PROFITABILITY"  # Análise de rentabilidade
    VARIANCE = "VARIANCE"  # Análise de variação
    BREAK_EVEN = "BREAK_EVEN"  # Ponto de equilíbrio
    COST_VOLUME_PROFIT = "COST_VOLUME_PROFIT"  # Custo-Volume-Lucro
    IDLE_CAPACITY = "IDLE_CAPACITY"  # Capacidade ociosa
    TREND = "TREND"  # Análise de tendência
    COMPARATIVE = "COMPARATIVE"  # Comparativo entre períodos
    WHAT_IF = "WHAT_IF"  # Simulação/cenários
    CUSTOM = "CUSTOM"  # Personalizada


class AnalysisStatus(str, enum.Enum):
    """Status da análise."""

    DRAFT = "DRAFT"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"


class AnalysisScope(str, enum.Enum):
    """Escopo da análise."""

    GLOBAL = "GLOBAL"  # Toda empresa
    COST_CENTER = "COST_CENTER"  # Por centro de custo
    PRODUCT = "PRODUCT"  # Por produto
    SERVICE = "SERVICE"  # Por serviço
    CUSTOMER = "CUSTOMER"  # Por cliente
    PROJECT = "PROJECT"  # Por projeto
    ACTIVITY = "ACTIVITY"  # Por atividade
    POOL = "POOL"  # Por pool
    CUSTOM = "CUSTOM"  # Personalizado


class ReportFormat(str, enum.Enum):
    """Formato do relatório."""

    PDF = "PDF"
    EXCEL = "EXCEL"
    CSV = "CSV"
    JSON = "JSON"
    HTML = "HTML"


class CostAnalysis(Base):
    """Análise de Custo - geração de relatórios e insights."""

    __tablename__ = "fin_cost_analyses"
    __table_args__ = (
        UniqueConstraint("condominio_id", "code", name="uq_cost_analysis_code"),
    )

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Multi-tenant
    condominio_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Identificação
    code = Column(String(30), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)

    # Classificação
    analysis_type = Column(
        Enum(AnalysisType, name="analysistype", create_type=True),
        nullable=False,
        default=AnalysisType.ABC_COSTING,
    )
    status = Column(
        Enum(AnalysisStatus, name="analysisstatus", create_type=True),
        nullable=False,
        default=AnalysisStatus.DRAFT,
    )
    scope = Column(
        Enum(AnalysisScope, name="analysisscope", create_type=True),
        nullable=False,
        default=AnalysisScope.GLOBAL,
    )

    # Período de análise
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    reference_period = Column(String(7), nullable=True)  # "2024-01"

    # Filtros aplicados
    cost_center_ids = Column(JSONB, nullable=True)  # ["uuid1", "uuid2"]
    activity_ids = Column(JSONB, nullable=True)
    pool_ids = Column(JSONB, nullable=True)
    object_ids = Column(JSONB, nullable=True)
    filters = Column(JSONB, nullable=True)
    # Ex: {"min_cost": 1000, "object_type": "SERVICE"}

    # Parâmetros da análise
    parameters = Column(JSONB, nullable=True)
    # Ex: {"include_overhead": true, "allocation_method": "ABC"}

    # Cenários (para WHAT_IF)
    scenarios = Column(JSONB, nullable=True)
    # Ex: [{"name": "Pessimista", "cost_increase": 0.1}]

    # Comparação (para COMPARATIVE)
    comparison_period_start = Column(DateTime(timezone=True), nullable=True)
    comparison_period_end = Column(DateTime(timezone=True), nullable=True)

    # Resultados
    results = Column(JSONB, nullable=True)
    # Estrutura depende do tipo de análise

    # Métricas calculadas
    total_cost = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    total_revenue = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    total_margin = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    margin_percent = Column(Numeric(8, 4), default=Decimal("0"), nullable=False)

    # ABC específico
    total_direct_cost = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    total_indirect_cost = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    total_allocated = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    unallocated_cost = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)

    # Capacidade
    practical_capacity = Column(Numeric(18, 4), nullable=True)
    used_capacity = Column(Numeric(18, 4), nullable=True)
    idle_capacity = Column(Numeric(18, 4), nullable=True)
    idle_capacity_cost = Column(Numeric(18, 2), nullable=True)

    # Variações
    cost_variance = Column(Numeric(18, 2), nullable=True)
    volume_variance = Column(Numeric(18, 2), nullable=True)
    efficiency_variance = Column(Numeric(18, 2), nullable=True)
    price_variance = Column(Numeric(18, 2), nullable=True)

    # Ponto de equilíbrio
    break_even_units = Column(Numeric(18, 4), nullable=True)
    break_even_revenue = Column(Numeric(18, 2), nullable=True)
    safety_margin = Column(Numeric(18, 2), nullable=True)
    safety_margin_percent = Column(Numeric(8, 4), nullable=True)

    # Insights gerados
    insights = Column(JSONB, nullable=True)
    # Ex: [{"type": "warning", "message": "Capacidade ociosa alta", "value": 35}]

    # Recomendações
    recommendations = Column(JSONB, nullable=True)
    # Ex: [{"action": "Reduzir overhead", "impact": 5000, "priority": "high"}]

    # Alertas
    alerts = Column(JSONB, nullable=True)
    # Ex: [{"level": "critical", "message": "Custo acima do orçamento"}]

    # Gráficos/Visualizações
    charts_data = Column(JSONB, nullable=True)
    # Ex: {"pie_cost_breakdown": [...], "bar_comparison": [...]}

    # Execução
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)

    # Relatório
    report_format = Column(
        Enum(ReportFormat, name="reportformat", create_type=True),
        nullable=True,
    )
    report_path = Column(String(300), nullable=True)
    report_generated_at = Column(DateTime(timezone=True), nullable=True)

    # Agendamento
    is_scheduled = Column(Boolean, default=False, nullable=False)
    schedule_cron = Column(String(50), nullable=True)
    next_run_at = Column(DateTime(timezone=True), nullable=True)
    last_run_at = Column(DateTime(timezone=True), nullable=True)

    # Compartilhamento
    shared_with = Column(JSONB, nullable=True)  # ["user_id1", "user_id2"]
    is_public = Column(Boolean, default=False, nullable=False)

    # Flags
    is_template = Column(Boolean, default=False, nullable=False)
    is_favorite = Column(Boolean, default=False, nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    # Observações
    notes = Column(Text, nullable=True)
    tags = Column(JSONB, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Audit
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    deleted_by = Column(UUID(as_uuid=True), nullable=True)

    def __repr__(self) -> str:
        """Representação string."""
        return f"<CostAnalysis {self.code} - {self.name}>"

    @property
    def is_completed(self) -> bool:
        """Verifica se a análise foi concluída."""
        return self.status == AnalysisStatus.COMPLETED

    @property
    def is_running(self) -> bool:
        """Verifica se está em execução."""
        return self.status == AnalysisStatus.RUNNING

    @property
    def capacity_usage_percent(self) -> Decimal:
        """Calcula percentual de uso da capacidade."""
        if not self.practical_capacity or self.practical_capacity == 0:
            return Decimal("0")
        return (self.used_capacity / self.practical_capacity) * 100

    @property
    def allocation_percent(self) -> Decimal:
        """Calcula percentual alocado."""
        total = self.total_direct_cost + self.total_indirect_cost
        if total == 0:
            return Decimal("0")
        return (self.total_allocated / total) * 100

    def start(self) -> None:
        """Inicia a execução da análise."""
        self.status = AnalysisStatus.RUNNING
        self.started_at = datetime.utcnow()

    def complete(self, results: dict = None) -> None:
        """Marca como concluída."""
        self.status = AnalysisStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        if self.started_at:
            delta = self.completed_at - self.started_at
            self.execution_time_ms = int(delta.total_seconds() * 1000)
        if results:
            self.results = results

    def fail(self, error: str) -> None:
        """Marca como falha."""
        self.status = AnalysisStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error_message = error

    def archive(self) -> None:
        """Arquiva a análise."""
        self.status = AnalysisStatus.ARCHIVED

    def add_insight(
        self,
        insight_type: str,
        message: str,
        value: float = None,
        priority: str = "medium",
    ) -> None:
        """Adiciona insight."""
        if self.insights is None:
            self.insights = []
        self.insights.append(
            {
                "type": insight_type,
                "message": message,
                "value": value,
                "priority": priority,
                "created_at": datetime.utcnow().isoformat(),
            }
        )

    def add_recommendation(
        self, action: str, impact: float, priority: str = "medium", details: str = None
    ) -> None:
        """Adiciona recomendação."""
        if self.recommendations is None:
            self.recommendations = []
        self.recommendations.append(
            {
                "action": action,
                "impact": impact,
                "priority": priority,
                "details": details,
                "created_at": datetime.utcnow().isoformat(),
            }
        )

    def add_alert(self, level: str, message: str, metric: str = None) -> None:
        """Adiciona alerta."""
        if self.alerts is None:
            self.alerts = []
        self.alerts.append(
            {
                "level": level,
                "message": message,
                "metric": metric,
                "created_at": datetime.utcnow().isoformat(),
            }
        )

    def calculate_break_even(
        self, fixed_cost: Decimal, unit_price: Decimal, unit_variable_cost: Decimal
    ) -> None:
        """Calcula ponto de equilíbrio."""
        contribution_margin = unit_price - unit_variable_cost
        if contribution_margin > 0:
            self.break_even_units = fixed_cost / contribution_margin
            self.break_even_revenue = self.break_even_units * unit_price
        else:
            self.break_even_units = None
            self.break_even_revenue = None

    def calculate_safety_margin(self, actual_revenue: Decimal) -> None:
        """Calcula margem de segurança."""
        if self.break_even_revenue and self.break_even_revenue > 0:
            self.safety_margin = actual_revenue - self.break_even_revenue
            self.safety_margin_percent = (self.safety_margin / actual_revenue) * 100
