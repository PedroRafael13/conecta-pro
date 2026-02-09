"""Schemas de Relatorio Agendado Financeiro."""

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from modules.financial.bi_dashboard.models.scheduled_report import (
    DeliveryMethod,
    ReportFormat,
    ReportFrequency,
    ReportStatus,
    ReportType,
)


class ReportBase(BaseModel):
    """Schema base de Relatorio."""

    nome: str = Field(..., min_length=1, max_length=200)
    descricao: str | None = Field(None, max_length=2000)
    tipo: ReportType = Field(default=ReportType.CASH_FLOW)
    formato: ReportFormat = Field(default=ReportFormat.PDF)


class ReportScheduleConfig(BaseModel):
    """Configuracao de agendamento."""

    frequencia: ReportFrequency = Field(default=ReportFrequency.MONTHLY)
    hora_execucao: time = Field(default_factory=lambda: time(8, 0))
    dia_semana: int | None = Field(None, ge=0, le=6)
    dia_mes: int | None = Field(None, ge=1, le=31)
    timezone: str = Field(default="America/Sao_Paulo", max_length=50)


class ReportPeriodConfig(BaseModel):
    """Configuracao de periodo de dados."""

    periodo_tipo: str = Field(default="last_month", max_length=50)
    periodo_dias: int = Field(default=30, ge=1, le=365)
    data_inicio: date | None = None
    data_fim: date | None = None


class ReportDeliveryConfig(BaseModel):
    """Configuracao de entrega."""

    metodo: DeliveryMethod = Field(default=DeliveryMethod.EMAIL)
    destinatarios_email: list[EmailStr] = Field(default_factory=list)
    webhook_url: str | None = Field(None, max_length=500)
    storage_path: str | None = Field(None, max_length=500)
    notificar_sucesso: bool = Field(default=True)
    notificar_erro: bool = Field(default=True)
    notificar_email: EmailStr | None = None


class ReportTemplateConfig(BaseModel):
    """Configuracao de template."""

    template_id: str | None = Field(None, max_length=100)
    logo_url: str | None = Field(None, max_length=500)
    header_text: str | None = None
    footer_text: str | None = None
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
    custom_query: str | None = None
    valido_de: date = Field(default_factory=date.today)
    valido_ate: date | None = None
    tags: list = Field(default_factory=list)


class ReportUpdate(BaseModel):
    """Schema para atualizar Relatorio."""

    nome: str | None = Field(None, min_length=1, max_length=200)
    descricao: str | None = Field(None, max_length=2000)
    tipo: ReportType | None = None
    formato: ReportFormat | None = None
    status: ReportStatus | None = None
    schedule: ReportScheduleConfig | None = None
    period: ReportPeriodConfig | None = None
    delivery: ReportDeliveryConfig | None = None
    template: ReportTemplateConfig | None = None
    filtros: dict | None = None
    ordenacao: list | None = None
    agrupamento: list | None = None
    custom_query: str | None = None
    valido_ate: date | None = None
    tags: list | None = None


class ReportResponse(ReportBase):
    """Schema de resposta de Relatorio."""

    id: UUID
    condominio_id: UUID
    codigo: str
    status: ReportStatus
    frequencia: ReportFrequency
    hora_execucao: time
    dia_semana: int | None = None
    dia_mes: int | None = None
    timezone: str = "America/Sao_Paulo"
    periodo_tipo: str = "last_month"
    periodo_dias: int = 30
    data_inicio: date | None = None
    data_fim: date | None = None
    valido_de: date
    valido_ate: date | None = None
    metodo_entrega: DeliveryMethod
    destinatarios_email: list = Field(default_factory=list)
    webhook_url: str | None = None
    storage_path: str | None = None
    template_id: str | None = None
    show_charts: bool = True
    show_summary: bool = True
    paper_size: str = "A4"
    orientation: str = "portrait"
    filtros: dict = Field(default_factory=dict)
    ordenacao: list = Field(default_factory=list)
    agrupamento: list = Field(default_factory=list)
    proxima_execucao_at: datetime | None = None
    ultima_execucao_at: datetime | None = None
    ultima_execucao_status: str | None = None
    ultima_execucao_erro: str | None = None
    total_execucoes: int = 0
    total_erros: int = 0
    ultimo_arquivo_url: str | None = None
    ultimo_arquivo_tamanho: int | None = None
    is_active: bool = True
    is_due: bool = False
    success_rate: Decimal = Decimal("100")
    tags: list = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ReportSchedule(BaseModel):
    """Informacoes de agendamento."""

    report_id: UUID
    proxima_execucao: datetime | None = None
    ultima_execucao: datetime | None = None
    frequencia: str
    is_due: bool
    time_until_next: int | None = None


class ReportExecution(BaseModel):
    """Resultado de execucao de relatorio."""

    report_id: UUID
    success: bool
    executed_at: datetime
    duration_ms: int
    file_url: str | None = None
    file_size: int | None = None
    error: str | None = None
    recipients_notified: int = 0


class ReportFilters(BaseModel):
    """Filtros para busca de Relatorios."""

    tipo: ReportType | None = None
    formato: ReportFormat | None = None
    status: ReportStatus | None = None
    frequencia: ReportFrequency | None = None
    metodo_entrega: DeliveryMethod | None = None
    is_due: bool | None = None
    search: str | None = Field(None, max_length=200)
    tags: list[str] | None = None
    created_after: datetime | None = None
    created_before: datetime | None = None


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
    override_period: ReportPeriodConfig | None = None
    override_recipients: list[EmailStr] | None = None
    save_file: bool = Field(default=True)
    send_notification: bool = Field(default=True)


class ReportPreview(BaseModel):
    """Preview de relatorio."""

    report_id: UUID
    period: ReportPeriodConfig
    data: Any
    row_count: int
    generated_at: datetime
