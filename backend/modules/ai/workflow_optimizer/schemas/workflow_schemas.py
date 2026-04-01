"""
Workflow Optimizer Schemas - Sprint 55.

Pydantic schemas para validacao e serializacao.
"""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# =============================================================================
# Enums
# =============================================================================


class WorkflowStatusEnum(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"
    DISABLED = "disabled"


class WorkflowTypeEnum(StrEnum):
    APPROVAL = "approval"
    NOTIFICATION = "notification"
    DATA_PROCESSING = "data_processing"
    INTEGRATION = "integration"
    MAINTENANCE = "maintenance"
    REPORT = "report"
    ALERT = "alert"
    SCHEDULING = "scheduling"
    COMMUNICATION = "communication"
    FINANCIAL = "financial"
    CUSTOM = "custom"


class TriggerTypeEnum(StrEnum):
    EVENT = "event"
    SCHEDULE = "schedule"
    WEBHOOK = "webhook"
    MANUAL = "manual"
    CONDITION = "condition"
    API = "api"


class StepTypeEnum(StrEnum):
    ACTION = "action"
    CONDITION = "condition"
    LOOP = "loop"
    PARALLEL = "parallel"
    WAIT = "wait"
    APPROVAL = "approval"
    NOTIFICATION = "notification"
    DATA_TRANSFORM = "data_transform"
    API_CALL = "api_call"
    SCRIPT = "script"


class ExecutionStatusEnum(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    WAITING = "waiting"
    PAUSED = "paused"


class OptimizationTypeEnum(StrEnum):
    PERFORMANCE = "performance"
    COST = "cost"
    RELIABILITY = "reliability"
    EFFICIENCY = "efficiency"
    AUTOMATION = "automation"


# =============================================================================
# Step Schemas
# =============================================================================


class WorkflowStep(BaseModel):
    """Schema para step de workflow."""

    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=200)
    step_type: StepTypeEnum
    config: dict[str, Any] = Field(default_factory=dict)
    next_steps: list[str] = Field(default_factory=list)
    condition: str | None = None
    timeout: int | None = None
    retry_count: int | None = None


class TriggerConfig(BaseModel):
    """Schema para configuracao de trigger."""

    trigger_type: TriggerTypeEnum
    event_name: str | None = None
    schedule: str | None = None  # Cron expression
    webhook_path: str | None = None
    condition: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Workflow Schemas
# =============================================================================


class WorkflowCreate(BaseModel):
    """Schema para criar workflow."""

    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    workflow_type: WorkflowTypeEnum = WorkflowTypeEnum.CUSTOM
    category: str | None = Field(None, max_length=100)
    tags: list[str] = Field(default_factory=list)
    trigger_config: dict[str, Any] = Field(default_factory=dict)
    steps: list[dict[str, Any]] = Field(default_factory=list)
    variables: dict[str, Any] = Field(default_factory=dict)
    settings: dict[str, Any] = Field(default_factory=dict)
    max_concurrent: int = Field(default=1, ge=1, le=100)
    timeout_seconds: int = Field(default=300, ge=30, le=86400)
    retry_count: int = Field(default=3, ge=0, le=10)
    condominio_id: UUID | None = None


class WorkflowUpdate(BaseModel):
    """Schema para atualizar workflow."""

    name: str | None = Field(None, max_length=200)
    description: str | None = None
    status: WorkflowStatusEnum | None = None
    workflow_type: WorkflowTypeEnum | None = None
    category: str | None = None
    tags: list[str] | None = None
    trigger_config: dict[str, Any] | None = None
    steps: list[dict[str, Any]] | None = None
    variables: dict[str, Any] | None = None
    settings: dict[str, Any] | None = None
    max_concurrent: int | None = Field(None, ge=1, le=100)
    timeout_seconds: int | None = Field(None, ge=30, le=86400)


class WorkflowResponse(BaseModel):
    """Schema de resposta para workflow."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    code: str
    description: str | None
    version: str
    workflow_type: str
    category: str | None
    tags: list[str]
    status: str
    trigger_config: dict[str, Any]
    steps: list[dict[str, Any]]
    variables: dict[str, Any]
    is_ai_optimized: bool
    optimization_score: float
    execution_count: int
    success_count: int
    failure_count: int
    success_rate: float
    avg_execution_time: float
    max_concurrent: int
    timeout_seconds: int
    created_at: datetime
    last_run_at: datetime | None
    ativo: bool


class WorkflowListResponse(BaseModel):
    """Schema para listagem de workflows."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    code: str
    workflow_type: str
    status: str
    execution_count: int
    success_rate: float
    last_run_at: datetime | None


# =============================================================================
# Execution Schemas
# =============================================================================


class ExecutionCreate(BaseModel):
    """Schema para criar execucao."""

    workflow_id: UUID
    input_data: dict[str, Any] = Field(default_factory=dict)
    trigger_type: str | None = None
    trigger_data: dict[str, Any] = Field(default_factory=dict)


class ExecutionResponse(BaseModel):
    """Schema de resposta para execucao."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workflow_id: UUID
    status: str
    current_step: int
    total_steps: int
    progress_percent: float
    input_data: dict[str, Any]
    output_data: dict[str, Any]
    error_message: str | None
    error_step: str | None
    started_at: datetime | None
    completed_at: datetime | None
    execution_time_ms: int
    trigger_type: str | None
    retry_attempt: int
    created_at: datetime


class ExecutionLog(BaseModel):
    """Schema para log de execucao."""

    timestamp: datetime
    level: str  # debug, info, warning, error
    message: str
    step: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Template Schemas
# =============================================================================


class TemplateCreate(BaseModel):
    """Schema para criar template."""

    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    workflow_type: WorkflowTypeEnum = WorkflowTypeEnum.CUSTOM
    category: str | None = None
    tags: list[str] = Field(default_factory=list)
    trigger_template: dict[str, Any] = Field(default_factory=dict)
    steps_template: list[dict[str, Any]] = Field(default_factory=list)
    variables_template: dict[str, Any] = Field(default_factory=dict)
    required_params: list[dict[str, Any]] = Field(default_factory=list)
    use_cases: list[str] = Field(default_factory=list)
    complexity: str = Field(default="medium")


class TemplateUpdate(BaseModel):
    """Schema para atualizar template."""

    name: str | None = Field(None, max_length=200)
    description: str | None = None
    workflow_type: WorkflowTypeEnum | None = None
    tags: list[str] | None = None
    trigger_template: dict[str, Any] | None = None
    steps_template: list[dict[str, Any]] | None = None
    is_active: bool | None = None


class TemplateResponse(BaseModel):
    """Schema de resposta para template."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    code: str
    description: str | None
    version: str
    workflow_type: str
    category: str | None
    tags: list[str]
    trigger_template: dict[str, Any]
    steps_template: list[dict[str, Any]]
    required_params: list[dict[str, Any]]
    use_cases: list[str]
    complexity: str
    ai_recommended: bool
    usage_count: int
    avg_rating: float
    is_active: bool
    created_at: datetime


# =============================================================================
# Optimization Schemas
# =============================================================================


class OptimizationSuggestion(BaseModel):
    """Schema para sugestao de otimizacao."""

    optimization_type: OptimizationTypeEnum
    title: str
    description: str
    suggestion: str
    estimated_improvement: float  # Percentual
    confidence: float  # 0-1
    priority: int  # 1-10
    current_state: dict[str, Any]
    proposed_state: dict[str, Any]
    changes: list[dict[str, Any]]


class OptimizationResponse(BaseModel):
    """Schema de resposta para otimizacao."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workflow_id: UUID
    optimization_type: str
    title: str
    description: str | None
    suggestion: str
    estimated_improvement: float
    confidence: float
    priority: int
    status: str
    applied_at: datetime | None
    actual_improvement: float | None
    created_at: datetime


class ApplyOptimizationRequest(BaseModel):
    """Schema para aplicar otimizacao."""

    optimization_id: UUID
    apply_changes: bool = True
    custom_changes: dict[str, Any] | None = None


# =============================================================================
# Analysis Schemas
# =============================================================================


class WorkflowAnalysisRequest(BaseModel):
    """Schema para request de analise."""

    workflow_id: UUID
    analysis_type: str = "full"  # full, performance, reliability, cost
    period_days: int = Field(default=30, ge=1, le=365)


class WorkflowAnalysisResult(BaseModel):
    """Schema para resultado de analise."""

    workflow_id: UUID
    analysis_type: str

    # Metricas gerais
    total_executions: int
    success_rate: float
    failure_rate: float
    avg_execution_time_ms: float

    # Performance
    p50_execution_time_ms: float
    p95_execution_time_ms: float
    p99_execution_time_ms: float

    # Bottlenecks
    bottleneck_steps: list[dict[str, Any]]
    frequent_errors: list[dict[str, Any]]

    # Sugestoes
    optimizations: list[OptimizationSuggestion]

    # Score geral
    health_score: float  # 0-100
    efficiency_score: float  # 0-100
    reliability_score: float  # 0-100

    processing_time_ms: int


# =============================================================================
# Dashboard Schemas
# =============================================================================


class WorkflowDashboard(BaseModel):
    """Schema para dashboard de workflows."""

    # Totais
    total_workflows: int
    active_workflows: int
    total_executions: int
    executions_today: int

    # Por status
    workflows_by_status: dict[str, int]
    executions_by_status: dict[str, int]

    # Por tipo
    workflows_by_type: dict[str, int]

    # Performance
    avg_success_rate: float
    avg_execution_time: float
    total_failures_today: int

    # Top workflows
    top_executed: list[dict[str, Any]]
    top_failing: list[dict[str, Any]]
    recently_optimized: list[dict[str, Any]]

    # Tendencias
    executions_trend: list[dict[str, Any]]
    success_rate_trend: list[dict[str, Any]]

    # IA
    pending_optimizations: int
    applied_optimizations: int
    estimated_savings: float
