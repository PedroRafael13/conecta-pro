"""Repository para ScheduledReport."""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy import select, update, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.analytics_dashboard.models import (
    ScheduledReport,
    ReportStatus,
)
from modules.hr.analytics_dashboard.schemas import (
    ScheduledReportCreate,
    ScheduledReportUpdate,
)

logger = logging.getLogger(__name__)


class ReportRepository:
    """Repository para operações de relatórios agendados."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_report(
        self,
        data: ScheduledReportCreate,
        condominio_id: UUID,
        owner_id: UUID,
    ) -> ScheduledReport:
        """Cria novo relatório agendado."""
        report = ScheduledReport(
            condominio_id=condominio_id,
            owner_id=owner_id,
            created_by=owner_id,
            **data.model_dump(exclude_unset=True),
        )

        # Calcular próxima execução
        report.next_run_at = report.calculate_next_run()

        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def get_report_by_id(
        self,
        report_id: UUID,
    ) -> Optional[ScheduledReport]:
        """Busca relatório por ID."""
        query = select(ScheduledReport).where(
            ScheduledReport.id == report_id,
            ScheduledReport.is_active.is_(True),
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_reports(
        self,
        condominio_id: UUID,
        owner_id: UUID = None,
        report_type: str = None,
        status: ReportStatus = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[ScheduledReport], int]:
        """Lista relatórios com filtros."""
        conditions = [
            ScheduledReport.condominio_id == condominio_id,
            ScheduledReport.is_active.is_(True),
        ]

        if owner_id:
            conditions.append(ScheduledReport.owner_id == owner_id)

        if report_type:
            conditions.append(ScheduledReport.report_type == report_type)

        if status:
            conditions.append(ScheduledReport.status == status.value)

        # Query principal
        query = (
            select(ScheduledReport)
            .where(and_(*conditions))
            .order_by(
                ScheduledReport.next_run_at.asc().nulls_last(),
                ScheduledReport.name,
            )
        )

        # Contagem total
        count_query = select(func.count(ScheduledReport.id)).where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Paginação
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self.db.execute(query)
        reports = result.scalars().all()

        return list(reports), total

    async def update_report(
        self,
        report_id: UUID,
        data: ScheduledReportUpdate,
    ) -> Optional[ScheduledReport]:
        """Atualiza relatório."""
        report = await self.get_report_by_id(report_id)
        if not report:
            return None

        update_data = data.model_dump(exclude_unset=True)

        # Se mudou frequência ou horário, recalcular próxima execução
        recalculate = any(
            key in update_data
            for key in ["frequency", "schedule_time", "schedule_day"]
        )

        for field, value in update_data.items():
            setattr(report, field, value)

        if recalculate and report.status == ReportStatus.ACTIVE.value:
            report.next_run_at = report.calculate_next_run()

        report.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def delete_report(self, report_id: UUID) -> bool:
        """Deleta relatório (soft delete)."""
        stmt = (
            update(ScheduledReport)
            .where(ScheduledReport.id == report_id)
            .values(
                is_active=False,
                status=ReportStatus.DISABLED.value,
                updated_at=datetime.utcnow(),
            )
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    async def get_due_reports(
        self,
        limit: int = 50,
    ) -> List[ScheduledReport]:
        """Busca relatórios prontos para execução."""
        query = (
            select(ScheduledReport)
            .where(
                ScheduledReport.status == ReportStatus.ACTIVE.value,
                ScheduledReport.is_active.is_(True),
                ScheduledReport.next_run_at <= datetime.utcnow(),
            )
            .order_by(ScheduledReport.next_run_at)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def record_run(
        self,
        report_id: UUID,
        success: bool,
        error: str = None,
        file_path: str = None,
        file_size: int = None,
        duration_ms: int = None,
    ) -> Optional[ScheduledReport]:
        """Registra execução de relatório."""
        report = await self.get_report_by_id(report_id)
        if not report:
            return None

        report.record_run(
            success=success,
            error=error,
            file_path=file_path,
            file_size=file_size,
            duration_ms=duration_ms,
        )

        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def pause_report(self, report_id: UUID) -> bool:
        """Pausa relatório."""
        stmt = (
            update(ScheduledReport)
            .where(ScheduledReport.id == report_id)
            .values(
                status=ReportStatus.PAUSED.value,
                updated_at=datetime.utcnow(),
            )
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    async def resume_report(self, report_id: UUID) -> Optional[ScheduledReport]:
        """Retoma relatório pausado."""
        report = await self.get_report_by_id(report_id)
        if not report:
            return None

        report.resume()
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def get_reports_by_recipient(
        self,
        email: str,
        condominio_id: UUID = None,
    ) -> List[ScheduledReport]:
        """Busca relatórios por destinatário."""
        conditions = [
            ScheduledReport.is_active.is_(True),
            ScheduledReport.status == ReportStatus.ACTIVE.value,
        ]

        if condominio_id:
            conditions.append(ScheduledReport.condominio_id == condominio_id)

        query = (
            select(ScheduledReport)
            .where(and_(*conditions))
            .filter(
                or_(
                    ScheduledReport.recipients.contains([email]),
                    ScheduledReport.cc_recipients.contains([email]),
                )
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_upcoming_reports(
        self,
        condominio_id: UUID,
        hours_ahead: int = 24,
    ) -> List[ScheduledReport]:
        """Busca relatórios que serão executados nas próximas horas."""
        future = datetime.utcnow() + timedelta(hours=hours_ahead)

        query = (
            select(ScheduledReport)
            .where(
                ScheduledReport.condominio_id == condominio_id,
                ScheduledReport.status == ReportStatus.ACTIVE.value,
                ScheduledReport.is_active.is_(True),
                ScheduledReport.next_run_at.between(datetime.utcnow(), future),
            )
            .order_by(ScheduledReport.next_run_at)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_statistics(  # pylint: disable=too-many-locals
        self,
        condominio_id: UUID = None,
    ) -> dict:
        """Retorna estatísticas de relatórios."""
        conditions = [ScheduledReport.is_active.is_(True)]
        if condominio_id:
            conditions.append(ScheduledReport.condominio_id == condominio_id)

        # Por status
        status_query = (
            select(
                ScheduledReport.status,
                func.count(ScheduledReport.id),
            )
            .where(and_(*conditions))
            .group_by(ScheduledReport.status)
        )
        status_result = await self.db.execute(status_query)
        by_status = {row[0]: row[1] for row in status_result.all()}

        # Por tipo
        type_query = (
            select(
                ScheduledReport.report_type,
                func.count(ScheduledReport.id),
            )
            .where(and_(*conditions))
            .group_by(ScheduledReport.report_type)
        )
        type_result = await self.db.execute(type_query)
        by_type = {row[0]: row[1] for row in type_result.all()}

        # Por frequência
        freq_query = (
            select(
                ScheduledReport.frequency,
                func.count(ScheduledReport.id),
            )
            .where(and_(*conditions))
            .group_by(ScheduledReport.frequency)
        )
        freq_result = await self.db.execute(freq_query)
        by_frequency = {row[0]: row[1] for row in freq_result.all()}

        # Execuções totais
        runs_query = select(
            func.sum(ScheduledReport.run_count),
            func.sum(ScheduledReport.success_count),
            func.sum(ScheduledReport.failure_count),
        ).where(and_(*conditions))
        runs_result = await self.db.execute(runs_query)
        runs = runs_result.one()

        total_runs = runs[0] or 0
        success_runs = runs[1] or 0
        failure_runs = runs[2] or 0

        return {
            "by_status": by_status,
            "by_type": by_type,
            "by_frequency": by_frequency,
            "total_runs": total_runs,
            "success_runs": success_runs,
            "failure_runs": failure_runs,
            "success_rate": round(success_runs / total_runs * 100, 2) if total_runs > 0 else 0,
        }

    async def cleanup_completed(
        self,
        older_than_days: int = 90,
        dry_run: bool = True,
    ) -> dict:
        """Remove relatórios completados antigos."""
        cutoff = datetime.utcnow() - timedelta(days=older_than_days)

        conditions = [
            ScheduledReport.status == ReportStatus.COMPLETED.value,
            ScheduledReport.updated_at < cutoff,
        ]

        # Contar
        count_query = select(func.count(ScheduledReport.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        count = count_result.scalar()

        if not dry_run and count > 0:
            stmt = (
                update(ScheduledReport)
                .where(and_(*conditions))
                .values(is_active=False)
            )
            await self.db.execute(stmt)
            await self.db.commit()

        return {
            "count": count,
            "deleted": not dry_run,
            "cutoff_date": cutoff.isoformat(),
        }
