"""Skill IA: HR Predictor — Análises preditivas de RH."""

import logging
from datetime import date, datetime

from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.operacional.models.employee import Employee

logger = logging.getLogger(__name__)


class PredictorSkill:
    """Skill IA para análises preditivas de RH."""

    SKILL_NAME = "hr_predictor"
    DESCRIPTION = "Previsões de turnover, custos e necessidades de pessoal"

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def predict_turnover_risk(self) -> dict:
        """Identifica funcionários com maior risco de turnover."""
        result = await self.db.execute(select(Employee).where(Employee.status == "Ativo"))
        employees = result.scalars().all()

        risk_list = []
        today = date.today()

        for emp in employees:
            risk_score = 0
            factors = []

            if emp.data_admissao:
                months = (today - emp.data_admissao).days // 30
                if months < 6:
                    risk_score += 30
                    factors.append("less_than_6_months")
                elif months > 60:
                    risk_score += 15
                    factors.append("tenure_over_5_years")

            from modules.people_management.common.utils.clt_calculator import SALARIO_MINIMO

            if emp.salario_base and float(emp.salario_base) < float(SALARIO_MINIMO) * 1.5:
                risk_score += 25
                factors.append("low_salary")

            if risk_score > 20:
                risk_list.append(
                    {
                        "employee_id": str(emp.id),
                        "name": emp.nome,
                        "risk_score": min(risk_score, 100),
                        "factors": factors,
                    }
                )

        risk_list.sort(key=lambda x: x["risk_score"], reverse=True)

        return {
            "total_analyzed": len(employees),
            "at_risk": len(risk_list),
            "high_risk": [r for r in risk_list if r["risk_score"] >= 50],
            "medium_risk": [r for r in risk_list if 20 < r["risk_score"] < 50],
            "analyzed_at": datetime.utcnow().isoformat(),
        }

    async def headcount_forecast(self, months_ahead: int = 6) -> dict:
        """Previsão de headcount para os próximos meses."""
        active_result = await self.db.execute(
            select(func.count()).select_from(Employee).where(Employee.status == "Ativo")
        )
        current = active_result.scalar() or 0

        year = date.today().year
        terminated_result = await self.db.execute(
            select(func.count())
            .select_from(Employee)
            .where(
                Employee.status == "Desligado",
                extract("year", Employee.data_demissao) == year,
            )
        )
        terminated_ytd = terminated_result.scalar() or 0
        months_elapsed = max(1, date.today().month)
        monthly_turnover = terminated_ytd / months_elapsed

        forecast = []
        headcount = float(current)
        for m in range(1, months_ahead + 1):
            headcount = max(0, headcount - monthly_turnover)
            forecast.append({"month": m, "projected_headcount": round(headcount)})

        return {
            "current_headcount": current,
            "monthly_turnover_rate": round(monthly_turnover, 2),
            "forecast": forecast,
            "needs_hiring": monthly_turnover > 2,
        }
