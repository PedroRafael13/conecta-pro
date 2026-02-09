"""
Report Repository - Acesso a dados de relatórios.

Implementa operações CRUD e consultas para o módulo de relatórios.
"""

import logging
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import asc, desc, func, or_
from sqlalchemy.orm import Session

from modules.ai.report_generator.models import (
    AIReportSchedule,
    AIReportTemplate,
    Report,
    ReportExecution,
    ReportSection,
    ReportWidget,
)
from modules.ai.report_generator.models.report import ReportStatusEnum, ReportTypeEnum
from modules.ai.report_generator.models.report_execution import ExecutionStatusEnum
from modules.ai.report_generator.models.report_schedule import ScheduleStatusEnum
from modules.ai.report_generator.models.report_template import TemplateStatusEnum

logger = logging.getLogger(__name__)


class ReportRepository:
    """Repositório para operações de relatórios."""

    def __init__(self, db: Session):
        """Inicializa repositório."""
        self.db = db

    # ============== REPORT CRUD ==============

    def create_report(self, report: Report) -> Report:
        """Cria novo relatório."""
        # Gera código único
        if not report.code:
            count = self.db.query(Report).count()
            report.code = f"RPT-{count + 1:06d}"

        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        logger.info(f"Relatório criado: {report.code}")
        return report

    def get_report(self, report_id: UUID) -> Report | None:
        """Busca relatório por ID."""
        return self.db.query(Report).filter(Report.id == report_id, Report.is_active).first()

    def get_report_by_code(self, code: str) -> Report | None:
        """Busca relatório por código."""
        return self.db.query(Report).filter(Report.code == code, Report.is_active).first()

    def update_report(self, report: Report) -> Report:
        """Atualiza relatório."""
        report.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(report)
        return report

    def delete_report(self, report_id: UUID) -> bool:
        """Soft delete de relatório."""
        report = self.get_report(report_id)
        if report:
            report.is_active = False
            report.deleted_at = datetime.utcnow()
            self.db.commit()
            return True
        return False

    def list_reports(
        self,
        organization_id: UUID | None = None,
        report_type: ReportTypeEnum | None = None,
        status: ReportStatusEnum | None = None,
        category: str | None = None,
        template_id: UUID | None = None,
        created_by: UUID | None = None,
        period_start: datetime | None = None,
        period_end: datetime | None = None,
        search: str | None = None,
        tags: list[str] | None = None,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "created_at",
        order_dir: str = "desc",
    ) -> tuple[list[Report], int]:
        """Lista relatórios com filtros."""
        query = self.db.query(Report).filter(Report.is_active)

        if organization_id:
            query = query.filter(Report.organization_id == organization_id)
        if report_type:
            query = query.filter(Report.report_type == report_type)
        if status:
            query = query.filter(Report.status == status)
        if category:
            query = query.filter(Report.category == category)
        if template_id:
            query = query.filter(Report.template_id == template_id)
        if created_by:
            query = query.filter(Report.created_by == created_by)
        if period_start:
            query = query.filter(Report.created_at >= period_start)
        if period_end:
            query = query.filter(Report.created_at <= period_end)
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    Report.name.ilike(search_filter),
                    Report.code.ilike(search_filter),
                    Report.description.ilike(search_filter),
                )
            )
        if tags:
            for tag in tags:
                query = query.filter(Report.tags.contains([tag]))

        total = query.count()

        # Ordenação
        order_column = getattr(Report, order_by, Report.created_at)
        if order_dir == "desc":
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(asc(order_column))

        reports = query.offset(skip).limit(limit).all()
        return reports, total

    def get_recent_reports(self, organization_id: UUID | None = None, limit: int = 10) -> list[Report]:
        """Busca relatórios recentes."""
        query = self.db.query(Report).filter(Report.is_active, Report.status == ReportStatusEnum.COMPLETED)
        if organization_id:
            query = query.filter(Report.organization_id == organization_id)
        return query.order_by(desc(Report.generated_at)).limit(limit).all()

    # ============== TEMPLATE CRUD ==============

    def create_template(self, template: AIReportTemplate) -> AIReportTemplate:
        """Cria novo template."""
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        logger.info(f"Template criado: {template.code}")
        return template

    def get_template(self, template_id: UUID) -> AIReportTemplate | None:
        """Busca template por ID."""
        return (
            self.db.query(AIReportTemplate)
            .filter(AIReportTemplate.id == template_id, AIReportTemplate.is_active)
            .first()
        )

    def get_template_by_code(self, code: str) -> AIReportTemplate | None:
        """Busca template por código."""
        return self.db.query(AIReportTemplate).filter(AIReportTemplate.code == code, AIReportTemplate.is_active).first()

    def update_template(self, template: AIReportTemplate) -> AIReportTemplate:
        """Atualiza template."""
        template.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(template)
        return template

    def delete_template(self, template_id: UUID) -> bool:
        """Soft delete de template."""
        template = self.get_template(template_id)
        if template:
            template.is_active = False
            template.deleted_at = datetime.utcnow()
            self.db.commit()
            return True
        return False

    def list_templates(
        self,
        organization_id: UUID | None = None,
        category: str | None = None,
        status: TemplateStatusEnum | None = None,
        is_public: bool | None = None,
        is_system: bool | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[AIReportTemplate], int]:
        """Lista templates com filtros."""
        query = self.db.query(AIReportTemplate).filter(AIReportTemplate.is_active)

        if organization_id:
            query = query.filter(
                or_(
                    AIReportTemplate.organization_id == organization_id,
                    AIReportTemplate.is_public,
                    AIReportTemplate.is_system,
                )
            )
        if category:
            query = query.filter(AIReportTemplate.category == category)
        if status:
            query = query.filter(AIReportTemplate.status == status)
        if is_public is not None:
            query = query.filter(AIReportTemplate.is_public == is_public)
        if is_system is not None:
            query = query.filter(AIReportTemplate.is_system == is_system)
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    AIReportTemplate.name.ilike(search_filter),
                    AIReportTemplate.code.ilike(search_filter),
                    AIReportTemplate.description.ilike(search_filter),
                )
            )

        total = query.count()
        templates = query.order_by(desc(AIReportTemplate.usage_count)).offset(skip).limit(limit).all()
        return templates, total

    def get_most_used_templates(self, limit: int = 10) -> list[AIReportTemplate]:
        """Busca templates mais usados."""
        return (
            self.db.query(AIReportTemplate)
            .filter(AIReportTemplate.is_active, AIReportTemplate.status == TemplateStatusEnum.ACTIVE)
            .order_by(desc(AIReportTemplate.usage_count))
            .limit(limit)
            .all()
        )

    # ============== SCHEDULE CRUD ==============

    def create_schedule(self, schedule: AIReportSchedule) -> AIReportSchedule:
        """Cria novo agendamento."""
        # Calcula próxima execução
        schedule.next_run_at = schedule.calculate_next_run()

        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        logger.info(f"Agendamento criado: {schedule.name}")
        return schedule

    def get_schedule(self, schedule_id: UUID) -> AIReportSchedule | None:
        """Busca agendamento por ID."""
        return (
            self.db.query(AIReportSchedule)
            .filter(AIReportSchedule.id == schedule_id, AIReportSchedule.is_active)
            .first()
        )

    def update_schedule(self, schedule: AIReportSchedule) -> AIReportSchedule:
        """Atualiza agendamento."""
        schedule.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(schedule)
        return schedule

    def delete_schedule(self, schedule_id: UUID) -> bool:
        """Soft delete de agendamento."""
        schedule = self.get_schedule(schedule_id)
        if schedule:
            schedule.is_active = False
            schedule.deleted_at = datetime.utcnow()
            self.db.commit()
            return True
        return False

    def list_schedules(
        self,
        organization_id: UUID | None = None,
        template_id: UUID | None = None,
        status: ScheduleStatusEnum | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[AIReportSchedule], int]:
        """Lista agendamentos com filtros."""
        query = self.db.query(AIReportSchedule).filter(AIReportSchedule.is_active)

        if organization_id:
            query = query.filter(AIReportSchedule.organization_id == organization_id)
        if template_id:
            query = query.filter(AIReportSchedule.template_id == template_id)
        if status:
            query = query.filter(AIReportSchedule.status == status)

        total = query.count()
        schedules = query.order_by(asc(AIReportSchedule.next_run_at)).offset(skip).limit(limit).all()
        return schedules, total

    def get_due_schedules(self) -> list[AIReportSchedule]:
        """Busca agendamentos prontos para execução."""
        now = datetime.utcnow()
        return (
            self.db.query(AIReportSchedule)
            .filter(
                AIReportSchedule.is_active,
                AIReportSchedule.status == ScheduleStatusEnum.ACTIVE,
                AIReportSchedule.next_run_at <= now,
            )
            .order_by(asc(AIReportSchedule.next_run_at))
            .all()
        )

    def get_failed_schedules(self) -> list[AIReportSchedule]:
        """Busca agendamentos com falha."""
        return (
            self.db.query(AIReportSchedule)
            .filter(AIReportSchedule.is_active, AIReportSchedule.status == ScheduleStatusEnum.FAILED)
            .all()
        )

    # ============== EXECUTION CRUD ==============

    def create_execution(self, execution: ReportExecution) -> ReportExecution:
        """Cria nova execução."""
        # Define número da execução
        if execution.schedule_id:
            count = self.db.query(ReportExecution).filter(ReportExecution.schedule_id == execution.schedule_id).count()
            execution.execution_number = count + 1
        else:
            execution.execution_number = 1

        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        return execution

    def get_execution(self, execution_id: UUID) -> ReportExecution | None:
        """Busca execução por ID."""
        return self.db.query(ReportExecution).filter(ReportExecution.id == execution_id).first()

    def update_execution(self, execution: ReportExecution) -> ReportExecution:
        """Atualiza execução."""
        execution.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(execution)
        return execution

    def list_executions(
        self,
        report_id: UUID | None = None,
        template_id: UUID | None = None,
        schedule_id: UUID | None = None,
        status: ExecutionStatusEnum | None = None,
        trigger: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[ReportExecution], int]:
        """Lista execuções com filtros."""
        query = self.db.query(ReportExecution)

        if report_id:
            query = query.filter(ReportExecution.report_id == report_id)
        if template_id:
            query = query.filter(ReportExecution.template_id == template_id)
        if schedule_id:
            query = query.filter(ReportExecution.schedule_id == schedule_id)
        if status:
            query = query.filter(ReportExecution.status == status)
        if trigger:
            query = query.filter(ReportExecution.trigger == trigger)

        total = query.count()
        executions = query.order_by(desc(ReportExecution.created_at)).offset(skip).limit(limit).all()
        return executions, total

    def get_running_executions(self) -> list[ReportExecution]:
        """Busca execuções em andamento."""
        running_statuses = [
            ExecutionStatusEnum.PENDING,
            ExecutionStatusEnum.QUEUED,
            ExecutionStatusEnum.RUNNING,
            ExecutionStatusEnum.COLLECTING_DATA,
            ExecutionStatusEnum.PROCESSING,
            ExecutionStatusEnum.GENERATING_INSIGHTS,
            ExecutionStatusEnum.RENDERING,
            ExecutionStatusEnum.EXPORTING,
            ExecutionStatusEnum.DELIVERING,
        ]
        return self.db.query(ReportExecution).filter(ReportExecution.status.in_(running_statuses)).all()

    # ============== SECTION CRUD ==============

    def create_section(self, section: ReportSection) -> ReportSection:
        """Cria nova seção."""
        self.db.add(section)
        self.db.commit()
        self.db.refresh(section)
        return section

    def get_section(self, section_id: UUID) -> ReportSection | None:
        """Busca seção por ID."""
        return self.db.query(ReportSection).filter(ReportSection.id == section_id, ReportSection.is_active).first()

    def list_sections_by_report(self, report_id: UUID) -> list[ReportSection]:
        """Lista seções de um relatório."""
        return (
            self.db.query(ReportSection)
            .filter(ReportSection.report_id == report_id, ReportSection.is_active)
            .order_by(asc(ReportSection.order))
            .all()
        )

    def list_sections_by_template(self, template_id: UUID) -> list[ReportSection]:
        """Lista seções de um template."""
        return (
            self.db.query(ReportSection)
            .filter(ReportSection.template_id == template_id, ReportSection.is_active)
            .order_by(asc(ReportSection.order))
            .all()
        )

    # ============== WIDGET CRUD ==============

    def create_widget(self, widget: ReportWidget) -> ReportWidget:
        """Cria novo widget."""
        self.db.add(widget)
        self.db.commit()
        self.db.refresh(widget)
        return widget

    def get_widget(self, widget_id: UUID) -> ReportWidget | None:
        """Busca widget por ID."""
        return self.db.query(ReportWidget).filter(ReportWidget.id == widget_id, ReportWidget.is_active).first()

    def list_widgets_by_template(self, template_id: UUID) -> list[ReportWidget]:
        """Lista widgets de um template."""
        return (
            self.db.query(ReportWidget)
            .filter(ReportWidget.template_id == template_id, ReportWidget.is_active)
            .order_by(asc(ReportWidget.order))
            .all()
        )

    def list_reusable_widgets(
        self, organization_id: UUID | None = None, widget_type: str | None = None
    ) -> list[ReportWidget]:
        """Lista widgets reutilizáveis."""
        query = self.db.query(ReportWidget).filter(ReportWidget.is_active, ReportWidget.is_reusable)
        if organization_id:
            query = query.filter(or_(ReportWidget.organization_id == organization_id, ReportWidget.is_system))
        if widget_type:
            query = query.filter(ReportWidget.widget_type == widget_type)
        return query.all()

    # ============== STATISTICS ==============

    def get_report_stats(self, organization_id: UUID | None = None, days: int = 30) -> dict[str, Any]:
        """Obtém estatísticas de relatórios."""
        start_date = datetime.utcnow() - timedelta(days=days)

        query = self.db.query(Report).filter(Report.is_active, Report.created_at >= start_date)
        if organization_id:
            query = query.filter(Report.organization_id == organization_id)

        total = query.count()
        completed = query.filter(Report.status == ReportStatusEnum.COMPLETED).count()
        failed = query.filter(Report.status == ReportStatusEnum.FAILED).count()

        # Média de tempo de geração
        avg_time = self.db.query(func.avg(Report.generation_time_ms)).filter(
            Report.is_active, Report.status == ReportStatusEnum.COMPLETED, Report.created_at >= start_date
        )
        if organization_id:
            avg_time = avg_time.filter(Report.organization_id == organization_id)
        avg_generation_time = avg_time.scalar() or 0

        # Total de insights
        total_insights = self.db.query(func.sum(func.jsonb_array_length(Report.insights))).filter(
            Report.is_active, Report.created_at >= start_date
        )
        if organization_id:
            total_insights = total_insights.filter(Report.organization_id == organization_id)

        # Por tipo
        by_type = self.db.query(Report.report_type, func.count(Report.id)).filter(
            Report.is_active, Report.created_at >= start_date
        )
        if organization_id:
            by_type = by_type.filter(Report.organization_id == organization_id)
        by_type = by_type.group_by(Report.report_type).all()

        # Por status
        by_status = self.db.query(Report.status, func.count(Report.id)).filter(
            Report.is_active, Report.created_at >= start_date
        )
        if organization_id:
            by_status = by_status.filter(Report.organization_id == organization_id)
        by_status = by_status.group_by(Report.status).all()

        return {
            "total_reports": total,
            "completed": completed,
            "failed": failed,
            "success_rate": (completed / total * 100) if total > 0 else 0,
            "average_generation_time_ms": int(avg_generation_time),
            "total_insights": total_insights.scalar() or 0,
            "by_type": {t.value: c for t, c in by_type},
            "by_status": {s.value: c for s, c in by_status},
        }

    def get_schedule_stats(self, organization_id: UUID | None = None) -> dict[str, Any]:
        """Obtém estatísticas de agendamentos."""
        query = self.db.query(AIReportSchedule).filter(AIReportSchedule.is_active)
        if organization_id:
            query = query.filter(AIReportSchedule.organization_id == organization_id)

        total = query.count()
        active = query.filter(AIReportSchedule.status == ScheduleStatusEnum.ACTIVE).count()
        paused = query.filter(AIReportSchedule.status == ScheduleStatusEnum.PAUSED).count()
        failed = query.filter(AIReportSchedule.status == ScheduleStatusEnum.FAILED).count()

        # Total de execuções
        total_runs = self.db.query(func.sum(AIReportSchedule.total_runs)).filter(AIReportSchedule.is_active)
        if organization_id:
            total_runs = total_runs.filter(AIReportSchedule.organization_id == organization_id)

        successful_runs = self.db.query(func.sum(AIReportSchedule.successful_runs)).filter(AIReportSchedule.is_active)
        if organization_id:
            successful_runs = successful_runs.filter(AIReportSchedule.organization_id == organization_id)

        return {
            "total_schedules": total,
            "active": active,
            "paused": paused,
            "failed": failed,
            "total_runs": total_runs.scalar() or 0,
            "successful_runs": successful_runs.scalar() or 0,
            "overall_success_rate": ((successful_runs.scalar() or 0) / (total_runs.scalar() or 1) * 100),
        }

    def get_execution_metrics(self, days: int = 7, organization_id: UUID | None = None) -> dict[str, Any]:
        """Obtém métricas de execuções."""
        start_date = datetime.utcnow() - timedelta(days=days)

        query = self.db.query(ReportExecution).filter(ReportExecution.created_at >= start_date)
        if organization_id:
            query = query.filter(ReportExecution.organization_id == organization_id)

        total = query.count()
        completed = query.filter(ReportExecution.status == ExecutionStatusEnum.COMPLETED).count()
        failed = query.filter(
            ReportExecution.status.in_([ExecutionStatusEnum.FAILED, ExecutionStatusEnum.TIMEOUT])
        ).count()

        # Média de tempos
        avg_metrics = self.db.query(
            func.avg(ReportExecution.data_collection_time_ms),
            func.avg(ReportExecution.processing_time_ms),
            func.avg(ReportExecution.insight_generation_time_ms),
            func.avg(ReportExecution.rendering_time_ms),
            func.avg(ReportExecution.total_time_ms),
        ).filter(ReportExecution.status == ExecutionStatusEnum.COMPLETED, ReportExecution.created_at >= start_date)
        if organization_id:
            avg_metrics = avg_metrics.filter(ReportExecution.organization_id == organization_id)
        metrics = avg_metrics.first()

        return {
            "total_executions": total,
            "completed": completed,
            "failed": failed,
            "success_rate": (completed / total * 100) if total > 0 else 0,
            "avg_data_collection_time_ms": int(metrics[0] or 0) if metrics else 0,
            "avg_processing_time_ms": int(metrics[1] or 0) if metrics else 0,
            "avg_insight_generation_time_ms": int(metrics[2] or 0) if metrics else 0,
            "avg_rendering_time_ms": int(metrics[3] or 0) if metrics else 0,
            "avg_total_time_ms": int(metrics[4] or 0) if metrics else 0,
        }

    def get_dashboard_data(self, organization_id: UUID | None = None) -> dict[str, Any]:
        """Obtém dados para dashboard."""
        return {
            "report_stats": self.get_report_stats(organization_id),
            "schedule_stats": self.get_schedule_stats(organization_id),
            "execution_metrics": self.get_execution_metrics(organization_id=organization_id),
            "recent_reports": [r.to_summary_dict() for r in self.get_recent_reports(organization_id, 5)],
            "most_used_templates": [
                {"id": str(t.id), "code": t.code, "name": t.name, "usage_count": t.usage_count}
                for t in self.get_most_used_templates(5)
            ],
            "due_schedules": len(self.get_due_schedules()),
            "running_executions": len(self.get_running_executions()),
        }
