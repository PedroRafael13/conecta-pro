"""
Report Scheduler - Agendamento de relatórios.

Gerencia agendamentos e execução automática de relatórios.
"""

import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from modules.ai.report_generator.models import AIReportSchedule, ReportExecution
from modules.ai.report_generator.models.report_execution import ExecutionTriggerEnum
from modules.ai.report_generator.models.report_schedule import (
    ScheduleFrequencyEnum,
    ScheduleStatusEnum,
)
from modules.ai.report_generator.repositories import ReportRepository

logger = logging.getLogger(__name__)


class ReportScheduler:
    """Serviço de agendamento de relatórios."""

    def __init__(self, db: Session):
        """Inicializa scheduler."""
        self.db = db
        self.repository = ReportRepository(db)

    def create_schedule(
        self,
        name: str,
        template_id: UUID,
        frequency: ScheduleFrequencyEnum,
        run_time: str | None = None,
        timezone: str = "America/Sao_Paulo",
        days_of_week: list[int] | None = None,
        days_of_month: list[int] | None = None,
        period_type: str | None = None,
        parameters: dict[str, Any] | None = None,
        filters: dict[str, Any] | None = None,
        output_formats: list[str] | None = None,
        email_recipients: list[str] | None = None,
        email_subject: str | None = None,
        email_body: str | None = None,
        webhook_url: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        max_runs: int | None = None,
        created_by: UUID | None = None,
        organization_id: UUID | None = None,
    ) -> AIReportSchedule:
        """Cria novo agendamento."""
        from datetime import time as dt_time

        # Converte run_time string para time
        run_time_obj = None
        if run_time:
            parts = run_time.split(":")
            run_time_obj = dt_time(int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)

        schedule = AIReportSchedule(
            name=name,
            template_id=template_id,
            frequency=frequency,
            run_time=run_time_obj,
            timezone=timezone,
            days_of_week=days_of_week or [],
            days_of_month=days_of_month or [],
            period_type=period_type or "previous_day",
            parameters=parameters or {},
            filters=filters or {},
            output_formats=output_formats or ["pdf"],
            delivery_methods=["email"] if email_recipients else ["storage"],
            email_recipients=email_recipients or [],
            email_subject=email_subject,
            email_body=email_body,
            webhook_url=webhook_url,
            start_date=start_date,
            end_date=end_date,
            max_runs=max_runs,
            created_by=created_by,
            organization_id=organization_id,
            status=ScheduleStatusEnum.ACTIVE,
        )

        return self.repository.create_schedule(schedule)

    def update_schedule(self, schedule_id: UUID, **kwargs) -> AIReportSchedule | None:
        """Atualiza agendamento."""
        schedule = self.repository.get_schedule(schedule_id)
        if not schedule:
            return None

        for key, value in kwargs.items():
            if hasattr(schedule, key) and value is not None:
                setattr(schedule, key, value)

        # Recalcula próxima execução se necessário
        if any(k in kwargs for k in ["frequency", "run_time", "days_of_week", "days_of_month"]):
            schedule.next_run_at = schedule.calculate_next_run()

        return self.repository.update_schedule(schedule)

    def pause_schedule(self, schedule_id: UUID) -> AIReportSchedule | None:
        """Pausa agendamento."""
        schedule = self.repository.get_schedule(schedule_id)
        if schedule:
            schedule.pause()
            return self.repository.update_schedule(schedule)
        return None

    def resume_schedule(self, schedule_id: UUID) -> AIReportSchedule | None:
        """Retoma agendamento."""
        schedule = self.repository.get_schedule(schedule_id)
        if schedule:
            schedule.resume()
            return self.repository.update_schedule(schedule)
        return None

    def cancel_schedule(self, schedule_id: UUID) -> AIReportSchedule | None:
        """Cancela agendamento."""
        schedule = self.repository.get_schedule(schedule_id)
        if schedule:
            schedule.cancel()
            return self.repository.update_schedule(schedule)
        return None

    def get_due_schedules(self) -> list[AIReportSchedule]:
        """Busca agendamentos prontos para execução."""
        return self.repository.get_due_schedules()

    def process_due_schedules(self) -> list[dict[str, Any]]:
        """Processa todos os agendamentos pendentes."""
        results = []
        due_schedules = self.get_due_schedules()

        for schedule in due_schedules:
            try:
                result = self._execute_schedule(schedule)
                results.append(
                    {
                        "schedule_id": str(schedule.id),
                        "schedule_name": schedule.name,
                        "status": "success",
                        "execution_id": result.get("execution_id"),
                    }
                )
            except Exception as e:
                logger.error(f"Erro ao executar agendamento {schedule.id}: {e}")
                results.append(
                    {
                        "schedule_id": str(schedule.id),
                        "schedule_name": schedule.name,
                        "status": "error",
                        "error": str(e),
                    }
                )

        return results

    def _execute_schedule(self, schedule: AIReportSchedule) -> dict[str, Any]:
        """Executa um agendamento específico."""
        # Calcula período
        period_start, period_end = schedule.get_report_period()

        # Cria execução
        execution = ReportExecution(
            template_id=schedule.template_id,
            schedule_id=schedule.id,
            trigger=ExecutionTriggerEnum.SCHEDULED,
            parameters=schedule.parameters,
            filters=schedule.filters,
            period_start=period_start,
            period_end=period_end,
            requested_formats=schedule.output_formats,
            organization_id=schedule.organization_id,
        )
        execution = self.repository.create_execution(execution)

        # Atualiza schedule
        schedule.record_success()
        self.repository.update_schedule(schedule)

        logger.info(f"Agendamento executado: {schedule.name}")

        return {
            "execution_id": str(execution.id),
            "schedule_id": str(schedule.id),
            "period_start": period_start.isoformat() if period_start else None,
            "period_end": period_end.isoformat() if period_end else None,
        }

    def get_schedule_summary(self, organization_id: UUID | None = None) -> dict[str, Any]:
        """Retorna resumo dos agendamentos."""
        schedules, total = self.repository.list_schedules(organization_id=organization_id, limit=1000)

        active = sum(1 for s in schedules if s.status == ScheduleStatusEnum.ACTIVE)
        paused = sum(1 for s in schedules if s.status == ScheduleStatusEnum.PAUSED)
        failed = sum(1 for s in schedules if s.status == ScheduleStatusEnum.FAILED)

        due = len(self.get_due_schedules())

        # Por frequência
        by_frequency = {}
        for schedule in schedules:
            freq = schedule.frequency.value
            by_frequency[freq] = by_frequency.get(freq, 0) + 1

        # Próximas execuções
        upcoming = sorted(
            [s for s in schedules if s.next_run_at and s.status == ScheduleStatusEnum.ACTIVE],
            key=lambda x: x.next_run_at,
        )[:5]

        return {
            "total": total,
            "active": active,
            "paused": paused,
            "failed": failed,
            "due_now": due,
            "by_frequency": by_frequency,
            "upcoming": [
                {
                    "id": str(s.id),
                    "name": s.name,
                    "next_run": s.next_run_at.isoformat() if s.next_run_at else None,
                }
                for s in upcoming
            ],
        }

    def retry_failed_schedules(self) -> list[dict[str, Any]]:
        """Tenta reexecutar agendamentos com falha."""
        results = []
        failed_schedules = self.repository.get_failed_schedules()

        for schedule in failed_schedules:
            if schedule.consecutive_failures < schedule.max_consecutive_failures:
                schedule.resume()
                self.repository.update_schedule(schedule)
                results.append(
                    {
                        "schedule_id": str(schedule.id),
                        "action": "resumed",
                    }
                )
            else:
                results.append(
                    {
                        "schedule_id": str(schedule.id),
                        "action": "skipped",
                        "reason": "Max consecutive failures reached",
                    }
                )

        return results
