"""Schemas para contracheques/holerites."""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from modules.hr.employee_portal.models import PaySlipStatus, PaySlipType


class PaySlipEarningItem(BaseModel):
    """Item de provento no contracheque."""

    code: str = Field(..., min_length=1, max_length=10)
    description: str = Field(..., min_length=1, max_length=100)
    reference: Optional[Decimal] = Field(None, ge=0)
    reference_unit: Optional[str] = Field(None, max_length=20)
    value: Decimal = Field(..., ge=0)


class PaySlipDeductionItem(BaseModel):
    """Item de desconto no contracheque."""

    code: str = Field(..., min_length=1, max_length=10)
    description: str = Field(..., min_length=1, max_length=100)
    reference: Optional[Decimal] = Field(None, ge=0)
    reference_unit: Optional[str] = Field(None, max_length=20)
    value: Decimal = Field(..., ge=0)


class PaySlipBase(BaseModel):
    """Schema base para contracheque."""

    payslip_type: PaySlipType = PaySlipType.MONTHLY
    reference_month: int = Field(..., ge=1, le=12)
    reference_year: int = Field(..., ge=2000, le=2100)
    payment_date: Optional[date] = None


class PaySlipCreate(PaySlipBase):
    """Schema para criação de contracheque."""

    employee_id: UUID
    period_id: Optional[UUID] = None
    employee_name: str = Field(..., min_length=1, max_length=200)
    employee_cpf: str = Field(..., min_length=11, max_length=14)
    employee_position: Optional[str] = Field(None, max_length=100)
    employee_department: Optional[str] = Field(None, max_length=100)
    employee_admission_date: Optional[date] = None

    gross_salary: Decimal = Field(..., ge=0)
    total_earnings: Decimal = Field(default=Decimal("0"), ge=0)
    total_deductions: Decimal = Field(default=Decimal("0"), ge=0)
    net_salary: Decimal = Field(default=Decimal("0"), ge=0)

    inss_base: Optional[Decimal] = Field(None, ge=0)
    irrf_base: Optional[Decimal] = Field(None, ge=0)
    fgts_base: Optional[Decimal] = Field(None, ge=0)

    inss_value: Optional[Decimal] = Field(None, ge=0)
    irrf_value: Optional[Decimal] = Field(None, ge=0)
    fgts_value: Optional[Decimal] = Field(None, ge=0)
    fgts_deposit: Optional[Decimal] = Field(None, ge=0)

    earnings: List[PaySlipEarningItem] = Field(default_factory=list)
    deductions: List[PaySlipDeductionItem] = Field(default_factory=list)

    worked_days: Optional[int] = Field(None, ge=0, le=31)
    worked_hours: Optional[Decimal] = Field(None, ge=0)
    overtime_hours_50: Optional[Decimal] = Field(None, ge=0)
    overtime_hours_100: Optional[Decimal] = Field(None, ge=0)
    night_hours: Optional[Decimal] = Field(None, ge=0)
    absence_days: Optional[int] = Field(None, ge=0)
    absence_hours: Optional[Decimal] = Field(None, ge=0)

    dependents_count: int = Field(default=0, ge=0)
    dependents_irrf_deduction: Optional[Decimal] = Field(None, ge=0)


class PaySlipUpdate(BaseModel):
    """Schema para atualização de contracheque."""

    payment_date: Optional[date] = None
    gross_salary: Optional[Decimal] = Field(None, ge=0)
    total_earnings: Optional[Decimal] = Field(None, ge=0)
    total_deductions: Optional[Decimal] = Field(None, ge=0)
    net_salary: Optional[Decimal] = Field(None, ge=0)
    earnings: Optional[List[PaySlipEarningItem]] = None
    deductions: Optional[List[PaySlipDeductionItem]] = None
    internal_notes: Optional[str] = None
    employee_notes: Optional[str] = None


class PaySlipResponse(BaseModel):
    """Schema de resposta para contracheque."""

    id: UUID
    condominio_id: UUID
    employee_id: UUID
    period_id: Optional[UUID]
    payslip_code: str
    payslip_type: str
    status: str

    reference_month: int
    reference_year: int
    reference_period: str
    payment_date: Optional[date]

    employee_name: str
    employee_cpf: str
    employee_position: Optional[str]
    employee_department: Optional[str]
    employee_admission_date: Optional[date]

    gross_salary: Decimal
    total_earnings: Decimal
    total_deductions: Decimal
    net_salary: Decimal

    inss_base: Optional[Decimal]
    irrf_base: Optional[Decimal]
    fgts_base: Optional[Decimal]

    inss_value: Optional[Decimal]
    irrf_value: Optional[Decimal]
    fgts_value: Optional[Decimal]
    fgts_deposit: Optional[Decimal]

    earnings: List[PaySlipEarningItem]
    deductions: List[PaySlipDeductionItem]

    worked_days: Optional[int]
    worked_hours: Optional[Decimal]
    overtime_hours_50: Optional[Decimal]
    overtime_hours_100: Optional[Decimal]
    night_hours: Optional[Decimal]
    absence_days: Optional[int]
    absence_hours: Optional[Decimal]

    dependents_count: int
    dependents_irrf_deduction: Optional[Decimal]

    pdf_path: Optional[str]
    pdf_generated_at: Optional[datetime]

    first_viewed_at: Optional[datetime]
    view_count: int
    downloaded_at: Optional[datetime]
    download_count: int

    acknowledged_at: Optional[datetime]
    contested: bool
    contest_reason: Optional[str]
    contest_date: Optional[datetime]
    contest_resolved: Optional[bool]
    contest_resolution: Optional[str]

    is_rectification: bool
    original_payslip_id: Optional[UUID]
    rectification_reason: Optional[str]

    employee_notes: Optional[str]
    is_published: bool
    is_viewable: bool
    can_contest: bool

    created_at: datetime
    updated_at: Optional[datetime]
    published_at: Optional[datetime]

    model_config = {"from_attributes": True}


class PaySlipSummary(BaseModel):
    """Resumo do contracheque para listagem."""

    id: UUID
    payslip_code: str
    payslip_type: str
    reference_period: str
    payment_date: Optional[date]
    net_salary: Decimal
    status: str
    viewed: bool
    downloaded: bool
    acknowledged: bool
    contested: bool

    model_config = {"from_attributes": True}


class PaySlipListResponse(BaseModel):
    """Lista paginada de contracheques."""

    items: List[PaySlipSummary]
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

    ip_address: Optional[str] = None
    device_info: Optional[str] = None


class PaySlipFilterRequest(BaseModel):
    """Filtros para busca de contracheques."""

    employee_id: Optional[UUID] = None
    payslip_type: Optional[PaySlipType] = None
    status: Optional[PaySlipStatus] = None
    reference_year: Optional[int] = Field(None, ge=2000, le=2100)
    reference_month: Optional[int] = Field(None, ge=1, le=12)
    payment_date_from: Optional[date] = None
    payment_date_to: Optional[date] = None
    only_unread: bool = False
    only_pending_ack: bool = False
    only_contested: bool = False
