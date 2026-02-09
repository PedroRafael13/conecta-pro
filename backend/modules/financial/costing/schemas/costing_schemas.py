"""Costing Schemas - Validação Pydantic para ABC e Rateio."""

from datetime import datetime
from decimal import Decimal
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
    description: str | None = Field(None, max_length=1000)
    driver_type: DriverType = DriverType.TRANSACTION
    driver_category: DriverCategory = DriverCategory.ACTIVITY
    measure_unit: DriverMeasureUnit = DriverMeasureUnit.QUANTITY
    measure_symbol: str | None = Field(None, max_length=10)
    unit_cost: Decimal = Field(default=Decimal("0"), ge=0)
    practical_capacity: Decimal | None = Field(None, ge=0)
    theoretical_capacity: Decimal | None = Field(None, ge=0)
    custom_formula: str | None = None
    formula_variables: dict | None = None
    data_source: str | None = Field(None, max_length=100)
    is_automated: bool = False
    notes: str | None = None
    tags: list[str] | None = None


class CostDriverCreate(CostDriverBase):
    """Schema para criar Cost Driver."""

    condominio_id: UUID


class CostDriverUpdate(BaseModel):
    """Schema para atualizar Cost Driver."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=1000)
    driver_type: DriverType | None = None
    driver_category: DriverCategory | None = None
    status: DriverStatus | None = None
    measure_unit: DriverMeasureUnit | None = None
    measure_symbol: str | None = Field(None, max_length=10)
    unit_cost: Decimal | None = Field(None, ge=0)
    practical_capacity: Decimal | None = Field(None, ge=0)
    theoretical_capacity: Decimal | None = Field(None, ge=0)
    custom_formula: str | None = None
    formula_variables: dict | None = None
    is_automated: bool | None = None
    notes: str | None = None
    tags: list[str] | None = None
    active: bool | None = None


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

    driver_type: DriverType | None = None
    driver_category: DriverCategory | None = None
    status: DriverStatus | None = None
    is_automated: bool | None = None
    active: bool | None = None
    search: str | None = None


# =============================================================================
# COST ACTIVITY SCHEMAS
# =============================================================================


class CostActivityBase(BaseModel):
    """Schema base para Cost Activity."""

    code: str = Field(..., min_length=1, max_length=30)
    name: str = Field(..., min_length=1, max_length=150)
    short_name: str | None = Field(None, max_length=50)
    description: str | None = Field(None, max_length=2000)
    activity_type: ActivityType = ActivityType.PRIMARY
    activity_level: ActivityLevel = ActivityLevel.UNIT
    value_added_type: ValueAddedType = ValueAddedType.VALUE_ADDED
    parent_id: UUID | None = None
    cost_pool_id: UUID | None = None
    primary_driver_id: UUID | None = None
    cost_center_id: UUID | None = None
    practical_capacity: Decimal | None = Field(None, ge=0)
    capacity_unit: str | None = Field(None, max_length=20)
    standard_time: Decimal | None = Field(None, ge=0)
    process_name: str | None = Field(None, max_length=100)
    subprocess_name: str | None = Field(None, max_length=100)
    department: str | None = Field(None, max_length=100)
    responsible_name: str | None = Field(None, max_length=100)
    is_core: bool = False
    is_outsourceable: bool = False
    is_automatable: bool = False
    notes: str | None = None
    tags: list[str] | None = None


class CostActivityCreate(CostActivityBase):
    """Schema para criar Cost Activity."""

    condominio_id: UUID


class CostActivityUpdate(BaseModel):
    """Schema para atualizar Cost Activity."""

    name: str | None = Field(None, min_length=1, max_length=150)
    short_name: str | None = Field(None, max_length=50)
    description: str | None = Field(None, max_length=2000)
    activity_type: ActivityType | None = None
    activity_level: ActivityLevel | None = None
    status: ActivityStatus | None = None
    value_added_type: ValueAddedType | None = None
    parent_id: UUID | None = None
    cost_pool_id: UUID | None = None
    primary_driver_id: UUID | None = None
    cost_center_id: UUID | None = None
    practical_capacity: Decimal | None = Field(None, ge=0)
    standard_time: Decimal | None = Field(None, ge=0)
    benchmark_cost: Decimal | None = Field(None, ge=0)
    benchmark_time: Decimal | None = Field(None, ge=0)
    is_core: bool | None = None
    is_outsourceable: bool | None = None
    is_automatable: bool | None = None
    notes: str | None = None
    tags: list[str] | None = None
    active: bool | None = None


class CostActivityResponse(CostActivityBase):
    """Schema de resposta para Cost Activity."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    condominio_id: UUID
    status: ActivityStatus
    level: int
    path: str | None
    total_cost: Decimal
    fixed_cost: Decimal
    variable_cost: Decimal
    allocated_cost: Decimal
    activity_rate: Decimal
    used_capacity: Decimal
    actual_time: Decimal | None
    time_variance: Decimal | None
    executions_count: int
    benchmark_cost: Decimal | None
    benchmark_time: Decimal | None
    active: bool
    created_at: datetime
    updated_at: datetime


class CostActivityFilter(BaseModel):
    """Filtros para Cost Activity."""

    activity_type: ActivityType | None = None
    activity_level: ActivityLevel | None = None
    status: ActivityStatus | None = None
    value_added_type: ValueAddedType | None = None
    cost_pool_id: UUID | None = None
    cost_center_id: UUID | None = None
    is_core: bool | None = None
    is_outsourceable: bool | None = None
    is_automatable: bool | None = None
    active: bool | None = None
    search: str | None = None


# =============================================================================
# COST POOL SCHEMAS
# =============================================================================


class CostPoolBase(BaseModel):
    """Schema base para Cost Pool."""

    code: str = Field(..., min_length=1, max_length=30)
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=1000)
    pool_type: PoolType = PoolType.OVERHEAD
    allocation_basis: AllocationBasis = AllocationBasis.ACTIVITY_BASED
    parent_id: UUID | None = None
    cost_center_id: UUID | None = None
    budget_amount: Decimal = Field(default=Decimal("0"), ge=0)
    custom_allocation_formula: str | None = None
    allocation_weights: dict | None = None
    manager_name: str | None = Field(None, max_length=100)
    department: str | None = Field(None, max_length=100)
    is_homogeneous: bool = True
    auto_allocate: bool = False
    notes: str | None = None
    tags: list[str] | None = None


class CostPoolCreate(CostPoolBase):
    """Schema para criar Cost Pool."""

    condominio_id: UUID


class CostPoolUpdate(BaseModel):
    """Schema para atualizar Cost Pool."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=1000)
    pool_type: PoolType | None = None
    status: PoolStatus | None = None
    allocation_basis: AllocationBasis | None = None
    parent_id: UUID | None = None
    cost_center_id: UUID | None = None
    budget_amount: Decimal | None = Field(None, ge=0)
    custom_allocation_formula: str | None = None
    allocation_weights: dict | None = None
    is_homogeneous: bool | None = None
    auto_allocate: bool | None = None
    notes: str | None = None
    tags: list[str] | None = None
    active: bool | None = None


class CostPoolResponse(CostPoolBase):
    """Schema de resposta para Cost Pool."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    condominio_id: UUID
    status: PoolStatus
    level: int
    path: str | None
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

    pool_type: PoolType | None = None
    status: PoolStatus | None = None
    allocation_basis: AllocationBasis | None = None
    cost_center_id: UUID | None = None
    is_homogeneous: bool | None = None
    active: bool | None = None
    search: str | None = None


class CostPoolAddCost(BaseModel):
    """Schema para adicionar custo ao pool."""

    amount: Decimal = Field(..., gt=0)
    component_name: str | None = Field(None, max_length=100)
    description: str | None = None


# =============================================================================
# COST OBJECT SCHEMAS
# =============================================================================


class CostObjectBase(BaseModel):
    """Schema base para Cost Object."""

    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=150)
    short_name: str | None = Field(None, max_length=50)
    description: str | None = Field(None, max_length=2000)
    object_type: CostObjectType = CostObjectType.SERVICE
    category: str | None = Field(None, max_length=100)
    subcategory: str | None = Field(None, max_length=100)
    parent_id: UUID | None = None
    reference_type: str | None = Field(None, max_length=50)
    reference_id: UUID | None = None
    revenue_budget: Decimal = Field(default=Decimal("0"), ge=0)
    cost_budget: Decimal = Field(default=Decimal("0"), ge=0)
    quantity: Decimal = Field(default=Decimal("0"), ge=0)
    unit_of_measure: str | None = Field(None, max_length=20)
    unit_price: Decimal = Field(default=Decimal("0"), ge=0)
    owner_name: str | None = Field(None, max_length=100)
    department: str | None = Field(None, max_length=100)
    is_strategic: bool = False
    notes: str | None = None
    tags: list[str] | None = None


class CostObjectCreate(CostObjectBase):
    """Schema para criar Cost Object."""

    condominio_id: UUID


class CostObjectUpdate(BaseModel):
    """Schema para atualizar Cost Object."""

    name: str | None = Field(None, min_length=1, max_length=150)
    short_name: str | None = Field(None, max_length=50)
    description: str | None = Field(None, max_length=2000)
    object_type: CostObjectType | None = None
    status: CostObjectStatus | None = None
    category: str | None = Field(None, max_length=100)
    subcategory: str | None = Field(None, max_length=100)
    parent_id: UUID | None = None
    revenue: Decimal | None = Field(None, ge=0)
    revenue_budget: Decimal | None = Field(None, ge=0)
    cost_budget: Decimal | None = Field(None, ge=0)
    quantity: Decimal | None = Field(None, ge=0)
    unit_price: Decimal | None = Field(None, ge=0)
    is_strategic: bool | None = None
    notes: str | None = None
    tags: list[str] | None = None
    active: bool | None = None


class CostObjectResponse(CostObjectBase):
    """Schema de resposta para Cost Object."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    condominio_id: UUID
    status: CostObjectStatus
    level: int
    path: str | None
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
    profitability_level: ProfitabilityLevel | None
    profitability_score: Decimal | None
    unit_cost: Decimal
    allocations_count: int
    active: bool
    created_at: datetime
    updated_at: datetime


class CostObjectFilter(BaseModel):
    """Filtros para Cost Object."""

    object_type: CostObjectType | None = None
    status: CostObjectStatus | None = None
    profitability_level: ProfitabilityLevel | None = None
    category: str | None = None
    is_strategic: bool | None = None
    is_profitable: bool | None = None
    active: bool | None = None
    search: str | None = None


class CostObjectAddDirectCost(BaseModel):
    """Schema para adicionar custo direto."""

    material_cost: Decimal | None = Field(None, ge=0)
    labor_cost: Decimal | None = Field(None, ge=0)
    other_cost: Decimal | None = Field(None, ge=0)
    description: str | None = None


# =============================================================================
# COST ALLOCATION SCHEMAS
# =============================================================================


class CostAllocationBase(BaseModel):
    """Schema base para Cost Allocation."""

    description: str | None = Field(None, max_length=200)
    reference: str | None = Field(None, max_length=100)
    allocation_type: AllocationType = AllocationType.ACTIVITY_TO_OBJECT
    allocation_method: AllocationMethod = AllocationMethod.DRIVER_BASED
    source_pool_id: UUID | None = None
    source_activity_id: UUID | None = None
    source_cost_center_id: UUID | None = None
    activity_id: UUID | None = None
    cost_object_id: UUID | None = None
    target_cost_center_id: UUID | None = None
    driver_id: UUID | None = None
    allocated_amount: Decimal = Field(..., gt=0)
    driver_quantity: Decimal | None = Field(None, ge=0)
    driver_rate: Decimal | None = Field(None, ge=0)
    allocation_percentage: Decimal | None = Field(None, ge=0, le=100)
    allocation_weight: Decimal | None = Field(None, ge=0)
    reference_period: str = Field(..., min_length=7, max_length=7)  # "2024-01"
    notes: str | None = None

    @field_validator("reference_period")
    @classmethod
    def validate_period(cls, v: str) -> str:
        """Valida formato do período."""
        if not v or len(v) != 7 or v[4] != "-":
            raise ValueError("Período deve estar no formato YYYY-MM")
        try:
            year = int(v[:4])
            month = int(v[5:7])
            if not 1 <= month <= 12 or not 2000 <= year <= 2100:
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

    description: str | None = Field(None, max_length=200)
    reference: str | None = Field(None, max_length=100)
    allocated_amount: Decimal | None = Field(None, gt=0)
    driver_quantity: Decimal | None = Field(None, ge=0)
    driver_rate: Decimal | None = Field(None, ge=0)
    allocation_percentage: Decimal | None = Field(None, ge=0, le=100)
    notes: str | None = None


class CostAllocationResponse(CostAllocationBase):
    """Schema de resposta para Cost Allocation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    condominio_id: UUID
    allocation_number: str
    batch_id: UUID | None
    status: AllocationStatus
    allocation_date: datetime
    effective_date: datetime | None
    is_validated: bool
    validated_at: datetime | None
    approved_at: datetime | None
    executed_at: datetime | None
    is_reversed: bool
    reversed_at: datetime | None
    reversal_reason: str | None
    is_posted: bool
    is_automatic: bool
    is_recurring: bool
    active: bool
    created_at: datetime
    updated_at: datetime


class CostAllocationFilter(BaseModel):
    """Filtros para Cost Allocation."""

    allocation_type: AllocationType | None = None
    status: AllocationStatus | None = None
    allocation_method: AllocationMethod | None = None
    source_pool_id: UUID | None = None
    activity_id: UUID | None = None
    cost_object_id: UUID | None = None
    driver_id: UUID | None = None
    reference_period: str | None = None
    batch_id: UUID | None = None
    is_reversed: bool | None = None
    is_posted: bool | None = None
    active: bool | None = None


class CostAllocationApprove(BaseModel):
    """Schema para aprovar alocação."""

    notes: str | None = None


class CostAllocationReverse(BaseModel):
    """Schema para estornar alocação."""

    reason: str = Field(..., min_length=5, max_length=500)


class CostAllocationBatch(BaseModel):
    """Schema para criar lote de alocações."""

    allocations: list[CostAllocationCreate] = Field(..., min_length=1)
    execute_immediately: bool = False
    description: str | None = None


# =============================================================================
# COST ANALYSIS SCHEMAS
# =============================================================================


class CostAnalysisBase(BaseModel):
    """Schema base para Cost Analysis."""

    code: str = Field(..., min_length=1, max_length=30)
    name: str = Field(..., min_length=1, max_length=150)
    description: str | None = Field(None, max_length=2000)
    analysis_type: AnalysisType = AnalysisType.ABC_COSTING
    scope: AnalysisScope = AnalysisScope.GLOBAL
    period_start: datetime
    period_end: datetime
    cost_center_ids: list[UUID] | None = None
    activity_ids: list[UUID] | None = None
    pool_ids: list[UUID] | None = None
    object_ids: list[UUID] | None = None
    filters: dict | None = None
    parameters: dict | None = None
    scenarios: list[dict] | None = None
    comparison_period_start: datetime | None = None
    comparison_period_end: datetime | None = None
    is_scheduled: bool = False
    schedule_cron: str | None = Field(None, max_length=50)
    notes: str | None = None
    tags: list[str] | None = None


class CostAnalysisCreate(CostAnalysisBase):
    """Schema para criar Cost Analysis."""

    condominio_id: UUID


class CostAnalysisUpdate(BaseModel):
    """Schema para atualizar Cost Analysis."""

    name: str | None = Field(None, min_length=1, max_length=150)
    description: str | None = Field(None, max_length=2000)
    period_start: datetime | None = None
    period_end: datetime | None = None
    filters: dict | None = None
    parameters: dict | None = None
    scenarios: list[dict] | None = None
    is_scheduled: bool | None = None
    schedule_cron: str | None = Field(None, max_length=50)
    notes: str | None = None
    tags: list[str] | None = None
    active: bool | None = None


class CostAnalysisResponse(CostAnalysisBase):
    """Schema de resposta para Cost Analysis."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    condominio_id: UUID
    status: AnalysisStatus
    reference_period: str | None
    results: dict | None
    total_cost: Decimal
    total_revenue: Decimal
    total_margin: Decimal
    margin_percent: Decimal
    total_direct_cost: Decimal
    total_indirect_cost: Decimal
    total_allocated: Decimal
    unallocated_cost: Decimal
    practical_capacity: Decimal | None
    used_capacity: Decimal | None
    idle_capacity: Decimal | None
    idle_capacity_cost: Decimal | None
    cost_variance: Decimal | None
    break_even_units: Decimal | None
    break_even_revenue: Decimal | None
    safety_margin: Decimal | None
    insights: list[dict] | None
    recommendations: list[dict] | None
    alerts: list[dict] | None
    started_at: datetime | None
    completed_at: datetime | None
    execution_time_ms: int | None
    report_format: ReportFormat | None
    report_path: str | None
    is_template: bool
    is_favorite: bool
    active: bool
    created_at: datetime
    updated_at: datetime


class CostAnalysisFilter(BaseModel):
    """Filtros para Cost Analysis."""

    analysis_type: AnalysisType | None = None
    status: AnalysisStatus | None = None
    scope: AnalysisScope | None = None
    is_scheduled: bool | None = None
    is_template: bool | None = None
    is_favorite: bool | None = None
    active: bool | None = None
    search: str | None = None


class CostAnalysisRun(BaseModel):
    """Schema para executar análise."""

    force_recalculate: bool = False
    generate_report: bool = False
    report_format: ReportFormat | None = None


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
