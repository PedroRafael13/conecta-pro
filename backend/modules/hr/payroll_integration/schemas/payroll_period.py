"""Schemas para período de folha de pagamento."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from modules.hr.payroll_integration.models import PeriodStatus, PeriodType


class PayrollPeriodBase(BaseModel):
    """Schema base para período de folha."""

    name: str = Field(..., min_length=1, max_length=100)
    period_type: PeriodType = Field(default=PeriodType.MONTHLY)
    reference_month: int = Field(..., ge=1, le=12)
    reference_year: int = Field(..., ge=2000, le=2100)
    start_date: date
    end_date: date
    payment_date: date | None = None
    notes: str | None = None
    settings: dict | None = Field(default_factory=dict)

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v: date, info) -> date:
        """Valida que end_date >= start_date."""
        start = info.data.get("start_date")
        if start and v < start:
            raise ValueError("Data fim deve ser maior ou igual à data início")
        return v

    @model_validator(mode="after")
    def generate_code(self) -> "PayrollPeriodBase":
        """Gera código do período se não informado."""
        return self


class PayrollPeriodCreate(PayrollPeriodBase):
    """Schema para criação de período."""

    code: str | None = Field(None, max_length=20)

    @model_validator(mode="after")
    def auto_code(self) -> "PayrollPeriodCreate":
        """Gera código automaticamente se não informado."""
        if not self.code:
            self.code = f"{self.reference_year}-{self.reference_month:02d}"
        return self


class PayrollPeriodUpdate(BaseModel):
    """Schema para atualização de período."""

    name: str | None = Field(None, min_length=1, max_length=100)
    payment_date: date | None = None
    notes: str | None = None
    settings: dict | None = None


class PayrollPeriodStatusUpdate(BaseModel):
    """Schema para atualização de status."""

    status: PeriodStatus
    reason: str | None = None


class PayrollPeriodResponse(BaseModel):
    """Schema de resposta para período."""

    id: UUID
    condominio_id: UUID
    code: str
    name: str
    period_type: str
    reference_month: int
    reference_year: int
    start_date: date
    end_date: date
    payment_date: date | None
    calculation_date: datetime | None
    approval_date: datetime | None
    closing_date: datetime | None
    status: str
    total_employees: int
    total_earnings: Decimal
    total_deductions: Decimal
    total_net: Decimal
    total_employer_cost: Decimal | None
    total_regular_hours: Decimal | None
    total_overtime_hours: Decimal | None
    notes: str | None
    settings: dict | None
    is_open: bool
    is_editable: bool
    can_calculate: bool
    can_approve: bool
    can_close: bool
    can_export: bool
    days_count: int
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class PayrollPeriodSummary(BaseModel):
    """Resumo de período para listagens."""

    id: UUID
    code: str
    name: str
    period_type: str
    reference_month: int
    reference_year: int
    start_date: date
    end_date: date
    status: str
    total_employees: int
    total_net: Decimal

    model_config = {"from_attributes": True}


class PayrollPeriodListResponse(BaseModel):
    """Resposta paginada de períodos."""

    items: list[PayrollPeriodSummary]
    total: int
    page: int
    page_size: int
    total_pages: int


class PeriodCalculationRequest(BaseModel):
    """Request para cálculo de período."""

    recalculate_all: bool = Field(
        default=False,
        description="Recalcular todos os eventos mesmo já calculados",
    )
    employee_ids: list[UUID] | None = Field(
        None,
        description="IDs específicos de funcionários para calcular",
    )
    event_categories: list[str] | None = Field(
        None,
        description="Categorias específicas para calcular",
    )
    include_inactive: bool = Field(
        default=False,
        description="Incluir funcionários inativos",
    )


class PeriodCalculationResponse(BaseModel):
    """Resposta do cálculo de período."""

    period_id: UUID
    status: str
    started_at: datetime
    completed_at: datetime | None
    duration_ms: int | None
    total_employees: int
    calculated_employees: int
    total_events: int
    new_events: int
    updated_events: int
    errors: list[dict] = Field(default_factory=list)
    warnings: list[dict] = Field(default_factory=list)
    totals: dict = Field(default_factory=dict)


class PeriodApprovalRequest(BaseModel):
    """Request para aprovação de período."""

    notes: str | None = None
    force: bool = Field(
        default=False,
        description="Forçar aprovação mesmo com warnings",
    )


class PeriodCloseRequest(BaseModel):
    """Request para fechamento de período."""

    generate_export: bool = Field(
        default=True,
        description="Gerar exportação automaticamente ao fechar",
    )
    export_format: str | None = None
    notes: str | None = None
