"""
Service Schemas - Pydantic Models
Sprint 31: Gestão de Serviços
"""
# pylint: disable=too-few-public-methods

from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from modules.services.models.service_catalog import ServiceCategory, ServiceStatus, ServiceType
from modules.services.models.service_execution import ExecutionStatus
from modules.services.models.service_order import OrderPriority, OrderStatus
from modules.services.models.service_report import ReportType
from modules.services.models.sla_config import SLAMetricType

# ============================================================
# SERVICE CATALOG SCHEMAS
# ============================================================


class ServiceCatalogBase(BaseModel):
    """Base schema for ServiceCatalog."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    short_description: str | None = Field(None, max_length=500)
    category: ServiceCategory = ServiceCategory.OUTROS
    service_type: ServiceType = ServiceType.RECORRENTE
    base_price: Decimal | None = Field(None, ge=0)
    unit_price: Decimal | None = Field(None, ge=0)
    price_unit: str | None = Field(None, max_length=50)
    estimated_duration_hours: Decimal | None = Field(None, ge=0)
    required_skills: list[str] | None = None
    requires_scheduling: bool = True
    requires_approval: bool = False
    allows_remote: bool = False
    is_emergency_available: bool = False
    emergency_surcharge_percent: Decimal | None = Field(None, ge=0, le=100)
    default_sla_response_hours: int | None = Field(None, ge=0)
    default_sla_resolution_hours: int | None = Field(None, ge=0)
    tags: list[str] | None = None


class ServiceCatalogCreate(ServiceCatalogBase):
    """Schema for creating a service catalog entry."""


class ServiceCatalogUpdate(BaseModel):
    """Schema for updating a service catalog entry."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    short_description: str | None = Field(None, max_length=500)
    category: ServiceCategory | None = None
    service_type: ServiceType | None = None
    status: ServiceStatus | None = None
    base_price: Decimal | None = Field(None, ge=0)
    unit_price: Decimal | None = Field(None, ge=0)
    price_unit: str | None = None
    estimated_duration_hours: Decimal | None = Field(None, ge=0)
    required_skills: list[str] | None = None
    requires_scheduling: bool | None = None
    requires_approval: bool | None = None
    allows_remote: bool | None = None
    is_emergency_available: bool | None = None
    emergency_surcharge_percent: Decimal | None = Field(None, ge=0, le=100)
    default_sla_response_hours: int | None = Field(None, ge=0)
    default_sla_resolution_hours: int | None = Field(None, ge=0)
    tags: list[str] | None = None
    notes: str | None = None


class ServiceCatalogResponse(ServiceCatalogBase):
    """Response schema for ServiceCatalog."""

    id: UUID
    code: str
    status: ServiceStatus
    min_price: Decimal | None = None
    max_price: Decimal | None = None
    min_team_size: int | None = None
    max_team_size: int | None = None
    total_orders: int = 0
    completed_orders: int = 0
    avg_rating: Decimal | None = None
    total_revenue: Decimal = Decimal("0")
    completion_rate: float = 0.0
    is_available: bool = True
    ativo: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class ServiceCatalogListResponse(BaseModel):
    """List response for ServiceCatalog."""

    id: UUID
    code: str
    name: str
    category: ServiceCategory
    service_type: ServiceType
    status: ServiceStatus
    base_price: Decimal | None = None
    unit_price: Decimal | None = None
    avg_rating: Decimal | None = None
    total_orders: int = 0
    is_available: bool = True

    class Config:
        """Pydantic config."""

        from_attributes = True


class ServiceCatalogStats(BaseModel):
    """Statistics for ServiceCatalog."""

    total_services: int = 0
    active_services: int = 0
    by_category: dict[str, int] = {}
    by_type: dict[str, int] = {}
    total_revenue: Decimal = Decimal("0")
    avg_rating: float | None = None


# ============================================================
# SERVICE ORDER SCHEMAS
# ============================================================


class ServiceOrderBase(BaseModel):
    """Base schema for ServiceOrder."""

    service_id: UUID
    client_id: UUID
    condominium_id: UUID | None = None
    contract_id: UUID | None = None
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    requirements: str | None = None
    priority: OrderPriority = OrderPriority.NORMAL
    requester_name: str | None = Field(None, max_length=200)
    requester_email: str | None = Field(None, max_length=255)
    requester_phone: str | None = Field(None, max_length=20)
    location_address: str | None = Field(None, max_length=500)
    requested_date: date | None = None
    requested_time_start: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")
    requested_time_end: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")
    is_flexible_schedule: bool = True
    estimated_value: Decimal | None = Field(None, ge=0)


class ServiceOrderCreate(ServiceOrderBase):
    """Schema for creating a service order."""

    special_instructions: str | None = None


class ServiceOrderUpdate(BaseModel):
    """Schema for updating a service order."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    requirements: str | None = None
    special_instructions: str | None = None
    priority: OrderPriority | None = None
    requester_name: str | None = None
    requester_email: str | None = None
    requester_phone: str | None = None
    location_address: str | None = None
    location_details: str | None = None
    requested_date: date | None = None
    requested_time_start: str | None = None
    requested_time_end: str | None = None
    scheduled_date: date | None = None
    scheduled_time_start: str | None = None
    scheduled_time_end: str | None = None
    estimated_value: Decimal | None = None
    discount_value: Decimal | None = None
    discount_reason: str | None = None
    internal_notes: str | None = None


class ServiceOrderResponse(ServiceOrderBase):
    """Response schema for ServiceOrder."""

    id: UUID
    order_number: str
    status: OrderStatus
    scheduled_date: date | None = None
    scheduled_time_start: str | None = None
    scheduled_time_end: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    actual_duration_hours: Decimal | None = None
    final_value: Decimal | None = None
    discount_value: Decimal | None = None
    additional_charges: Decimal | None = None
    rating: int | None = None
    assigned_technician_name: str | None = None
    sla_response_met: bool | None = None
    sla_resolution_met: bool | None = None
    is_overdue: bool = False
    ativo: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class ServiceOrderListResponse(BaseModel):
    """List response for ServiceOrder."""

    id: UUID
    order_number: str
    title: str
    status: OrderStatus
    priority: OrderPriority
    client_id: UUID
    scheduled_date: date | None = None
    assigned_technician_name: str | None = None
    is_overdue: bool = False
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class ServiceOrderFilter(BaseModel):
    """Filter for ServiceOrder queries."""

    status: OrderStatus | None = None
    priority: OrderPriority | None = None
    client_id: UUID | None = None
    condominium_id: UUID | None = None
    service_id: UUID | None = None
    technician_id: UUID | None = None
    scheduled_date_from: date | None = None
    scheduled_date_to: date | None = None
    is_overdue: bool | None = None
    search: str | None = None


class ServiceOrderStats(BaseModel):
    """Statistics for ServiceOrders."""

    total_orders: int = 0
    by_status: dict[str, int] = {}
    by_priority: dict[str, int] = {}
    overdue_count: int = 0
    avg_completion_time_hours: float | None = None
    avg_rating: float | None = None
    sla_compliance_percent: float | None = None


# ============================================================
# SERVICE EXECUTION SCHEMAS
# ============================================================


class ServiceExecutionBase(BaseModel):
    """Base schema for ServiceExecution."""

    order_id: UUID
    technician_id: UUID | None = None
    technician_name: str | None = Field(None, max_length=200)
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None


class ServiceExecutionCreate(ServiceExecutionBase):
    """Schema for creating a service execution."""

    checklist_items: list[dict[str, Any]] | None = None


class ServiceExecutionUpdate(BaseModel):
    """Schema for updating a service execution."""

    technician_id: UUID | None = None
    technician_name: str | None = None
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None
    work_description: str | None = None
    findings: str | None = None
    recommendations: str | None = None
    internal_notes: str | None = None
    client_notes: str | None = None
    labor_cost: Decimal | None = None
    travel_cost: Decimal | None = None


class ServiceExecutionResponse(ServiceExecutionBase):
    """Response schema for ServiceExecution."""

    id: UUID
    execution_number: str
    sequence: int
    status: ExecutionStatus
    actual_start: datetime | None = None
    actual_end: datetime | None = None
    travel_duration_minutes: int | None = None
    execution_duration_minutes: int | None = None
    total_duration_minutes: int | None = None
    work_description: str | None = None
    findings: str | None = None
    recommendations: str | None = None
    checklist_completed: bool = False
    checklist_completion_percent: Decimal | None = None
    materials_cost: Decimal | None = None
    total_cost: Decimal | None = None
    has_signatures: bool = False
    is_finished: bool = False
    ativo: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


# ============================================================
# SERVICE REPORT SCHEMAS
# ============================================================


class ServiceReportBase(BaseModel):
    """Base schema for ServiceReport."""

    order_id: UUID
    report_type: ReportType = ReportType.EXECUCAO
    title: str = Field(..., min_length=1, max_length=200)
    summary: str | None = None
    findings: str | None = None
    conclusions: str | None = None
    recommendations: str | None = None


class ServiceReportCreate(ServiceReportBase):
    """Schema for creating a service report."""

    author_id: UUID | None = None
    author_name: str | None = None


class ServiceReportUpdate(BaseModel):
    """Schema for updating a service report."""

    title: str | None = Field(None, min_length=1, max_length=200)
    summary: str | None = None
    introduction: str | None = None
    methodology: str | None = None
    findings: str | None = None
    analysis: str | None = None
    conclusions: str | None = None
    recommendations: str | None = None
    sections: list[dict[str, Any]] | None = None


class ServiceReportResponse(ServiceReportBase):
    """Response schema for ServiceReport."""

    id: UUID
    report_number: str
    author_name: str | None = None
    reviewer_name: str | None = None
    is_draft: bool = True
    is_reviewed: bool = False
    is_approved: bool = False
    is_sent: bool = False
    version: int = 1
    pdf_url: str | None = None
    is_complete: bool = False
    non_conformity_count: int = 0
    photo_count: int = 0
    ativo: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


# ============================================================
# SLA CONFIG SCHEMAS
# ============================================================


class SLAConfigBase(BaseModel):
    """Base schema for SLAConfig."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    metric_type: SLAMetricType = SLAMetricType.TEMPO_RESOLUCAO
    response_time_minutes: int | None = Field(None, ge=0)
    resolution_time_minutes: int | None = Field(None, ge=0)
    target_availability_percent: Decimal | None = Field(None, ge=0, le=100)
    penalty_enabled: bool = False
    penalty_percent_per_breach: Decimal | None = Field(None, ge=0, le=100)
    bonus_enabled: bool = False
    business_hours_only: bool = True


class SLAConfigCreate(SLAConfigBase):
    """Schema for creating an SLA config."""

    service_id: UUID | None = None
    client_id: UUID | None = None
    contract_id: UUID | None = None


class SLAConfigUpdate(BaseModel):
    """Schema for updating an SLA config."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    response_time_minutes: int | None = Field(None, ge=0)
    resolution_time_minutes: int | None = Field(None, ge=0)
    target_availability_percent: Decimal | None = None
    penalty_enabled: bool | None = None
    penalty_percent_per_breach: Decimal | None = None
    bonus_enabled: bool | None = None
    bonus_percent_on_exceed: Decimal | None = None
    business_hours_only: bool | None = None
    business_hours_start: str | None = None
    business_hours_end: str | None = None
    is_active: bool | None = None
    notes: str | None = None


class SLAConfigResponse(SLAConfigBase):
    """Response schema for SLAConfig."""

    id: UUID
    code: str | None = None
    service_id: UUID | None = None
    client_id: UUID | None = None
    contract_id: UUID | None = None
    is_active: bool = True
    is_default: bool = False
    total_orders: int = 0
    orders_within_sla: int = 0
    orders_breached: int = 0
    current_compliance_percent: Decimal | None = None
    compliance_status: str = "sem_dados"
    breach_rate: float = 0.0
    ativo: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


# ============================================================
# AI SCHEMAS
# ============================================================


class ServiceAnalysis(BaseModel):
    """AI analysis of service performance."""

    service_id: UUID
    service_name: str
    performance_score: float = Field(..., ge=0, le=100)
    revenue_score: float = Field(..., ge=0, le=100)
    demand_score: float = Field(..., ge=0, le=100)
    efficiency_score: float = Field(..., ge=0, le=100)
    trends: dict[str, Any] = {}
    insights: list[str] = []
    recommendations: list[str] = []


class ServiceRecommendation(BaseModel):
    """Service recommendation."""

    service_id: UUID
    service_name: str
    recommendation_type: str
    confidence: float = Field(..., ge=0, le=1)
    reason: str
    potential_impact: str | None = None
    priority: str = "normal"


class SLAAnalysis(BaseModel):
    """SLA compliance analysis."""

    sla_id: UUID
    sla_name: str
    compliance_percent: float
    trend: str  # improving, stable, declining
    at_risk_orders: int = 0
    breach_forecast: dict[str, Any] = {}
    recommendations: list[str] = []
