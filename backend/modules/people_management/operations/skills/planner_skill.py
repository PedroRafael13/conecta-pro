"""Skill IA: Workforce Planner — Planejamento inteligente de escalas."""

import logging
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.operacional.models.allocation import Allocation
from modules.operacional.models.employee import Employee
from modules.operacional.models.post import Post

logger = logging.getLogger(__name__)


class PlannerSkill:
    """Skill IA para planejamento de força de trabalho e escalas."""

    SKILL_NAME = "workforce_planner"
    DESCRIPTION = "Planejamento inteligente de escalas e alocações"

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def coverage_analysis(self) -> dict:
        """Analisa cobertura de postos vs. funcionários alocados."""
        posts_result = await self.db.execute(select(func.count()).select_from(Post).where(Post.status == "Ativo"))
        total_posts = posts_result.scalar() or 0

        alloc_result = await self.db.execute(
            select(func.count(func.distinct(Allocation.post_id)))
            .select_from(Allocation)
            .where(Allocation.status == "Ativo")
        )
        covered_posts = alloc_result.scalar() or 0

        active_result = await self.db.execute(
            select(func.count()).select_from(Employee).where(Employee.status == "Ativo")
        )
        total_employees = active_result.scalar() or 0

        allocated_result = await self.db.execute(
            select(func.count(func.distinct(Allocation.employee_id)))
            .select_from(Allocation)
            .where(Allocation.status == "Ativo")
        )
        allocated_employees = allocated_result.scalar() or 0

        coverage_rate = round(covered_posts / max(total_posts, 1) * 100, 1)
        utilization_rate = round(allocated_employees / max(total_employees, 1) * 100, 1)

        alerts = []
        if coverage_rate < 90:
            alerts.append(
                {"type": "low_coverage", "message": f"Cobertura de postos em {coverage_rate}% — postos descobertos"}
            )
        if utilization_rate < 80:
            alerts.append(
                {"type": "low_utilization", "message": f"Utilização de {utilization_rate}% — funcionários sem alocação"}
            )

        return {
            "total_posts": total_posts,
            "covered_posts": covered_posts,
            "uncovered_posts": total_posts - covered_posts,
            "coverage_rate": coverage_rate,
            "total_employees": total_employees,
            "allocated_employees": allocated_employees,
            "unallocated_employees": total_employees - allocated_employees,
            "utilization_rate": utilization_rate,
            "alerts": alerts,
            "analyzed_at": datetime.utcnow().isoformat(),
        }

    async def overtime_forecast(self) -> dict:
        """Previsão de horas extras baseada em cobertura."""
        analysis = await self.coverage_analysis()
        uncovered = analysis["uncovered_posts"]

        from modules.people_management.common.utils.clt_calculator import SALARIO_MINIMO, calcular_hora_normal

        valor_hora = calcular_hora_normal(SALARIO_MINIMO)
        weekly_overtime = uncovered * 44
        monthly_overtime = weekly_overtime * 4
        monthly_cost = float(Decimal(str(monthly_overtime)) * valor_hora * Decimal("1.5"))

        return {
            "uncovered_posts": uncovered,
            "estimated_weekly_overtime_hours": weekly_overtime,
            "estimated_monthly_overtime_hours": monthly_overtime,
            "estimated_monthly_cost": round(monthly_cost, 2),
            "recommendation": "Contratar mais funcionários" if uncovered > 3 else "Situação sob controle",
        }
