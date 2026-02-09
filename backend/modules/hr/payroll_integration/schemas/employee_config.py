"""Schemas para configuração de folha por funcionário."""

from datetime import date, datetime, time
from decimal import Decimal
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
    discount_rate: Decimal | None = Field(None, ge=0, le=100)
    discount_type: str | None = Field(
        None,
        pattern="^(percentage|fixed)$",
    )
    provider: str | None = None
    plan_type: str | None = None  # employee_only, family, etc.


class LoanConfigSchema(BaseModel):
    """Configuração de empréstimo consignado."""

    bank: str = Field(..., min_length=1, max_length=100)
    contract: str = Field(..., min_length=1, max_length=50)
    installment_value: Decimal = Field(..., ge=0)
    total_installments: int = Field(..., ge=1)
    paid_installments: int = Field(default=0, ge=0)
    start_date: date
    end_date: date | None = None
    interest_rate: Decimal | None = Field(None, ge=0)

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
    bank_code: str | None = None
    branch: str | None = None
    account: str | None = None
    document: str | None = None  # CPF do beneficiário


class DependentSchema(BaseModel):
    """Configuração de dependente."""

    name: str = Field(..., min_length=1, max_length=200)
    cpf: str | None = Field(None, min_length=11, max_length=11)
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

    esocial_matricula: str | None = None
    totvs_chapa: str | None = None
    senior_codigo: str | None = None
    adp_id: str | None = None
    custom_code: str | None = None


class EmployeePayrollConfigBase(BaseModel):
    """Schema base para configuração de folha."""

    contract_type: ContractType = Field(default=ContractType.CLT)
    admission_date: date
    termination_date: date | None = None
    experience_end_date: date | None = None
    base_salary: Decimal = Field(..., ge=0)
    salary_type: str = Field(
        default="monthly",
        pattern="^(monthly|hourly|daily)$",
    )
    hourly_rate: Decimal | None = Field(None, ge=0)
    daily_rate: Decimal | None = Field(None, ge=0)
    work_schedule_type: WorkScheduleType = Field(default=WorkScheduleType.STANDARD)
    weekly_hours: Decimal = Field(default=Decimal("44.0"), ge=0, le=44)
    daily_hours: Decimal = Field(default=Decimal("8.0"), ge=0, le=12)
    monthly_hours: Decimal = Field(default=Decimal("220.0"), ge=0)
    work_start: time | None = None
    work_end: time | None = None
    lunch_start: time | None = None
    lunch_end: time | None = None
    lunch_duration_minutes: int = Field(default=60, ge=0, le=120)
    overtime_rule: OvertimeRule = Field(default=OvertimeRule.PAY)
    overtime_rate_50: Decimal = Field(default=Decimal("50.0"), ge=0)
    overtime_rate_100: Decimal = Field(default=Decimal("100.0"), ge=0)
    overtime_threshold: Decimal = Field(default=Decimal("44.0"), ge=0)
    night_shift_rate: Decimal = Field(default=Decimal("20.0"), ge=0)
    night_shift_start: time | None = None
    night_shift_end: time | None = None
    night_hour_reduction: bool = True
    bank_hours_enabled: bool = False
    bank_hours_policy: BankHoursPolicy | None = None
    bank_hours_balance: Decimal = Field(default=Decimal("0"), ge=-999, le=999)
    bank_hours_limit: Decimal | None = Field(None, ge=0)
    bank_hours_hybrid_threshold: Decimal | None = Field(None, ge=0)
    hazard_pay_rate: Decimal | None = Field(None, ge=0, le=30)
    unhealthy_pay_rate: Decimal | None = Field(None, ge=0, le=40)
    unhealthy_pay_base: str | None = Field(
        None,
        pattern="^(salary|minimum_wage)$",
    )
    dependents_count: int = Field(default=0, ge=0)
    union_id: str | None = None
    union_contribution_enabled: bool = False
    union_contribution_type: str | None = Field(
        None,
        pattern="^(annual|monthly)$",
    )
    union_contribution_value: Decimal | None = Field(None, ge=0)


class EmployeePayrollConfigCreate(EmployeePayrollConfigBase):
    """Schema para criação de configuração."""

    employee_id: UUID
    benefits: list[BenefitConfigSchema] | None = Field(default_factory=list)
    loans: list[LoanConfigSchema] | None = Field(default_factory=list)
    alimony: list[AlimonyConfigSchema] | None = Field(default_factory=list)
    dependents: list[DependentSchema] | None = Field(default_factory=list)
    calculation_config: CalculationConfigSchema | None = None
    external_codes: ExternalCodesSchema | None = None


class EmployeePayrollConfigUpdate(BaseModel):
    """Schema para atualização de configuração."""

    termination_date: date | None = None
    base_salary: Decimal | None = Field(None, ge=0)
    hourly_rate: Decimal | None = Field(None, ge=0)
    work_schedule_type: WorkScheduleType | None = None
    weekly_hours: Decimal | None = Field(None, ge=0, le=44)
    work_start: time | None = None
    work_end: time | None = None
    overtime_rule: OvertimeRule | None = None
    bank_hours_enabled: bool | None = None
    bank_hours_policy: BankHoursPolicy | None = None
    bank_hours_balance: Decimal | None = None
    hazard_pay_rate: Decimal | None = Field(None, ge=0, le=30)
    unhealthy_pay_rate: Decimal | None = Field(None, ge=0, le=40)
    dependents_count: int | None = Field(None, ge=0)
    benefits: list[BenefitConfigSchema] | None = None
    loans: list[LoanConfigSchema] | None = None
    alimony: list[AlimonyConfigSchema] | None = None
    dependents: list[DependentSchema] | None = None
    calculation_config: CalculationConfigSchema | None = None
    external_codes: ExternalCodesSchema | None = None


class EmployeePayrollConfigResponse(BaseModel):
    """Schema de resposta para configuração."""

    id: UUID
    condominio_id: UUID
    employee_id: UUID
    contract_type: str
    admission_date: date
    termination_date: date | None
    experience_end_date: date | None
    base_salary: Decimal
    salary_type: str
    hourly_rate: Decimal | None
    daily_rate: Decimal | None
    calculated_hourly_rate: Decimal
    work_schedule_type: str
    weekly_hours: Decimal
    daily_hours: Decimal
    monthly_hours: Decimal
    work_start: time | None
    work_end: time | None
    overtime_rule: str
    overtime_rate_50: Decimal
    overtime_rate_100: Decimal
    overtime_50_rate: Decimal
    overtime_100_rate: Decimal
    night_shift_rate: Decimal
    night_shift_hourly_rate: Decimal
    bank_hours_enabled: bool
    bank_hours_policy: str | None
    bank_hours_balance: Decimal
    hazard_pay_rate: Decimal | None
    unhealthy_pay_rate: Decimal | None
    dependents_count: int
    benefits: dict | None
    loans: list[dict] | None
    alimony: list[dict] | None
    dependents: list[dict] | None
    calculation_config: dict | None
    external_codes: dict | None
    total_loans_installment: Decimal
    is_trust_position: bool
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class SalaryCalculationRequest(BaseModel):
    """Request para cálculo de salário."""

    gross_salary: Decimal = Field(..., ge=0)
    overtime_hours_50: Decimal = Field(default=Decimal("0"), ge=0)
    overtime_hours_100: Decimal = Field(default=Decimal("0"), ge=0)
    night_hours: Decimal = Field(default=Decimal("0"), ge=0)
    absence_hours: Decimal = Field(default=Decimal("0"), ge=0)
    additional_earnings: list[dict] | None = Field(default_factory=list)
    additional_deductions: list[dict] | None = Field(default_factory=list)
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
    reference_date: date | None = None


class BankHoursBalanceResponse(BaseModel):
    """Resposta de saldo de banco de horas."""

    employee_id: UUID
    current_balance: Decimal
    policy: str | None
    limit: Decimal | None
    expiration_date: date | None
    history: list[dict] = Field(default_factory=list)
