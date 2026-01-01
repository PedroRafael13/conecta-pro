"""Schemas de Relatorio Agendado Financeiro."""

from datetime import datetime, date, time
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, EmailStr

from modules.financial.bi_dashboard.models.scheduled_report import (
    ReportType,
    ReportFormat,
    ReportFrequency,
    ReportStatus,
    DeliveryMethod,
)


class ReportBase(BaseModel):
    """Schema base de Relatorio."""

    nome: str = Field(..., min_length=1, max_length=200)
    descricao: Optional[str] = Field(None, max_length=2000)
    tipo: ReportType = Field(default=ReportType.CASH_FLOW)
    formato: ReportFormat = Field(default=ReportFormat.PDF)


class ReportScheduleConfig(BaseModel):
    """Configuracao de agendamento."""

    frequencia: ReportFrequency = Field(default=ReportFrequency.MONTHLY)
    hora_execucao: time = Field(default_factory=lambda: time(8, 0))
    dia_semana: Optional[int] = Field(None, ge=0, le=6)
    dia_mes: Optional[int] = Field(None, ge=1, le=31)
    timezone: str = Field(default="America/Sao_Paulo", max_length=50)


class ReportPeriodConfig(BaseModel):
    """Configuracao de periodo de dados."""

    periodo_tipo: str = Field(default="last_month", max_length=50)
    periodo_dias: int = Field(default=30, ge=1, le=365)
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None


class ReportDeliveryConfig(BaseModel):
    """Configuracao de entrega."""

    metodo: DeliveryMethod = Field(default=DeliveryMethod.EMAIL)
    destinatarios_email: list[EmailStr] = Field(default_factory=list)
    webhook_url: Optional[str] = Field(None, max_length=500)
    storage_path: Optional[str] = Field(None, max_length=500)
    notificar_sucesso: bool = Field(default=True)
    notificar_erro: bool = Field(default=True)
    notificar_email: Optional[EmailStr] = None


class ReportTemplateConfig(BaseModel):
    """Configuracao de template."""

    template_id: Optional[str] = Field(None, max_length=100)
    logo_url: Optional[str] = Field(None, max_length=500)
    header_text: Optional[str] = None
    footer_text: Optional[str] = None
    show_charts: bool = Field(default=True)
    show_summary: bool = Field(default=True)
    paper_size: str = Field(default="A4", max_length=20)
    orientation: str = Field(default="portrait", max_length=20)


class ReportCreate(ReportBase):
    """Schema para criar Relatorio."""

    codigo: str = Field(..., min_length=1, max_length=50)
    schedule: ReportScheduleConfig = Field(default_factory=ReportScheduleConfig)
    period: ReportPeriodConfig = Field(default_factory=ReportPeriodConfig)
    delivery: ReportDeliveryConfig = Field(default_factory=ReportDeliveryConfig)
    template: ReportTemplateConfig = Field(default_factory=ReportTemplateConfig)
    filtros: dict = Field(default_factory=dict)
    ordenacao: list = Field(default_factory=list)
    agrupamento: list = Field(default_factory=list)
    custom_query: Optional[str] = None
    valido_de: date = Field(default_factory=date.today)
    valido_ate: Optional[date] = None
    tags: list = Field(default_factory=list)


class ReportUpdate(BaseModel):
    """Schema para atualizar Relatorio."""

    nome: Optional[str] = Field(None, min_length=1, max_length=200)
    descricao: Optional[str] = Field(None, max_length=2000)
    tipo: Optional[ReportType] = None
    formato: Optional[ReportFormat] = None
    status: Optional[ReportStatus] = None
    schedule: Optional[ReportScheduleConfig] = None
    period: Optional[ReportPeriodConfig] = None
    delivery: Optional[ReportDeliveryConfig] = None
    template: Optional[ReportTemplateConfig] = None
    filtros: Optional[dict] = None
    ordenacao: Optional[list] = None
    agrupamento: Optional[list] = None
    custom_query: Optional[str] = None
    valido_ate: Optional[date] = None
    tags: Optional[list] = None


class ReportResponse(ReportBase):
    """Schema de resposta de Relatorio."""

    id: UUID
    condominio_id: UUID
    codigo: str
    status: ReportStatus
    frequencia: ReportFrequency
    hora_execucao: time
    dia_semana: Optional[int] = None
    dia_mes: Optional[int] = None
    timezone: str = "America/Sao_Paulo"
    periodo_tipo: str = "last_month"
    periodo_dias: int = 30
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    valido_de: date
    valido_ate: Optional[date] = None
    metodo_entrega: DeliveryMethod
    destinatarios_email: list = Field(default_factory=list)
    webhook_url: Optional[str] = None
    storage_path: Optional[str] = None
    template_id: Optional[str] = None
    show_charts: bool = True
    show_summary: bool = True
    paper_size: str = "A4"
    orientation: str = "portrait"
    filtros: dict = Field(default_factory=dict)
    ordenacao: list = Field(default_factory=list)
    agrupamento: list = Field(default_factory=list)
    proxima_execucao_at: Optional[datetime] = None
    ultima_execucao_at: Optional[datetime] = None
    ultima_execucao_status: Optional[str] = None
    ultima_execucao_erro: Optional[str] = None
    total_execucoes: int = 0
    total_erros: int = 0
    ultimo_arquivo_url: Optional[str] = None
    ultimo_arquivo_tamanho: Optional[int] = None
    is_active: bool = True
    is_due: bool = False
    success_rate: Decimal = Decimal("100")
    tags: list = Field(default_factory=list)
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ReportSchedule(BaseModel):
    """Informacoes de agendamento."""

    report_id: UUID
    proxima_execucao: Optional[datetime] = None
    ultima_execucao: Optional[datetime] = None
    frequencia: str
    is_due: bool
    time_until_next: Optional[int] = None


class ReportExecution(BaseModel):
    """Resultado de execucao de relatorio."""

    report_id: UUID
    success: bool
    executed_at: datetime
    duration_ms: int
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    error: Optional[str] = None
    recipients_notified: int = 0


class ReportFilters(BaseModel):
    """Filtros para busca de Relatorios."""

    tipo: Optional[ReportType] = None
    formato: Optional[ReportFormat] = None
    status: Optional[ReportStatus] = None
    frequencia: Optional[ReportFrequency] = None
    metodo_entrega: Optional[DeliveryMethod] = None
    is_due: Optional[bool] = None
    search: Optional[str] = Field(None, max_length=200)
    tags: Optional[list[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


class ReportStats(BaseModel):
    """Estatisticas de Relatorios."""

    total: int = 0
    active: int = 0
    paused: int = 0
    expired: int = 0
    due_today: int = 0
    total_executions: int = 0
    total_errors: int = 0
    success_rate: Decimal = Decimal("100")
    by_type: dict = Field(default_factory=dict)
    by_format: dict = Field(default_factory=dict)
    by_frequency: dict = Field(default_factory=dict)


class ReportExecuteNow(BaseModel):
    """Executar relatorio imediatamente."""

    report_id: UUID
    override_period: Optional[ReportPeriodConfig] = None
    override_recipients: Optional[list[EmailStr]] = None
    save_file: bool = Field(default=True)
    send_notification: bool = Field(default=True)


class ReportPreview(BaseModel):
    """Preview de relatorio."""

    report_id: UUID
    period: ReportPeriodConfig
    data: Any
    row_count: int
    generated_at: datetime
