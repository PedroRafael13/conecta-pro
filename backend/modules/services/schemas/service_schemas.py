"""
Service Schemas - Pydantic Models
Sprint 31: Gestão de Serviços
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field

from modules.services.models.service_catalog import (
    ServiceCategory, ServiceType, ServiceStatus
)
from modules.services.models.service_order import OrderStatus, OrderPriority
from modules.services.models.service_execution import ExecutionStatus
from modules.services.models.service_report import ReportType
from modules.services.models.sla_config import SLAMetricType


# ============================================================
# SERVICE CATALOG SCHEMAS
# ============================================================

class ServiceCatalogBase(BaseModel):
    """Base schema for ServiceCatalog."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    category: ServiceCategory = ServiceCategory.OUTROS
    service_type: ServiceType = ServiceType.RECORRENTE
    base_price: Optional[Decimal] = Field(None, ge=0)
    unit_price: Optional[Decimal] = Field(None, ge=0)
    price_unit: Optional[str] = Field(None, max_length=50)
    estimated_duration_hours: Optional[Decimal] = Field(None, ge=0)
    required_skills: Optional[List[str]] = None
    requires_scheduling: bool = True
    requires_approval: bool = False
    allows_remote: bool = False
    is_emergency_available: bool = False
    emergency_surcharge_percent: Optional[Decimal] = Field(None, ge=0, le=100)
    default_sla_response_hours: Optional[int] = Field(None, ge=0)
    default_sla_resolution_hours: Optional[int] = Field(None, ge=0)
    tags: Optional[List[str]] = None


class ServiceCatalogCreate(ServiceCatalogBase):
    """Schema for creating a service catalog entry."""


class ServiceCatalogUpdate(BaseModel):
    """Schema for updating a service catalog entry."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    category: Optional[ServiceCategory] = None
    service_type: Optional[ServiceType] = None
    status: Optional[ServiceStatus] = None
    base_price: Optional[Decimal] = Field(None, ge=0)
    unit_price: Optional[Decimal] = Field(None, ge=0)
    price_unit: Optional[str] = None
    estimated_duration_hours: Optional[Decimal] = Field(None, ge=0)
    required_skills: Optional[List[str]] = None
    requires_scheduling: Optional[bool] = None
    requires_approval: Optional[bool] = None
    allows_remote: Optional[bool] = None
    is_emergency_available: Optional[bool] = None
    emergency_surcharge_percent: Optional[Decimal] = Field(None, ge=0, le=100)
    default_sla_response_hours: Optional[int] = Field(None, ge=0)
    default_sla_resolution_hours: Optional[int] = Field(None, ge=0)
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class ServiceCatalogResponse(ServiceCatalogBase):
    """Response schema for ServiceCatalog."""
    id: UUID
    code: str
    status: ServiceStatus
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    min_team_size: Optional[int] = None
    max_team_size: Optional[int] = None
    total_orders: int = 0
    completed_orders: int = 0
    avg_rating: Optional[Decimal] = None
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
    base_price: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    avg_rating: Optional[Decimal] = None
    total_orders: int = 0
    is_available: bool = True

    class Config:
        """Pydantic config."""
        from_attributes = True


class ServiceCatalogStats(BaseModel):
    """Statistics for ServiceCatalog."""
    total_services: int = 0
    active_services: int = 0
    by_category: Dict[str, int] = {}
    by_type: Dict[str, int] = {}
    total_revenue: Decimal = Decimal("0")
    avg_rating: Optional[float] = None


# ============================================================
# SERVICE ORDER SCHEMAS
# ============================================================

class ServiceOrderBase(BaseModel):
    """Base schema for ServiceOrder."""
    service_id: UUID
    client_id: UUID
    condominium_id: Optional[UUID] = None
    contract_id: Optional[UUID] = None
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    requirements: Optional[str] = None
    priority: OrderPriority = OrderPriority.NORMAL
    requester_name: Optional[str] = Field(None, max_length=200)
    requester_email: Optional[str] = Field(None, max_length=255)
    requester_phone: Optional[str] = Field(None, max_length=20)
    location_address: Optional[str] = Field(None, max_length=500)
    requested_date: Optional[date] = None
    requested_time_start: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    requested_time_end: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    is_flexible_schedule: bool = True
    estimated_value: Optional[Decimal] = Field(None, ge=0)


class ServiceOrderCreate(ServiceOrderBase):
    """Schema for creating a service order."""
    special_instructions: Optional[str] = None


class ServiceOrderUpdate(BaseModel):
    """Schema for updating a service order."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    requirements: Optional[str] = None
    special_instructions: Optional[str] = None
    priority: Optional[OrderPriority] = None
    requester_name: Optional[str] = None
    requester_email: Optional[str] = None
    requester_phone: Optional[str] = None
    location_address: Optional[str] = None
    location_details: Optional[str] = None
    requested_date: Optional[date] = None
    requested_time_start: Optional[str] = None
    requested_time_end: Optional[str] = None
    scheduled_date: Optional[date] = None
    scheduled_time_start: Optional[str] = None
    scheduled_time_end: Optional[str] = None
    estimated_value: Optional[Decimal] = None
    discount_value: Optional[Decimal] = None
    discount_reason: Optional[str] = None
    internal_notes: Optional[str] = None


class ServiceOrderResponse(ServiceOrderBase):
    """Response schema for ServiceOrder."""
    id: UUID
    order_number: str
    status: OrderStatus
    scheduled_date: Optional[date] = None
    scheduled_time_start: Optional[str] = None
    scheduled_time_end: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    actual_duration_hours: Optional[Decimal] = None
    final_value: Optional[Decimal] = None
    discount_value: Optional[Decimal] = None
    additional_charges: Optional[Decimal] = None
    rating: Optional[int] = None
    assigned_technician_name: Optional[str] = None
    sla_response_met: Optional[bool] = None
    sla_resolution_met: Optional[bool] = None
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
    scheduled_date: Optional[date] = None
    assigned_technician_name: Optional[str] = None
    is_overdue: bool = False
    created_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True


class ServiceOrderFilter(BaseModel):
    """Filter for ServiceOrder queries."""
    status: Optional[OrderStatus] = None
    priority: Optional[OrderPriority] = None
    client_id: Optional[UUID] = None
    condominium_id: Optional[UUID] = None
    service_id: Optional[UUID] = None
    technician_id: Optional[UUID] = None
    scheduled_date_from: Optional[date] = None
    scheduled_date_to: Optional[date] = None
    is_overdue: Optional[bool] = None
    search: Optional[str] = None


class ServiceOrderStats(BaseModel):
    """Statistics for ServiceOrders."""
    total_orders: int = 0
    by_status: Dict[str, int] = {}
    by_priority: Dict[str, int] = {}
    overdue_count: int = 0
    avg_completion_time_hours: Optional[float] = None
    avg_rating: Optional[float] = None
    sla_compliance_percent: Optional[float] = None


# ============================================================
# SERVICE EXECUTION SCHEMAS
# ============================================================

class ServiceExecutionBase(BaseModel):
    """Base schema for ServiceExecution."""
    order_id: UUID
    technician_id: Optional[UUID] = None
    technician_name: Optional[str] = Field(None, max_length=200)
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None


class ServiceExecutionCreate(ServiceExecutionBase):
    """Schema for creating a service execution."""
    checklist_items: Optional[List[Dict[str, Any]]] = None


class ServiceExecutionUpdate(BaseModel):
    """Schema for updating a service execution."""
    technician_id: Optional[UUID] = None
    technician_name: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    work_description: Optional[str] = None
    findings: Optional[str] = None
    recommendations: Optional[str] = None
    internal_notes: Optional[str] = None
    client_notes: Optional[str] = None
    labor_cost: Optional[Decimal] = None
    travel_cost: Optional[Decimal] = None


class ServiceExecutionResponse(ServiceExecutionBase):
    """Response schema for ServiceExecution."""
    id: UUID
    execution_number: str
    sequence: int
    status: ExecutionStatus
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    travel_duration_minutes: Optional[int] = None
    execution_duration_minutes: Optional[int] = None
    total_duration_minutes: Optional[int] = None
    work_description: Optional[str] = None
    findings: Optional[str] = None
    recommendations: Optional[str] = None
    checklist_completed: bool = False
    checklist_completion_percent: Optional[Decimal] = None
    materials_cost: Optional[Decimal] = None
    total_cost: Optional[Decimal] = None
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
    summary: Optional[str] = None
    findings: Optional[str] = None
    conclusions: Optional[str] = None
    recommendations: Optional[str] = None


class ServiceReportCreate(ServiceReportBase):
    """Schema for creating a service report."""
    author_id: Optional[UUID] = None
    author_name: Optional[str] = None


class ServiceReportUpdate(BaseModel):
    """Schema for updating a service report."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    summary: Optional[str] = None
    introduction: Optional[str] = None
    methodology: Optional[str] = None
    findings: Optional[str] = None
    analysis: Optional[str] = None
    conclusions: Optional[str] = None
    recommendations: Optional[str] = None
    sections: Optional[List[Dict[str, Any]]] = None


class ServiceReportResponse(ServiceReportBase):
    """Response schema for ServiceReport."""
    id: UUID
    report_number: str
    author_name: Optional[str] = None
    reviewer_name: Optional[str] = None
    is_draft: bool = True
    is_reviewed: bool = False
    is_approved: bool = False
    is_sent: bool = False
    version: int = 1
    pdf_url: Optional[str] = None
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
    description: Optional[str] = None
    metric_type: SLAMetricType = SLAMetricType.TEMPO_RESOLUCAO
    response_time_minutes: Optional[int] = Field(None, ge=0)
    resolution_time_minutes: Optional[int] = Field(None, ge=0)
    target_availability_percent: Optional[Decimal] = Field(
        None, ge=0, le=100
    )
    penalty_enabled: bool = False
    penalty_percent_per_breach: Optional[Decimal] = Field(None, ge=0, le=100)
    bonus_enabled: bool = False
    business_hours_only: bool = True


class SLAConfigCreate(SLAConfigBase):
    """Schema for creating an SLA config."""
    service_id: Optional[UUID] = None
    client_id: Optional[UUID] = None
    contract_id: Optional[UUID] = None


class SLAConfigUpdate(BaseModel):
    """Schema for updating an SLA config."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    response_time_minutes: Optional[int] = Field(None, ge=0)
    resolution_time_minutes: Optional[int] = Field(None, ge=0)
    target_availability_percent: Optional[Decimal] = None
    penalty_enabled: Optional[bool] = None
    penalty_percent_per_breach: Optional[Decimal] = None
    bonus_enabled: Optional[bool] = None
    bonus_percent_on_exceed: Optional[Decimal] = None
    business_hours_only: Optional[bool] = None
    business_hours_start: Optional[str] = None
    business_hours_end: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class SLAConfigResponse(SLAConfigBase):
    """Response schema for SLAConfig."""
    id: UUID
    code: Optional[str] = None
    service_id: Optional[UUID] = None
    client_id: Optional[UUID] = None
    contract_id: Optional[UUID] = None
    is_active: bool = True
    is_default: bool = False
    total_orders: int = 0
    orders_within_sla: int = 0
    orders_breached: int = 0
    current_compliance_percent: Optional[Decimal] = None
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
    trends: Dict[str, Any] = {}
    insights: List[str] = []
    recommendations: List[str] = []


class ServiceRecommendation(BaseModel):
    """Service recommendation."""
    service_id: UUID
    service_name: str
    recommendation_type: str
    confidence: float = Field(..., ge=0, le=1)
    reason: str
    potential_impact: Optional[str] = None
    priority: str = "normal"


class SLAAnalysis(BaseModel):
    """SLA compliance analysis."""
    sla_id: UUID
    sla_name: str
    compliance_percent: float
    trend: str  # improving, stable, declining
    at_risk_orders: int = 0
    breach_forecast: Dict[str, Any] = {}
    recommendations: List[str] = []
