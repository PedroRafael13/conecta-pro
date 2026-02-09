"""Schemas Pydantic para ScheduledReport."""

from datetime import datetime, time
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from modules.hr.analytics_dashboard.models import (
    DeliveryMethod,
    ReportFormat,
    ReportStatus,
    ReportType,
    ScheduleFrequency,
)


class ScheduledReportBase(BaseModel):
    """Schema base para relatório agendado."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    report_type: ReportType = ReportType.ATTENDANCE


class ScheduledReportCreate(ScheduledReportBase):
    """Schema para criação de relatório agendado."""

    # Configuração do relatório
    template_id: UUID | None = None
    report_config: dict | None = None
    columns: list[str] | None = None
    filters: dict | None = None
    grouping: list[str] | None = None
    sorting: list[dict] | None = None

    # Período dos dados
    period_type: str = Field(
        default="previous_month",
        pattern=("^(previous_day|previous_week|previous_month|previous_quarter|custom|rolling_\\d+_days)$"),
    )
    custom_period_start: datetime | None = None
    custom_period_end: datetime | None = None
    rolling_days: int | None = Field(None, ge=1, le=365)

    # Formato
    output_format: ReportFormat = ReportFormat.PDF
    include_charts: bool = True
    include_summary: bool = True
    language: str = Field(default="pt-BR", pattern="^[a-z]{2}-[A-Z]{2}$")

    # Agendamento
    frequency: ScheduleFrequency = ScheduleFrequency.MONTHLY
    schedule_time: time = Field(default=time(6, 0))
    schedule_day: int | None = Field(None, ge=1, le=31)
    schedule_month: int | None = Field(None, ge=1, le=12)
    timezone: str = Field(default="America/Sao_Paulo")

    # Entrega
    delivery_method: DeliveryMethod = DeliveryMethod.EMAIL
    recipients: list[EmailStr] = Field(..., min_length=1)
    cc_recipients: list[EmailStr] | None = None
    email_subject: str | None = Field(None, max_length=200)
    email_body: str | None = Field(None, max_length=2000)

    # Configuração alternativa
    sftp_config: dict | None = None
    webhook_url: str | None = None
    storage_path: str | None = None

    # Limites
    end_date: datetime | None = None
    max_runs: int | None = Field(None, ge=1)

    # Notificações
    notify_on_success: bool = False
    notify_on_failure: bool = True
    notification_recipients: list[EmailStr] | None = None

    tags: list[str] | None = None
    settings: dict | None = None

    @field_validator("schedule_day")
    @classmethod
    def validate_schedule_day(cls, v, info):
        """Valida dia do agendamento baseado na frequência."""
        frequency = info.data.get("frequency")
        if frequency == ScheduleFrequency.WEEKLY and v is not None:
            if v < 0 or v > 6:
                raise ValueError("Para frequência semanal, schedule_day deve ser 0-6")
        return v


class ScheduledReportUpdate(BaseModel):
    """Schema para atualização de relatório agendado."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    report_type: ReportType | None = None

    report_config: dict | None = None
    columns: list[str] | None = None
    filters: dict | None = None
    grouping: list[str] | None = None

    period_type: str | None = None
    custom_period_start: datetime | None = None
    custom_period_end: datetime | None = None

    output_format: ReportFormat | None = None
    include_charts: bool | None = None
    include_summary: bool | None = None

    frequency: ScheduleFrequency | None = None
    schedule_time: time | None = None
    schedule_day: int | None = None

    delivery_method: DeliveryMethod | None = None
    recipients: list[EmailStr] | None = None
    cc_recipients: list[EmailStr] | None = None
    email_subject: str | None = None
    email_body: str | None = None

    status: ReportStatus | None = None

    end_date: datetime | None = None
    max_runs: int | None = None

    notify_on_success: bool | None = None
    notify_on_failure: bool | None = None

    tags: list[str] | None = None
    settings: dict | None = None


class ScheduledReportResponse(ScheduledReportBase):
    """Schema de resposta de relatório agendado."""

    id: UUID
    condominio_id: UUID
    owner_id: UUID

    template_id: UUID | None = None
    report_config: dict | None = None
    columns: list[str] | None = None
    filters: dict | None = None

    period_type: str
    custom_period_start: datetime | None = None
    custom_period_end: datetime | None = None

    output_format: str
    include_charts: bool
    include_summary: bool
    language: str

    frequency: str
    schedule_time: time
    schedule_day: int | None = None
    timezone: str

    next_run_at: datetime | None = None
    last_run_at: datetime | None = None

    delivery_method: str
    recipients: list[str]
    cc_recipients: list[str] | None = None

    run_count: int
    success_count: int
    failure_count: int
    success_rate: float
    last_status: str | None = None
    last_error: str | None = None

    status: str

    end_date: datetime | None = None
    max_runs: int | None = None

    tags: list[str] | None = None

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReportRunRequest(BaseModel):
    """Schema para execução manual de relatório."""

    report_id: UUID
    period_start: datetime | None = None
    period_end: datetime | None = None
    output_format: ReportFormat | None = None
    send_email: bool = True
    download_only: bool = False


class ReportRunResponse(BaseModel):
    """Schema de resposta de execução de relatório."""

    report_id: UUID
    run_id: UUID
    status: str
    file_path: str | None = None
    file_size_bytes: int | None = None
    download_url: str | None = None
    generation_time_ms: int
    started_at: datetime
    completed_at: datetime


class ReportHistoryItem(BaseModel):
    """Schema para item do histórico de execuções."""

    run_id: UUID
    status: str
    file_path: str | None = None
    file_size_bytes: int | None = None
    generation_time_ms: int | None = None
    error_message: str | None = None
    executed_at: datetime


class ReportHistoryResponse(BaseModel):
    """Schema de resposta do histórico de execuções."""

    report_id: UUID
    report_name: str
    total_runs: int
    success_count: int
    failure_count: int
    history: list[ReportHistoryItem]


class ReportTemplateCreate(BaseModel):
    """Schema para criação de template de relatório."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    report_type: ReportType
    config: dict
    columns: list[str]
    grouping: list[str] | None = None
    sorting: list[dict] | None = None
    header_template: str | None = None
    footer_template: str | None = None
    is_public: bool = False


class ReportTemplateResponse(BaseModel):
    """Schema de resposta de template de relatório."""

    id: UUID
    name: str
    description: str | None = None
    report_type: str
    config: dict
    columns: list[str]
    is_public: bool
    usage_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
