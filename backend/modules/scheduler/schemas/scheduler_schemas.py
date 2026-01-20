"""Scheduler Schemas - Pydantic Schemas.

Sprint 35 - Task Scheduler.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from modules.scheduler.models.scheduled_task import TaskCategory, TaskStatus, TaskType
from modules.scheduler.models.task_execution import ExecutionStatus
from modules.scheduler.models.task_lock import LockStatus
from modules.scheduler.models.task_queue import QueuePriority, QueueStatus
from modules.scheduler.models.task_worker import WorkerStatus

# ============ Task Schemas ============


class TaskCreate(BaseModel):
    """Schema para criar tarefa."""

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    task_type: TaskType = TaskType.CRON
    category: TaskCategory = TaskCategory.CUSTOM

    # Agendamento
    cron_expression: Optional[str] = Field(None, description="Ex: '0 0 * * *'")
    interval_seconds: Optional[int] = Field(None, ge=1)
    scheduled_at: Optional[datetime] = None
    timezone: str = "America/Sao_Paulo"

    # Handler
    handler: str = Field(..., min_length=1, max_length=200)
    handler_module: Optional[str] = None
    handler_args: Optional[dict] = None
    handler_kwargs: Optional[dict] = None

    # Configuração
    timeout_seconds: int = Field(3600, ge=1, le=86400)
    max_retries: int = Field(3, ge=0, le=10)
    retry_delay_seconds: int = Field(60, ge=1)
    priority: int = Field(5, ge=1, le=10)
    queue_name: str = "default"

    # Opções
    allow_overlap: bool = False
    max_concurrent: int = Field(1, ge=1, le=10)

    # Notificações
    notify_on_success: bool = False
    notify_on_failure: bool = True
    notify_emails: Optional[list[str]] = None
    notify_webhook: Optional[str] = None

    # Metadados
    tags: Optional[list[str]] = None
    extra_data: Optional[dict] = None


class TaskUpdate(BaseModel):
    """Schema para atualizar tarefa."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None

    cron_expression: Optional[str] = None
    interval_seconds: Optional[int] = Field(None, ge=1)
    timezone: Optional[str] = None

    handler_args: Optional[dict] = None
    handler_kwargs: Optional[dict] = None

    timeout_seconds: Optional[int] = Field(None, ge=1, le=86400)
    max_retries: Optional[int] = Field(None, ge=0, le=10)
    priority: Optional[int] = Field(None, ge=1, le=10)

    notify_on_success: Optional[bool] = None
    notify_on_failure: Optional[bool] = None
    notify_emails: Optional[list[str]] = None

    tags: Optional[list[str]] = None
    extra_data: Optional[dict] = None


class TaskResponse(BaseModel):
    """Schema de resposta de tarefa."""

    id: UUID
    tenant_id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    task_type: TaskType
    category: TaskCategory
    status: TaskStatus
    cron_expression: Optional[str] = None
    interval_seconds: Optional[int] = None
    scheduled_at: Optional[datetime] = None
    timezone: str
    handler: str
    handler_module: Optional[str] = None
    timeout_seconds: int
    max_retries: int
    priority: int
    queue_name: str
    allow_overlap: bool
    total_executions: int
    successful_executions: int
    failed_executions: int
    success_rate: Optional[float] = None
    avg_duration_seconds: Optional[float] = None
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    tags: Optional[list[str]] = None
    active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Config."""

        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema de lista de tarefas."""

    items: list[TaskResponse]
    total: int
    page: int = 1
    page_size: int = 50


class TaskStatsResponse(BaseModel):
    """Schema de estatísticas de tarefas."""

    period_days: int
    total_tasks: int
    by_status: dict
    executions: dict


# ============ Execution Schemas ============


class ExecutionResponse(BaseModel):
    """Schema de resposta de execução."""

    id: UUID
    tenant_id: UUID
    task_id: UUID
    execution_number: int
    run_id: str
    status: ExecutionStatus
    worker_hostname: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    queued_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    attempt_number: int
    progress_percent: float
    progress_message: Optional[str] = None
    output_result: Optional[dict] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    trigger_type: Optional[str] = None
    triggered_by: Optional[UUID] = None
    created_at: datetime

    class Config:
        """Config."""

        from_attributes = True


class ExecutionLogResponse(BaseModel):
    """Schema de resposta de log de execução."""

    id: UUID
    execution_id: UUID
    timestamp: datetime
    level: str
    message: str
    context: Optional[dict] = None

    class Config:
        """Config."""

        from_attributes = True


class ExecutionStatsResponse(BaseModel):
    """Schema de estatísticas de execução."""

    total: int
    success: int
    failed: int
    success_rate: float
    avg_duration_seconds: float


# ============ Queue Schemas ============


class QueueItemCreate(BaseModel):
    """Schema para criar item na fila."""

    handler: str = Field(..., min_length=1, max_length=200)
    payload: dict = Field(default_factory=dict)
    queue_name: str = "default"
    priority: QueuePriority = QueuePriority.NORMAL
    scheduled_at: Optional[datetime] = None
    not_after: Optional[datetime] = None
    timeout_seconds: int = Field(3600, ge=1)
    max_attempts: int = Field(3, ge=1, le=10)
    deduplication_id: Optional[str] = None
    group_id: Optional[str] = None
    correlation_id: Optional[str] = None
    extra_data: Optional[dict] = None


class QueueItemResponse(BaseModel):
    """Schema de resposta de item da fila."""

    id: UUID
    tenant_id: UUID
    queue_name: str
    message_id: str
    task_id: Optional[UUID] = None
    execution_id: Optional[UUID] = None
    status: QueueStatus
    priority: QueuePriority
    handler: str
    payload: dict
    scheduled_at: Optional[datetime] = None
    attempt: int
    max_attempts: int
    enqueued_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    group_id: Optional[str] = None
    correlation_id: Optional[str] = None

    class Config:
        """Config."""

        from_attributes = True


class QueueStatsResponse(BaseModel):
    """Schema de estatísticas da fila."""

    queue_name: str
    by_status: dict
    oldest_pending_at: Optional[datetime] = None
    oldest_pending_age_seconds: float


# ============ Worker Schemas ============


class WorkerResponse(BaseModel):
    """Schema de resposta de worker."""

    id: UUID
    name: str
    worker_id: str
    hostname: str
    ip_address: Optional[str] = None
    pid: Optional[int] = None
    status: WorkerStatus
    queues: list[str]
    concurrency: int
    tasks_in_progress: int
    total_tasks_processed: int
    tasks_succeeded: int
    tasks_failed: int
    success_rate: Optional[float] = None
    utilization_percent: float
    cpu_percent: Optional[float] = None
    memory_percent: Optional[float] = None
    last_heartbeat_at: Optional[datetime] = None
    last_task_at: Optional[datetime] = None
    version: Optional[str] = None
    started_at: Optional[datetime] = None
    active: bool

    class Config:
        """Config."""

        from_attributes = True


class WorkerStatsResponse(BaseModel):
    """Schema de estatísticas de workers."""

    total_workers: int
    active_workers: int
    idle_workers: int
    busy_workers: int
    offline_workers: int
    total_tasks_processed: int
    total_concurrency: int
    avg_utilization: float


# ============ Lock Schemas ============


class LockCreate(BaseModel):
    """Schema para criar lock."""

    lock_key: str = Field(..., min_length=1, max_length=500)
    lock_name: Optional[str] = None
    ttl_seconds: int = Field(3600, ge=1, le=86400)
    reason: Optional[str] = None
    extra_data: Optional[dict] = None


class LockResponse(BaseModel):
    """Schema de resposta de lock."""

    id: UUID
    tenant_id: UUID
    lock_key: str
    lock_name: Optional[str] = None
    status: LockStatus
    owner_id: str
    owner_hostname: Optional[str] = None
    acquired_at: datetime
    expires_at: datetime
    ttl_seconds: int
    remaining_seconds: Optional[int] = None
    renew_count: int
    reason: Optional[str] = None

    class Config:
        """Config."""

        from_attributes = True


# ============ Trigger Schemas ============


class TriggerTaskRequest(BaseModel):
    """Schema para disparar tarefa manualmente."""

    override_args: Optional[dict] = None
    override_kwargs: Optional[dict] = None
    priority: Optional[int] = Field(None, ge=1, le=10)
    queue_name: Optional[str] = None


class TriggerTaskResponse(BaseModel):
    """Schema de resposta ao disparar tarefa."""

    task_id: UUID
    execution_id: UUID
    run_id: str
    status: ExecutionStatus
    message: str
