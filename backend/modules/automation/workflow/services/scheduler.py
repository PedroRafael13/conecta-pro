"""
Workflow Scheduler - Agendador de execucoes.

Gerencia execucoes agendadas e filas de workflows.
"""

import asyncio
import heapq
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Set
import uuid

from modules._deprecated_workflows_dataclass.models.workflow import Workflow
from modules._deprecated_workflows_dataclass.models.trigger import ScheduleConfig, ScheduleFrequency, Trigger

logger = logging.getLogger(__name__)


@dataclass(order=True)
class ScheduledJob:
    """Job agendado."""
    run_at: datetime
    id: str = field(compare=False)
    trigger_id: str = field(compare=False)
    workflow_id: str = field(compare=False)
    input_data: Dict[str, Any] = field(compare=False, default_factory=dict)
    recurring: bool = field(compare=False, default=False)
    created_at: datetime = field(compare=False, default_factory=datetime.utcnow)


@dataclass
class JobResult:
    """Resultado de execucao de job."""
    job_id: str
    execution_id: str
    success: bool
    error: str = ""
    executed_at: datetime = field(default_factory=datetime.utcnow)


class WorkflowScheduler:
    """
    Agendador de workflows.

    Responsavel por:
    - Gerenciar fila de execucoes agendadas
    - Executar jobs no tempo correto
    - Recriar jobs recorrentes
    - Gerenciar concorrencia
    """

    def __init__(self, max_concurrent: int = 10):
        self._job_queue: List[ScheduledJob] = []  # Min-heap
        self._job_map: Dict[str, ScheduledJob] = {}
        self._running_jobs: Set[str] = set()
        self._results: Dict[str, JobResult] = {}

        self._executor: Optional[Callable] = None
        self._running = False
        self._scheduler_task: Optional[asyncio.Task] = None
        self._semaphore = asyncio.Semaphore(max_concurrent)

        self._max_concurrent = max_concurrent
        self._timezone = "America/Sao_Paulo"

    def set_executor(self, executor: Callable) -> None:
        """Define funcao executora de workflows."""
        self._executor = executor

    async def start(self) -> None:
        """Inicia scheduler."""
        if self._running:
            return

        self._running = True
        self._scheduler_task = asyncio.create_task(self._run_scheduler())
        logger.info("Workflow Scheduler iniciado")

    async def stop(self) -> None:
        """Para scheduler."""
        self._running = False
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
        logger.info("Workflow Scheduler parado")

    def schedule(
        self,
        trigger: Trigger,
        workflow: Workflow,
        run_at: datetime = None,
        input_data: Dict[str, Any] = None,
    ) -> str:
        """
        Agenda execucao de workflow.

        Args:
            trigger: Trigger com configuracao de schedule
            workflow: Workflow a executar
            run_at: Data/hora de execucao (opcional)
            input_data: Dados de entrada

        Returns:
            ID do job agendado
        """
        if run_at is None:
            run_at = self._calculate_next_run(trigger)

        if run_at is None:
            raise ValueError("Nao foi possivel calcular proxima execucao")

        job = ScheduledJob(
            id=str(uuid.uuid4()),
            run_at=run_at,
            trigger_id=trigger.id,
            workflow_id=workflow.id,
            input_data=input_data or {},
            recurring=trigger.schedule_config.frequency != ScheduleFrequency.ONCE
            if trigger.schedule_config else False,
        )

        heapq.heappush(self._job_queue, job)
        self._job_map[job.id] = job

        logger.info(
            f"Job {job.id} agendado para {run_at} "
            f"(workflow: {workflow.name})"
        )

        return job.id

    def cancel_job(self, job_id: str) -> bool:
        """Cancela job agendado."""
        if job_id not in self._job_map:
            return False

        job = self._job_map.pop(job_id)

        # Remove da fila (lazy removal - marca como cancelado)
        # O job sera ignorado quando processado

        logger.info(f"Job {job_id} cancelado")
        return True

    def cancel_trigger_jobs(self, trigger_id: str) -> int:
        """Cancela todos os jobs de um trigger."""
        cancelled = 0
        to_cancel = [
            job_id for job_id, job in self._job_map.items()
            if job.trigger_id == trigger_id
        ]

        for job_id in to_cancel:
            if self.cancel_job(job_id):
                cancelled += 1

        return cancelled

    def get_job(self, job_id: str) -> Optional[ScheduledJob]:
        """Obtem job por ID."""
        return self._job_map.get(job_id)

    def get_pending_jobs(
        self,
        workflow_id: str = None,
        trigger_id: str = None,
        limit: int = 100,
    ) -> List[ScheduledJob]:
        """Lista jobs pendentes."""
        jobs = list(self._job_map.values())

        if workflow_id:
            jobs = [j for j in jobs if j.workflow_id == workflow_id]

        if trigger_id:
            jobs = [j for j in jobs if j.trigger_id == trigger_id]

        # Ordena por data de execucao
        jobs.sort(key=lambda j: j.run_at)

        return jobs[:limit]

    def get_job_result(self, job_id: str) -> Optional[JobResult]:
        """Obtem resultado de job executado."""
        return self._results.get(job_id)

    async def _run_scheduler(self) -> None:
        """Loop principal do scheduler."""
        while self._running:
            try:
                now = datetime.utcnow()

                # Processa jobs prontos
                while self._job_queue:
                    # Peek proximo job
                    next_job = self._job_queue[0]

                    # Verifica se foi cancelado
                    if next_job.id not in self._job_map:
                        heapq.heappop(self._job_queue)
                        continue

                    # Verifica se e hora de executar
                    if next_job.run_at > now:
                        break

                    # Remove da fila
                    job = heapq.heappop(self._job_queue)

                    # Executa em background
                    asyncio.create_task(self._execute_job(job))

                # Aguarda antes de verificar novamente
                await asyncio.sleep(1)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro no scheduler: {e}")
                await asyncio.sleep(5)

    async def _execute_job(self, job: ScheduledJob) -> None:
        """Executa job."""
        async with self._semaphore:
            if job.id not in self._job_map:
                return  # Foi cancelado

            self._running_jobs.add(job.id)

            try:
                logger.info(f"Executando job {job.id}")

                if not self._executor:
                    raise ValueError("Executor nao configurado")

                # Executa workflow
                execution_id = await self._executor(
                    workflow_id=job.workflow_id,
                    trigger_id=job.trigger_id,
                    input_data=job.input_data,
                )

                # Registra resultado
                self._results[job.id] = JobResult(
                    job_id=job.id,
                    execution_id=execution_id,
                    success=True,
                )

                logger.info(f"Job {job.id} executado com sucesso")

            except Exception as e:
                logger.error(f"Erro ao executar job {job.id}: {e}")
                self._results[job.id] = JobResult(
                    job_id=job.id,
                    execution_id="",
                    success=False,
                    error=str(e),
                )

            finally:
                self._running_jobs.discard(job.id)
                self._job_map.pop(job.id, None)

                # Reagenda se recorrente
                if job.recurring:
                    await self._reschedule_job(job)

    async def _reschedule_job(self, job: ScheduledJob) -> None:
        """Reagenda job recorrente."""
        # Obtem trigger para calcular proxima execucao
        # Em producao, buscaria do repositorio
        # Por simplicidade, calcula baseado no ultimo run_at

        # Cria novo job
        new_job = ScheduledJob(
            id=str(uuid.uuid4()),
            run_at=job.run_at + timedelta(days=1),  # Simplificado
            trigger_id=job.trigger_id,
            workflow_id=job.workflow_id,
            input_data=job.input_data,
            recurring=True,
        )

        heapq.heappush(self._job_queue, new_job)
        self._job_map[new_job.id] = new_job

        logger.info(f"Job reagendado: {new_job.id} para {new_job.run_at}")

    def _calculate_next_run(self, trigger: Trigger) -> Optional[datetime]:
        """Calcula proxima execucao baseado no trigger."""
        config = trigger.schedule_config
        if not config:
            return None

        now = datetime.utcnow()

        if config.frequency == ScheduleFrequency.ONCE:
            return config.run_at

        if config.frequency == ScheduleFrequency.MINUTELY:
            return now + timedelta(minutes=config.interval)

        if config.frequency == ScheduleFrequency.HOURLY:
            return now + timedelta(hours=config.interval)

        if config.frequency == ScheduleFrequency.DAILY:
            next_run = now.replace(
                hour=config.time_of_day.hour if config.time_of_day else 0,
                minute=config.time_of_day.minute if config.time_of_day else 0,
                second=0,
                microsecond=0,
            )
            if next_run <= now:
                next_run += timedelta(days=config.interval)
            return next_run

        if config.frequency == ScheduleFrequency.WEEKLY:
            if not config.days_of_week:
                return now + timedelta(weeks=1)

            for i in range(7):
                check_date = now + timedelta(days=i)
                if check_date.weekday() in config.days_of_week:
                    next_run = check_date.replace(
                        hour=config.time_of_day.hour if config.time_of_day else 0,
                        minute=config.time_of_day.minute if config.time_of_day else 0,
                        second=0,
                    )
                    if next_run > now:
                        return next_run

            return now + timedelta(weeks=1)

        if config.frequency == ScheduleFrequency.MONTHLY:
            next_run = now.replace(
                day=min(config.day_of_month, 28),
                hour=config.time_of_day.hour if config.time_of_day else 0,
                minute=config.time_of_day.minute if config.time_of_day else 0,
                second=0,
            )
            if next_run <= now:
                if now.month == 12:
                    next_run = next_run.replace(year=now.year + 1, month=1)
                else:
                    next_run = next_run.replace(month=now.month + 1)
            return next_run

        return now + timedelta(minutes=1)

    # Estatisticas

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatisticas do scheduler."""
        return {
            "running": self._running,
            "pending_jobs": len(self._job_map),
            "running_jobs": len(self._running_jobs),
            "max_concurrent": self._max_concurrent,
            "total_executed": len(self._results),
            "successful": sum(1 for r in self._results.values() if r.success),
            "failed": sum(1 for r in self._results.values() if not r.success),
        }

    def get_next_scheduled_job(self) -> Optional[ScheduledJob]:
        """Retorna proximo job a ser executado."""
        for job in self._job_queue:
            if job.id in self._job_map:
                return job
        return None
