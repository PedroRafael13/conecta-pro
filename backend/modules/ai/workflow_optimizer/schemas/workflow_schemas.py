"""
Workflow Optimizer Schemas - Sprint 55.

Pydantic schemas para validacao e serializacao.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


# =============================================================================
# Enums
# =============================================================================


class WorkflowStatusEnum(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"
    DISABLED = "disabled"


class WorkflowTypeEnum(str, Enum):
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


class TriggerTypeEnum(str, Enum):
    EVENT = "event"
    SCHEDULE = "schedule"
    WEBHOOK = "webhook"
    MANUAL = "manual"
    CONDITION = "condition"
    API = "api"


class StepTypeEnum(str, Enum):
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


class ExecutionStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    WAITING = "waiting"
    PAUSED = "paused"


class OptimizationTypeEnum(str, Enum):
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
    config: Dict[str, Any] = Field(default_factory=dict)
    next_steps: List[str] = Field(default_factory=list)
    condition: Optional[str] = None
    timeout: Optional[int] = None
    retry_count: Optional[int] = None


class TriggerConfig(BaseModel):
    """Schema para configuracao de trigger."""

    trigger_type: TriggerTypeEnum
    event_name: Optional[str] = None
    schedule: Optional[str] = None  # Cron expression
    webhook_path: Optional[str] = None
    condition: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Workflow Schemas
# =============================================================================


class WorkflowCreate(BaseModel):
    """Schema para criar workflow."""

    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    workflow_type: WorkflowTypeEnum = WorkflowTypeEnum.CUSTOM
    category: Optional[str] = Field(None, max_length=100)
    tags: List[str] = Field(default_factory=list)
    trigger_config: Dict[str, Any] = Field(default_factory=dict)
    steps: List[Dict[str, Any]] = Field(default_factory=list)
    variables: Dict[str, Any] = Field(default_factory=dict)
    settings: Dict[str, Any] = Field(default_factory=dict)
    max_concurrent: int = Field(default=1, ge=1, le=100)
    timeout_seconds: int = Field(default=300, ge=30, le=86400)
    retry_count: int = Field(default=3, ge=0, le=10)
    condominio_id: Optional[UUID] = None


class WorkflowUpdate(BaseModel):
    """Schema para atualizar workflow."""

    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    status: Optional[WorkflowStatusEnum] = None
    workflow_type: Optional[WorkflowTypeEnum] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    trigger_config: Optional[Dict[str, Any]] = None
    steps: Optional[List[Dict[str, Any]]] = None
    variables: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None
    max_concurrent: Optional[int] = Field(None, ge=1, le=100)
    timeout_seconds: Optional[int] = Field(None, ge=30, le=86400)


class WorkflowResponse(BaseModel):
    """Schema de resposta para workflow."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    code: str
    description: Optional[str]
    version: str
    workflow_type: str
    category: Optional[str]
    tags: List[str]
    status: str
    trigger_config: Dict[str, Any]
    steps: List[Dict[str, Any]]
    variables: Dict[str, Any]
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
    last_run_at: Optional[datetime]
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
    last_run_at: Optional[datetime]


# =============================================================================
# Execution Schemas
# =============================================================================


class ExecutionCreate(BaseModel):
    """Schema para criar execucao."""

    workflow_id: UUID
    input_data: Dict[str, Any] = Field(default_factory=dict)
    trigger_type: Optional[str] = None
    trigger_data: Dict[str, Any] = Field(default_factory=dict)


class ExecutionResponse(BaseModel):
    """Schema de resposta para execucao."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workflow_id: UUID
    status: str
    current_step: int
    total_steps: int
    progress_percent: float
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    error_message: Optional[str]
    error_step: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    execution_time_ms: int
    trigger_type: Optional[str]
    retry_attempt: int
    created_at: datetime


class ExecutionLog(BaseModel):
    """Schema para log de execucao."""

    timestamp: datetime
    level: str  # debug, info, warning, error
    message: str
    step: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Template Schemas
# =============================================================================


class TemplateCreate(BaseModel):
    """Schema para criar template."""

    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    workflow_type: WorkflowTypeEnum = WorkflowTypeEnum.CUSTOM
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    trigger_template: Dict[str, Any] = Field(default_factory=dict)
    steps_template: List[Dict[str, Any]] = Field(default_factory=list)
    variables_template: Dict[str, Any] = Field(default_factory=dict)
    required_params: List[Dict[str, Any]] = Field(default_factory=list)
    use_cases: List[str] = Field(default_factory=list)
    complexity: str = Field(default="medium")


class TemplateUpdate(BaseModel):
    """Schema para atualizar template."""

    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    workflow_type: Optional[WorkflowTypeEnum] = None
    tags: Optional[List[str]] = None
    trigger_template: Optional[Dict[str, Any]] = None
    steps_template: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None


class TemplateResponse(BaseModel):
    """Schema de resposta para template."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    code: str
    description: Optional[str]
    version: str
    workflow_type: str
    category: Optional[str]
    tags: List[str]
    trigger_template: Dict[str, Any]
    steps_template: List[Dict[str, Any]]
    required_params: List[Dict[str, Any]]
    use_cases: List[str]
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
    current_state: Dict[str, Any]
    proposed_state: Dict[str, Any]
    changes: List[Dict[str, Any]]


class OptimizationResponse(BaseModel):
    """Schema de resposta para otimizacao."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workflow_id: UUID
    optimization_type: str
    title: str
    description: Optional[str]
    suggestion: str
    estimated_improvement: float
    confidence: float
    priority: int
    status: str
    applied_at: Optional[datetime]
    actual_improvement: Optional[float]
    created_at: datetime


class ApplyOptimizationRequest(BaseModel):
    """Schema para aplicar otimizacao."""

    optimization_id: UUID
    apply_changes: bool = True
    custom_changes: Optional[Dict[str, Any]] = None


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
    bottleneck_steps: List[Dict[str, Any]]
    frequent_errors: List[Dict[str, Any]]

    # Sugestoes
    optimizations: List[OptimizationSuggestion]

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
    workflows_by_status: Dict[str, int]
    executions_by_status: Dict[str, int]

    # Por tipo
    workflows_by_type: Dict[str, int]

    # Performance
    avg_success_rate: float
    avg_execution_time: float
    total_failures_today: int

    # Top workflows
    top_executed: List[Dict[str, Any]]
    top_failing: List[Dict[str, Any]]
    recently_optimized: List[Dict[str, Any]]

    # Tendencias
    executions_trend: List[Dict[str, Any]]
    success_rate_trend: List[Dict[str, Any]]

    # IA
    pending_optimizations: int
    applied_optimizations: int
    estimated_savings: float
