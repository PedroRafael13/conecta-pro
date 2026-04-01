"""Schemas de KPI Financeiro."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from modules.financial.bi_dashboard.models.kpi_definition import (
    AlertLevel,
    KPICategory,
    KPIFrequency,
    KPIStatus,
    KPITrend,
)


class KPIBase(BaseModel):
    """Schema base de KPI."""

    nome: str = Field(..., min_length=1, max_length=200)
    nome_curto: str | None = Field(None, max_length=50)
    descricao: str | None = Field(None, max_length=2000)
    categoria: KPICategory = Field(default=KPICategory.CUSTOM)
    frequencia: KPIFrequency = Field(default=KPIFrequency.DAILY)
    formula: str = Field(..., min_length=1)
    formula_descricao: str | None = None


class KPIThresholds(BaseModel):
    """Thresholds do KPI."""

    warning_min: Decimal | None = None
    warning_max: Decimal | None = None
    critical_min: Decimal | None = None
    critical_max: Decimal | None = None


class KPIFormatting(BaseModel):
    """Formatacao do KPI."""

    unidade: str = Field(default="R$", max_length=20)
    formato: str = Field(default="currency", max_length=50)
    casas_decimais: int = Field(default=2, ge=0, le=8)
    is_percentage: bool = Field(default=False)
    is_inverted: bool = Field(default=False)


class KPITarget(BaseModel):
    """Meta do KPI."""

    valor: Decimal | None = None
    minimo: Decimal | None = None
    maximo: Decimal | None = None


class KPICreate(KPIBase):
    """Schema para criar KPI."""

    codigo: str = Field(..., min_length=1, max_length=50)
    variaveis: dict = Field(default_factory=dict)
    data_sources: list = Field(default_factory=list)
    meta: KPITarget = Field(default_factory=KPITarget)
    thresholds: KPIThresholds = Field(default_factory=KPIThresholds)
    formatting: KPIFormatting = Field(default_factory=KPIFormatting)
    alert_enabled: bool = Field(default=True)
    icon: str | None = Field(None, max_length=100)
    color: str = Field(default="#1976d2", max_length=20)
    show_in_summary: bool = Field(default=True)
    order: int = Field(default=0, ge=0)
    benchmark_valor: Decimal | None = None
    benchmark_fonte: str | None = Field(None, max_length=200)
    historico_dias: int = Field(default=365, ge=30, le=1825)
    tags: list = Field(default_factory=list)


class KPIUpdate(BaseModel):
    """Schema para atualizar KPI."""

    nome: str | None = Field(None, min_length=1, max_length=200)
    nome_curto: str | None = Field(None, max_length=50)
    descricao: str | None = Field(None, max_length=2000)
    categoria: KPICategory | None = None
    status: KPIStatus | None = None
    frequencia: KPIFrequency | None = None
    formula: str | None = None
    formula_descricao: str | None = None
    variaveis: dict | None = None
    data_sources: list | None = None
    meta: KPITarget | None = None
    thresholds: KPIThresholds | None = None
    formatting: KPIFormatting | None = None
    alert_enabled: bool | None = None
    icon: str | None = Field(None, max_length=100)
    color: str | None = Field(None, max_length=20)
    show_in_summary: bool | None = None
    order: int | None = Field(None, ge=0)
    benchmark_valor: Decimal | None = None
    benchmark_fonte: str | None = Field(None, max_length=200)
    historico_dias: int | None = Field(None, ge=30, le=1825)
    tags: list | None = None


class KPIResponse(KPIBase):
    """Schema de resposta de KPI."""

    id: UUID
    condominio_id: UUID
    codigo: str
    status: KPIStatus
    variaveis: dict = Field(default_factory=dict)
    data_sources: list = Field(default_factory=list)
    valor_atual: Decimal | None = None
    valor_anterior: Decimal | None = None
    variacao_percentual: Decimal | None = None
    trend: KPITrend | None = None
    ultimo_calculo_at: datetime | None = None
    meta_valor: Decimal | None = None
    meta_minimo: Decimal | None = None
    meta_maximo: Decimal | None = None
    meta_atingida: bool = False
    meta_percentual: Decimal | None = None
    threshold_warning_min: Decimal | None = None
    threshold_warning_max: Decimal | None = None
    threshold_critical_min: Decimal | None = None
    threshold_critical_max: Decimal | None = None
    alert_level: AlertLevel = AlertLevel.NORMAL
    alert_message: str | None = None
    alert_enabled: bool = True
    unidade: str = "R$"
    formato: str = "currency"
    casas_decimais: int = 2
    is_percentage: bool = False
    is_inverted: bool = False
    icon: str | None = None
    color: str = "#1976d2"
    show_in_summary: bool = True
    order: int = 0
    benchmark_valor: Decimal | None = None
    benchmark_fonte: str | None = None
    historico_dias: int = 365
    tags: list = Field(default_factory=list)
    is_active: bool = True
    is_on_target: bool = False
    progress_to_target: Decimal = Decimal("0")
    is_improving: bool = False
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class KPIValue(BaseModel):
    """Valor calculado do KPI."""

    kpi_id: UUID
    codigo: str
    nome: str
    valor: Decimal
    valor_anterior: Decimal | None = None
    variacao: Decimal | None = None
    trend: str | None = None
    meta: Decimal | None = None
    meta_atingida: bool = False
    alert_level: str = "NORMAL"
    formatted_value: str
    color: str
    calculated_at: datetime


class KPIHistoryEntry(BaseModel):
    """Entrada do historico de KPI."""

    date: datetime
    value: Decimal


class KPIHistory(BaseModel):
    """Historico de valores do KPI."""

    kpi_id: UUID
    codigo: str
    nome: str
    entries: list[KPIHistoryEntry]
    min_value: Decimal | None = None
    max_value: Decimal | None = None
    avg_value: Decimal | None = None
    trend: str | None = None
    period_days: int


class KPIFilters(BaseModel):
    """Filtros para busca de KPIs."""

    categoria: KPICategory | None = None
    status: KPIStatus | None = None
    frequencia: KPIFrequency | None = None
    alert_level: AlertLevel | None = None
    show_in_summary: bool | None = None
    search: str | None = Field(None, max_length=200)
    tags: list[str] | None = None


class KPISummary(BaseModel):
    """Resumo de KPIs."""

    total: int = 0
    active: int = 0
    on_target: int = 0
    improving: int = 0
    warning: int = 0
    critical: int = 0
    by_category: dict = Field(default_factory=dict)
    by_trend: dict = Field(default_factory=dict)
    top_performers: list[dict] = Field(default_factory=list)
    needs_attention: list[dict] = Field(default_factory=list)


class KPICalculate(BaseModel):
    """Solicitar calculo de KPI."""

    kpi_ids: list[UUID] | None = None
    force_refresh: bool = Field(default=False)
    save_history: bool = Field(default=True)


class KPIBenchmark(BaseModel):
    """Comparacao com benchmark."""

    kpi_id: UUID
    valor_atual: Decimal
    benchmark_valor: Decimal
    diferenca: Decimal
    diferenca_percentual: Decimal
    status: str
    fonte: str | None = None
