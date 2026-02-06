"""
Gerador de Relatórios Departamentais - Conecta PRO
=================================================

Gera relatórios detalhados e personalizados por departamento,
mostrando pendências, tendências e métricas de produtividade.

Autor: Conecta PRO Team + Claude AI
Data: 2026-01-10
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from ..models import PendingTask, Department, TaskCategory, TaskPriority, TaskStatus
from ..dashboard.unified_dashboard import UnifiedDashboard

logger = logging.getLogger(__name__)


@dataclass
class DepartmentMetrics:
    """Métricas consolidadas de um departamento."""
    
    department: str
    total_tasks: int
    critical_tasks: int
    high_tasks: int
    overdue_tasks: int
    avg_resolution_time: float
    productivity_score: float
    compliance_rate: float
    
    # Tendências (variação % vs período anterior)
    tasks_trend: float
    resolution_trend: float
    productivity_trend: float


@dataclass
class CategoryBreakdown:
    """Breakdown por categoria."""
    
    category: str
    count: int
    percentage: float
    avg_urgency: float


class DepartmentReportGenerator:
    """Gerador de relatórios departamentais inteligentes."""
    
    def __init__(self, db: Session, dashboard: UnifiedDashboard):
        self.db = db
        self.dashboard = dashboard
    
    async def generate_hr_report(self) -> Dict[str, Any]:
        """Relatório específico do RH."""
        base_metrics = await self._get_department_metrics(Department.HR)
        
        # Métricas específicas do RH
        hr_specific = {
            "missing_documents": await self._count_missing_documents(),
            "expiring_contracts": await self._count_expiring_contracts(),
            "pending_medical_exams": await self._count_pending_medical_exams(),
            "training_backlog": await self._count_training_backlog(),
            "performance_reviews_due": await self._count_pending_reviews()
        }
        
        return {
            **asdict(base_metrics),
            "hr_metrics": hr_specific,
            "recommendations": await self._generate_hr_recommendations(hr_specific),
            "action_plan": await self._create_hr_action_plan(hr_specific)
        }
    
    async def generate_commercial_report(self) -> Dict[str, Any]:
        """Relatório específico do Comercial."""
        base_metrics = await self._get_department_metrics(Department.COMMERCIAL)
        
        commercial_specific = {
            "pending_quotes": await self._count_pending_quotes(),
            "overdue_proposals": await self._count_overdue_proposals(),
            "follow_ups_needed": await self._count_follow_ups_needed(),
            "contracts_pending_signature": await self._count_pending_signatures(),
            "pipeline_stalled": await self._count_stalled_pipeline()
        }
        
        return {
            **asdict(base_metrics),
            "commercial_metrics": commercial_specific,
            "recommendations": await self._generate_commercial_recommendations(commercial_specific)
        }
    
    async def generate_financial_report(self) -> Dict[str, Any]:
        """Relatório específico do Financeiro."""
        base_metrics = await self._get_department_metrics(Department.FINANCIAL)
        
        financial_specific = {
            "overdue_payments": await self._count_overdue_payments(),
            "pending_approvals": await self._count_pending_approvals(),
            "missing_receipts": await self._count_missing_receipts(),
            "reconciliation_pending": await self._count_pending_reconciliation(),
            "budget_reviews_due": await self._count_budget_reviews()
        }
        
        return {
            **asdict(base_metrics),
            "financial_metrics": financial_specific,
            "recommendations": await self._generate_financial_recommendations(financial_specific)
        }
    
    async def generate_facilities_report(self) -> Dict[str, Any]:
        """Relatório específico do Facilities.""" 
        base_metrics = await self._get_department_metrics(Department.FACILITIES)
        
        facilities_specific = {
            "overdue_maintenance": await self._count_overdue_maintenance(),
            "pending_inspections": await self._count_pending_inspections(),
            "equipment_issues": await self._count_equipment_issues(),
            "supplier_evaluations": await self._count_supplier_evaluations(),
            "service_contracts_expiring": await self._count_expiring_contracts()
        }
        
        return {
            **asdict(base_metrics),
            "facilities_metrics": facilities_specific,
            "recommendations": await self._generate_facilities_recommendations(facilities_specific)
        }
    
    async def generate_executive_summary(self) -> Dict[str, Any]:
        """Resumo executivo consolidado."""
        all_departments = []
        
        for dept in [Department.HR, Department.COMMERCIAL, Department.FINANCIAL, Department.FACILITIES]:
            metrics = await self._get_department_metrics(dept)
            all_departments.append(metrics)
        
        # Identifica departamentos com problemas
        problem_departments = sorted(
            all_departments,
            key=lambda d: d.critical_tasks + d.overdue_tasks,
            reverse=True
        )
        
        return {
            "summary": {
                "total_departments": len(all_departments),
                "total_tasks": sum(d.total_tasks for d in all_departments),
                "total_critical": sum(d.critical_tasks for d in all_departments),
                "avg_productivity": sum(d.productivity_score for d in all_departments) / len(all_departments)
            },
            "departments": [asdict(d) for d in all_departments],
            "problem_departments": [asdict(d) for d in problem_departments[:3]],
            "system_health": await self._assess_overall_health(all_departments),
            "executive_recommendations": await self._generate_executive_recommendations(problem_departments)
        }
    
    # Métodos auxiliares
    
    async def _get_department_metrics(self, department: Department) -> DepartmentMetrics:
        """Calcula métricas base de um departamento."""
        tasks = self.db.query(PendingTask).filter(
            PendingTask.department == department,
            PendingTask.status == TaskStatus.PENDING
        ).all()
        
        total = len(tasks)
        critical = len([t for t in tasks if t.priority == TaskPriority.CRITICAL])
        high = len([t for t in tasks if t.priority == TaskPriority.HIGH])
        overdue = len([t for t in tasks if t.due_date and t.due_date < date.today()])
        
        # Mockando outras métricas por enquanto
        return DepartmentMetrics(
            department=department.value,
            total_tasks=total,
            critical_tasks=critical,
            high_tasks=high,
            overdue_tasks=overdue,
            avg_resolution_time=3.2,  # Mock
            productivity_score=85.0,  # Mock
            compliance_rate=92.0,     # Mock
            tasks_trend=-5.2,         # Mock
            resolution_trend=12.1,    # Mock
            productivity_trend=3.8    # Mock
        )
    
    async def _count_missing_documents(self) -> int:
        """Mock - contar documentos faltando no RH."""
        return 8
    
    async def _count_expiring_contracts(self) -> int:
        """Mock - contar contratos vencendo."""
        return 3
    
    async def _count_pending_medical_exams(self) -> int:
        """Mock - contar exames médicos pendentes."""
        return 12
    
    async def _count_training_backlog(self) -> int:
        """Mock - contar treinamentos atrasados."""
        return 5
    
    async def _count_pending_reviews(self) -> int:
        """Mock - contar avaliações pendentes."""
        return 7
    
    async def _count_pending_quotes(self) -> int:
        """Mock - contar orçamentos pendentes."""
        return 15
    
    async def _count_overdue_proposals(self) -> int:
        """Mock - contar propostas atrasadas."""
        return 6
    
    async def _count_follow_ups_needed(self) -> int:
        """Mock - contar follow-ups necessários."""
        return 22
    
    async def _count_pending_signatures(self) -> int:
        """Mock - contar contratos pendentes de assinatura."""
        return 4
    
    async def _count_stalled_pipeline(self) -> int:
        """Mock - contar pipeline travado."""
        return 9
    
    async def _count_overdue_payments(self) -> int:
        """Mock - contar pagamentos atrasados."""
        return 11
    
    async def _count_pending_approvals(self) -> int:
        """Mock - contar aprovações pendentes."""
        return 8
    
    async def _count_missing_receipts(self) -> int:
        """Mock - contar recibos faltando."""
        return 14
    
    async def _count_pending_reconciliation(self) -> int:
        """Mock - contar reconciliações pendentes."""
        return 6
    
    async def _count_budget_reviews(self) -> int:
        """Mock - contar revisões de orçamento."""
        return 3
    
    async def _count_overdue_maintenance(self) -> int:
        """Mock - contar manutenções atrasadas."""
        return 7
    
    async def _count_pending_inspections(self) -> int:
        """Mock - contar inspeções pendentes."""
        return 4
    
    async def _count_equipment_issues(self) -> int:
        """Mock - contar problemas de equipamento."""
        return 9
    
    async def _count_supplier_evaluations(self) -> int:
        """Mock - contar avaliações de fornecedor."""
        return 5
    
    async def _generate_hr_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Gera recomendações para o RH."""
        recommendations = []
        
        if metrics["missing_documents"] > 5:
            recommendations.append("📋 Priorizar coleta de documentos faltantes")
        
        if metrics["pending_medical_exams"] > 10:
            recommendations.append("🏥 Agendar exames médicos em massa")
        
        if metrics["expiring_contracts"] > 0:
            recommendations.append("📝 Renovar contratos próximos do vencimento")
        
        return recommendations
    
    async def _create_hr_action_plan(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Cria plano de ação para RH."""
        actions = []
        
        if metrics["missing_documents"] > 0:
            actions.append({
                "action": "Campanha de coleta de documentos",
                "priority": "high",
                "deadline": (date.today() + timedelta(days=7)).isoformat(),
                "responsible": "Analista de RH"
            })
        
        return actions
    
    async def _generate_commercial_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Gera recomendações para Comercial."""
        recommendations = []
        
        if metrics["pending_quotes"] > 10:
            recommendations.append("💰 Acelerar processo de cotação")
        
        if metrics["overdue_proposals"] > 5:
            recommendations.append("📊 Revisar propostas atrasadas")
        
        return recommendations
    
    async def _generate_financial_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Gera recomendações para Financeiro."""
        recommendations = []
        
        if metrics["overdue_payments"] > 5:
            recommendations.append("💳 Regularizar pagamentos atrasados")
        
        return recommendations
    
    async def _generate_facilities_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Gera recomendações para Facilities."""
        recommendations = []
        
        if metrics["overdue_maintenance"] > 5:
            recommendations.append("🔧 Acelerar manutenções pendentes")
        
        return recommendations
    
    async def _assess_overall_health(self, departments: List[DepartmentMetrics]) -> Dict[str, Any]:
        """Avalia saúde geral do sistema."""
        total_critical = sum(d.critical_tasks for d in departments)
        avg_productivity = sum(d.productivity_score for d in departments) / len(departments)
        
        if total_critical <= 5 and avg_productivity >= 85:
            status = "healthy"
        elif total_critical <= 15 and avg_productivity >= 75:
            status = "warning"
        else:
            status = "critical"
        
        return {
            "status": status,
            "overall_score": avg_productivity,
            "critical_tasks": total_critical,
            "departments_at_risk": len([d for d in departments if d.productivity_score < 70])
        }
    
    async def _generate_executive_recommendations(self, problem_departments: List[DepartmentMetrics]) -> List[str]:
        """Gera recomendações executivas."""
        recommendations = []
        
        if problem_departments:
            worst = problem_departments[0]
            recommendations.append(
                f"🎯 Atenção prioritária ao departamento {worst.department} "
                f"({worst.critical_tasks + worst.overdue_tasks} tarefas críticas)"
            )
        
        high_critical = [d for d in problem_departments if d.critical_tasks > 10]
        if high_critical:
            recommendations.append("🚨 Múltiplos departamentos com tarefas críticas - revisar processos")
        
        return recommendations[:3]
