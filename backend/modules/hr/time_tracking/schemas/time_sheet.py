"""Schemas Pydantic para TimeSheet."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from modules.hr.time_tracking.models import TimeSheetStatus


class DailySummaryEntry(BaseModel):
    """Resumo de um dia."""

    date: date
    expected: int = 0  # minutos
    worked: int = 0
    overtime: int = 0
    night: int = 0
    late: int = 0
    early: int = 0
    is_holiday: bool = False
    is_absent: bool = False
    notes: str | None = None


class PendingIssue(BaseModel):
    """Pendência na folha."""

    type: str
    date: date
    description: str
    severity: str = "medium"


class TimeSheetBase(BaseModel):
    """Schema base para TimeSheet."""

    reference_month: int = Field(..., ge=1, le=12)
    reference_year: int = Field(..., ge=2000, le=2100)
    employee_id: str = Field(..., min_length=1, max_length=50)
    employee_name: str = Field(..., min_length=1, max_length=200)


class TimeSheetCreate(TimeSheetBase):
    """Schema para criação de TimeSheet."""

    employee_registration: str | None = Field(None, max_length=50)
    employee_cpf: str | None = Field(None, max_length=14)
    employee_pis: str | None = Field(None, max_length=15)
    department_id: str | None = Field(None, max_length=50)
    department_name: str | None = Field(None, max_length=100)
    position_name: str | None = Field(None, max_length=100)

    work_schedule_id: str | None = Field(None, max_length=50)
    work_schedule_name: str | None = Field(None, max_length=200)
    weekly_hours_expected: int = Field(2640, ge=0)

    hourly_rate: Decimal = Field(Decimal("0"), ge=0)

    condominium_id: str | None = Field(None, max_length=50)
    condominium_name: str | None = Field(None, max_length=200)


class TimeSheetUpdate(BaseModel):
    """Schema para atualização de TimeSheet."""

    status: TimeSheetStatus | None = None
    hourly_rate: Decimal | None = Field(None, ge=0)
    notes: str | None = None
    internal_notes: str | None = None


class TimeSheetRecalculate(BaseModel):
    """Schema para recálculo."""

    force: bool = False


class TimeSheetEmployeeApproval(BaseModel):
    """Schema para aprovação do funcionário."""

    notes: str | None = Field(None, max_length=500)


class TimeSheetManagerApproval(BaseModel):
    """Schema para aprovação do gestor."""

    notes: str | None = Field(None, max_length=500)


class TimeSheetHRApproval(BaseModel):
    """Schema para aprovação do RH."""

    notes: str | None = Field(None, max_length=500)


class TimeSheetReview(BaseModel):
    """Schema para revisão."""

    notes: str | None = Field(None, max_length=500)


class TimeSheetClose(BaseModel):
    """Schema para fechamento."""


class TimeSheetPayroll(BaseModel):
    """Schema para envio à folha."""

    payroll_reference: str = Field(..., min_length=1, max_length=100)
    batch_id: str | None = Field(None, max_length=50)


class TimeSheetReopen(BaseModel):
    """Schema para reabertura."""

    reason: str = Field(..., min_length=10, max_length=500)


class TimeSheetResponse(TimeSheetBase):
    """Schema de resposta para TimeSheet."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    status: TimeSheetStatus

    period_start: date
    period_end: date

    employee_registration: str | None = None
    employee_cpf: str | None = None
    employee_pis: str | None = None
    department_id: str | None = None
    department_name: str | None = None
    position_name: str | None = None

    work_schedule_id: str | None = None
    work_schedule_name: str | None = None
    weekly_hours_expected: int = 2640

    # Dias
    total_days: int = 0
    work_days_expected: int = 0
    work_days_worked: int = 0
    absent_days: int = 0
    justified_absent_days: int = 0
    unjustified_absent_days: int = 0
    vacation_days: int = 0
    holiday_days: int = 0
    leave_days: int = 0
    medical_leave_days: int = 0

    # Horas (minutos)
    hours_expected_minutes: int = 0
    hours_worked_minutes: int = 0
    hours_balance_minutes: int = 0

    # Horas extras
    overtime_50_minutes: int = 0
    overtime_100_minutes: int = 0
    overtime_total_minutes: int = 0
    overtime_approved_minutes: int = 0
    overtime_pending_minutes: int = 0

    # Noturno
    night_hours_minutes: int = 0

    # Atrasos
    late_minutes: int = 0
    early_departure_minutes: int = 0
    late_count: int = 0
    early_departure_count: int = 0

    # Intervalos
    break_expected_minutes: int = 0
    break_actual_minutes: int = 0
    break_irregular_count: int = 0

    # Banco de horas
    time_bank_previous_balance: int = 0
    time_bank_credits: int = 0
    time_bank_debits: int = 0
    time_bank_current_balance: int = 0
    time_bank_expiring_minutes: int = 0

    # DSR
    dsr_entitled: bool = True
    dsr_lost_days: int = 0
    dsr_lost_reason: str | None = None

    # Valores
    hourly_rate: Decimal = Decimal("0")
    overtime_50_value: Decimal = Decimal("0")
    overtime_100_value: Decimal = Decimal("0")
    night_additional_value: Decimal = Decimal("0")
    total_additional_value: Decimal = Decimal("0")
    total_deduction_value: Decimal = Decimal("0")

    # Ocorrências
    total_entries: int = 0
    anomaly_count: int = 0
    anomaly_resolved_count: int = 0
    justification_count: int = 0
    justification_approved_count: int = 0
    justification_pending_count: int = 0
    manual_entries_count: int = 0

    # Detalhes
    daily_summary: list[dict] | None = None
    has_pending_issues: bool = False
    pending_issues: list[dict] | None = None

    # Revisão
    reviewed_by_name: str | None = None
    reviewed_at: datetime | None = None

    # Aprovações
    approved_by_employee: bool = False
    employee_approved_at: datetime | None = None

    approved_by_manager: bool = False
    manager_name: str | None = None
    manager_approved_at: datetime | None = None

    approved_by_hr: bool = False
    hr_approver_name: str | None = None
    hr_approved_at: datetime | None = None

    # Fechamento
    closed_at: datetime | None = None
    closed_by_name: str | None = None

    # Folha
    sent_to_payroll_at: datetime | None = None
    payroll_reference: str | None = None

    condominium_name: str | None = None

    # Calculados
    hours_worked: float
    hours_expected: float
    hours_balance: float
    overtime_total_hours: float
    is_fully_approved: bool
    can_close: bool
    period_display: str
    status_display: str

    created_at: datetime
    updated_at: datetime
    last_calculated_at: datetime | None = None


class TimeSheetListResponse(BaseModel):
    """Schema para listagem de TimeSheet."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    reference_month: int
    reference_year: int
    period_display: str
    employee_id: str
    employee_name: str
    status: TimeSheetStatus
    status_display: str
    hours_worked: float
    hours_balance: float
    overtime_total_hours: float
    has_pending_issues: bool
    is_fully_approved: bool
    condominium_name: str | None = None


class TimeSheetFilter(BaseModel):
    """Schema para filtros de TimeSheet."""

    employee_id: str | None = None
    reference_month: int | None = Field(None, ge=1, le=12)
    reference_year: int | None = Field(None, ge=2000, le=2100)
    status: TimeSheetStatus | None = None
    condominium_id: str | None = None
    department_id: str | None = None
    has_pending_issues: bool | None = None
    is_fully_approved: bool | None = None


class TimeSheetStats(BaseModel):
    """Schema para estatísticas de TimeSheet."""

    total_sheets: int = 0
    open_count: int = 0
    closed_count: int = 0
    sent_to_payroll_count: int = 0
    total_overtime_hours: float = 0
    total_overtime_value: Decimal = Decimal("0")
    total_deductions_value: Decimal = Decimal("0")
    average_hours_worked: float = 0
    late_count_total: int = 0
    absent_days_total: int = 0
    by_status: dict = Field(default_factory=dict)
    pending_approval_count: int = 0


class TimeSheetBatchAction(BaseModel):
    """Schema para ação em lote."""

    sheet_ids: list[str] = Field(..., min_length=1)
    action: str = Field(..., pattern=r"^(close|send_to_payroll|reopen)$")
    notes: str | None = Field(None, max_length=500)
    payroll_reference: str | None = Field(None, max_length=100)
