"""Schemas para configuração de folha por funcionário."""

from datetime import date, datetime, time
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from modules.hr.payroll_integration.models import (
    BankHoursPolicy,
    ContractType,
    OvertimeRule,
    WorkScheduleType,
)


class BenefitConfigSchema(BaseModel):
    """Configuração de benefício."""

    benefit_type: str = Field(..., min_length=1, max_length=50)
    value: Decimal = Field(..., ge=0)
    discount_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    discount_type: Optional[str] = Field(
        None,
        pattern="^(percentage|fixed)$",
    )
    provider: Optional[str] = None
    plan_type: Optional[str] = None  # employee_only, family, etc.


class LoanConfigSchema(BaseModel):
    """Configuração de empréstimo consignado."""

    bank: str = Field(..., min_length=1, max_length=100)
    contract: str = Field(..., min_length=1, max_length=50)
    installment_value: Decimal = Field(..., ge=0)
    total_installments: int = Field(..., ge=1)
    paid_installments: int = Field(default=0, ge=0)
    start_date: date
    end_date: Optional[date] = None
    interest_rate: Optional[Decimal] = Field(None, ge=0)

    @field_validator("paid_installments")
    @classmethod
    def validate_paid(cls, v: int, info) -> int:
        """Valida que paid <= total."""
        total = info.data.get("total_installments", 0)
        if v > total:
            raise ValueError("Parcelas pagas não podem exceder total")
        return v


class AlimonyConfigSchema(BaseModel):
    """Configuração de pensão alimentícia."""

    beneficiary: str = Field(..., min_length=1, max_length=200)
    calculation_type: str = Field(
        ...,
        pattern="^(percentage|fixed)$",
    )
    value: Decimal = Field(..., ge=0)
    base: str = Field(
        default="net_salary",
        pattern="^(gross_salary|net_salary|specific_events)$",
    )
    bank_code: Optional[str] = None
    branch: Optional[str] = None
    account: Optional[str] = None
    document: Optional[str] = None  # CPF do beneficiário


class DependentSchema(BaseModel):
    """Configuração de dependente."""

    name: str = Field(..., min_length=1, max_length=200)
    cpf: Optional[str] = Field(None, min_length=11, max_length=11)
    birth_date: date
    relationship: str = Field(
        ...,
        pattern="^(filho|conjuge|pai|mae|outro)$",
    )
    has_disability: bool = False


class CalculationConfigSchema(BaseModel):
    """Configuração de cálculo."""

    round_hours: bool = True
    round_precision: int = Field(default=5, ge=1, le=30)  # minutos
    tolerance_minutes: int = Field(default=10, ge=0, le=30)
    ignore_small_overtime: bool = True
    small_overtime_threshold: int = Field(default=5, ge=0, le=30)
    auto_approve_entries: bool = False


class ExternalCodesSchema(BaseModel):
    """Códigos externos para integração."""

    esocial_matricula: Optional[str] = None
    totvs_chapa: Optional[str] = None
    senior_codigo: Optional[str] = None
    adp_id: Optional[str] = None
    custom_code: Optional[str] = None


class EmployeePayrollConfigBase(BaseModel):
    """Schema base para configuração de folha."""

    contract_type: ContractType = Field(default=ContractType.CLT)
    admission_date: date
    termination_date: Optional[date] = None
    experience_end_date: Optional[date] = None
    base_salary: Decimal = Field(..., ge=0)
    salary_type: str = Field(
        default="monthly",
        pattern="^(monthly|hourly|daily)$",
    )
    hourly_rate: Optional[Decimal] = Field(None, ge=0)
    daily_rate: Optional[Decimal] = Field(None, ge=0)
    work_schedule_type: WorkScheduleType = Field(default=WorkScheduleType.STANDARD)
    weekly_hours: Decimal = Field(default=Decimal("44.0"), ge=0, le=44)
    daily_hours: Decimal = Field(default=Decimal("8.0"), ge=0, le=12)
    monthly_hours: Decimal = Field(default=Decimal("220.0"), ge=0)
    work_start: Optional[time] = None
    work_end: Optional[time] = None
    lunch_start: Optional[time] = None
    lunch_end: Optional[time] = None
    lunch_duration_minutes: int = Field(default=60, ge=0, le=120)
    overtime_rule: OvertimeRule = Field(default=OvertimeRule.PAY)
    overtime_rate_50: Decimal = Field(default=Decimal("50.0"), ge=0)
    overtime_rate_100: Decimal = Field(default=Decimal("100.0"), ge=0)
    overtime_threshold: Decimal = Field(default=Decimal("44.0"), ge=0)
    night_shift_rate: Decimal = Field(default=Decimal("20.0"), ge=0)
    night_shift_start: Optional[time] = None
    night_shift_end: Optional[time] = None
    night_hour_reduction: bool = True
    bank_hours_enabled: bool = False
    bank_hours_policy: Optional[BankHoursPolicy] = None
    bank_hours_balance: Decimal = Field(default=Decimal("0"), ge=-999, le=999)
    bank_hours_limit: Optional[Decimal] = Field(None, ge=0)
    bank_hours_hybrid_threshold: Optional[Decimal] = Field(None, ge=0)
    hazard_pay_rate: Optional[Decimal] = Field(None, ge=0, le=30)
    unhealthy_pay_rate: Optional[Decimal] = Field(None, ge=0, le=40)
    unhealthy_pay_base: Optional[str] = Field(
        None,
        pattern="^(salary|minimum_wage)$",
    )
    dependents_count: int = Field(default=0, ge=0)
    union_id: Optional[str] = None
    union_contribution_enabled: bool = False
    union_contribution_type: Optional[str] = Field(
        None,
        pattern="^(annual|monthly)$",
    )
    union_contribution_value: Optional[Decimal] = Field(None, ge=0)


class EmployeePayrollConfigCreate(EmployeePayrollConfigBase):
    """Schema para criação de configuração."""

    employee_id: UUID
    benefits: Optional[List[BenefitConfigSchema]] = Field(default_factory=list)
    loans: Optional[List[LoanConfigSchema]] = Field(default_factory=list)
    alimony: Optional[List[AlimonyConfigSchema]] = Field(default_factory=list)
    dependents: Optional[List[DependentSchema]] = Field(default_factory=list)
    calculation_config: Optional[CalculationConfigSchema] = None
    external_codes: Optional[ExternalCodesSchema] = None


class EmployeePayrollConfigUpdate(BaseModel):
    """Schema para atualização de configuração."""

    termination_date: Optional[date] = None
    base_salary: Optional[Decimal] = Field(None, ge=0)
    hourly_rate: Optional[Decimal] = Field(None, ge=0)
    work_schedule_type: Optional[WorkScheduleType] = None
    weekly_hours: Optional[Decimal] = Field(None, ge=0, le=44)
    work_start: Optional[time] = None
    work_end: Optional[time] = None
    overtime_rule: Optional[OvertimeRule] = None
    bank_hours_enabled: Optional[bool] = None
    bank_hours_policy: Optional[BankHoursPolicy] = None
    bank_hours_balance: Optional[Decimal] = None
    hazard_pay_rate: Optional[Decimal] = Field(None, ge=0, le=30)
    unhealthy_pay_rate: Optional[Decimal] = Field(None, ge=0, le=40)
    dependents_count: Optional[int] = Field(None, ge=0)
    benefits: Optional[List[BenefitConfigSchema]] = None
    loans: Optional[List[LoanConfigSchema]] = None
    alimony: Optional[List[AlimonyConfigSchema]] = None
    dependents: Optional[List[DependentSchema]] = None
    calculation_config: Optional[CalculationConfigSchema] = None
    external_codes: Optional[ExternalCodesSchema] = None


class EmployeePayrollConfigResponse(BaseModel):
    """Schema de resposta para configuração."""

    id: UUID
    condominio_id: UUID
    employee_id: UUID
    contract_type: str
    admission_date: date
    termination_date: Optional[date]
    experience_end_date: Optional[date]
    base_salary: Decimal
    salary_type: str
    hourly_rate: Optional[Decimal]
    daily_rate: Optional[Decimal]
    calculated_hourly_rate: Decimal
    work_schedule_type: str
    weekly_hours: Decimal
    daily_hours: Decimal
    monthly_hours: Decimal
    work_start: Optional[time]
    work_end: Optional[time]
    overtime_rule: str
    overtime_rate_50: Decimal
    overtime_rate_100: Decimal
    overtime_50_rate: Decimal
    overtime_100_rate: Decimal
    night_shift_rate: Decimal
    night_shift_hourly_rate: Decimal
    bank_hours_enabled: bool
    bank_hours_policy: Optional[str]
    bank_hours_balance: Decimal
    hazard_pay_rate: Optional[Decimal]
    unhealthy_pay_rate: Optional[Decimal]
    dependents_count: int
    benefits: Optional[dict]
    loans: Optional[List[dict]]
    alimony: Optional[List[dict]]
    dependents: Optional[List[dict]]
    calculation_config: Optional[dict]
    external_codes: Optional[dict]
    total_loans_installment: Decimal
    is_trust_position: bool
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class SalaryCalculationRequest(BaseModel):
    """Request para cálculo de salário."""

    gross_salary: Decimal = Field(..., ge=0)
    overtime_hours_50: Decimal = Field(default=Decimal("0"), ge=0)
    overtime_hours_100: Decimal = Field(default=Decimal("0"), ge=0)
    night_hours: Decimal = Field(default=Decimal("0"), ge=0)
    absence_hours: Decimal = Field(default=Decimal("0"), ge=0)
    additional_earnings: Optional[List[dict]] = Field(default_factory=list)
    additional_deductions: Optional[List[dict]] = Field(default_factory=list)
    dependents_count: int = Field(default=0, ge=0)


class SalaryCalculationResponse(BaseModel):
    """Resposta de cálculo de salário."""

    gross_salary: Decimal
    overtime_50_value: Decimal
    overtime_100_value: Decimal
    night_shift_value: Decimal
    absence_deduction: Decimal
    total_earnings: Decimal
    inss: Decimal
    inss_base: Decimal
    irrf: Decimal
    irrf_base: Decimal
    fgts: Decimal
    total_deductions: Decimal
    net_salary: Decimal
    employer_cost: Decimal
    breakdown: dict


class BankHoursAdjustmentRequest(BaseModel):
    """Request para ajuste de banco de horas."""

    adjustment_type: str = Field(
        ...,
        pattern="^(credit|debit|reset)$",
    )
    hours: Decimal = Field(..., ge=0)
    reason: str = Field(..., min_length=1, max_length=500)
    reference_date: Optional[date] = None


class BankHoursBalanceResponse(BaseModel):
    """Resposta de saldo de banco de horas."""

    employee_id: UUID
    current_balance: Decimal
    policy: Optional[str]
    limit: Optional[Decimal]
    expiration_date: Optional[date]
    history: List[dict] = Field(default_factory=list)
