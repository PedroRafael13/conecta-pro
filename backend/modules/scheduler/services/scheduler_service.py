"""SchedulerService - Orquestração de Tarefas Agendadas.

Sprint 35 - Task Scheduler.
"""

import hashlib
import logging
import re
import uuid
from datetime import datetime, timedelta

from croniter import croniter
from sqlalchemy import Integer, func, or_
from sqlalchemy.orm import Session

from modules.scheduler.models.scheduled_task import (
    ScheduledTask,
    TaskCategory,
    TaskStatus,
    TaskType,
)
from modules.scheduler.models.task_execution import ExecutionStatus, TaskExecution, TaskExecutionLog
from modules.scheduler.models.task_lock import LockStatus, TaskLock
from modules.scheduler.models.task_queue import (
    PRIORITY_VALUES,
    QueuePriority,
    QueueStatus,
    TaskQueue,
)
from modules.scheduler.models.task_worker import TaskWorker, WorkerStatus

logger = logging.getLogger(__name__)


class SchedulerService:
    """Serviço de orquestração do scheduler."""

    def __init__(self, db: Session):
        """Inicializa o serviço."""
        self.db = db

    # ==================== Task Management ====================

    def create_task(
        self,
        tenant_id: uuid.UUID,
        name: str,
        handler: str,
        task_type: TaskType = TaskType.CRON,
        category: TaskCategory = TaskCategory.CUSTOM,
        cron_expression: str | None = None,
        interval_seconds: int | None = None,
        scheduled_at: datetime | None = None,
        handler_module: str | None = None,
        handler_args: dict | None = None,
        handler_kwargs: dict | None = None,
        timeout_seconds: int = 3600,
        max_retries: int = 3,
        priority: int = 5,
        queue_name: str = "default",
        tags: list[str] | None = None,
        created_by: uuid.UUID | None = None,
        **kwargs,
    ) -> ScheduledTask:
        """Cria uma nova tarefa agendada."""
        # Gerar slug único
        slug = self._generate_slug(name)

        # Validar cron expression se fornecido
        if task_type == TaskType.CRON and cron_expression:
            if not self._validate_cron(cron_expression):
                raise ValueError(f"Cron expression inválida: {cron_expression}")

        task = ScheduledTask(
            tenant_id=tenant_id,
            name=name,
            slug=slug,
            task_type=task_type,
            category=category,
            status=TaskStatus.DRAFT,
            cron_expression=cron_expression,
            interval_seconds=interval_seconds,
            scheduled_at=scheduled_at,
            handler=handler,
            handler_module=handler_module,
            handler_args=handler_args or {},
            handler_kwargs=handler_kwargs or {},
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            priority=priority,
            queue_name=queue_name,
            tags=tags or [],
            created_by=created_by,
            **kwargs,
        )

        # Calcular próxima execução
        task.next_run_at = self._calculate_next_run(task)

        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        logger.info(f"Tarefa criada: {task.name} ({task.id})")
        return task

    def update_task(
        self,
        task_id: uuid.UUID,
        tenant_id: uuid.UUID,
        updated_by: uuid.UUID | None = None,
        **updates,
    ) -> ScheduledTask | None:
        """Atualiza uma tarefa."""
        task = self.get_task(task_id, tenant_id)
        if not task:
            return None

        # Validar cron se estiver sendo atualizado
        if "cron_expression" in updates and updates["cron_expression"]:
            if not self._validate_cron(updates["cron_expression"]):
                raise ValueError(f"Cron expression inválida: {updates['cron_expression']}")

        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)

        task.updated_by = updated_by

        # Recalcular próxima execução
        task.next_run_at = self._calculate_next_run(task)

        self.db.commit()
        self.db.refresh(task)

        logger.info(f"Tarefa atualizada: {task.name} ({task.id})")
        return task

    def get_task(
        self,
        task_id: uuid.UUID,
        tenant_id: uuid.UUID,
    ) -> ScheduledTask | None:
        """Busca uma tarefa por ID."""
        return (
            self.db.query(ScheduledTask)
            .filter(
                ScheduledTask.id == task_id,
                ScheduledTask.tenant_id == tenant_id,
            )
            .first()
        )

    def list_tasks(
        self,
        tenant_id: uuid.UUID,
        status: TaskStatus | None = None,
        category: TaskCategory | None = None,
        task_type: TaskType | None = None,
        queue_name: str | None = None,
        tags: list[str] | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[ScheduledTask], int]:
        """Lista tarefas com filtros."""
        query = self.db.query(ScheduledTask).filter(
            ScheduledTask.tenant_id == tenant_id,
            ScheduledTask.active.is_(True),
        )

        if status:
            query = query.filter(ScheduledTask.status == status)
        if category:
            query = query.filter(ScheduledTask.category == category)
        if task_type:
            query = query.filter(ScheduledTask.task_type == task_type)
        if queue_name:
            query = query.filter(ScheduledTask.queue_name == queue_name)
        if tags:
            query = query.filter(ScheduledTask.tags.overlap(tags))
        if search:
            query = query.filter(
                or_(
                    ScheduledTask.name.ilike(f"%{search}%"),
                    ScheduledTask.description.ilike(f"%{search}%"),
                )
            )

        total = query.count()
        tasks = query.order_by(ScheduledTask.created_at.desc()).offset(skip).limit(limit).all()

        return tasks, total

    def activate_task(
        self,
        task_id: uuid.UUID,
        tenant_id: uuid.UUID,
    ) -> ScheduledTask | None:
        """Ativa uma tarefa."""
        task = self.get_task(task_id, tenant_id)
        if not task:
            return None

        task.status = TaskStatus.ACTIVE
        task.next_run_at = self._calculate_next_run(task)
        self.db.commit()

        logger.info(f"Tarefa ativada: {task.name}")
        return task

    def pause_task(
        self,
        task_id: uuid.UUID,
        tenant_id: uuid.UUID,
    ) -> ScheduledTask | None:
        """Pausa uma tarefa."""
        task = self.get_task(task_id, tenant_id)
        if not task:
            return None

        task.status = TaskStatus.PAUSED
        self.db.commit()

        logger.info(f"Tarefa pausada: {task.name}")
        return task

    def delete_task(
        self,
        task_id: uuid.UUID,
        tenant_id: uuid.UUID,
        hard_delete: bool = False,
    ) -> bool:
        """Remove uma tarefa."""
        task = self.get_task(task_id, tenant_id)
        if not task:
            return False

        if hard_delete:
            self.db.delete(task)
        else:
            task.active = False
            task.status = TaskStatus.DISABLED

        self.db.commit()
        logger.info(f"Tarefa removida: {task.name}")
        return True

    # ==================== Execution Management ====================

    def create_execution(
        self,
        task: ScheduledTask,
        trigger_type: str = "scheduler",
        triggered_by: uuid.UUID | None = None,
    ) -> TaskExecution:
        """Cria uma nova execução de tarefa."""
        # Gerar run_id único
        run_id = f"{task.slug}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"

        # Buscar próximo número de execução
        execution_number = (
            self.db.query(func.max(TaskExecution.execution_number)).filter(TaskExecution.task_id == task.id).scalar()
            or 0
        ) + 1

        execution = TaskExecution(
            tenant_id=task.tenant_id,
            task_id=task.id,
            execution_number=execution_number,
            run_id=run_id,
            status=ExecutionStatus.PENDING,
            scheduled_at=task.next_run_at or datetime.utcnow(),
            max_attempts=task.max_retries,
            input_args=task.handler_args,
            input_kwargs=task.handler_kwargs,
            trigger_type=trigger_type,
            triggered_by=triggered_by,
        )

        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)

        logger.info(f"Execução criada: {run_id}")
        return execution

    def get_execution(
        self,
        execution_id: uuid.UUID,
        tenant_id: uuid.UUID,
    ) -> TaskExecution | None:
        """Busca uma execução."""
        return (
            self.db.query(TaskExecution)
            .filter(
                TaskExecution.id == execution_id,
                TaskExecution.tenant_id == tenant_id,
            )
            .first()
        )

    def list_executions(
        self,
        tenant_id: uuid.UUID,
        task_id: uuid.UUID | None = None,
        status: ExecutionStatus | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[TaskExecution], int]:
        """Lista execuções."""
        query = self.db.query(TaskExecution).filter(
            TaskExecution.tenant_id == tenant_id,
        )

        if task_id:
            query = query.filter(TaskExecution.task_id == task_id)
        if status:
            query = query.filter(TaskExecution.status == status)
        if start_date:
            query = query.filter(TaskExecution.created_at >= start_date)
        if end_date:
            query = query.filter(TaskExecution.created_at <= end_date)

        total = query.count()
        executions = query.order_by(TaskExecution.created_at.desc()).offset(skip).limit(limit).all()

        return executions, total

    def update_execution_status(
        self,
        execution_id: uuid.UUID,
        status: ExecutionStatus,
        result: dict | None = None,
        error_message: str | None = None,
        error_traceback: str | None = None,
    ) -> TaskExecution | None:
        """Atualiza o status de uma execução."""
        execution = self.db.query(TaskExecution).filter(TaskExecution.id == execution_id).first()
        if not execution:
            return None

        execution.status = status

        if status == ExecutionStatus.RUNNING:
            execution.started_at = datetime.utcnow()
        elif status in [ExecutionStatus.SUCCESS, ExecutionStatus.FAILED, ExecutionStatus.TIMEOUT]:
            execution.completed_at = datetime.utcnow()
            if execution.started_at:
                execution.duration_seconds = (execution.completed_at - execution.started_at).total_seconds()

        if result:
            execution.output_result = result
        if error_message:
            execution.error_message = error_message
        if error_traceback:
            execution.error_traceback = error_traceback

        # Atualizar métricas da tarefa
        task = execution.task
        if task:
            task.total_executions += 1
            task.last_run_at = datetime.utcnow()

            if status == ExecutionStatus.SUCCESS:
                task.successful_executions += 1
                task.last_success_at = datetime.utcnow()
            elif status == ExecutionStatus.FAILED:
                task.failed_executions += 1
                task.last_failure_at = datetime.utcnow()

            if execution.duration_seconds:
                task.last_duration_seconds = execution.duration_seconds
                # Atualizar média
                if task.avg_duration_seconds:
                    task.avg_duration_seconds = task.avg_duration_seconds * 0.9 + execution.duration_seconds * 0.1
                else:
                    task.avg_duration_seconds = execution.duration_seconds

            # Calcular próxima execução
            task.next_run_at = self._calculate_next_run(task)

        self.db.commit()
        return execution

    def add_execution_log(
        self,
        execution_id: uuid.UUID,
        level: str,
        message: str,
        context: dict | None = None,
    ) -> TaskExecutionLog:
        """Adiciona log à execução."""
        log = TaskExecutionLog(
            execution_id=execution_id,
            level=level,
            message=message,
            context=context,
        )
        self.db.add(log)
        self.db.commit()
        return log

    # ==================== Queue Management ====================

    def enqueue(
        self,
        tenant_id: uuid.UUID,
        handler: str,
        payload: dict,
        queue_name: str = "default",
        priority: QueuePriority = QueuePriority.NORMAL,
        scheduled_at: datetime | None = None,
        deduplication_id: str | None = None,
        task_id: uuid.UUID | None = None,
        execution_id: uuid.UUID | None = None,
        created_by: uuid.UUID | None = None,
        **kwargs,
    ) -> TaskQueue:
        """Adiciona item à fila."""
        # Verificar deduplicação
        if deduplication_id:
            existing = (
                self.db.query(TaskQueue)
                .filter(
                    TaskQueue.tenant_id == tenant_id,
                    TaskQueue.deduplication_id == deduplication_id,
                    TaskQueue.status.in_([QueueStatus.PENDING, QueueStatus.CLAIMED]),
                )
                .first()
            )
            if existing:
                logger.info(f"Item duplicado ignorado: {deduplication_id}")
                return existing

        # Gerar message_id
        message_id = f"{queue_name}-{uuid.uuid4().hex}"

        item = TaskQueue(
            tenant_id=tenant_id,
            queue_name=queue_name,
            message_id=message_id,
            task_id=task_id,
            execution_id=execution_id,
            status=QueueStatus.PENDING,
            priority=priority,
            priority_value=PRIORITY_VALUES.get(priority, 5),
            handler=handler,
            payload=payload,
            scheduled_at=scheduled_at,
            deduplication_id=deduplication_id,
            created_by=created_by,
            **kwargs,
        )

        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)

        logger.info(f"Item enfileirado: {message_id}")
        return item

    def dequeue(
        self,
        queue_name: str = "default",
        worker_id: uuid.UUID | None = None,
        limit: int = 1,
    ) -> list[TaskQueue]:
        """Busca itens da fila para processar."""
        now = datetime.utcnow()

        # Buscar itens disponíveis
        query = (
            self.db.query(TaskQueue)
            .filter(
                TaskQueue.queue_name == queue_name,
                TaskQueue.status == QueueStatus.PENDING,
                or_(TaskQueue.scheduled_at.is_(None), TaskQueue.scheduled_at <= now),
                or_(TaskQueue.not_after.is_(None), TaskQueue.not_after > now),
            )
            .order_by(TaskQueue.priority_value.asc(), TaskQueue.enqueued_at.asc())
            .limit(limit)
            .with_for_update(skip_locked=True)
        )

        items = query.all()

        # Marcar como claimed
        for item in items:
            item.status = QueueStatus.CLAIMED
            item.claimed_by = worker_id
            item.claimed_at = now
            item.claim_expires_at = now + timedelta(seconds=item.visibility_timeout_seconds)

        self.db.commit()
        return items

    def complete_queue_item(
        self,
        item_id: uuid.UUID,
        result: dict | None = None,
        success: bool = True,
    ) -> TaskQueue | None:
        """Completa um item da fila."""
        item = self.db.query(TaskQueue).filter(TaskQueue.id == item_id).first()
        if not item:
            return None

        item.status = QueueStatus.COMPLETED if success else QueueStatus.FAILED
        item.completed_at = datetime.utcnow()
        if item.started_at:
            item.processing_time_ms = int((item.completed_at - item.started_at).total_seconds() * 1000)
        if result:
            item.result = result

        self.db.commit()
        return item

    def requeue_failed(
        self,
        item_id: uuid.UUID,
    ) -> TaskQueue | None:
        """Reenfileira item que falhou."""
        item = self.db.query(TaskQueue).filter(TaskQueue.id == item_id).first()
        if not item:
            return None

        if not item.can_retry:
            item.status = QueueStatus.DEAD
            self.db.commit()
            return item

        # Calcular próximo retry com backoff
        delay = item.retry_delay_seconds * (item.retry_backoff**item.attempt)
        item.retry_at = datetime.utcnow() + timedelta(seconds=delay)
        item.scheduled_at = item.retry_at
        item.attempt += 1
        item.status = QueueStatus.PENDING
        item.claimed_by = None
        item.claimed_at = None

        self.db.commit()
        return item

    # ==================== Lock Management ====================

    def acquire_lock(
        self,
        tenant_id: uuid.UUID,
        lock_key: str,
        owner_id: str,
        ttl_seconds: int = 3600,
        wait: bool = False,
        wait_timeout: int = 30,
        **kwargs,
    ) -> TaskLock | None:
        """Adquire um lock."""
        # Verificar se já existe lock ativo
        existing = (
            self.db.query(TaskLock)
            .filter(
                TaskLock.tenant_id == tenant_id,
                TaskLock.lock_key == lock_key,
                TaskLock.status == LockStatus.ACQUIRED,
                TaskLock.expires_at > datetime.utcnow(),
            )
            .first()
        )

        if existing:
            if existing.owner_id == owner_id:
                # Renovar lock do mesmo owner
                existing.renew(ttl_seconds)
                self.db.commit()
                return existing

            if not wait:
                return None

            # Adicionar à fila de espera
            # (simplificado - em produção usaria Redis pub/sub)
            logger.info(f"Lock ocupado, aguardando: {lock_key}")
            return None

        # Criar novo lock
        lock = TaskLock(
            tenant_id=tenant_id,
            lock_key=lock_key,
            owner_id=owner_id,
            status=LockStatus.ACQUIRED,
            expires_at=datetime.utcnow() + timedelta(seconds=ttl_seconds),
            ttl_seconds=ttl_seconds,
            **kwargs,
        )

        self.db.add(lock)
        self.db.commit()
        self.db.refresh(lock)

        logger.info(f"Lock adquirido: {lock_key}")
        return lock

    def release_lock(
        self,
        tenant_id: uuid.UUID,
        lock_key: str,
        owner_id: str,
    ) -> bool:
        """Libera um lock."""
        lock = (
            self.db.query(TaskLock)
            .filter(
                TaskLock.tenant_id == tenant_id,
                TaskLock.lock_key == lock_key,
                TaskLock.owner_id == owner_id,
                TaskLock.status == LockStatus.ACQUIRED,
            )
            .first()
        )

        if not lock:
            return False

        lock.release()
        self.db.commit()

        logger.info(f"Lock liberado: {lock_key}")
        return True

    def renew_lock(
        self,
        tenant_id: uuid.UUID,
        lock_key: str,
        owner_id: str,
        ttl_seconds: int | None = None,
    ) -> TaskLock | None:
        """Renova um lock."""
        lock = (
            self.db.query(TaskLock)
            .filter(
                TaskLock.tenant_id == tenant_id,
                TaskLock.lock_key == lock_key,
                TaskLock.owner_id == owner_id,
                TaskLock.status == LockStatus.ACQUIRED,
            )
            .first()
        )

        if not lock:
            return None

        if lock.renew(ttl_seconds):
            self.db.commit()
            return lock

        return None

    # ==================== Worker Management ====================

    def register_worker(
        self,
        name: str,
        hostname: str,
        queues: list[str] | None = None,
        concurrency: int = 4,
        **kwargs,
    ) -> TaskWorker:
        """Registra um worker."""
        worker_id = f"{hostname}-{uuid.uuid4().hex[:8]}"

        worker = TaskWorker(
            name=name,
            worker_id=worker_id,
            hostname=hostname,
            queues=queues or ["default"],
            concurrency=concurrency,
            status=WorkerStatus.STARTING,
            started_at=datetime.utcnow(),
            last_heartbeat_at=datetime.utcnow(),
            **kwargs,
        )

        self.db.add(worker)
        self.db.commit()
        self.db.refresh(worker)

        logger.info(f"Worker registrado: {worker_id}")
        return worker

    def heartbeat(
        self,
        worker_id: str,
        cpu_percent: float | None = None,
        memory_percent: float | None = None,
        tasks_in_progress: int | None = None,
    ) -> TaskWorker | None:
        """Atualiza heartbeat do worker."""
        worker = self.db.query(TaskWorker).filter(TaskWorker.worker_id == worker_id).first()
        if not worker:
            return None

        worker.update_heartbeat()
        if cpu_percent is not None:
            worker.cpu_percent = cpu_percent
        if memory_percent is not None:
            worker.memory_percent = memory_percent
        if tasks_in_progress is not None:
            worker.tasks_in_progress = tasks_in_progress

        self.db.commit()
        return worker

    def get_available_workers(
        self,
        queue_name: str = "default",
    ) -> list[TaskWorker]:
        """Busca workers disponíveis para uma fila."""
        cutoff = datetime.utcnow() - timedelta(seconds=90)  # 3x heartbeat

        return (
            self.db.query(TaskWorker)
            .filter(
                TaskWorker.queues.contains([queue_name]),
                TaskWorker.status.in_([WorkerStatus.IDLE, WorkerStatus.BUSY]),
                TaskWorker.last_heartbeat_at >= cutoff,
                TaskWorker.active.is_(True),
            )
            .all()
        )

    # ==================== Scheduler Operations ====================

    def get_due_tasks(
        self,
        limit: int = 100,
    ) -> list[ScheduledTask]:
        """Busca tarefas que devem ser executadas agora."""
        now = datetime.utcnow()

        return (
            self.db.query(ScheduledTask)
            .filter(
                ScheduledTask.status == TaskStatus.ACTIVE,
                ScheduledTask.next_run_at <= now,
                ScheduledTask.active.is_(True),
                or_(ScheduledTask.valid_until.is_(None), ScheduledTask.valid_until > now),
            )
            .order_by(ScheduledTask.priority.asc(), ScheduledTask.next_run_at.asc())
            .limit(limit)
            .all()
        )

    def schedule_task_execution(
        self,
        task: ScheduledTask,
    ) -> TaskExecution | None:
        """Agenda execução de uma tarefa."""
        # Verificar lock se não permite overlap
        if not task.allow_overlap:
            lock_key = f"task:{task.id}"
            lock = self.acquire_lock(
                tenant_id=task.tenant_id,
                lock_key=lock_key,
                owner_id=f"scheduler-{uuid.uuid4().hex[:8]}",
                ttl_seconds=task.timeout_seconds + 60,
                task_id=task.id,
            )
            if not lock:
                logger.info(f"Tarefa já em execução, pulando: {task.name}")
                return None

        # Criar execução
        execution = self.create_execution(task, trigger_type="scheduler")

        # Enfileirar
        self.enqueue(
            tenant_id=task.tenant_id,
            handler=task.handler,
            payload={
                "args": task.handler_args,
                "kwargs": task.handler_kwargs,
            },
            queue_name=task.queue_name,
            priority=QueuePriority.NORMAL,
            task_id=task.id,
            execution_id=execution.id,
        )

        return execution

    def run_scheduler_cycle(self) -> dict:
        """Executa um ciclo do scheduler."""
        results = {
            "tasks_checked": 0,
            "tasks_scheduled": 0,
            "expired_locks_cleaned": 0,
            "stale_claims_released": 0,
        }

        # 1. Buscar tarefas pendentes
        due_tasks = self.get_due_tasks()
        results["tasks_checked"] = len(due_tasks)

        for task in due_tasks:
            try:
                execution = self.schedule_task_execution(task)
                if execution:
                    results["tasks_scheduled"] += 1
            except Exception as e:
                logger.error(f"Erro ao agendar tarefa {task.name}: {e}")

        # 2. Limpar locks expirados
        expired_locks = (
            self.db.query(TaskLock)
            .filter(
                TaskLock.status == LockStatus.ACQUIRED,
                TaskLock.expires_at < datetime.utcnow(),
            )
            .all()
        )
        for lock in expired_locks:
            lock.expire()
            results["expired_locks_cleaned"] += 1

        # 3. Liberar claims expirados na fila
        stale_claims = (
            self.db.query(TaskQueue)
            .filter(
                TaskQueue.status == QueueStatus.CLAIMED,
                TaskQueue.claim_expires_at < datetime.utcnow(),
            )
            .all()
        )
        for item in stale_claims:
            item.status = QueueStatus.PENDING
            item.claimed_by = None
            item.claimed_at = None
            item.attempt += 1
            results["stale_claims_released"] += 1

        self.db.commit()

        logger.info(f"Ciclo do scheduler: {results}")
        return results

    # ==================== Statistics ====================

    def get_task_stats(
        self,
        tenant_id: uuid.UUID,
        period_days: int = 30,
    ) -> dict:
        """Retorna estatísticas das tarefas."""
        cutoff = datetime.utcnow() - timedelta(days=period_days)

        total = (
            self.db.query(ScheduledTask)
            .filter(
                ScheduledTask.tenant_id == tenant_id,
                ScheduledTask.active.is_(True),
            )
            .count()
        )

        by_status = (
            self.db.query(ScheduledTask.status, func.count(ScheduledTask.id))
            .filter(
                ScheduledTask.tenant_id == tenant_id,
                ScheduledTask.active.is_(True),
            )
            .group_by(ScheduledTask.status)
            .all()
        )

        executions = (
            self.db.query(
                func.count(TaskExecution.id).label("total"),
                func.sum(func.cast(TaskExecution.status == ExecutionStatus.SUCCESS, Integer)).label("success"),
                func.sum(func.cast(TaskExecution.status == ExecutionStatus.FAILED, Integer)).label("failed"),
                func.avg(TaskExecution.duration_seconds).label("avg_duration"),
            )
            .filter(
                TaskExecution.tenant_id == tenant_id,
                TaskExecution.created_at >= cutoff,
            )
            .first()
        )

        return {
            "period_days": period_days,
            "total_tasks": total,
            "by_status": {s.value: c for s, c in by_status},
            "executions": {
                "total": executions.total or 0,
                "success": executions.success or 0,
                "failed": executions.failed or 0,
                "success_rate": ((executions.success / executions.total * 100) if executions.total else 0),
                "avg_duration_seconds": float(executions.avg_duration or 0),
            },
        }

    def get_queue_stats(
        self,
        queue_name: str = "default",
    ) -> dict:
        """Retorna estatísticas da fila."""
        by_status = (
            self.db.query(TaskQueue.status, func.count(TaskQueue.id))
            .filter(TaskQueue.queue_name == queue_name)
            .group_by(TaskQueue.status)
            .all()
        )

        oldest_pending = (
            self.db.query(func.min(TaskQueue.enqueued_at))
            .filter(
                TaskQueue.queue_name == queue_name,
                TaskQueue.status == QueueStatus.PENDING,
            )
            .scalar()
        )

        return {
            "queue_name": queue_name,
            "by_status": {s.value: c for s, c in by_status},
            "oldest_pending_at": oldest_pending,
            "oldest_pending_age_seconds": (
                (datetime.utcnow() - oldest_pending).total_seconds() if oldest_pending else 0
            ),
        }

    # ==================== Helper Methods ====================

    def _generate_slug(self, name: str) -> str:
        """Gera slug único a partir do nome."""
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", name.lower()).strip("-")
        hash_suffix = hashlib.sha256(f"{name}{datetime.utcnow()}".encode()).hexdigest()[:6]
        return f"{slug}-{hash_suffix}"

    def _validate_cron(self, expression: str) -> bool:
        """Valida uma cron expression."""
        try:
            croniter(expression)
            return True
        except (ValueError, KeyError):
            return False

    def _calculate_next_run(self, task: ScheduledTask) -> datetime | None:
        """Calcula a próxima execução da tarefa."""
        now = datetime.utcnow()

        if task.status != TaskStatus.ACTIVE:
            return None

        if task.task_type == TaskType.CRON and task.cron_expression:
            try:
                cron = croniter(task.cron_expression, now)
                return cron.get_next(datetime)
            except Exception:
                return None

        elif task.task_type == TaskType.INTERVAL and task.interval_seconds:
            if task.last_run_at:
                return task.last_run_at + timedelta(seconds=task.interval_seconds)
            return now + timedelta(seconds=task.interval_seconds)

        elif task.task_type == TaskType.ONCE and task.scheduled_at:
            if task.scheduled_at > now:
                return task.scheduled_at
            return None

        return None
