"""Schemas de KPI Financeiro."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from modules.financial.bi_dashboard.models.kpi_definition import (
    KPICategory,
    KPIFrequency,
    KPIStatus,
    KPITrend,
    AlertLevel,
)


class KPIBase(BaseModel):
    """Schema base de KPI."""

    nome: str = Field(..., min_length=1, max_length=200)
    nome_curto: Optional[str] = Field(None, max_length=50)
    descricao: Optional[str] = Field(None, max_length=2000)
    categoria: KPICategory = Field(default=KPICategory.CUSTOM)
    frequencia: KPIFrequency = Field(default=KPIFrequency.DAILY)
    formula: str = Field(..., min_length=1)
    formula_descricao: Optional[str] = None


class KPIThresholds(BaseModel):
    """Thresholds do KPI."""

    warning_min: Optional[Decimal] = None
    warning_max: Optional[Decimal] = None
    critical_min: Optional[Decimal] = None
    critical_max: Optional[Decimal] = None


class KPIFormatting(BaseModel):
    """Formatacao do KPI."""

    unidade: str = Field(default="R$", max_length=20)
    formato: str = Field(default="currency", max_length=50)
    casas_decimais: int = Field(default=2, ge=0, le=8)
    is_percentage: bool = Field(default=False)
    is_inverted: bool = Field(default=False)


class KPITarget(BaseModel):
    """Meta do KPI."""

    valor: Optional[Decimal] = None
    minimo: Optional[Decimal] = None
    maximo: Optional[Decimal] = None


class KPICreate(KPIBase):
    """Schema para criar KPI."""

    codigo: str = Field(..., min_length=1, max_length=50)
    variaveis: dict = Field(default_factory=dict)
    data_sources: list = Field(default_factory=list)
    meta: KPITarget = Field(default_factory=KPITarget)
    thresholds: KPIThresholds = Field(default_factory=KPIThresholds)
    formatting: KPIFormatting = Field(default_factory=KPIFormatting)
    alert_enabled: bool = Field(default=True)
    icon: Optional[str] = Field(None, max_length=100)
    color: str = Field(default="#1976d2", max_length=20)
    show_in_summary: bool = Field(default=True)
    order: int = Field(default=0, ge=0)
    benchmark_valor: Optional[Decimal] = None
    benchmark_fonte: Optional[str] = Field(None, max_length=200)
    historico_dias: int = Field(default=365, ge=30, le=1825)
    tags: list = Field(default_factory=list)


class KPIUpdate(BaseModel):
    """Schema para atualizar KPI."""

    nome: Optional[str] = Field(None, min_length=1, max_length=200)
    nome_curto: Optional[str] = Field(None, max_length=50)
    descricao: Optional[str] = Field(None, max_length=2000)
    categoria: Optional[KPICategory] = None
    status: Optional[KPIStatus] = None
    frequencia: Optional[KPIFrequency] = None
    formula: Optional[str] = None
    formula_descricao: Optional[str] = None
    variaveis: Optional[dict] = None
    data_sources: Optional[list] = None
    meta: Optional[KPITarget] = None
    thresholds: Optional[KPIThresholds] = None
    formatting: Optional[KPIFormatting] = None
    alert_enabled: Optional[bool] = None
    icon: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, max_length=20)
    show_in_summary: Optional[bool] = None
    order: Optional[int] = Field(None, ge=0)
    benchmark_valor: Optional[Decimal] = None
    benchmark_fonte: Optional[str] = Field(None, max_length=200)
    historico_dias: Optional[int] = Field(None, ge=30, le=1825)
    tags: Optional[list] = None


class KPIResponse(KPIBase):
    """Schema de resposta de KPI."""

    id: UUID
    condominio_id: UUID
    codigo: str
    status: KPIStatus
    variaveis: dict = Field(default_factory=dict)
    data_sources: list = Field(default_factory=list)
    valor_atual: Optional[Decimal] = None
    valor_anterior: Optional[Decimal] = None
    variacao_percentual: Optional[Decimal] = None
    trend: Optional[KPITrend] = None
    ultimo_calculo_at: Optional[datetime] = None
    meta_valor: Optional[Decimal] = None
    meta_minimo: Optional[Decimal] = None
    meta_maximo: Optional[Decimal] = None
    meta_atingida: bool = False
    meta_percentual: Optional[Decimal] = None
    threshold_warning_min: Optional[Decimal] = None
    threshold_warning_max: Optional[Decimal] = None
    threshold_critical_min: Optional[Decimal] = None
    threshold_critical_max: Optional[Decimal] = None
    alert_level: AlertLevel = AlertLevel.NORMAL
    alert_message: Optional[str] = None
    alert_enabled: bool = True
    unidade: str = "R$"
    formato: str = "currency"
    casas_decimais: int = 2
    is_percentage: bool = False
    is_inverted: bool = False
    icon: Optional[str] = None
    color: str = "#1976d2"
    show_in_summary: bool = True
    order: int = 0
    benchmark_valor: Optional[Decimal] = None
    benchmark_fonte: Optional[str] = None
    historico_dias: int = 365
    tags: list = Field(default_factory=list)
    is_active: bool = True
    is_on_target: bool = False
    progress_to_target: Decimal = Decimal("0")
    is_improving: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class KPIValue(BaseModel):
    """Valor calculado do KPI."""

    kpi_id: UUID
    codigo: str
    nome: str
    valor: Decimal
    valor_anterior: Optional[Decimal] = None
    variacao: Optional[Decimal] = None
    trend: Optional[str] = None
    meta: Optional[Decimal] = None
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
    min_value: Optional[Decimal] = None
    max_value: Optional[Decimal] = None
    avg_value: Optional[Decimal] = None
    trend: Optional[str] = None
    period_days: int


class KPIFilters(BaseModel):
    """Filtros para busca de KPIs."""

    categoria: Optional[KPICategory] = None
    status: Optional[KPIStatus] = None
    frequencia: Optional[KPIFrequency] = None
    alert_level: Optional[AlertLevel] = None
    show_in_summary: Optional[bool] = None
    search: Optional[str] = Field(None, max_length=200)
    tags: Optional[list[str]] = None


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

    kpi_ids: Optional[list[UUID]] = None
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
    fonte: Optional[str] = None
