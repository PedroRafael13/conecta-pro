"""
AIWorkflow Model - Sprint 55.

Modelo para workflows e automacoes otimizadas por IA.
"""

from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    DateTime,
    Integer,
    Float,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from core.models.base import Base


class WorkflowStatusEnum(str, enum.Enum):
    """Status do workflow."""

    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"
    DISABLED = "disabled"


class WorkflowTypeEnum(str, enum.Enum):
    """Tipo de workflow."""

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


class TriggerTypeEnum(str, enum.Enum):
    """Tipo de trigger."""

    EVENT = "event"
    SCHEDULE = "schedule"
    WEBHOOK = "webhook"
    MANUAL = "manual"
    CONDITION = "condition"
    API = "api"


class StepTypeEnum(str, enum.Enum):
    """Tipo de step."""

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


class ExecutionStatusEnum(str, enum.Enum):
    """Status de execucao."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    WAITING = "waiting"
    PAUSED = "paused"


class OptimizationTypeEnum(str, enum.Enum):
    """Tipo de otimizacao."""

    PERFORMANCE = "performance"
    COST = "cost"
    RELIABILITY = "reliability"
    EFFICIENCY = "efficiency"
    AUTOMATION = "automation"


class AIWorkflow(Base):
    """
    Modelo de AIWorkflow.

    Representa um workflow automatizado.
    """

    __tablename__ = "ai_workflows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identificacao
    name = Column(String(200), nullable=False)
    code = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(20), default="1.0.0")

    # Tipo e categoria
    workflow_type = Column(
        SQLEnum(WorkflowTypeEnum, name="workflow_type_enum"),
        default=WorkflowTypeEnum.CUSTOM,
    )
    category = Column(String(100), nullable=True)
    tags = Column(ARRAY(String), default=[])

    # Status
    status = Column(
        SQLEnum(WorkflowStatusEnum, name="workflow_status_enum"),
        default=WorkflowStatusEnum.DRAFT,
    )

    # Configuracao
    trigger_config = Column(JSONB, default={})  # {type, params, schedule}
    steps = Column(JSONB, default=[])  # [{id, type, name, config, next}]
    variables = Column(JSONB, default={})  # Variaveis do workflow
    settings = Column(JSONB, default={})  # Configuracoes gerais

    # IA - Otimizacao
    is_ai_optimized = Column(Boolean, default=False)
    ai_suggestions = Column(JSONB, default=[])  # Sugestoes de otimizacao
    optimization_score = Column(Float, default=0.0)  # 0-1
    last_optimization = Column(DateTime, nullable=True)

    # Estatisticas
    execution_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    avg_execution_time = Column(Float, default=0.0)  # em segundos
    total_execution_time = Column(Float, default=0.0)

    # Performance
    success_rate = Column(Float, default=0.0)
    efficiency_score = Column(Float, default=0.0)

    # Limites
    max_concurrent = Column(Integer, default=1)
    timeout_seconds = Column(Integer, default=300)
    retry_count = Column(Integer, default=3)
    retry_delay = Column(Integer, default=60)

    # Relacionamentos
    condominio_id = Column(UUID(as_uuid=True), nullable=True)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    owner_id = Column(UUID(as_uuid=True), nullable=True)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_run_at = Column(DateTime, nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)

    # Relationships
    executions = relationship(
        "AIWorkflowExecution",
        back_populates="workflow",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<AIWorkflow {self.name}>"


class AIWorkflowExecution(Base):
    """
    Modelo de Execucao de AIWorkflow AI.

    Representa uma execucao de workflow no módulo AI.
    """

    __tablename__ = "ai_workflow_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Status
    status = Column(
        SQLEnum(ExecutionStatusEnum, name="execution_status_enum"),
        default=ExecutionStatusEnum.PENDING,
    )

    # Progresso
    current_step = Column(Integer, default=0)
    total_steps = Column(Integer, default=0)
    progress_percent = Column(Float, default=0.0)

    # Input/Output
    input_data = Column(JSONB, default={})
    output_data = Column(JSONB, default={})
    context = Column(JSONB, default={})  # Contexto durante execucao

    # Logs
    logs = Column(JSONB, default=[])  # [{timestamp, level, message, step}]
    step_results = Column(JSONB, default={})  # {step_id: {status, output, error}}

    # Erro
    error_message = Column(Text, nullable=True)
    error_step = Column(String(100), nullable=True)
    error_details = Column(JSONB, default={})

    # Tempo
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    execution_time_ms = Column(Integer, default=0)

    # Trigger
    trigger_type = Column(String(50), nullable=True)
    trigger_data = Column(JSONB, default={})
    triggered_by = Column(UUID(as_uuid=True), nullable=True)

    # Retry
    retry_attempt = Column(Integer, default=0)
    parent_execution_id = Column(UUID(as_uuid=True), nullable=True)

    # Relacionamentos
    workflow_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ai_workflows.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workflow = relationship("AIWorkflow", back_populates="executions")

    def __repr__(self) -> str:
        return f"<AIWorkflowExecution {self.id}>"


class WorkflowTemplate(Base):
    """
    Modelo de Template de AIWorkflow.

    Templates pre-definidos para workflows.
    """

    __tablename__ = "ai_workflow_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identificacao
    name = Column(String(200), nullable=False)
    code = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(20), default="1.0.0")

    # Tipo
    workflow_type = Column(
        SQLEnum(WorkflowTypeEnum, name="workflow_type_enum_template"),
        default=WorkflowTypeEnum.CUSTOM,
    )
    category = Column(String(100), nullable=True)
    tags = Column(ARRAY(String), default=[])

    # Definicao
    trigger_template = Column(JSONB, default={})
    steps_template = Column(JSONB, default=[])
    variables_template = Column(JSONB, default={})
    settings_template = Column(JSONB, default={})

    # Parametros
    required_params = Column(JSONB, default=[])  # [{name, type, description}]
    optional_params = Column(JSONB, default=[])

    # IA
    ai_recommended = Column(Boolean, default=False)
    use_cases = Column(ARRAY(String), default=[])
    complexity = Column(String(20), default="medium")  # simple, medium, complex

    # Estatisticas
    usage_count = Column(Integer, default=0)
    avg_rating = Column(Float, default=0.0)
    total_ratings = Column(Integer, default=0)

    # Config
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<WorkflowTemplate {self.name}>"


class WorkflowOptimization(Base):
    """
    Modelo de Otimizacao de AIWorkflow.

    Registro de otimizacoes sugeridas pela IA.
    """

    __tablename__ = "ai_workflow_optimizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Tipo
    optimization_type = Column(
        SQLEnum(OptimizationTypeEnum, name="optimization_type_enum"),
        nullable=False,
    )

    # Sugestao
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    suggestion = Column(Text, nullable=False)

    # Impacto estimado
    estimated_improvement = Column(Float, default=0.0)  # Percentual
    confidence = Column(Float, default=0.0)  # 0-1
    priority = Column(Integer, default=0)  # 1-10

    # Detalhes
    current_state = Column(JSONB, default={})
    proposed_state = Column(JSONB, default={})
    changes = Column(JSONB, default=[])  # Lista de mudancas

    # Analise
    analysis_data = Column(JSONB, default={})
    metrics_before = Column(JSONB, default={})
    metrics_after = Column(JSONB, default={})

    # Status
    status = Column(String(50), default="pending")  # pending, applied, rejected, expired
    applied_at = Column(DateTime, nullable=True)
    applied_by = Column(UUID(as_uuid=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Resultado
    actual_improvement = Column(Float, nullable=True)

    # Relacionamentos
    workflow_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ai_workflows.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<WorkflowOptimization {self.title}>"


class WorkflowMetrics(Base):
    """
    Modelo de Metricas de AIWorkflow.

    Metricas agregadas para analise.
    """

    __tablename__ = "ai_workflow_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Periodo
    period_type = Column(String(20), nullable=False)  # hourly, daily, weekly, monthly
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)

    # Contadores
    executions_total = Column(Integer, default=0)
    executions_success = Column(Integer, default=0)
    executions_failed = Column(Integer, default=0)
    executions_cancelled = Column(Integer, default=0)

    # Tempo
    total_execution_time_ms = Column(Integer, default=0)
    avg_execution_time_ms = Column(Float, default=0.0)
    min_execution_time_ms = Column(Integer, default=0)
    max_execution_time_ms = Column(Integer, default=0)
    p95_execution_time_ms = Column(Integer, default=0)

    # Performance
    success_rate = Column(Float, default=0.0)
    failure_rate = Column(Float, default=0.0)
    throughput = Column(Float, default=0.0)  # execucoes por hora

    # Erros
    errors_by_type = Column(JSONB, default={})  # {error_type: count}
    errors_by_step = Column(JSONB, default={})  # {step_id: count}

    # Custos (se aplicavel)
    estimated_cost = Column(Float, default=0.0)
    estimated_savings = Column(Float, default=0.0)

    # Relacionamentos
    workflow_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ai_workflows.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<WorkflowMetrics {self.workflow_id} {self.period_type}>"
