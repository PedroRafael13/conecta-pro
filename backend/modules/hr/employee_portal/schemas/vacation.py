"""Schemas para solicitações de férias."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from modules.hr.employee_portal.models import VacationType


class VacationPeriodCreate(BaseModel):
    """Schema para criação de período aquisitivo."""

    employee_id: UUID
    start_date: date
    end_date: date
    concession_start: date
    concession_end: date
    total_days_entitled: int = Field(default=30, ge=0, le=30)
    absences_count: int = Field(default=0, ge=0)


class VacationPeriodResponse(BaseModel):
    """Schema de resposta para período aquisitivo."""

    id: UUID
    condominio_id: UUID
    employee_id: UUID
    start_date: date
    end_date: date
    concession_start: date
    concession_end: date
    total_days_entitled: int
    days_used: int
    days_sold: int
    days_remaining: int
    absences_count: int
    is_expired: bool
    is_fully_used: bool
    double_payment: bool
    expires_at: date | None
    is_within_concession: bool
    days_until_expiration: int
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class VacationPeriodSummary(BaseModel):
    """Resumo do período aquisitivo."""

    id: UUID
    start_date: date
    end_date: date
    days_remaining: int
    days_until_expiration: int
    is_expired: bool


class VacationRequestBase(BaseModel):
    """Schema base para solicitação de férias."""

    vacation_type: VacationType = VacationType.FULL
    start_date: date
    end_date: date
    days_requested: int = Field(..., ge=5, le=30)
    sell_days: int = Field(default=0, ge=0, le=10)
    sell_requested: bool = False
    advance_13th_requested: bool = False
    employee_notes: str | None = Field(None, max_length=1000)


class VacationRequestCreate(VacationRequestBase):
    """Schema para criação de solicitação de férias."""

    vacation_period_id: UUID | None = None
    substitute_employee_id: UUID | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> "VacationRequestCreate":
        """Valida datas e período."""
        if self.end_date < self.start_date:
            raise ValueError("Data final deve ser maior ou igual à data inicial")

        days_diff = (self.end_date - self.start_date).days + 1
        if days_diff != self.days_requested:
            raise ValueError(f"Dias solicitados ({self.days_requested}) não corresponde ao período ({days_diff} dias)")

        if self.sell_days > 0 and not self.sell_requested:
            raise ValueError("sell_requested deve ser True quando sell_days > 0")

        if self.sell_days > 10:
            raise ValueError("Abono pecuniário limitado a 10 dias (CLT)")

        return self

    @field_validator("start_date")
    @classmethod
    def validate_start_date(cls, v: date) -> date:
        """Valida data de início."""
        if v < date.today():
            raise ValueError("Data de início não pode ser no passado")
        return v


class VacationRequestUpdate(BaseModel):
    """Schema para atualização de solicitação de férias."""

    start_date: date | None = None
    end_date: date | None = None
    days_requested: int | None = Field(None, ge=5, le=30)
    sell_days: int | None = Field(None, ge=0, le=10)
    sell_requested: bool | None = None
    advance_13th_requested: bool | None = None
    employee_notes: str | None = Field(None, max_length=1000)
    substitute_employee_id: UUID | None = None


class VacationRequestResponse(BaseModel):
    """Schema de resposta para solicitação de férias."""

    id: UUID
    condominio_id: UUID
    employee_id: UUID
    vacation_period_id: UUID | None
    request_code: str
    vacation_type: str
    status: str

    start_date: date
    end_date: date
    days_requested: int
    sell_days: int
    sell_requested: bool
    advance_13th_requested: bool
    advance_13th_approved: bool | None

    vacation_salary: Decimal | None
    vacation_bonus: Decimal | None
    sell_value: Decimal | None
    advance_13th_value: Decimal | None
    inss_deduction: Decimal | None
    irrf_deduction: Decimal | None
    other_deductions: Decimal | None
    net_value: Decimal | None

    calculation_details: dict | None
    employee_notes: str | None
    manager_notes: str | None
    hr_notes: str | None

    submitted_at: datetime | None
    manager_approved: bool | None
    manager_approved_at: datetime | None
    manager_rejection_reason: str | None
    hr_approved: bool | None
    hr_approved_at: datetime | None
    hr_rejection_reason: str | None

    scheduled_at: datetime | None
    cancelled_at: datetime | None
    cancel_reason: str | None
    interrupted_at: datetime | None
    interrupt_reason: str | None
    days_enjoyed_before_interrupt: int | None

    return_date: date | None
    actual_return_date: date | None
    payment_date: date | None
    paid_at: datetime | None
    payslip_id: UUID | None

    substitute_employee_id: UUID | None
    substitute_name: str | None

    is_pending: bool
    is_approved: bool
    can_cancel: bool
    days_until_start: int
    is_within_legal_notice: bool

    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class VacationRequestSummary(BaseModel):
    """Resumo da solicitação de férias."""

    id: UUID
    request_code: str
    vacation_type: str
    status: str
    start_date: date
    end_date: date
    days_requested: int
    sell_days: int
    net_value: Decimal | None
    days_until_start: int


class VacationRequestListResponse(BaseModel):
    """Lista paginada de solicitações de férias."""

    items: list[VacationRequestSummary]
    total: int
    page: int
    page_size: int
    pages: int


class VacationApprovalRequest(BaseModel):
    """Request para aprovação/rejeição de férias."""

    approved: bool
    notes: str | None = Field(None, max_length=1000)
    rejection_reason: str | None = Field(None, max_length=1000)

    @model_validator(mode="after")
    def validate_rejection(self) -> "VacationApprovalRequest":
        """Valida motivo de rejeição."""
        if not self.approved and not self.rejection_reason:
            raise ValueError("Motivo de rejeição é obrigatório")
        return self


class VacationBalanceResponse(BaseModel):
    """Resposta com saldo de férias."""

    employee_id: UUID
    periods: list[VacationPeriodSummary]
    total_days_available: int
    total_days_used: int
    total_days_sold: int
    total_days_remaining: int
    pending_requests_count: int
    next_period_start: date | None
    has_expiring_period: bool
    days_until_next_expiration: int | None


class VacationCalculationRequest(BaseModel):
    """Request para cálculo de férias."""

    employee_id: UUID
    vacation_period_id: UUID | None = None
    start_date: date
    days_requested: int = Field(..., ge=5, le=30)
    sell_days: int = Field(default=0, ge=0, le=10)
    advance_13th: bool = False


class VacationCalculationResponse(BaseModel):
    """Resposta do cálculo de férias."""

    base_salary: Decimal
    daily_rate: Decimal

    vacation_days_value: Decimal
    vacation_bonus: Decimal  # 1/3 constitucional
    sell_value: Decimal
    advance_13th_value: Decimal

    gross_total: Decimal

    inss_base: Decimal
    inss_value: Decimal
    irrf_base: Decimal
    irrf_value: Decimal
    other_deductions: Decimal

    net_total: Decimal

    payment_date: date  # 2 dias antes do início
    return_date: date

    calculation_details: dict


class VacationCancelRequest(BaseModel):
    """Request para cancelamento de férias."""

    reason: str = Field(..., min_length=10, max_length=1000)


class VacationInterruptRequest(BaseModel):
    """Request para interrupção de férias."""

    reason: str = Field(..., min_length=10, max_length=1000)
    interrupt_date: date
    days_enjoyed: int = Field(..., ge=1)
