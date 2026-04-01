"""Scheduler Schemas - Pydantic Schemas.

Sprint 35 - Task Scheduler.
"""

from datetime import datetime
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
    description: str | None = None
    task_type: TaskType = TaskType.CRON
    category: TaskCategory = TaskCategory.CUSTOM

    # Agendamento
    cron_expression: str | None = Field(None, description="Ex: '0 0 * * *'")
    interval_seconds: int | None = Field(None, ge=1)
    scheduled_at: datetime | None = None
    timezone: str = "America/Sao_Paulo"

    # Handler
    handler: str = Field(..., min_length=1, max_length=200)
    handler_module: str | None = None
    handler_args: dict | None = None
    handler_kwargs: dict | None = None

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
    notify_emails: list[str] | None = None
    notify_webhook: str | None = None

    # Metadados
    tags: list[str] | None = None
    extra_data: dict | None = None


class TaskUpdate(BaseModel):
    """Schema para atualizar tarefa."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    status: TaskStatus | None = None

    cron_expression: str | None = None
    interval_seconds: int | None = Field(None, ge=1)
    timezone: str | None = None

    handler_args: dict | None = None
    handler_kwargs: dict | None = None

    timeout_seconds: int | None = Field(None, ge=1, le=86400)
    max_retries: int | None = Field(None, ge=0, le=10)
    priority: int | None = Field(None, ge=1, le=10)

    notify_on_success: bool | None = None
    notify_on_failure: bool | None = None
    notify_emails: list[str] | None = None

    tags: list[str] | None = None
    extra_data: dict | None = None


class TaskResponse(BaseModel):
    """Schema de resposta de tarefa."""

    id: UUID
    tenant_id: UUID
    name: str
    slug: str
    description: str | None = None
    task_type: TaskType
    category: TaskCategory
    status: TaskStatus
    cron_expression: str | None = None
    interval_seconds: int | None = None
    scheduled_at: datetime | None = None
    timezone: str
    handler: str
    handler_module: str | None = None
    timeout_seconds: int
    max_retries: int
    priority: int
    queue_name: str
    allow_overlap: bool
    total_executions: int
    successful_executions: int
    failed_executions: int
    success_rate: float | None = None
    avg_duration_seconds: float | None = None
    last_run_at: datetime | None = None
    next_run_at: datetime | None = None
    tags: list[str] | None = None
    active: bool
    created_at: datetime
    updated_at: datetime | None = None

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
    worker_hostname: str | None = None
    scheduled_at: datetime | None = None
    queued_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_seconds: float | None = None
    attempt_number: int
    progress_percent: float
    progress_message: str | None = None
    output_result: dict | None = None
    error_type: str | None = None
    error_message: str | None = None
    trigger_type: str | None = None
    triggered_by: UUID | None = None
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
    context: dict | None = None

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
    scheduled_at: datetime | None = None
    not_after: datetime | None = None
    timeout_seconds: int = Field(3600, ge=1)
    max_attempts: int = Field(3, ge=1, le=10)
    deduplication_id: str | None = None
    group_id: str | None = None
    correlation_id: str | None = None
    extra_data: dict | None = None


class QueueItemResponse(BaseModel):
    """Schema de resposta de item da fila."""

    id: UUID
    tenant_id: UUID
    queue_name: str
    message_id: str
    task_id: UUID | None = None
    execution_id: UUID | None = None
    status: QueueStatus
    priority: QueuePriority
    handler: str
    payload: dict
    scheduled_at: datetime | None = None
    attempt: int
    max_attempts: int
    enqueued_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    processing_time_ms: int | None = None
    error_message: str | None = None
    group_id: str | None = None
    correlation_id: str | None = None

    class Config:
        """Config."""

        from_attributes = True


class QueueStatsResponse(BaseModel):
    """Schema de estatísticas da fila."""

    queue_name: str
    by_status: dict
    oldest_pending_at: datetime | None = None
    oldest_pending_age_seconds: float


# ============ Worker Schemas ============


class WorkerResponse(BaseModel):
    """Schema de resposta de worker."""

    id: UUID
    name: str
    worker_id: str
    hostname: str
    ip_address: str | None = None
    pid: int | None = None
    status: WorkerStatus
    queues: list[str]
    concurrency: int
    tasks_in_progress: int
    total_tasks_processed: int
    tasks_succeeded: int
    tasks_failed: int
    success_rate: float | None = None
    utilization_percent: float
    cpu_percent: float | None = None
    memory_percent: float | None = None
    last_heartbeat_at: datetime | None = None
    last_task_at: datetime | None = None
    version: str | None = None
    started_at: datetime | None = None
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
    lock_name: str | None = None
    ttl_seconds: int = Field(3600, ge=1, le=86400)
    reason: str | None = None
    extra_data: dict | None = None


class LockResponse(BaseModel):
    """Schema de resposta de lock."""

    id: UUID
    tenant_id: UUID
    lock_key: str
    lock_name: str | None = None
    status: LockStatus
    owner_id: str
    owner_hostname: str | None = None
    acquired_at: datetime
    expires_at: datetime
    ttl_seconds: int
    remaining_seconds: int | None = None
    renew_count: int
    reason: str | None = None

    class Config:
        """Config."""

        from_attributes = True


# ============ Trigger Schemas ============


class TriggerTaskRequest(BaseModel):
    """Schema para disparar tarefa manualmente."""

    override_args: dict | None = None
    override_kwargs: dict | None = None
    priority: int | None = Field(None, ge=1, le=10)
    queue_name: str | None = None


class TriggerTaskResponse(BaseModel):
    """Schema de resposta ao disparar tarefa."""

    task_id: UUID
    execution_id: UUID
    run_id: str
    status: ExecutionStatus
    message: str
