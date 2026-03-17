"""Skill IA: Smart Recruiter — Recrutamento inteligente."""

import logging
from datetime import datetime

from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.operacional.models.employee import Employee

logger = logging.getLogger(__name__)


class RecruiterSkill:
    """Skill IA para análise de recrutamento e retenção."""

    SKILL_NAME = "smart_recruiter"
    DESCRIPTION = "Análise preditiva de recrutamento e fit cultural"

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def analyze_workforce_gaps(self) -> dict:
        """Analisa gaps na força de trabalho por cargo e setor."""
        result = await self.db.execute(
            select(Employee.cargo, func.count(Employee.id).label("total"))
            .where(Employee.status == "Ativo")
            .group_by(Employee.cargo)
        )
        by_role = {row[0] or "Não definido": row[1] for row in result.all()}
        total = sum(by_role.values())

        suggestions = []
        if total < 10:
            suggestions.append({"type": "small_team", "message": "Equipe reduzida — considerar contratações"})

        return {
            "total_active": total,
            "by_role": by_role,
            "suggestions": suggestions,
            "analyzed_at": datetime.utcnow().isoformat(),
        }

    async def turnover_analysis(self, year: int) -> dict:
        """Calcula taxa de turnover do ano."""
        active_result = await self.db.execute(
            select(func.count()).select_from(Employee).where(Employee.status == "Ativo")
        )
        active = active_result.scalar() or 0

        terminated_result = await self.db.execute(
            select(func.count())
            .select_from(Employee)
            .where(
                Employee.status == "Desligado",
                extract("year", Employee.data_demissao) == year,
            )
        )
        terminated = terminated_result.scalar() or 0

        hired_result = await self.db.execute(
            select(func.count())
            .select_from(Employee)
            .where(
                extract("year", Employee.data_admissao) == year,
            )
        )
        hired = hired_result.scalar() or 0

        avg_headcount = max(1, (active + active + terminated - hired) / 2)
        turnover_rate = (terminated / avg_headcount) * 100

        return {
            "year": year,
            "active_employees": active,
            "hired": hired,
            "terminated": terminated,
            "turnover_rate": round(turnover_rate, 2),
            "health": "good" if turnover_rate < 15 else "warning" if turnover_rate < 30 else "critical",
        }
