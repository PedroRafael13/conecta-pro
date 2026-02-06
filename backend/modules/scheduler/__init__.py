"""Task Scheduler Module - Sprint 35.

Módulo de agendamento de tarefas com:
- Tarefas agendadas (cron expressions)
- Fila de tarefas com prioridades
- Workers distribuídos
- Locks para evitar duplicação
- Histórico de execuções
- Monitoramento e alertas
"""

from modules.scheduler.models import (
    ExecutionStatus,
    LockStatus,
    QueuePriority,
    QueueStatus,
    ScheduledTask,
    TaskCategory,
    TaskExecution,
    TaskLock,
    TaskQueue,
    TaskStatus,
    TaskType,
    TaskWorker,
    WorkerStatus,
)
from modules.scheduler.services import SchedulerService, TaskExecutor

__all__ = [
    # Models
    "ScheduledTask",
    "TaskExecution",
    "TaskQueue",
    "TaskWorker",
    "TaskLock",
    # Enums
    "TaskStatus",
    "TaskType",
    "TaskCategory",
    "ExecutionStatus",
    "QueueStatus",
    "QueuePriority",
    "WorkerStatus",
    "LockStatus",
    # Services
    "SchedulerService",
    "TaskExecutor",
]
