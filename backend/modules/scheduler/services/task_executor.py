"""TaskExecutor - Executor de Tarefas.

Sprint 35 - Task Scheduler.
"""

import asyncio
import importlib
import logging
import os
import signal
import sys
import time
import traceback
import uuid
from datetime import datetime, timedelta
from typing import Any, Callable, Optional

from sqlalchemy.orm import Session

from modules.scheduler.models.scheduled_task import ScheduledTask
from modules.scheduler.models.task_execution import ExecutionStatus, TaskExecution
from modules.scheduler.models.task_queue import QueueStatus, TaskQueue
from modules.scheduler.models.task_worker import TaskWorker, WorkerStatus
from modules.scheduler.services.scheduler_service import SchedulerService

logger = logging.getLogger(__name__)


class TaskExecutor:
    """Executor de tarefas agendadas.

    Responsável por:
    - Buscar tarefas da fila
    - Executar handlers
    - Gerenciar timeouts
    - Reportar resultados
    """

    def __init__(
        self,
        db: Session,
        worker_name: str = "worker",
        queues: Optional[list[str]] = None,
        concurrency: int = 4,
    ):
        """Inicializa o executor."""
        self.db = db
        self.scheduler_service = SchedulerService(db)
        self.worker_name = worker_name
        self.queues = queues or ["default"]
        self.concurrency = concurrency
        self.worker: Optional[TaskWorker] = None
        self.running = False
        self._handlers: dict[str, Callable] = {}
        self._current_tasks: dict[str, TaskExecution] = {}

    def register_handler(self, name: str, handler: Callable) -> None:
        """Registra um handler de tarefa."""
        self._handlers[name] = handler
        logger.info(f"Handler registrado: {name}")

    def get_handler(self, name: str) -> Optional[Callable]:
        """Busca um handler registrado ou tenta importar dinamicamente."""
        if name in self._handlers:
            return self._handlers[name]

        # Tentar importar dinamicamente
        try:
            if "." in name:
                module_path, func_name = name.rsplit(".", 1)
                module = importlib.import_module(module_path)
                handler = getattr(module, func_name)
                self._handlers[name] = handler
                return handler
        except (ImportError, AttributeError) as e:
            logger.error(f"Erro ao importar handler {name}: {e}")

        return None

    def start(self) -> None:
        """Inicia o executor."""
        # Registrar worker
        self.worker = self.scheduler_service.register_worker(
            name=self.worker_name,
            hostname=os.uname().nodename,
            queues=self.queues,
            concurrency=self.concurrency,
            pid=os.getpid(),
            python_version=sys.version.split()[0],
            platform=sys.platform,
        )
        self.worker.status = WorkerStatus.IDLE
        self.db.commit()

        self.running = True
        logger.info(f"Executor iniciado: {self.worker.worker_id}")

        # Configurar signal handlers
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

    def stop(self, graceful: bool = True) -> None:
        """Para o executor."""
        self.running = False

        if self.worker:
            if graceful:
                self.worker.status = WorkerStatus.DRAINING
                self.db.commit()
                # Aguardar tarefas em andamento
                while self._current_tasks:
                    time.sleep(1)

            self.worker.status = WorkerStatus.STOPPED
            self.db.commit()

        logger.info("Executor parado")

    def _handle_shutdown(self, signum: int, frame: Any) -> None:
        """Handler para sinais de shutdown."""
        logger.info(f"Sinal de shutdown recebido: {signum}")
        self.stop(graceful=True)

    def run_forever(self, poll_interval: float = 1.0) -> None:
        """Executa o loop principal do executor."""
        self.start()

        while self.running:
            try:
                # Atualizar heartbeat
                self._update_heartbeat()

                # Buscar e processar tarefas
                if self.worker and self.worker.available_slots > 0:
                    self._process_queue()

                time.sleep(poll_interval)

            except Exception as e:
                logger.error(f"Erro no loop principal: {e}")
                time.sleep(5)

    def _update_heartbeat(self) -> None:
        """Atualiza o heartbeat do worker."""
        if not self.worker:
            return

        try:
            import psutil

            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
        except ImportError:
            cpu = None
            memory = None

        self.scheduler_service.heartbeat(
            worker_id=self.worker.worker_id,
            cpu_percent=cpu,
            memory_percent=memory,
            tasks_in_progress=len(self._current_tasks),
        )

    def _process_queue(self) -> None:
        """Processa itens da fila."""
        for queue_name in self.queues:
            if not self.worker or self.worker.available_slots <= 0:
                break

            items = self.scheduler_service.dequeue(
                queue_name=queue_name,
                worker_id=self.worker.id if self.worker else None,
                limit=self.worker.available_slots if self.worker else 1,
            )

            for item in items:
                self._execute_queue_item(item)

    def _execute_queue_item(self, item: TaskQueue) -> None:
        """Executa um item da fila."""
        execution_id = str(item.execution_id) if item.execution_id else str(item.id)

        try:
            # Atualizar status
            item.status = QueueStatus.PROCESSING
            item.started_at = datetime.utcnow()
            self.db.commit()

            if self.worker:
                self.worker.record_task_start()
                self.db.commit()

            # Atualizar execução se existir
            if item.execution_id:
                self.scheduler_service.update_execution_status(
                    item.execution_id,
                    ExecutionStatus.RUNNING,
                )

            # Buscar handler
            handler = self.get_handler(item.handler)
            if not handler:
                raise ValueError(f"Handler não encontrado: {item.handler}")

            # Executar com timeout
            result = self._execute_with_timeout(
                handler,
                item.payload,
                timeout_seconds=item.timeout_seconds,
            )

            # Sucesso
            self.scheduler_service.complete_queue_item(
                item.id,
                result=result,
                success=True,
            )

            if item.execution_id:
                self.scheduler_service.update_execution_status(
                    item.execution_id,
                    ExecutionStatus.SUCCESS,
                    result=result,
                )

            if self.worker:
                self.worker.record_task_complete(success=True)
                self.db.commit()

            logger.info(f"Tarefa completada: {item.message_id} (exec: {execution_id})")

        except TimeoutError:
            self._handle_task_failure(
                item,
                error_type="TimeoutError",
                error_message=f"Timeout após {item.timeout_seconds} segundos",
            )

        except Exception as e:
            self._handle_task_failure(
                item,
                error_type=type(e).__name__,
                error_message=str(e),
                error_traceback=traceback.format_exc(),
            )

    def _execute_with_timeout(
        self,
        handler: Callable,
        payload: dict,
        timeout_seconds: int,
    ) -> Any:
        """Executa handler com timeout."""
        args = payload.get("args", [])
        kwargs = payload.get("kwargs", {})

        # Se for async, usar asyncio
        if asyncio.iscoroutinefunction(handler):
            return asyncio.run(
                asyncio.wait_for(
                    handler(*args, **kwargs),
                    timeout=timeout_seconds,
                )
            )

        # Execução síncrona com signal para timeout
        def timeout_handler(signum: int, frame: Any) -> None:
            raise TimeoutError(f"Timeout após {timeout_seconds} segundos")

        # Configurar timeout (apenas Unix)
        if hasattr(signal, "SIGALRM"):
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_seconds)

        try:
            result = handler(*args, **kwargs)
            return result
        finally:
            if hasattr(signal, "SIGALRM"):
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)

    def _handle_task_failure(
        self,
        item: TaskQueue,
        error_type: str,
        error_message: str,
        error_traceback: Optional[str] = None,
    ) -> None:
        """Trata falha na execução."""
        logger.error(f"Falha na tarefa {item.message_id}: {error_message}")

        item.error_message = error_message
        item.error_code = error_type

        # Verificar retry
        if item.can_retry:
            self.scheduler_service.requeue_failed(item.id)
            logger.info(f"Tarefa reenfileirada para retry: {item.message_id}")
        else:
            item.status = QueueStatus.DEAD
            self.db.commit()

        # Atualizar execução
        if item.execution_id:
            self.scheduler_service.update_execution_status(
                item.execution_id,
                ExecutionStatus.FAILED,
                error_message=error_message,
                error_traceback=error_traceback,
            )

        if self.worker:
            self.worker.record_task_complete(success=False)
            self.db.commit()

    # ==================== Direct Task Execution ====================

    def execute_task_now(
        self,
        task: ScheduledTask,
        triggered_by: Optional[uuid.UUID] = None,
    ) -> TaskExecution:
        """Executa uma tarefa imediatamente (bypass da fila)."""
        execution = self.scheduler_service.create_execution(
            task,
            trigger_type="manual",
            triggered_by=triggered_by,
        )

        self.scheduler_service.update_execution_status(
            execution.id,
            ExecutionStatus.RUNNING,
        )

        try:
            handler = self.get_handler(task.handler)
            if not handler:
                raise ValueError(f"Handler não encontrado: {task.handler}")

            result = self._execute_with_timeout(
                handler,
                {
                    "args": task.handler_args,
                    "kwargs": task.handler_kwargs,
                },
                timeout_seconds=task.timeout_seconds,
            )

            self.scheduler_service.update_execution_status(
                execution.id,
                ExecutionStatus.SUCCESS,
                result=result,
            )

            logger.info(f"Tarefa executada: {task.name}")

        except Exception as e:
            self.scheduler_service.update_execution_status(
                execution.id,
                ExecutionStatus.FAILED,
                error_message=str(e),
                error_traceback=traceback.format_exc(),
            )
            logger.error(f"Falha na tarefa {task.name}: {e}")

        return execution

    def cancel_execution(
        self,
        execution_id: uuid.UUID,
        reason: str = "Cancelled by user",
    ) -> Optional[TaskExecution]:
        """Cancela uma execução em andamento."""
        execution = self.db.query(TaskExecution).filter(TaskExecution.id == execution_id).first()

        if not execution:
            return None

        if execution.status not in [ExecutionStatus.PENDING, ExecutionStatus.QUEUED]:
            logger.warning(f"Não é possível cancelar execução: {execution.status}")
            return None

        execution.status = ExecutionStatus.CANCELLED
        execution.error_message = reason
        execution.completed_at = datetime.utcnow()
        self.db.commit()

        # Cancelar item na fila se existir
        queue_item = (
            self.db.query(TaskQueue)
            .filter(
                TaskQueue.execution_id == execution_id,
                TaskQueue.status.in_([QueueStatus.PENDING, QueueStatus.CLAIMED]),
            )
            .first()
        )

        if queue_item:
            queue_item.status = QueueStatus.CANCELLED
            self.db.commit()

        logger.info(f"Execução cancelada: {execution.run_id}")
        return execution


# ==================== Built-in Task Handlers ====================


def cleanup_old_executions(
    db: Session,
    retention_days: int = 30,
) -> dict:
    """Handler para limpar execuções antigas."""
    cutoff = datetime.utcnow() - timedelta(days=retention_days)

    deleted = (
        db.query(TaskExecution)
        .filter(
            TaskExecution.created_at < cutoff,
            TaskExecution.status.in_(
                [
                    ExecutionStatus.SUCCESS,
                    ExecutionStatus.FAILED,
                    ExecutionStatus.CANCELLED,
                ]
            ),
        )
        .delete(synchronize_session=False)
    )

    db.commit()

    return {"deleted_executions": deleted}


def cleanup_old_queue_items(
    db: Session,
    retention_days: int = 7,
) -> dict:
    """Handler para limpar itens antigos da fila."""
    cutoff = datetime.utcnow() - timedelta(days=retention_days)

    deleted = (
        db.query(TaskQueue)
        .filter(
            TaskQueue.created_at < cutoff,
            TaskQueue.status.in_(
                [
                    QueueStatus.COMPLETED,
                    QueueStatus.DEAD,
                    QueueStatus.CANCELLED,
                ]
            ),
        )
        .delete(synchronize_session=False)
    )

    db.commit()

    return {"deleted_queue_items": deleted}


def cleanup_expired_locks(
    db: Session,
) -> dict:
    """Handler para limpar locks expirados."""
    from modules.scheduler.models.task_lock import LockStatus, TaskLock

    expired = (
        db.query(TaskLock)
        .filter(
            TaskLock.status == LockStatus.ACQUIRED,
            TaskLock.expires_at < datetime.utcnow(),
        )
        .all()
    )

    for lock in expired:
        lock.expire()

    db.commit()

    return {"expired_locks": len(expired)}


def check_stale_workers(
    db: Session,
    stale_threshold_seconds: int = 120,
) -> dict:
    """Handler para detectar workers inativos."""
    cutoff = datetime.utcnow() - timedelta(seconds=stale_threshold_seconds)

    stale = (
        db.query(TaskWorker)
        .filter(
            TaskWorker.status.in_([WorkerStatus.IDLE, WorkerStatus.BUSY]),
            TaskWorker.last_heartbeat_at < cutoff,
            TaskWorker.active.is_(True),
        )
        .all()
    )

    for worker in stale:
        worker.status = WorkerStatus.OFFLINE
        logger.warning(f"Worker marcado como offline: {worker.worker_id}")

    db.commit()

    return {"stale_workers": len(stale)}


def generate_scheduler_report(
    db: Session,
    tenant_id: uuid.UUID,
) -> dict:
    """Handler para gerar relatório do scheduler."""
    service = SchedulerService(db)

    return {
        "tasks": service.get_task_stats(tenant_id),
        "queues": {
            queue: service.get_queue_stats(queue)
            for queue in ["default", "high", "low", "background"]
        },
        "generated_at": datetime.utcnow().isoformat(),
    }


# Handlers built-in disponíveis
BUILTIN_HANDLERS = {
    "scheduler.cleanup_executions": cleanup_old_executions,
    "scheduler.cleanup_queue": cleanup_old_queue_items,
    "scheduler.cleanup_locks": cleanup_expired_locks,
    "scheduler.check_workers": check_stale_workers,
    "scheduler.generate_report": generate_scheduler_report,
}
