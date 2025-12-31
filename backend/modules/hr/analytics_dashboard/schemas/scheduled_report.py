"""Schemas Pydantic para ScheduledReport."""

from datetime import datetime, time
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, field_validator

from modules.hr.analytics_dashboard.models import (
    ReportType,
    ReportFormat,
    ScheduleFrequency,
    DeliveryMethod,
    ReportStatus,
)


class ScheduledReportBase(BaseModel):
    """Schema base para relatório agendado."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    report_type: ReportType = ReportType.ATTENDANCE


class ScheduledReportCreate(ScheduledReportBase):
    """Schema para criação de relatório agendado."""

    # Configuração do relatório
    template_id: Optional[UUID] = None
    report_config: Optional[dict] = None
    columns: Optional[List[str]] = None
    filters: Optional[dict] = None
    grouping: Optional[List[str]] = None
    sorting: Optional[List[dict]] = None

    # Período dos dados
    period_type: str = Field(
        default="previous_month",
        pattern="^(previous_day|previous_week|previous_month|previous_quarter|custom|rolling_\\d+_days)$",
    )
    custom_period_start: Optional[datetime] = None
    custom_period_end: Optional[datetime] = None
    rolling_days: Optional[int] = Field(None, ge=1, le=365)

    # Formato
    output_format: ReportFormat = ReportFormat.PDF
    include_charts: bool = True
    include_summary: bool = True
    language: str = Field(default="pt-BR", pattern="^[a-z]{2}-[A-Z]{2}$")

    # Agendamento
    frequency: ScheduleFrequency = ScheduleFrequency.MONTHLY
    schedule_time: time = Field(default=time(6, 0))
    schedule_day: Optional[int] = Field(None, ge=1, le=31)
    schedule_month: Optional[int] = Field(None, ge=1, le=12)
    timezone: str = Field(default="America/Sao_Paulo")

    # Entrega
    delivery_method: DeliveryMethod = DeliveryMethod.EMAIL
    recipients: List[EmailStr] = Field(..., min_length=1)
    cc_recipients: Optional[List[EmailStr]] = None
    email_subject: Optional[str] = Field(None, max_length=200)
    email_body: Optional[str] = Field(None, max_length=2000)

    # Configuração alternativa
    sftp_config: Optional[dict] = None
    webhook_url: Optional[str] = None
    storage_path: Optional[str] = None

    # Limites
    end_date: Optional[datetime] = None
    max_runs: Optional[int] = Field(None, ge=1)

    # Notificações
    notify_on_success: bool = False
    notify_on_failure: bool = True
    notification_recipients: Optional[List[EmailStr]] = None

    tags: Optional[List[str]] = None
    settings: Optional[dict] = None

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

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    report_type: Optional[ReportType] = None

    report_config: Optional[dict] = None
    columns: Optional[List[str]] = None
    filters: Optional[dict] = None
    grouping: Optional[List[str]] = None

    period_type: Optional[str] = None
    custom_period_start: Optional[datetime] = None
    custom_period_end: Optional[datetime] = None

    output_format: Optional[ReportFormat] = None
    include_charts: Optional[bool] = None
    include_summary: Optional[bool] = None

    frequency: Optional[ScheduleFrequency] = None
    schedule_time: Optional[time] = None
    schedule_day: Optional[int] = None

    delivery_method: Optional[DeliveryMethod] = None
    recipients: Optional[List[EmailStr]] = None
    cc_recipients: Optional[List[EmailStr]] = None
    email_subject: Optional[str] = None
    email_body: Optional[str] = None

    status: Optional[ReportStatus] = None

    end_date: Optional[datetime] = None
    max_runs: Optional[int] = None

    notify_on_success: Optional[bool] = None
    notify_on_failure: Optional[bool] = None

    tags: Optional[List[str]] = None
    settings: Optional[dict] = None


class ScheduledReportResponse(ScheduledReportBase):
    """Schema de resposta de relatório agendado."""

    id: UUID
    condominio_id: UUID
    owner_id: UUID

    template_id: Optional[UUID] = None
    report_config: Optional[dict] = None
    columns: Optional[List[str]] = None
    filters: Optional[dict] = None

    period_type: str
    custom_period_start: Optional[datetime] = None
    custom_period_end: Optional[datetime] = None

    output_format: str
    include_charts: bool
    include_summary: bool
    language: str

    frequency: str
    schedule_time: time
    schedule_day: Optional[int] = None
    timezone: str

    next_run_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None

    delivery_method: str
    recipients: List[str]
    cc_recipients: Optional[List[str]] = None

    run_count: int
    success_count: int
    failure_count: int
    success_rate: float
    last_status: Optional[str] = None
    last_error: Optional[str] = None

    status: str

    end_date: Optional[datetime] = None
    max_runs: Optional[int] = None

    tags: Optional[List[str]] = None

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReportRunRequest(BaseModel):
    """Schema para execução manual de relatório."""

    report_id: UUID
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    output_format: Optional[ReportFormat] = None
    send_email: bool = True
    download_only: bool = False


class ReportRunResponse(BaseModel):
    """Schema de resposta de execução de relatório."""

    report_id: UUID
    run_id: UUID
    status: str
    file_path: Optional[str] = None
    file_size_bytes: Optional[int] = None
    download_url: Optional[str] = None
    generation_time_ms: int
    started_at: datetime
    completed_at: datetime


class ReportHistoryItem(BaseModel):
    """Schema para item do histórico de execuções."""

    run_id: UUID
    status: str
    file_path: Optional[str] = None
    file_size_bytes: Optional[int] = None
    generation_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    executed_at: datetime


class ReportHistoryResponse(BaseModel):
    """Schema de resposta do histórico de execuções."""

    report_id: UUID
    report_name: str
    total_runs: int
    success_count: int
    failure_count: int
    history: List[ReportHistoryItem]


class ReportTemplateCreate(BaseModel):
    """Schema para criação de template de relatório."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    report_type: ReportType
    config: dict
    columns: List[str]
    grouping: Optional[List[str]] = None
    sorting: Optional[List[dict]] = None
    header_template: Optional[str] = None
    footer_template: Optional[str] = None
    is_public: bool = False


class ReportTemplateResponse(BaseModel):
    """Schema de resposta de template de relatório."""

    id: UUID
    name: str
    description: Optional[str] = None
    report_type: str
    config: dict
    columns: List[str]
    is_public: bool
    usage_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
