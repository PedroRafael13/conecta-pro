"""Schemas Pydantic para Overtime."""

from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from modules.hr.time_tracking.models import (
    CompensationType,
    OvertimeReason,
    OvertimeStatus,
    OvertimeType,
)


class OvertimeBase(BaseModel):
    """Schema base para Overtime."""

    employee_id: str = Field(..., min_length=1, max_length=50)
    employee_name: str = Field(..., min_length=1, max_length=200)
    overtime_date: date
    start_time: time
    end_time: time

    overtime_type: OvertimeType = OvertimeType.HORA_EXTRA_50
    reason: OvertimeReason = OvertimeReason.DEMANDA_TRABALHO
    reason_description: str | None = Field(None, max_length=500)


class OvertimeCreate(OvertimeBase):
    """Schema para criação de Overtime."""

    employee_registration: str | None = Field(None, max_length=50)
    department_id: str | None = Field(None, max_length=50)
    department_name: str | None = Field(None, max_length=100)

    break_minutes: int = Field(0, ge=0, le=120)

    hourly_rate: Decimal = Field(Decimal("0"), ge=0)

    use_time_bank: bool = False

    work_schedule_id: str | None = Field(None, max_length=50)

    condominium_id: str | None = Field(None, max_length=50)
    condominium_name: str | None = Field(None, max_length=200)
    work_location: str | None = Field(None, max_length=200)

    time_entry_ids: list[str] | None = None

    notes: str | None = None


class OvertimePreApproval(BaseModel):
    """Schema para pré-aprovação."""

    notes: str | None = Field(None, max_length=500)


class OvertimeApproval(BaseModel):
    """Schema para aprovação."""

    approved: bool = True
    notes: str | None = Field(None, max_length=500)


class OvertimeRejection(BaseModel):
    """Schema para rejeição."""

    reason: str = Field(..., min_length=10, max_length=500)


class OvertimeCompensation(BaseModel):
    """Schema para compensação."""

    compensation_type: CompensationType
    compensation_date: date
    minutes: int = Field(..., gt=0)


class OvertimePayment(BaseModel):
    """Schema para pagamento."""

    payment_reference: str | None = Field(None, max_length=100)
    payroll_period: str = Field(..., pattern=r"^\d{4}-\d{2}$")


class OvertimeUpdate(BaseModel):
    """Schema para atualização de Overtime."""

    overtime_type: OvertimeType | None = None
    reason: OvertimeReason | None = None
    reason_description: str | None = Field(None, max_length=500)
    start_time: time | None = None
    end_time: time | None = None
    break_minutes: int | None = Field(None, ge=0, le=120)
    hourly_rate: Decimal | None = Field(None, ge=0)
    use_time_bank: bool | None = None
    notes: str | None = None


class OvertimeResponse(OvertimeBase):
    """Schema de resposta para Overtime."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    status: OvertimeStatus

    employee_registration: str | None = None
    department_id: str | None = None
    department_name: str | None = None

    start_datetime: datetime | None = None
    end_datetime: datetime | None = None

    duration_minutes: int
    break_minutes: int = 0
    net_duration_minutes: int
    night_minutes: int = 0
    is_night_shift: bool = False

    is_holiday: bool = False
    is_sunday: bool = False
    holiday_name: str | None = None

    hourly_rate: Decimal = Decimal("0")
    multiplier: Decimal = Decimal("1.50")
    total_value: Decimal = Decimal("0")
    night_additional_value: Decimal = Decimal("0")

    is_pre_approved: bool = False
    pre_approved_by_name: str | None = None
    pre_approved_at: datetime | None = None

    requires_approval: bool = True
    approved_by_name: str | None = None
    approved_at: datetime | None = None
    rejection_reason: str | None = None

    is_paid: bool = False
    paid_at: datetime | None = None
    payroll_period: str | None = None

    use_time_bank: bool = False
    time_bank_credited: bool = False
    time_bank_expires_at: date | None = None

    is_compensated: bool = False
    compensation_type: CompensationType | None = None
    compensation_date: date | None = None
    compensated_minutes: int = 0
    remaining_minutes: int = 0

    condominium_name: str | None = None
    work_location: str | None = None

    # Calculados
    duration_hours: float
    is_pending_approval: bool
    is_pending_payment: bool
    is_pending_compensation: bool
    days_until_expiration: int | None = None
    overtime_type_display: str
    status_display: str

    created_at: datetime
    updated_at: datetime


class OvertimeListResponse(BaseModel):
    """Schema para listagem de Overtime."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    employee_id: str
    employee_name: str
    overtime_date: date
    overtime_type: OvertimeType
    overtime_type_display: str
    status: OvertimeStatus
    status_display: str
    duration_hours: float
    total_value: Decimal
    use_time_bank: bool
    is_pending_approval: bool
    condominium_name: str | None = None


class OvertimeFilter(BaseModel):
    """Schema para filtros de Overtime."""

    employee_id: str | None = None
    overtime_type: OvertimeType | None = None
    status: OvertimeStatus | None = None
    reason: OvertimeReason | None = None
    condominium_id: str | None = None
    department_id: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    use_time_bank: bool | None = None
    is_pending_approval: bool | None = None
    is_pending_payment: bool | None = None
    is_pending_compensation: bool | None = None


class OvertimeStats(BaseModel):
    """Schema para estatísticas de Overtime."""

    total_overtimes: int = 0
    total_hours: float = 0
    total_value: Decimal = Decimal("0")
    pending_approval_count: int = 0
    pending_approval_hours: float = 0
    approved_count: int = 0
    approved_hours: float = 0
    paid_count: int = 0
    paid_value: Decimal = Decimal("0")
    time_bank_hours: float = 0
    by_type: dict = Field(default_factory=dict)
    by_status: dict = Field(default_factory=dict)
    by_reason: dict = Field(default_factory=dict)


class OvertimeSummary(BaseModel):
    """Resumo de horas extras do período."""

    period: str  # YYYY-MM
    employee_id: str
    employee_name: str
    total_hours: float = 0
    hours_50: float = 0
    hours_100: float = 0
    night_hours: float = 0
    total_value: Decimal = Decimal("0")
    value_50: Decimal = Decimal("0")
    value_100: Decimal = Decimal("0")
    night_value: Decimal = Decimal("0")
    time_bank_credits: float = 0
    time_bank_debits: float = 0
    time_bank_balance: float = 0
