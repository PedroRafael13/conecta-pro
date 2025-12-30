"""Schemas de Agendamento de Visita."""

from datetime import date, datetime, time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from modules.visitors.models.schedule import SchedulePriority, ScheduleStatus


class ScheduleBase(BaseModel):
    """Schema base de agendamento."""

    visitor_name: str = Field(..., min_length=2, max_length=200)
    visitor_document: Optional[str] = Field(None, max_length=50)
    visitor_phone: Optional[str] = Field(None, max_length=20)
    visitor_email: Optional[EmailStr] = None
    visitor_company: Optional[str] = Field(None, max_length=200)
    condominium_id: str = Field(..., max_length=50)
    condominium_name: Optional[str] = Field(None, max_length=200)
    unit_id: Optional[str] = Field(None, max_length=50)
    unit_number: Optional[str] = Field(None, max_length=20)
    block: Optional[str] = Field(None, max_length=20)
    resident_id: Optional[str] = Field(None, max_length=50)
    resident_name: Optional[str] = Field(None, max_length=200)
    purpose: str = Field(..., min_length=5, max_length=500)
    description: Optional[str] = None
    notes: Optional[str] = None


class ScheduleCreate(ScheduleBase):
    """Schema para criação de agendamento."""

    visitor_id: Optional[UUID] = None
    priority: SchedulePriority = Field(default=SchedulePriority.NORMAL)
    scheduled_date: date
    scheduled_time_from: Optional[time] = None
    scheduled_time_until: Optional[time] = None
    estimated_duration_minutes: Optional[int] = Field(None, ge=1)
    has_vehicle: bool = False
    vehicle_plate: Optional[str] = Field(None, max_length=10)
    vehicle_model: Optional[str] = Field(None, max_length=100)
    needs_parking: bool = False
    companions_count: int = Field(default=0, ge=0)
    companions_names: Optional[list[str]] = Field(default_factory=list)
    confirmation_required: bool = True
    requires_approval: bool = False
    notification_channels: Optional[list[str]] = Field(default_factory=list)
    created_by_id: Optional[str] = Field(None, max_length=50)
    created_by_name: Optional[str] = Field(None, max_length=200)

    @field_validator("scheduled_date")
    @classmethod
    def validate_scheduled_date(cls, v: date) -> date:
        """Valida que a data não é passada."""
        if v < datetime.utcnow().date():
            raise ValueError("Data do agendamento não pode ser no passado")
        return v

    @field_validator("scheduled_time_until")
    @classmethod
    def validate_time_range(cls, v: Optional[time], info) -> Optional[time]:
        """Valida range de horário."""
        time_from = info.data.get("scheduled_time_from")
        if v and time_from and v <= time_from:
            raise ValueError("Horário final deve ser após o horário inicial")
        return v


class ScheduleUpdate(BaseModel):
    """Schema para atualização de agendamento."""

    visitor_name: Optional[str] = Field(None, min_length=2, max_length=200)
    visitor_document: Optional[str] = Field(None, max_length=50)
    visitor_phone: Optional[str] = Field(None, max_length=20)
    visitor_email: Optional[EmailStr] = None
    visitor_company: Optional[str] = Field(None, max_length=200)
    visitor_id: Optional[UUID] = None
    priority: Optional[SchedulePriority] = None
    unit_id: Optional[str] = Field(None, max_length=50)
    unit_number: Optional[str] = Field(None, max_length=20)
    block: Optional[str] = Field(None, max_length=20)
    resident_id: Optional[str] = Field(None, max_length=50)
    resident_name: Optional[str] = Field(None, max_length=200)
    scheduled_date: Optional[date] = None
    scheduled_time_from: Optional[time] = None
    scheduled_time_until: Optional[time] = None
    estimated_duration_minutes: Optional[int] = Field(None, ge=1)
    purpose: Optional[str] = Field(None, min_length=5, max_length=500)
    description: Optional[str] = None
    notes: Optional[str] = None
    has_vehicle: Optional[bool] = None
    vehicle_plate: Optional[str] = Field(None, max_length=10)
    vehicle_model: Optional[str] = Field(None, max_length=100)
    needs_parking: Optional[bool] = None
    companions_count: Optional[int] = Field(None, ge=0)
    companions_names: Optional[list[str]] = None
    confirmation_required: Optional[bool] = None
    requires_approval: Optional[bool] = None


class ScheduleResponse(BaseModel):
    """Schema de resposta de agendamento."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    visitor_id: Optional[UUID] = None
    visitor_name: str
    visitor_document: Optional[str] = None
    visitor_phone: Optional[str] = None
    visitor_email: Optional[str] = None
    visitor_company: Optional[str] = None
    status: ScheduleStatus
    priority: SchedulePriority
    condominium_id: str
    condominium_name: Optional[str] = None
    unit_id: Optional[str] = None
    unit_number: Optional[str] = None
    block: Optional[str] = None
    resident_id: Optional[str] = None
    resident_name: Optional[str] = None
    scheduled_date: date
    scheduled_time_from: Optional[time] = None
    scheduled_time_until: Optional[time] = None
    estimated_duration_minutes: Optional[int] = None
    purpose: str
    description: Optional[str] = None
    notes: Optional[str] = None
    has_vehicle: bool
    vehicle_plate: Optional[str] = None
    vehicle_model: Optional[str] = None
    needs_parking: bool
    companions_count: int
    companions_names: Optional[list[str]] = None
    confirmation_required: bool
    confirmed_at: Optional[datetime] = None
    confirmed_by_name: Optional[str] = None
    confirmation_code: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    reschedule_count: int
    realized_at: Optional[datetime] = None
    check_in_at: Optional[datetime] = None
    check_out_at: Optional[datetime] = None
    reminder_sent: bool
    requires_approval: bool
    approved_at: Optional[datetime] = None
    approved_by_name: Optional[str] = None
    qr_code: Optional[str] = None
    is_past: bool
    is_today: bool
    is_future: bool
    is_confirmed: bool
    is_pending: bool
    is_cancelled: bool
    is_realized: bool
    can_check_in: bool
    days_until: int
    time_display: str
    status_display: str
    created_at: datetime
    updated_at: datetime


class ScheduleListResponse(BaseModel):
    """Schema de listagem de agendamentos."""

    items: list[ScheduleResponse]
    total: int
    page: int = 1
    page_size: int = 20
    pages: int = 1


class ScheduleConfirm(BaseModel):
    """Schema para confirmação de agendamento."""

    confirmed_by_id: Optional[str] = Field(None, max_length=50)
    confirmed_by_name: Optional[str] = Field(None, max_length=200)


class ScheduleCancel(BaseModel):
    """Schema para cancelamento de agendamento."""

    reason: str = Field(..., min_length=5, max_length=500)
    cancelled_by_id: Optional[str] = Field(None, max_length=50)
    cancelled_by_name: Optional[str] = Field(None, max_length=200)


class ScheduleReschedule(BaseModel):
    """Schema para reagendamento."""

    new_date: date
    new_time_from: Optional[time] = None
    new_time_until: Optional[time] = None
    reason: Optional[str] = Field(None, max_length=500)

    @field_validator("new_date")
    @classmethod
    def validate_new_date(cls, v: date) -> date:
        """Valida que a nova data não é passada."""
        if v < datetime.utcnow().date():
            raise ValueError("Nova data não pode ser no passado")
        return v


class ScheduleFilter(BaseModel):
    """Schema de filtros de agendamento."""

    visitor_id: Optional[UUID] = None
    visitor_name: Optional[str] = None
    condominium_id: Optional[str] = None
    unit_id: Optional[str] = None
    resident_id: Optional[str] = None
    status: Optional[ScheduleStatus] = None
    priority: Optional[SchedulePriority] = None
    scheduled_date: Optional[date] = None
    scheduled_date_from: Optional[date] = None
    scheduled_date_until: Optional[date] = None
    has_vehicle: Optional[bool] = None
    needs_parking: Optional[bool] = None
    confirmation_required: Optional[bool] = None
    is_confirmed: Optional[bool] = None
    requires_approval: Optional[bool] = None
    is_approved: Optional[bool] = None
    is_today: Optional[bool] = None


class ScheduleStats(BaseModel):
    """Schema de estatísticas de agendamentos."""

    total: int = 0
    pending: int = 0
    confirmed: int = 0
    cancelled: int = 0
    realized: int = 0
    no_show: int = 0
    by_status: dict = Field(default_factory=dict)
    by_priority: dict = Field(default_factory=dict)
    by_day_of_week: dict = Field(default_factory=dict)
    by_hour: dict = Field(default_factory=dict)
    avg_duration_minutes: float = 0
    with_vehicle: int = 0
    with_companions: int = 0
    total_companions: int = 0
    reschedule_rate: float = 0
    no_show_rate: float = 0


class ScheduleCalendar(BaseModel):
    """Calendário de agendamentos."""

    date: date
    schedules: list[ScheduleResponse]
    total: int
    pending: int
    confirmed: int


class ScheduleReminder(BaseModel):
    """Schema para envio de lembrete."""

    schedule_id: UUID
    channels: list[str] = Field(default_factory=lambda: ["email"])
    message: Optional[str] = None
