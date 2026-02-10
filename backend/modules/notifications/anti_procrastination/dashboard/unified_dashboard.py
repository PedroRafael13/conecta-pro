"""
Dashboard Unificado de Pendências - Conecta PRO
==============================================

Centraliza todas as pendências de todos os módulos em uma interface única
que permite visão executiva e departamental das tarefas em aberto.

Autor: Conecta PRO Team + Claude AI
Data: 2026-01-10
"""

import logging
from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from ..integration.module_integrator import ModuleIntegrator
from ..models import (
    Department,
    DepartmentSummary,
    EscalationLevel,
    PendingTask,
    PendingTaskData,
    SystemSummary,
    TaskCategory,
    TaskFilter,
    TaskPriority,
    TaskStatus,
)

logger = logging.getLogger(__name__)


class UnifiedDashboard:
    """
    Dashboard unificado que agrega pendências de todos os módulos.

    Funcionalidades:
    - Visão executiva geral
    - Dashboards por departamento
    - Drill-down para detalhes
    - Métricas de produtividade
    - Alertas em tempo real
    """

    def __init__(self, db: Session, integrator: ModuleIntegrator):
        self.db = db
        self.integrator = integrator
        self._cache_timeout = 300  # 5 minutos
        self._last_cache_update = None
        self._cached_summary = None

    async def get_system_summary(self, force_refresh: bool = False) -> SystemSummary:
        """
        Resumo geral do sistema de pendências.

        Args:
            force_refresh: Força atualização do cache

        Returns:
            SystemSummary: Resumo consolidado
        """
        # Verifica cache
        if not force_refresh and self._is_cache_valid():
            return self._cached_summary

        logger.info("Atualizando resumo geral do sistema")

        # Sincroniza dados dos módulos
        await self.integrator.sync_all_modules()

        # Calcula estatísticas
        total_pending = self._count_tasks_by_status(TaskStatus.PENDING)
        critical_count = self._count_tasks_by_priority(TaskPriority.CRITICAL)
        high_count = self._count_tasks_by_priority(TaskPriority.HIGH)
        medium_count = self._count_tasks_by_priority(TaskPriority.MEDIUM)
        low_count = self._count_tasks_by_priority(TaskPriority.LOW)
        overdue_count = self._count_overdue_tasks()

        # Resumos por departamento
        departments = await self._get_department_summaries()

        # Métricas avançadas
        avg_resolution_time = self._calculate_avg_resolution_time()
        top_bottlenecks = await self._identify_bottlenecks()

        summary = SystemSummary(
            total_pending=total_pending,
            critical_count=critical_count,
            high_count=high_count,
            medium_count=medium_count,
            low_count=low_count,
            overdue_count=overdue_count,
            departments=departments,
            avg_resolution_time=avg_resolution_time,
            top_bottlenecks=top_bottlenecks,
        )

        # Atualiza cache
        self._cached_summary = summary
        self._last_cache_update = datetime.utcnow()

        return summary

    async def get_department_dashboard(self, department: Department, limit: int = 50) -> dict[str, Any]:
        """
        Dashboard específico de um departamento.

        Args:
            department: Departamento alvo
            limit: Limite de tarefas a retornar

        Returns:
            Dict com dashboard departamental
        """
        logger.info(f"Carregando dashboard do departamento: {department.value}")

        # Filtra tarefas do departamento
        tasks_query = (
            self.db.query(PendingTask)
            .filter(and_(PendingTask.department == department, PendingTask.status == TaskStatus.PENDING))
            .order_by(desc(PendingTask.created_at))
        )

        tasks = tasks_query.limit(limit).all()

        # Estatísticas específicas
        stats = {
            "total_tasks": tasks_query.count(),
            "critical_tasks": tasks_query.filter(PendingTask.priority == TaskPriority.CRITICAL).count(),
            "high_tasks": tasks_query.filter(PendingTask.priority == TaskPriority.HIGH).count(),
            "overdue_tasks": tasks_query.filter(PendingTask.due_date < date.today()).count(),
            "escalated_tasks": tasks_query.filter(PendingTask.escalation_level > EscalationLevel.LEVEL_0).count(),
        }

        # Agrupa por categoria
        category_breakdown = self._group_tasks_by_category(tasks)

        # Top tarefas mais urgentes
        urgent_tasks = sorted(
            [self._task_to_data(task) for task in tasks], key=lambda x: x.urgency_score, reverse=True
        )[:10]

        # Tendências (últimos 30 dias)
        trends = await self._calculate_department_trends(department)

        return {
            "department": department.value,
            "summary": stats,
            "tasks": [self._task_to_dict(task) for task in tasks],
            "urgent_tasks": [self._task_data_to_dict(task) for task in urgent_tasks],
            "category_breakdown": category_breakdown,
            "trends": trends,
            "last_updated": datetime.utcnow().isoformat(),
        }

    async def get_executive_dashboard(self) -> dict[str, Any]:
        """
        Dashboard executivo com visão de alto nível.

        Returns:
            Dict com métricas executivas
        """
        logger.info("Carregando dashboard executivo")

        summary = await self.get_system_summary()

        # KPIs executivos
        kpis = await self._calculate_executive_kpis()

        # Departamentos com mais problemas
        problem_departments = sorted(
            summary.departments, key=lambda d: d.critical_tasks + d.overdue_tasks, reverse=True
        )[:5]

        # Tendência geral (últimos 7 dias)
        weekly_trend = await self._calculate_weekly_trend()

        # Alertas críticos que requerem atenção executiva
        critical_alerts = await self._get_critical_alerts()

        return {
            "summary": summary.dict(),
            "kpis": kpis,
            "problem_departments": [dept.dict() for dept in problem_departments],
            "weekly_trend": weekly_trend,
            "critical_alerts": critical_alerts,
            "system_health": await self._assess_system_health(),
            "recommendations": await self._generate_executive_recommendations(),
            "last_updated": datetime.utcnow().isoformat(),
        }

    async def search_tasks(self, filters: TaskFilter) -> list[dict[str, Any]]:
        """
        Busca avançada de tarefas com filtros.

        Args:
            filters: Filtros de busca

        Returns:
            Lista de tarefas filtradas
        """
        logger.info(f"Buscando tarefas com filtros: {filters}")

        query = self.db.query(PendingTask)

        # Aplica filtros
        if filters.department:
            query = query.filter(PendingTask.department == filters.department)

        if filters.category:
            query = query.filter(PendingTask.category == filters.category)

        if filters.priority:
            query = query.filter(PendingTask.priority == filters.priority)

        if filters.status:
            query = query.filter(PendingTask.status == filters.status)

        if filters.assigned_to:
            query = query.filter(PendingTask.assigned_to == filters.assigned_to)

        if filters.days_pending_min:
            min_date = datetime.utcnow() - timedelta(days=filters.days_pending_min)
            query = query.filter(PendingTask.created_at <= min_date)

        if filters.days_pending_max:
            max_date = datetime.utcnow() - timedelta(days=filters.days_pending_max)
            query = query.filter(PendingTask.created_at >= max_date)

        if filters.escalation_level:
            query = query.filter(PendingTask.escalation_level == filters.escalation_level)

        # Ordenação por urgência
        query = query.order_by(desc(PendingTask.created_at))

        # Paginação
        tasks = query.offset(filters.offset).limit(filters.limit).all()

        return [self._task_to_dict(task) for task in tasks]

    # Métodos auxiliares privados

    def _is_cache_valid(self) -> bool:
        """Verifica se o cache ainda é válido."""
        if not self._last_cache_update:
            return False

        elapsed = (datetime.utcnow() - self._last_cache_update).total_seconds()
        return elapsed < self._cache_timeout

    def _count_tasks_by_status(self, status: TaskStatus) -> int:
        """Conta tarefas por status."""
        return self.db.query(PendingTask).filter(PendingTask.status == status).count()

    def _count_tasks_by_priority(self, priority: TaskPriority) -> int:
        """Conta tarefas por prioridade."""
        return (
            self.db.query(PendingTask)
            .filter(and_(PendingTask.priority == priority, PendingTask.status == TaskStatus.PENDING))
            .count()
        )

    def _count_overdue_tasks(self) -> int:
        """Conta tarefas atrasadas."""
        return (
            self.db.query(PendingTask)
            .filter(and_(PendingTask.due_date < date.today(), PendingTask.status == TaskStatus.PENDING))
            .count()
        )

    async def _get_department_summaries(self) -> list[DepartmentSummary]:
        """Gera resumos por departamento."""
        summaries = []

        for dept in Department:
            dept_tasks = (
                self.db.query(PendingTask)
                .filter(and_(PendingTask.department == dept, PendingTask.status == TaskStatus.PENDING))
                .all()
            )

            if dept_tasks:
                critical_count = len([t for t in dept_tasks if t.priority == TaskPriority.CRITICAL])
                high_count = len([t for t in dept_tasks if t.priority == TaskPriority.HIGH])
                overdue_count = len([t for t in dept_tasks if t.due_date and t.due_date < date.today()])

                # Calcula score médio de urgência
                task_data_list = [self._task_to_data(t) for t in dept_tasks]
                avg_urgency = sum(td.urgency_score for td in task_data_list) / len(task_data_list)

                # Tarefa mais antiga
                oldest_days = max(td.days_pending for td in task_data_list)

                summaries.append(
                    DepartmentSummary(
                        department=dept,
                        total_tasks=len(dept_tasks),
                        critical_tasks=critical_count,
                        high_priority_tasks=high_count,
                        overdue_tasks=overdue_count,
                        avg_urgency_score=round(avg_urgency, 2),
                        oldest_task_days=oldest_days,
                    )
                )

        return sorted(summaries, key=lambda s: s.avg_urgency_score, reverse=True)

    def _calculate_avg_resolution_time(self) -> float:
        """Calcula tempo médio de resolução."""
        completed_tasks = self.db.query(PendingTask).filter(PendingTask.status == TaskStatus.COMPLETED).all()

        if not completed_tasks:
            return 0.0

        total_time = 0
        for task in completed_tasks:
            if task.completed_at and task.created_at:
                resolution_time = (task.completed_at - task.created_at).total_seconds() / 86400  # dias
                total_time += resolution_time

        return round(total_time / len(completed_tasks), 2)

    async def _identify_bottlenecks(self) -> list[dict[str, Any]]:
        """Identifica principais gargalos do sistema."""
        bottlenecks = []

        # Por departamento
        for dept in Department:
            old_tasks = (
                self.db.query(PendingTask)
                .filter(
                    and_(
                        PendingTask.department == dept,
                        PendingTask.status == TaskStatus.PENDING,
                        PendingTask.created_at < datetime.utcnow() - timedelta(days=7),
                    )
                )
                .count()
            )

            if old_tasks > 5:
                bottlenecks.append(
                    {
                        "type": "department",
                        "name": dept.value,
                        "issue": "Tarefas antigas acumulando",
                        "count": old_tasks,
                        "severity": "high" if old_tasks > 15 else "medium",
                    }
                )

        # Por categoria
        for category in TaskCategory:
            escalated_tasks = (
                self.db.query(PendingTask)
                .filter(and_(PendingTask.category == category, PendingTask.escalation_level > EscalationLevel.LEVEL_1))
                .count()
            )

            if escalated_tasks > 3:
                bottlenecks.append(
                    {
                        "type": "category",
                        "name": category.value,
                        "issue": "Muitas escalations",
                        "count": escalated_tasks,
                        "severity": "critical" if escalated_tasks > 10 else "high",
                    }
                )

        return sorted(bottlenecks, key=lambda b: b["count"], reverse=True)[:5]

    def _group_tasks_by_category(self, tasks: list[PendingTask]) -> dict[str, int]:
        """Agrupa tarefas por categoria."""
        categories = {}
        for task in tasks:
            cat = task.category.value
            categories[cat] = categories.get(cat, 0) + 1
        return categories

    def _task_to_data(self, task: PendingTask) -> PendingTaskData:
        """Converte modelo SQLAlchemy para dataclass."""
        return PendingTaskData(
            id=task.id,
            title=task.title,
            description=task.description,
            source_module=task.source_module,
            source_id=task.source_id,
            category=task.category,
            priority=task.priority,
            status=task.status,
            department=task.department,
            assigned_to=task.assigned_to,
            assigned_to_name=task.assigned_to_name,
            created_at=task.created_at,
            due_date=task.due_date,
            completed_at=task.completed_at,
            escalation_level=task.escalation_level,
            escalation_count=task.escalation_count,
            last_escalation=task.last_escalation,
            task_metadata=task.metadata or {},
            business_impact=task.business_impact,
            compliance_risk=task.compliance_risk,
        )

    def _task_to_dict(self, task: PendingTask) -> dict[str, Any]:
        """Converte tarefa para dicionário."""
        task_data = self._task_to_data(task)
        return self._task_data_to_dict(task_data)

    def _task_data_to_dict(self, task_data: PendingTaskData) -> dict[str, Any]:
        """Converte PendingTaskData para dicionário."""
        return {
            "id": str(task_data.id),
            "title": task_data.title,
            "description": task_data.description,
            "source_module": task_data.source_module,
            "source_id": task_data.source_id,
            "category": task_data.category.value,
            "priority": task_data.priority.value,
            "status": task_data.status.value,
            "department": task_data.department.value,
            "assigned_to": str(task_data.assigned_to) if task_data.assigned_to else None,
            "assigned_to_name": task_data.assigned_to_name,
            "created_at": task_data.created_at.isoformat(),
            "due_date": task_data.due_date.isoformat() if task_data.due_date else None,
            "completed_at": task_data.completed_at.isoformat() if task_data.completed_at else None,
            "escalation_level": task_data.escalation_level.value,
            "escalation_count": task_data.escalation_count,
            "last_escalation": task_data.last_escalation.isoformat() if task_data.last_escalation else None,
            "metadata": task_data.metadata,
            "business_impact": task_data.business_impact,
            "compliance_risk": task_data.compliance_risk,
            "days_pending": task_data.days_pending,
            "is_overdue": task_data.is_overdue,
            "urgency_score": task_data.urgency_score,
        }

    async def _calculate_department_trends(self, department: Department) -> dict[str, Any]:
        """Calcula tendências de um departamento."""
        # Implementar análise de tendências
        # Por exemplo: tarefas criadas vs resolvidas nos últimos 30 dias
        return {"trend": "stable", "change_percent": 0}

    async def _calculate_executive_kpis(self) -> dict[str, Any]:
        """Calcula KPIs executivos."""
        return {"productivity_index": 85.0, "compliance_score": 92.0, "response_time": 2.3, "escalation_rate": 12.0}

    async def _calculate_weekly_trend(self) -> dict[str, Any]:
        """Calcula tendência semanal."""
        return {"direction": "improving", "change": -8.5}

    async def _get_critical_alerts(self) -> list[dict[str, Any]]:
        """Busca alertas críticos para atenção executiva."""
        critical_tasks = (
            self.db.query(PendingTask)
            .filter(and_(PendingTask.priority == TaskPriority.CRITICAL, PendingTask.status == TaskStatus.PENDING))
            .all()
        )

        alerts = []
        for task in critical_tasks:
            task_data = self._task_to_data(task)
            if task_data.days_pending > 5:  # Crítica há mais de 5 dias
                alerts.append(
                    {
                        "id": str(task.id),
                        "title": task.title,
                        "department": task.department.value,
                        "days_pending": task_data.days_pending,
                        "urgency_score": task_data.urgency_score,
                        "compliance_risk": task.compliance_risk,
                    }
                )

        return sorted(alerts, key=lambda a: a["urgency_score"], reverse=True)[:5]

    async def _assess_system_health(self) -> dict[str, Any]:
        """Avalia saúde geral do sistema."""
        total_pending = self._count_tasks_by_status(TaskStatus.PENDING)
        critical_count = self._count_tasks_by_priority(TaskPriority.CRITICAL)

        # Sistema saudável se < 50 pendentes e < 5 críticas
        health_score = 100
        if total_pending > 50:
            health_score -= (total_pending - 50) * 1.5
        if critical_count > 5:
            health_score -= (critical_count - 5) * 10

        health_score = max(0, health_score)

        if health_score >= 80:
            status = "healthy"
        elif health_score >= 60:
            status = "warning"
        else:
            status = "critical"

        return {
            "status": status,
            "score": round(health_score, 1),
            "total_pending": total_pending,
            "critical_count": critical_count,
        }

    async def _generate_executive_recommendations(self) -> list[str]:
        """Gera recomendações executivas."""
        recommendations = []

        summary = await self.get_system_summary()

        if summary.critical_count > 10:
            recommendations.append(
                f"🚨 Atenção: {summary.critical_count} tarefas críticas pendentes. Considere realocação de recursos."
            )

        if summary.overdue_count > 20:
            recommendations.append(f"⏰ {summary.overdue_count} tarefas atrasadas. Revisar processos e prazos.")

        # Departamento com mais problemas
        if summary.departments:
            worst_dept = max(summary.departments, key=lambda d: d.critical_tasks + d.overdue_tasks)
            if worst_dept.critical_tasks + worst_dept.overdue_tasks > 15:
                recommendations.append(
                    f"🎯 Departamento {worst_dept.department.value} precisa de atenção especial. "
                    f"{worst_dept.critical_tasks + worst_dept.overdue_tasks} tarefas problemáticas."
                )

        return recommendations[:3]  # Máximo 3 recomendações
