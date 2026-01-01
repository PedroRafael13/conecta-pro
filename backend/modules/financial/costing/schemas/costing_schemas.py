"""Costing Schemas - Validação Pydantic para ABC e Rateio."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from modules.financial.costing.models import (
    ActivityLevel,
    ActivityStatus,
    ActivityType,
    AllocationBasis,
    AllocationMethod,
    AllocationStatus,
    AllocationType,
    AnalysisScope,
    AnalysisStatus,
    AnalysisType,
    CostObjectStatus,
    CostObjectType,
    DriverCategory,
    DriverMeasureUnit,
    DriverStatus,
    DriverType,
    PoolStatus,
    PoolType,
    ProfitabilityLevel,
    ReportFormat,
    ValueAddedType,
)


# =============================================================================
# COST DRIVER SCHEMAS
# =============================================================================


class CostDriverBase(BaseModel):
    """Schema base para Cost Driver."""

    code: str = Field(..., min_length=1, max_length=30)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    driver_type: DriverType = DriverType.TRANSACTION
    driver_category: DriverCategory = DriverCategory.ACTIVITY
    measure_unit: DriverMeasureUnit = DriverMeasureUnit.QUANTITY
    measure_symbol: Optional[str] = Field(None, max_length=10)
    unit_cost: Decimal = Field(default=Decimal("0"), ge=0)
    practical_capacity: Optional[Decimal] = Field(None, ge=0)
    theoretical_capacity: Optional[Decimal] = Field(None, ge=0)
    custom_formula: Optional[str] = None
    formula_variables: Optional[dict] = None
    data_source: Optional[str] = Field(None, max_length=100)
    is_automated: bool = False
    notes: Optional[str] = None
    tags: Optional[list[str]] = None


class CostDriverCreate(CostDriverBase):
    """Schema para criar Cost Driver."""

    condominio_id: UUID


class CostDriverUpdate(BaseModel):
    """Schema para atualizar Cost Driver."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    driver_type: Optional[DriverType] = None
    driver_category: Optional[DriverCategory] = None
    status: Optional[DriverStatus] = None
    measure_unit: Optional[DriverMeasureUnit] = None
    measure_symbol: Optional[str] = Field(None, max_length=10)
    unit_cost: Optional[Decimal] = Field(None, ge=0)
    practical_capacity: Optional[Decimal] = Field(None, ge=0)
    theoretical_capacity: Optional[Decimal] = Field(None, ge=0)
    custom_formula: Optional[str] = None
    formula_variables: Optional[dict] = None
    is_automated: Optional[bool] = None
    notes: Optional[str] = None
    tags: Optional[list[str]] = None
    active: Optional[bool] = None


class CostDriverResponse(CostDriverBase):
    """Schema de resposta para Cost Driver."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    condominio_id: UUID
    status: DriverStatus
    used_capacity: Decimal
    total_allocations: int
    total_allocated_amount: Decimal
    average_rate: Decimal
    is_primary: bool
    active: bool
    created_at: datetime
    updated_at: datetime

    @property
    def capacity_usage_percent(self) -> Decimal:
        """Calcula uso da capacidade."""
        if not self.practical_capacity or self.practical_capacity == 0:
            return Decimal("0")
        return (self.used_capacity / self.practical_capacity) * 100


class CostDriverFilter(BaseModel):
    """Filtros para Cost Driver."""

    driver_type: Optional[DriverType] = None
    driver_category: Optional[DriverCategory] = None
    status: Optional[DriverStatus] = None
    is_automated: Optional[bool] = None
    active: Optional[bool] = None
    search: Optional[str] = None


# =============================================================================
# COST ACTIVITY SCHEMAS
# =============================================================================


class CostActivityBase(BaseModel):
    """Schema base para Cost Activity."""

    code: str = Field(..., min_length=1, max_length=30)
    name: str = Field(..., min_length=1, max_length=150)
    short_name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=2000)
    activity_type: ActivityType = ActivityType.PRIMARY
    activity_level: ActivityLevel = ActivityLevel.UNIT
    value_added_type: ValueAddedType = ValueAddedType.VALUE_ADDED
    parent_id: Optional[UUID] = None
    cost_pool_id: Optional[UUID] = None
    primary_driver_id: Optional[UUID] = None
    cost_center_id: Optional[UUID] = None
    practical_capacity: Optional[Decimal] = Field(None, ge=0)
    capacity_unit: Optional[str] = Field(None, max_length=20)
    standard_time: Optional[Decimal] = Field(None, ge=0)
    process_name: Optional[str] = Field(None, max_length=100)
    subprocess_name: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    responsible_name: Optional[str] = Field(None, max_length=100)
    is_core: bool = False
    is_outsourceable: bool = False
    is_automatable: bool = False
    notes: Optional[str] = None
    tags: Optional[list[str]] = None


class CostActivityCreate(CostActivityBase):
    """Schema para criar Cost Activity."""

    condominio_id: UUID


class CostActivityUpdate(BaseModel):
    """Schema para atualizar Cost Activity."""

    name: Optional[str] = Field(None, min_length=1, max_length=150)
    short_name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=2000)
    activity_type: Optional[ActivityType] = None
    activity_level: Optional[ActivityLevel] = None
    status: Optional[ActivityStatus] = None
    value_added_type: Optional[ValueAddedType] = None
    parent_id: Optional[UUID] = None
    cost_pool_id: Optional[UUID] = None
    primary_driver_id: Optional[UUID] = None
    cost_center_id: Optional[UUID] = None
    practical_capacity: Optional[Decimal] = Field(None, ge=0)
    standard_time: Optional[Decimal] = Field(None, ge=0)
    benchmark_cost: Optional[Decimal] = Field(None, ge=0)
    benchmark_time: Optional[Decimal] = Field(None, ge=0)
    is_core: Optional[bool] = None
    is_outsourceable: Optional[bool] = None
    is_automatable: Optional[bool] = None
    notes: Optional[str] = None
    tags: Optional[list[str]] = None
    active: Optional[bool] = None


class CostActivityResponse(CostActivityBase):
    """Schema de resposta para Cost Activity."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    condominio_id: UUID
    status: ActivityStatus
    level: int
    path: Optional[str]
    total_cost: Decimal
    fixed_cost: Decimal
    variable_cost: Decimal
    allocated_cost: Decimal
    activity_rate: Decimal
    used_capacity: Decimal
    actual_time: Optional[Decimal]
    time_variance: Optional[Decimal]
    executions_count: int
    benchmark_cost: Optional[Decimal]
    benchmark_time: Optional[Decimal]
    active: bool
    created_at: datetime
    updated_at: datetime


class CostActivityFilter(BaseModel):
    """Filtros para Cost Activity."""

    activity_type: Optional[ActivityType] = None
    activity_level: Optional[ActivityLevel] = None
    status: Optional[ActivityStatus] = None
    value_added_type: Optional[ValueAddedType] = None
    cost_pool_id: Optional[UUID] = None
    cost_center_id: Optional[UUID] = None
    is_core: Optional[bool] = None
    is_outsourceable: Optional[bool] = None
    is_automatable: Optional[bool] = None
    active: Optional[bool] = None
    search: Optional[str] = None


# =============================================================================
# COST POOL SCHEMAS
# =============================================================================


class CostPoolBase(BaseModel):
    """Schema base para Cost Pool."""

    code: str = Field(..., min_length=1, max_length=30)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    pool_type: PoolType = PoolType.OVERHEAD
    allocation_basis: AllocationBasis = AllocationBasis.ACTIVITY_BASED
    parent_id: Optional[UUID] = None
    cost_center_id: Optional[UUID] = None
    budget_amount: Decimal = Field(default=Decimal("0"), ge=0)
    custom_allocation_formula: Optional[str] = None
    allocation_weights: Optional[dict] = None
    manager_name: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    is_homogeneous: bool = True
    auto_allocate: bool = False
    notes: Optional[str] = None
    tags: Optional[list[str]] = None


class CostPoolCreate(CostPoolBase):
    """Schema para criar Cost Pool."""

    condominio_id: UUID


class CostPoolUpdate(BaseModel):
    """Schema para atualizar Cost Pool."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    pool_type: Optional[PoolType] = None
    status: Optional[PoolStatus] = None
    allocation_basis: Optional[AllocationBasis] = None
    parent_id: Optional[UUID] = None
    cost_center_id: Optional[UUID] = None
    budget_amount: Optional[Decimal] = Field(None, ge=0)
    custom_allocation_formula: Optional[str] = None
    allocation_weights: Optional[dict] = None
    is_homogeneous: Optional[bool] = None
    auto_allocate: Optional[bool] = None
    notes: Optional[str] = None
    tags: Optional[list[str]] = None
    active: Optional[bool] = None


class CostPoolResponse(CostPoolBase):
    """Schema de resposta para Cost Pool."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    condominio_id: UUID
    status: PoolStatus
    level: int
    path: Optional[str]
    total_cost: Decimal
    allocated_cost: Decimal
    unallocated_cost: Decimal
    budget_variance: Decimal
    allocation_base_quantity: Decimal
    allocation_rate: Decimal
    activities_count: int
    allocations_count: int
    active: bool
    created_at: datetime
    updated_at: datetime


class CostPoolFilter(BaseModel):
    """Filtros para Cost Pool."""

    pool_type: Optional[PoolType] = None
    status: Optional[PoolStatus] = None
    allocation_basis: Optional[AllocationBasis] = None
    cost_center_id: Optional[UUID] = None
    is_homogeneous: Optional[bool] = None
    active: Optional[bool] = None
    search: Optional[str] = None


class CostPoolAddCost(BaseModel):
    """Schema para adicionar custo ao pool."""

    amount: Decimal = Field(..., gt=0)
    component_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None


# =============================================================================
# COST OBJECT SCHEMAS
# =============================================================================


class CostObjectBase(BaseModel):
    """Schema base para Cost Object."""

    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=150)
    short_name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=2000)
    object_type: CostObjectType = CostObjectType.SERVICE
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    parent_id: Optional[UUID] = None
    reference_type: Optional[str] = Field(None, max_length=50)
    reference_id: Optional[UUID] = None
    revenue_budget: Decimal = Field(default=Decimal("0"), ge=0)
    cost_budget: Decimal = Field(default=Decimal("0"), ge=0)
    quantity: Decimal = Field(default=Decimal("0"), ge=0)
    unit_of_measure: Optional[str] = Field(None, max_length=20)
    unit_price: Decimal = Field(default=Decimal("0"), ge=0)
    owner_name: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    is_strategic: bool = False
    notes: Optional[str] = None
    tags: Optional[list[str]] = None


class CostObjectCreate(CostObjectBase):
    """Schema para criar Cost Object."""

    condominio_id: UUID


class CostObjectUpdate(BaseModel):
    """Schema para atualizar Cost Object."""

    name: Optional[str] = Field(None, min_length=1, max_length=150)
    short_name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=2000)
    object_type: Optional[CostObjectType] = None
    status: Optional[CostObjectStatus] = None
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    parent_id: Optional[UUID] = None
    revenue: Optional[Decimal] = Field(None, ge=0)
    revenue_budget: Optional[Decimal] = Field(None, ge=0)
    cost_budget: Optional[Decimal] = Field(None, ge=0)
    quantity: Optional[Decimal] = Field(None, ge=0)
    unit_price: Optional[Decimal] = Field(None, ge=0)
    is_strategic: Optional[bool] = None
    notes: Optional[str] = None
    tags: Optional[list[str]] = None
    active: Optional[bool] = None


class CostObjectResponse(CostObjectBase):
    """Schema de resposta para Cost Object."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    condominio_id: UUID
    status: CostObjectStatus
    level: int
    path: Optional[str]
    revenue: Decimal
    direct_material_cost: Decimal
    direct_labor_cost: Decimal
    other_direct_cost: Decimal
    total_direct_cost: Decimal
    allocated_overhead: Decimal
    allocated_activity_cost: Decimal
    total_indirect_cost: Decimal
    total_cost: Decimal
    cost_variance: Decimal
    gross_margin: Decimal
    gross_margin_percent: Decimal
    contribution_margin: Decimal
    contribution_margin_percent: Decimal
    net_margin: Decimal
    net_margin_percent: Decimal
    profitability_level: Optional[ProfitabilityLevel]
    profitability_score: Optional[Decimal]
    unit_cost: Decimal
    allocations_count: int
    active: bool
    created_at: datetime
    updated_at: datetime


class CostObjectFilter(BaseModel):
    """Filtros para Cost Object."""

    object_type: Optional[CostObjectType] = None
    status: Optional[CostObjectStatus] = None
    profitability_level: Optional[ProfitabilityLevel] = None
    category: Optional[str] = None
    is_strategic: Optional[bool] = None
    is_profitable: Optional[bool] = None
    active: Optional[bool] = None
    search: Optional[str] = None


class CostObjectAddDirectCost(BaseModel):
    """Schema para adicionar custo direto."""

    material_cost: Optional[Decimal] = Field(None, ge=0)
    labor_cost: Optional[Decimal] = Field(None, ge=0)
    other_cost: Optional[Decimal] = Field(None, ge=0)
    description: Optional[str] = None


# =============================================================================
# COST ALLOCATION SCHEMAS
# =============================================================================


class CostAllocationBase(BaseModel):
    """Schema base para Cost Allocation."""

    description: Optional[str] = Field(None, max_length=200)
    reference: Optional[str] = Field(None, max_length=100)
    allocation_type: AllocationType = AllocationType.ACTIVITY_TO_OBJECT
    allocation_method: AllocationMethod = AllocationMethod.DRIVER_BASED
    source_pool_id: Optional[UUID] = None
    source_activity_id: Optional[UUID] = None
    source_cost_center_id: Optional[UUID] = None
    activity_id: Optional[UUID] = None
    cost_object_id: Optional[UUID] = None
    target_cost_center_id: Optional[UUID] = None
    driver_id: Optional[UUID] = None
    allocated_amount: Decimal = Field(..., gt=0)
    driver_quantity: Optional[Decimal] = Field(None, ge=0)
    driver_rate: Optional[Decimal] = Field(None, ge=0)
    allocation_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    allocation_weight: Optional[Decimal] = Field(None, ge=0)
    reference_period: str = Field(..., min_length=7, max_length=7)  # "2024-01"
    notes: Optional[str] = None

    @field_validator("reference_period")
    @classmethod
    def validate_period(cls, v: str) -> str:
        """Valida formato do período."""
        if not v or len(v) != 7 or v[4] != "-":
            raise ValueError("Período deve estar no formato YYYY-MM")
        try:
            year = int(v[:4])
            month = int(v[5:7])
            if not (1 <= month <= 12) or not (2000 <= year <= 2100):
                raise ValueError
        except ValueError:
            raise ValueError("Período inválido")
        return v


class CostAllocationCreate(CostAllocationBase):
    """Schema para criar Cost Allocation."""

    condominio_id: UUID
    allocation_date: datetime = Field(default_factory=datetime.utcnow)


class CostAllocationUpdate(BaseModel):
    """Schema para atualizar Cost Allocation."""

    description: Optional[str] = Field(None, max_length=200)
    reference: Optional[str] = Field(None, max_length=100)
    allocated_amount: Optional[Decimal] = Field(None, gt=0)
    driver_quantity: Optional[Decimal] = Field(None, ge=0)
    driver_rate: Optional[Decimal] = Field(None, ge=0)
    allocation_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    notes: Optional[str] = None


class CostAllocationResponse(CostAllocationBase):
    """Schema de resposta para Cost Allocation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    condominio_id: UUID
    allocation_number: str
    batch_id: Optional[UUID]
    status: AllocationStatus
    allocation_date: datetime
    effective_date: Optional[datetime]
    is_validated: bool
    validated_at: Optional[datetime]
    approved_at: Optional[datetime]
    executed_at: Optional[datetime]
    is_reversed: bool
    reversed_at: Optional[datetime]
    reversal_reason: Optional[str]
    is_posted: bool
    is_automatic: bool
    is_recurring: bool
    active: bool
    created_at: datetime
    updated_at: datetime


class CostAllocationFilter(BaseModel):
    """Filtros para Cost Allocation."""

    allocation_type: Optional[AllocationType] = None
    status: Optional[AllocationStatus] = None
    allocation_method: Optional[AllocationMethod] = None
    source_pool_id: Optional[UUID] = None
    activity_id: Optional[UUID] = None
    cost_object_id: Optional[UUID] = None
    driver_id: Optional[UUID] = None
    reference_period: Optional[str] = None
    batch_id: Optional[UUID] = None
    is_reversed: Optional[bool] = None
    is_posted: Optional[bool] = None
    active: Optional[bool] = None


class CostAllocationApprove(BaseModel):
    """Schema para aprovar alocação."""

    notes: Optional[str] = None


class CostAllocationReverse(BaseModel):
    """Schema para estornar alocação."""

    reason: str = Field(..., min_length=5, max_length=500)


class CostAllocationBatch(BaseModel):
    """Schema para criar lote de alocações."""

    allocations: list[CostAllocationCreate] = Field(..., min_length=1)
    execute_immediately: bool = False
    description: Optional[str] = None


# =============================================================================
# COST ANALYSIS SCHEMAS
# =============================================================================


class CostAnalysisBase(BaseModel):
    """Schema base para Cost Analysis."""

    code: str = Field(..., min_length=1, max_length=30)
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = Field(None, max_length=2000)
    analysis_type: AnalysisType = AnalysisType.ABC_COSTING
    scope: AnalysisScope = AnalysisScope.GLOBAL
    period_start: datetime
    period_end: datetime
    cost_center_ids: Optional[list[UUID]] = None
    activity_ids: Optional[list[UUID]] = None
    pool_ids: Optional[list[UUID]] = None
    object_ids: Optional[list[UUID]] = None
    filters: Optional[dict] = None
    parameters: Optional[dict] = None
    scenarios: Optional[list[dict]] = None
    comparison_period_start: Optional[datetime] = None
    comparison_period_end: Optional[datetime] = None
    is_scheduled: bool = False
    schedule_cron: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    tags: Optional[list[str]] = None


class CostAnalysisCreate(CostAnalysisBase):
    """Schema para criar Cost Analysis."""

    condominio_id: UUID


class CostAnalysisUpdate(BaseModel):
    """Schema para atualizar Cost Analysis."""

    name: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = Field(None, max_length=2000)
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    filters: Optional[dict] = None
    parameters: Optional[dict] = None
    scenarios: Optional[list[dict]] = None
    is_scheduled: Optional[bool] = None
    schedule_cron: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    tags: Optional[list[str]] = None
    active: Optional[bool] = None


class CostAnalysisResponse(CostAnalysisBase):
    """Schema de resposta para Cost Analysis."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    condominio_id: UUID
    status: AnalysisStatus
    reference_period: Optional[str]
    results: Optional[dict]
    total_cost: Decimal
    total_revenue: Decimal
    total_margin: Decimal
    margin_percent: Decimal
    total_direct_cost: Decimal
    total_indirect_cost: Decimal
    total_allocated: Decimal
    unallocated_cost: Decimal
    practical_capacity: Optional[Decimal]
    used_capacity: Optional[Decimal]
    idle_capacity: Optional[Decimal]
    idle_capacity_cost: Optional[Decimal]
    cost_variance: Optional[Decimal]
    break_even_units: Optional[Decimal]
    break_even_revenue: Optional[Decimal]
    safety_margin: Optional[Decimal]
    insights: Optional[list[dict]]
    recommendations: Optional[list[dict]]
    alerts: Optional[list[dict]]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    execution_time_ms: Optional[int]
    report_format: Optional[ReportFormat]
    report_path: Optional[str]
    is_template: bool
    is_favorite: bool
    active: bool
    created_at: datetime
    updated_at: datetime


class CostAnalysisFilter(BaseModel):
    """Filtros para Cost Analysis."""

    analysis_type: Optional[AnalysisType] = None
    status: Optional[AnalysisStatus] = None
    scope: Optional[AnalysisScope] = None
    is_scheduled: Optional[bool] = None
    is_template: Optional[bool] = None
    is_favorite: Optional[bool] = None
    active: Optional[bool] = None
    search: Optional[str] = None


class CostAnalysisRun(BaseModel):
    """Schema para executar análise."""

    force_recalculate: bool = False
    generate_report: bool = False
    report_format: Optional[ReportFormat] = None


# =============================================================================
# STATISTICS AND DASHBOARD SCHEMAS
# =============================================================================


class CostingStats(BaseModel):
    """Estatísticas gerais de custos."""

    total_drivers: int
    total_activities: int
    total_pools: int
    total_objects: int
    total_allocations: int

    total_cost: Decimal
    total_allocated: Decimal
    total_unallocated: Decimal
    allocation_percent: Decimal

    total_revenue: Decimal
    total_margin: Decimal
    margin_percent: Decimal

    practical_capacity: Decimal
    used_capacity: Decimal
    idle_capacity: Decimal
    capacity_usage_percent: Decimal

    profitable_objects: int
    unprofitable_objects: int
    profitability_rate: Decimal


class ABCDashboard(BaseModel):
    """Dashboard ABC."""

    period: str
    cost_breakdown: list[dict]  # Por tipo de custo
    activity_costs: list[dict]  # Top atividades por custo
    object_profitability: list[dict]  # Rentabilidade por objeto
    capacity_analysis: dict  # Análise de capacidade
    trends: list[dict]  # Tendências
    alerts: list[dict]  # Alertas


class CostTrend(BaseModel):
    """Tendência de custo."""

    period: str
    total_cost: Decimal
    direct_cost: Decimal
    indirect_cost: Decimal
    allocated_cost: Decimal
    variance: Decimal
    variance_percent: Decimal


class AllocationSummary(BaseModel):
    """Resumo de alocações por período."""

    period: str
    total_allocations: int
    total_amount: Decimal
    by_type: dict[str, Decimal]
    by_method: dict[str, Decimal]
    pending_count: int
    pending_amount: Decimal
