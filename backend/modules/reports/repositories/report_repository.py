"""
Repository para o módulo de Relatórios Gerenciais
Sprint 34: Relatórios Gerenciais
"""
# pylint: disable=too-many-locals,too-many-public-methods,singleton-comparison

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from modules.reports.models import (
    ReportTemplate,
    ReportSchedule,
    ReportExport,
    ExecutiveKPI,
    Benchmark,
    TemplateStatus,
    ScheduleStatus,
    ExportStatus,
    KPIStatus,
    KPIAlertLevel,
    BenchmarkStatus,
)

logger = logging.getLogger(__name__)


class ReportRepository:
    """Repository para operações de relatórios."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== ReportTemplate ====================

    async def create_template(self, template: ReportTemplate) -> ReportTemplate:
        """Cria um template de relatório."""
        self.db.add(template)
        await self.db.flush()
        await self.db.refresh(template)
        return template

    async def get_template(
        self,
        tenant_id: UUID,
        template_id: UUID
    ) -> Optional[ReportTemplate]:
        """Busca template por ID."""
        result = await self.db.execute(
            select(ReportTemplate).where(
                and_(
                    ReportTemplate.tenant_id == tenant_id,
                    ReportTemplate.id == template_id,
                    ReportTemplate.ativo == True
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_template_by_code(
        self,
        tenant_id: UUID,
        code: str
    ) -> Optional[ReportTemplate]:
        """Busca template por código."""
        result = await self.db.execute(
            select(ReportTemplate).where(
                and_(
                    ReportTemplate.tenant_id == tenant_id,
                    ReportTemplate.code == code,
                    ReportTemplate.ativo == True
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_templates(
        self,
        tenant_id: UUID,
        category: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[ReportTemplate], int]:
        """Lista templates com filtros."""
        query = select(ReportTemplate).where(
            and_(
                ReportTemplate.tenant_id == tenant_id,
                ReportTemplate.ativo == True
            )
        )

        if category:
            query = query.where(ReportTemplate.category == category)
        if status:
            query = query.where(ReportTemplate.status == status)
        if search:
            query = query.where(
                or_(
                    ReportTemplate.name.ilike(f"%{search}%"),
                    ReportTemplate.code.ilike(f"%{search}%"),
                    ReportTemplate.description.ilike(f"%{search}%")
                )
            )

        # Total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Resultados
        query = query.order_by(desc(ReportTemplate.updated_at))
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)

        return result.scalars().all(), total

    async def update_template(self, template: ReportTemplate) -> ReportTemplate:
        """Atualiza um template."""
        await self.db.flush()
        await self.db.refresh(template)
        return template

    async def delete_template(self, template: ReportTemplate) -> None:
        """Remove template (soft delete)."""
        template.ativo = False
        template.updated_at = datetime.utcnow()
        await self.db.flush()

    async def get_top_templates(
        self,
        tenant_id: UUID,
        limit: int = 10
    ) -> List[ReportTemplate]:
        """Retorna templates mais usados."""
        result = await self.db.execute(
            select(ReportTemplate).where(
                and_(
                    ReportTemplate.tenant_id == tenant_id,
                    ReportTemplate.ativo == True,
                    ReportTemplate.status == TemplateStatus.ACTIVE
                )
            ).order_by(desc(ReportTemplate.usage_count)).limit(limit)
        )
        return result.scalars().all()

    # ==================== ReportSchedule ====================

    async def create_schedule(self, schedule: ReportSchedule) -> ReportSchedule:
        """Cria um agendamento."""
        self.db.add(schedule)
        await self.db.flush()
        await self.db.refresh(schedule)
        return schedule

    async def get_schedule(
        self,
        tenant_id: UUID,
        schedule_id: UUID
    ) -> Optional[ReportSchedule]:
        """Busca agendamento por ID."""
        result = await self.db.execute(
            select(ReportSchedule).where(
                and_(
                    ReportSchedule.tenant_id == tenant_id,
                    ReportSchedule.id == schedule_id,
                    ReportSchedule.ativo == True
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_schedules(
        self,
        tenant_id: UUID,
        template_id: Optional[UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[ReportSchedule], int]:
        """Lista agendamentos com filtros."""
        query = select(ReportSchedule).where(
            and_(
                ReportSchedule.tenant_id == tenant_id,
                ReportSchedule.ativo == True
            )
        )

        if template_id:
            query = query.where(ReportSchedule.template_id == template_id)
        if status:
            query = query.where(ReportSchedule.status == status)

        # Total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Resultados
        query = query.order_by(ReportSchedule.next_execution_at)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)

        return result.scalars().all(), total

    async def get_due_schedules(
        self,
        tenant_id: Optional[UUID] = None
    ) -> List[ReportSchedule]:
        """Retorna agendamentos a serem executados."""
        now = datetime.utcnow()
        query = select(ReportSchedule).where(
            and_(
                ReportSchedule.status == ScheduleStatus.ACTIVE,
                ReportSchedule.ativo == True,
                ReportSchedule.next_execution_at <= now
            )
        )

        if tenant_id:
            query = query.where(ReportSchedule.tenant_id == tenant_id)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_schedule(self, schedule: ReportSchedule) -> ReportSchedule:
        """Atualiza um agendamento."""
        await self.db.flush()
        await self.db.refresh(schedule)
        return schedule

    async def delete_schedule(self, schedule: ReportSchedule) -> None:
        """Remove agendamento (soft delete)."""
        schedule.ativo = False
        schedule.status = ScheduleStatus.CANCELLED
        schedule.updated_at = datetime.utcnow()
        await self.db.flush()

    # ==================== ReportExport ====================

    async def create_export(self, export: ReportExport) -> ReportExport:
        """Cria uma exportação."""
        self.db.add(export)
        await self.db.flush()
        await self.db.refresh(export)
        return export

    async def get_export(
        self,
        tenant_id: UUID,
        export_id: UUID
    ) -> Optional[ReportExport]:
        """Busca exportação por ID."""
        result = await self.db.execute(
            select(ReportExport).where(
                and_(
                    ReportExport.tenant_id == tenant_id,
                    ReportExport.id == export_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_export_by_token(self, token: str) -> Optional[ReportExport]:
        """Busca exportação por token de download."""
        result = await self.db.execute(
            select(ReportExport).where(
                ReportExport.download_token == token
            )
        )
        return result.scalar_one_or_none()

    async def list_exports(
        self,
        tenant_id: UUID,
        template_id: Optional[UUID] = None,
        schedule_id: Optional[UUID] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[ReportExport], int]:
        """Lista exportações com filtros."""
        query = select(ReportExport).where(
            ReportExport.tenant_id == tenant_id
        )

        if template_id:
            query = query.where(ReportExport.template_id == template_id)
        if schedule_id:
            query = query.where(ReportExport.schedule_id == schedule_id)
        if status:
            query = query.where(ReportExport.status == status)
        if start_date:
            query = query.where(ReportExport.created_at >= start_date)
        if end_date:
            query = query.where(ReportExport.created_at <= end_date)

        # Total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Resultados
        query = query.order_by(desc(ReportExport.created_at))
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)

        return result.scalars().all(), total

    async def get_pending_exports(
        self,
        tenant_id: Optional[UUID] = None
    ) -> List[ReportExport]:
        """Retorna exportações pendentes."""
        query = select(ReportExport).where(
            ReportExport.status == ExportStatus.PENDING
        )

        if tenant_id:
            query = query.where(ReportExport.tenant_id == tenant_id)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_export(self, export: ReportExport) -> ReportExport:
        """Atualiza uma exportação."""
        await self.db.flush()
        await self.db.refresh(export)
        return export

    async def get_export_stats(
        self,
        tenant_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """Retorna estatísticas de exportações."""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        # Total
        total_result = await self.db.execute(
            select(func.count(ReportExport.id)).where(
                and_(
                    ReportExport.tenant_id == tenant_id,
                    ReportExport.created_at >= start_date,
                    ReportExport.created_at <= end_date
                )
            )
        )
        total = total_result.scalar() or 0

        # Por status
        status_result = await self.db.execute(
            select(ReportExport.status, func.count(ReportExport.id)).where(
                and_(
                    ReportExport.tenant_id == tenant_id,
                    ReportExport.created_at >= start_date,
                    ReportExport.created_at <= end_date
                )
            ).group_by(ReportExport.status)
        )
        by_status = {str(row[0].value): row[1] for row in status_result.all()}

        # Por formato
        format_result = await self.db.execute(
            select(ReportExport.format, func.count(ReportExport.id)).where(
                and_(
                    ReportExport.tenant_id == tenant_id,
                    ReportExport.created_at >= start_date,
                    ReportExport.created_at <= end_date
                )
            ).group_by(ReportExport.format)
        )
        by_format = {str(row[0].value): row[1] for row in format_result.all()}

        return {
            "total": total,
            "by_status": by_status,
            "by_format": by_format,
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat()
        }

    # ==================== ExecutiveKPI ====================

    async def create_kpi(self, kpi: ExecutiveKPI) -> ExecutiveKPI:
        """Cria um KPI."""
        self.db.add(kpi)
        await self.db.flush()
        await self.db.refresh(kpi)
        return kpi

    async def get_kpi(
        self,
        tenant_id: UUID,
        kpi_id: UUID
    ) -> Optional[ExecutiveKPI]:
        """Busca KPI por ID."""
        result = await self.db.execute(
            select(ExecutiveKPI).where(
                and_(
                    ExecutiveKPI.tenant_id == tenant_id,
                    ExecutiveKPI.id == kpi_id,
                    ExecutiveKPI.ativo == True
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_kpi_by_code(
        self,
        tenant_id: UUID,
        code: str
    ) -> Optional[ExecutiveKPI]:
        """Busca KPI por código."""
        result = await self.db.execute(
            select(ExecutiveKPI).where(
                and_(
                    ExecutiveKPI.tenant_id == tenant_id,
                    ExecutiveKPI.code == code,
                    ExecutiveKPI.ativo == True
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_kpis(
        self,
        tenant_id: UUID,
        category: Optional[str] = None,
        status: Optional[str] = None,
        alert_level: Optional[str] = None,
        visible_on_dashboard: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[ExecutiveKPI], int]:
        """Lista KPIs com filtros."""
        query = select(ExecutiveKPI).where(
            and_(
                ExecutiveKPI.tenant_id == tenant_id,
                ExecutiveKPI.ativo == True
            )
        )

        if category:
            query = query.where(ExecutiveKPI.category == category)
        if status:
            query = query.where(ExecutiveKPI.status == status)
        if alert_level:
            query = query.where(ExecutiveKPI.alert_level == alert_level)
        if visible_on_dashboard is not None:
            query = query.where(ExecutiveKPI.visible_on_dashboard == visible_on_dashboard)

        # Total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Resultados
        query = query.order_by(ExecutiveKPI.display_order, ExecutiveKPI.name)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)

        return result.scalars().all(), total

    async def get_dashboard_kpis(self, tenant_id: UUID) -> List[ExecutiveKPI]:
        """Retorna KPIs para dashboard."""
        result = await self.db.execute(
            select(ExecutiveKPI).where(
                and_(
                    ExecutiveKPI.tenant_id == tenant_id,
                    ExecutiveKPI.ativo == True,
                    ExecutiveKPI.status == KPIStatus.ACTIVE,
                    ExecutiveKPI.visible_on_dashboard == True
                )
            ).order_by(ExecutiveKPI.display_order, ExecutiveKPI.name)
        )
        return result.scalars().all()

    async def get_kpis_needing_attention(
        self,
        tenant_id: UUID
    ) -> List[ExecutiveKPI]:
        """Retorna KPIs que precisam de atenção."""
        result = await self.db.execute(
            select(ExecutiveKPI).where(
                and_(
                    ExecutiveKPI.tenant_id == tenant_id,
                    ExecutiveKPI.ativo == True,
                    ExecutiveKPI.status == KPIStatus.ACTIVE,
                    ExecutiveKPI.alert_level.in_([
                        KPIAlertLevel.WARNING,
                        KPIAlertLevel.CRITICAL
                    ])
                )
            ).order_by(ExecutiveKPI.alert_level)
        )
        return result.scalars().all()

    async def update_kpi(self, kpi: ExecutiveKPI) -> ExecutiveKPI:
        """Atualiza um KPI."""
        await self.db.flush()
        await self.db.refresh(kpi)
        return kpi

    async def delete_kpi(self, kpi: ExecutiveKPI) -> None:
        """Remove KPI (soft delete)."""
        kpi.ativo = False
        kpi.updated_at = datetime.utcnow()
        await self.db.flush()

    # ==================== Benchmark ====================

    async def create_benchmark(self, benchmark: Benchmark) -> Benchmark:
        """Cria um benchmark."""
        self.db.add(benchmark)
        await self.db.flush()
        await self.db.refresh(benchmark)
        return benchmark

    async def get_benchmark(
        self,
        tenant_id: UUID,
        benchmark_id: UUID
    ) -> Optional[Benchmark]:
        """Busca benchmark por ID."""
        result = await self.db.execute(
            select(Benchmark).where(
                and_(
                    Benchmark.tenant_id == tenant_id,
                    Benchmark.id == benchmark_id,
                    Benchmark.ativo == True
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_benchmark_by_code(
        self,
        tenant_id: UUID,
        code: str
    ) -> Optional[Benchmark]:
        """Busca benchmark por código."""
        result = await self.db.execute(
            select(Benchmark).where(
                and_(
                    Benchmark.tenant_id == tenant_id,
                    Benchmark.code == code,
                    Benchmark.ativo == True
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_benchmarks(
        self,
        tenant_id: UUID,
        category: Optional[str] = None,
        benchmark_type: Optional[str] = None,
        industry: Optional[str] = None,
        status: Optional[str] = None,
        visible_on_dashboard: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Benchmark], int]:
        """Lista benchmarks com filtros."""
        query = select(Benchmark).where(
            and_(
                Benchmark.tenant_id == tenant_id,
                Benchmark.ativo == True
            )
        )

        if category:
            query = query.where(Benchmark.category == category)
        if benchmark_type:
            query = query.where(Benchmark.benchmark_type == benchmark_type)
        if industry:
            query = query.where(Benchmark.industry == industry)
        if status:
            query = query.where(Benchmark.status == status)
        if visible_on_dashboard is not None:
            query = query.where(Benchmark.visible_on_dashboard == visible_on_dashboard)

        # Total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Resultados
        query = query.order_by(Benchmark.display_order, Benchmark.name)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)

        return result.scalars().all(), total

    async def get_dashboard_benchmarks(self, tenant_id: UUID) -> List[Benchmark]:
        """Retorna benchmarks para dashboard."""
        result = await self.db.execute(
            select(Benchmark).where(
                and_(
                    Benchmark.tenant_id == tenant_id,
                    Benchmark.ativo == True,
                    Benchmark.status == BenchmarkStatus.ACTIVE,
                    Benchmark.visible_on_dashboard == True
                )
            ).order_by(Benchmark.display_order, Benchmark.name)
        )
        return result.scalars().all()

    async def get_benchmarks_below_target(
        self,
        tenant_id: UUID
    ) -> List[Benchmark]:
        """Retorna benchmarks abaixo da meta."""
        result = await self.db.execute(
            select(Benchmark).where(
                and_(
                    Benchmark.tenant_id == tenant_id,
                    Benchmark.ativo == True,
                    Benchmark.status == BenchmarkStatus.ACTIVE,
                    Benchmark.comparison_result.in_(["below", "poor"])
                )
            )
        )
        return result.scalars().all()

    async def update_benchmark(self, benchmark: Benchmark) -> Benchmark:
        """Atualiza um benchmark."""
        await self.db.flush()
        await self.db.refresh(benchmark)
        return benchmark

    async def delete_benchmark(self, benchmark: Benchmark) -> None:
        """Remove benchmark (soft delete)."""
        benchmark.ativo = False
        benchmark.updated_at = datetime.utcnow()
        await self.db.flush()

    # ==================== Dashboard Stats ====================

    async def get_reports_dashboard_stats(self, tenant_id: UUID) -> dict:
        """Retorna estatísticas para dashboard de relatórios."""
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Templates ativos
        templates_result = await self.db.execute(
            select(func.count(ReportTemplate.id)).where(
                and_(
                    ReportTemplate.tenant_id == tenant_id,
                    ReportTemplate.ativo == True,
                    ReportTemplate.status == TemplateStatus.ACTIVE
                )
            )
        )
        total_templates = templates_result.scalar() or 0

        # Agendamentos ativos
        schedules_result = await self.db.execute(
            select(func.count(ReportSchedule.id)).where(
                and_(
                    ReportSchedule.tenant_id == tenant_id,
                    ReportSchedule.ativo == True,
                    ReportSchedule.status == ScheduleStatus.ACTIVE
                )
            )
        )
        active_schedules = schedules_result.scalar() or 0

        # Exportações hoje
        today_result = await self.db.execute(
            select(func.count(ReportExport.id)).where(
                and_(
                    ReportExport.tenant_id == tenant_id,
                    ReportExport.created_at >= today_start
                )
            )
        )
        exports_today = today_result.scalar() or 0

        # Exportações este mês
        month_result = await self.db.execute(
            select(func.count(ReportExport.id)).where(
                and_(
                    ReportExport.tenant_id == tenant_id,
                    ReportExport.created_at >= month_start
                )
            )
        )
        exports_this_month = month_result.scalar() or 0

        # Pendentes
        pending_result = await self.db.execute(
            select(func.count(ReportExport.id)).where(
                and_(
                    ReportExport.tenant_id == tenant_id,
                    ReportExport.status.in_([
                        ExportStatus.PENDING,
                        ExportStatus.PROCESSING
                    ])
                )
            )
        )
        pending_exports = pending_result.scalar() or 0

        # Falhas (últimos 7 dias)
        week_ago = now - timedelta(days=7)
        failed_result = await self.db.execute(
            select(func.count(ReportExport.id)).where(
                and_(
                    ReportExport.tenant_id == tenant_id,
                    ReportExport.status == ExportStatus.FAILED,
                    ReportExport.created_at >= week_ago
                )
            )
        )
        failed_exports = failed_result.scalar() or 0

        return {
            "total_templates": total_templates,
            "active_schedules": active_schedules,
            "exports_today": exports_today,
            "exports_this_month": exports_this_month,
            "pending_exports": pending_exports,
            "failed_exports": failed_exports
        }
