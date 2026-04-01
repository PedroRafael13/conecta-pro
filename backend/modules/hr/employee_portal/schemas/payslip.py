"""Schemas para contracheques/holerites."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from modules.hr.employee_portal.models import PaySlipStatus, PaySlipType


class PaySlipEarningItem(BaseModel):
    """Item de provento no contracheque."""

    code: str = Field(..., min_length=1, max_length=10)
    description: str = Field(..., min_length=1, max_length=100)
    reference: Decimal | None = Field(None, ge=0)
    reference_unit: str | None = Field(None, max_length=20)
    value: Decimal = Field(..., ge=0)


class PaySlipDeductionItem(BaseModel):
    """Item de desconto no contracheque."""

    code: str = Field(..., min_length=1, max_length=10)
    description: str = Field(..., min_length=1, max_length=100)
    reference: Decimal | None = Field(None, ge=0)
    reference_unit: str | None = Field(None, max_length=20)
    value: Decimal = Field(..., ge=0)


class PaySlipBase(BaseModel):
    """Schema base para contracheque."""

    payslip_type: PaySlipType = PaySlipType.MONTHLY
    reference_month: int = Field(..., ge=1, le=12)
    reference_year: int = Field(..., ge=2000, le=2100)
    payment_date: date | None = None


class PaySlipCreate(PaySlipBase):
    """Schema para criação de contracheque."""

    employee_id: UUID
    period_id: UUID | None = None
    employee_name: str = Field(..., min_length=1, max_length=200)
    employee_cpf: str = Field(..., min_length=11, max_length=14)
    employee_position: str | None = Field(None, max_length=100)
    employee_department: str | None = Field(None, max_length=100)
    employee_admission_date: date | None = None

    gross_salary: Decimal = Field(..., ge=0)
    total_earnings: Decimal = Field(default=Decimal("0"), ge=0)
    total_deductions: Decimal = Field(default=Decimal("0"), ge=0)
    net_salary: Decimal = Field(default=Decimal("0"), ge=0)

    inss_base: Decimal | None = Field(None, ge=0)
    irrf_base: Decimal | None = Field(None, ge=0)
    fgts_base: Decimal | None = Field(None, ge=0)

    inss_value: Decimal | None = Field(None, ge=0)
    irrf_value: Decimal | None = Field(None, ge=0)
    fgts_value: Decimal | None = Field(None, ge=0)
    fgts_deposit: Decimal | None = Field(None, ge=0)

    earnings: list[PaySlipEarningItem] = Field(default_factory=list)
    deductions: list[PaySlipDeductionItem] = Field(default_factory=list)

    worked_days: int | None = Field(None, ge=0, le=31)
    worked_hours: Decimal | None = Field(None, ge=0)
    overtime_hours_50: Decimal | None = Field(None, ge=0)
    overtime_hours_100: Decimal | None = Field(None, ge=0)
    night_hours: Decimal | None = Field(None, ge=0)
    absence_days: int | None = Field(None, ge=0)
    absence_hours: Decimal | None = Field(None, ge=0)

    dependents_count: int = Field(default=0, ge=0)
    dependents_irrf_deduction: Decimal | None = Field(None, ge=0)


class PaySlipUpdate(BaseModel):
    """Schema para atualização de contracheque."""

    payment_date: date | None = None
    gross_salary: Decimal | None = Field(None, ge=0)
    total_earnings: Decimal | None = Field(None, ge=0)
    total_deductions: Decimal | None = Field(None, ge=0)
    net_salary: Decimal | None = Field(None, ge=0)
    earnings: list[PaySlipEarningItem] | None = None
    deductions: list[PaySlipDeductionItem] | None = None
    internal_notes: str | None = None
    employee_notes: str | None = None


class PaySlipResponse(BaseModel):
    """Schema de resposta para contracheque."""

    id: UUID
    condominio_id: UUID
    employee_id: UUID
    period_id: UUID | None
    payslip_code: str
    payslip_type: str
    status: str

    reference_month: int
    reference_year: int
    reference_period: str
    payment_date: date | None

    employee_name: str
    employee_cpf: str
    employee_position: str | None
    employee_department: str | None
    employee_admission_date: date | None

    gross_salary: Decimal
    total_earnings: Decimal
    total_deductions: Decimal
    net_salary: Decimal

    inss_base: Decimal | None
    irrf_base: Decimal | None
    fgts_base: Decimal | None

    inss_value: Decimal | None
    irrf_value: Decimal | None
    fgts_value: Decimal | None
    fgts_deposit: Decimal | None

    earnings: list[PaySlipEarningItem]
    deductions: list[PaySlipDeductionItem]

    worked_days: int | None
    worked_hours: Decimal | None
    overtime_hours_50: Decimal | None
    overtime_hours_100: Decimal | None
    night_hours: Decimal | None
    absence_days: int | None
    absence_hours: Decimal | None

    dependents_count: int
    dependents_irrf_deduction: Decimal | None

    pdf_path: str | None
    pdf_generated_at: datetime | None

    first_viewed_at: datetime | None
    view_count: int
    downloaded_at: datetime | None
    download_count: int

    acknowledged_at: datetime | None
    contested: bool
    contest_reason: str | None
    contest_date: datetime | None
    contest_resolved: bool | None
    contest_resolution: str | None

    is_rectification: bool
    original_payslip_id: UUID | None
    rectification_reason: str | None

    employee_notes: str | None
    is_published: bool
    is_viewable: bool
    can_contest: bool

    created_at: datetime
    updated_at: datetime | None
    published_at: datetime | None

    model_config = {"from_attributes": True}


class PaySlipSummary(BaseModel):
    """Resumo do contracheque para listagem."""

    id: UUID
    payslip_code: str
    payslip_type: str
    reference_period: str
    payment_date: date | None
    net_salary: Decimal
    status: str
    viewed: bool
    downloaded: bool
    acknowledged: bool
    contested: bool

    model_config = {"from_attributes": True}


class PaySlipListResponse(BaseModel):
    """Lista paginada de contracheques."""

    items: list[PaySlipSummary]
    total: int
    page: int
    page_size: int
    pages: int


class PaySlipContestRequest(BaseModel):
    """Request para contestar contracheque."""

    reason: str = Field(..., min_length=10, max_length=2000)

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v: str) -> str:
        """Valida motivo da contestação."""
        if len(v.strip()) < 10:
            raise ValueError("Motivo deve ter pelo menos 10 caracteres")
        return v.strip()


class PaySlipAcknowledgeRequest(BaseModel):
    """Request para dar ciência no contracheque."""

    ip_address: str | None = None
    device_info: str | None = None


class PaySlipFilterRequest(BaseModel):
    """Filtros para busca de contracheques."""

    employee_id: UUID | None = None
    payslip_type: PaySlipType | None = None
    status: PaySlipStatus | None = None
    reference_year: int | None = Field(None, ge=2000, le=2100)
    reference_month: int | None = Field(None, ge=1, le=12)
    payment_date_from: date | None = None
    payment_date_to: date | None = None
    only_unread: bool = False
    only_pending_ack: bool = False
    only_contested: bool = False
