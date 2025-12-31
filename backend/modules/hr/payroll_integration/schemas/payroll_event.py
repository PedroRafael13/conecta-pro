"""Schemas para eventos de folha de pagamento."""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from modules.hr.payroll_integration.models import EventCategory, EventStatus, EventType


class PayrollEventBase(BaseModel):
    """Schema base para evento de folha."""

    event_code: str = Field(..., min_length=1, max_length=20)
    event_name: str = Field(..., min_length=1, max_length=100)
    event_type: EventType
    event_category: EventCategory
    reference: Optional[Decimal] = Field(None, ge=0)
    reference_unit: Optional[str] = Field(None, max_length=20)
    base_value: Optional[Decimal] = None
    rate: Optional[Decimal] = Field(None, ge=0)
    value: Decimal = Field(..., ge=0)
    source: Optional[str] = None
    event_date: Optional[date] = None
    event_start: Optional[date] = None
    event_end: Optional[date] = None
    esocial_code: Optional[str] = Field(None, max_length=20)
    esocial_incidences: Optional[dict] = Field(default_factory=dict)
    is_recurring: bool = False
    is_proportional: bool = False
    notes: Optional[str] = None


class PayrollEventCreate(PayrollEventBase):
    """Schema para criação de evento."""

    employee_id: UUID
    period_id: UUID


class PayrollEventUpdate(BaseModel):
    """Schema para atualização de evento."""

    event_name: Optional[str] = Field(None, min_length=1, max_length=100)
    reference: Optional[Decimal] = Field(None, ge=0)
    value: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None


class PayrollEventResponse(BaseModel):
    """Schema de resposta para evento."""

    id: UUID
    condominio_id: UUID
    period_id: UUID
    employee_id: UUID
    event_code: str
    event_name: str
    event_type: str
    event_category: str
    reference: Optional[Decimal]
    reference_unit: Optional[str]
    base_value: Optional[Decimal]
    rate: Optional[Decimal]
    value: Decimal
    source: Optional[str]
    event_date: Optional[date]
    esocial_code: Optional[str]
    esocial_incidences: Optional[dict]
    status: str
    is_recurring: bool
    is_proportional: bool
    original_value: Optional[Decimal]
    adjustment_reason: Optional[str]
    notes: Optional[str]
    is_earning: bool
    is_deduction: bool
    signed_value: Decimal
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class PayrollEventListResponse(BaseModel):
    """Lista paginada de eventos."""

    items: List["PayrollEventResponse"]
    total: int
    page: int
    page_size: int
    pages: int


class PayrollEventBulkCreate(BaseModel):
    """Schema para criação em lote de eventos."""

    period_id: UUID
    events: List[PayrollEventCreate]

    @field_validator("events")
    @classmethod
    def validate_events(cls, v: List[PayrollEventCreate]) -> List[PayrollEventCreate]:
        """Valida lista de eventos."""
        if not v:
            raise ValueError("Lista de eventos não pode estar vazia")
        if len(v) > 1000:
            raise ValueError("Máximo de 1000 eventos por lote")
        return v


class EventAdjustmentRequest(BaseModel):
    """Request para ajuste de evento."""

    new_value: Decimal = Field(..., ge=0)
    reason: str = Field(..., min_length=1, max_length=500)


class EventCancellationRequest(BaseModel):
    """Request para cancelamento de evento."""

    reason: str = Field(..., min_length=1, max_length=500)


class EmployeeEventSummary(BaseModel):
    """Resumo de evento por funcionário."""

    event_code: str
    event_name: str
    event_type: str
    value: Decimal


class EmployeePayrollSummary(BaseModel):
    """Resumo de folha por funcionário."""

    employee_id: UUID
    employee_name: str
    employee_cpf: Optional[str]
    department: Optional[str]
    position: Optional[str]
    admission_date: Optional[date]
    base_salary: Decimal
    total_earnings: Decimal
    total_deductions: Decimal
    net_salary: Decimal
    total_hours: Optional[Decimal]
    overtime_hours: Optional[Decimal]
    absence_hours: Optional[Decimal]
    events: List[EmployeeEventSummary] = Field(default_factory=list)
    inss: Decimal = Field(default=Decimal("0"))
    irrf: Decimal = Field(default=Decimal("0"))
    fgts: Decimal = Field(default=Decimal("0"))


class EventsByCategory(BaseModel):
    """Eventos agrupados por categoria."""

    category: str
    category_name: str
    events: List[PayrollEventResponse]
    total: Decimal


class PeriodEventsResponse(BaseModel):
    """Resposta de eventos do período."""

    period_id: UUID
    period_code: str
    period_name: str
    total_employees: int
    total_events: int
    total_earnings: Decimal
    total_deductions: Decimal
    total_net: Decimal
    events_by_category: List[EventsByCategory]
    employees_summary: List[EmployeePayrollSummary]
