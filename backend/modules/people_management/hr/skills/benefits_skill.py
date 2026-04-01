"""Skill IA: Benefits Optimizer — Otimização inteligente de benefícios."""

import logging
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.operacional.models.employee import Employee
from modules.people_management.hr.models.benefits import EmployeeBenefit

logger = logging.getLogger(__name__)


class BenefitsSkill:
    """Skill IA para análise e otimização de pacotes de benefícios."""

    SKILL_NAME = "benefits_optimizer"
    DESCRIPTION = "Análise inteligente e otimização de pacotes de benefícios"

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def analyze_employee_benefits(self, employee_id: str) -> dict:
        """Analisa o pacote de benefícios de um funcionário."""
        emp_result = await self.db.execute(select(Employee).where(Employee.id == employee_id))
        employee = emp_result.scalar_one_or_none()
        if not employee:
            raise ValueError(f"Funcionário {employee_id} não encontrado")

        ben_result = await self.db.execute(
            select(EmployeeBenefit).where(
                EmployeeBenefit.employee_id == employee_id,
                EmployeeBenefit.status == "active",
            )
        )
        benefits = ben_result.scalars().all()

        total_company = Decimal("0")
        total_employee = Decimal("0")
        benefit_list = []

        for b in benefits:
            company_cost = Decimal(str(b.company_contribution or 0))
            employee_cost = Decimal(str(b.employee_contribution or 0))
            total_company += company_cost
            total_employee += employee_cost
            benefit_list.append(
                {
                    "type": b.type,
                    "plan_name": b.plan_name,
                    "company_contribution": float(company_cost),
                    "employee_contribution": float(employee_cost),
                }
            )

        salario = Decimal(str(employee.salario_base or 0))
        benefit_ratio = float(total_company / salario * 100) if salario > 0 else 0

        suggestions = []
        if not any(b["type"] == "health" for b in benefit_list):
            suggestions.append({"type": "missing_benefit", "message": "Sem plano de saúde — benefício mais valorizado"})
        if benefit_ratio < 15:
            suggestions.append(
                {"type": "low_benefits", "message": f"Benefícios representam apenas {benefit_ratio:.1f}% do salário"}
            )

        return {
            "employee_id": employee_id,
            "employee_name": employee.nome,
            "benefits": benefit_list,
            "total_company_cost": float(total_company),
            "total_employee_cost": float(total_employee),
            "benefit_salary_ratio": round(benefit_ratio, 2),
            "suggestions": suggestions,
        }

    async def company_benefits_summary(self) -> dict:
        """Resumo geral de custos de benefícios da empresa."""
        result = await self.db.execute(select(EmployeeBenefit).where(EmployeeBenefit.status == "active"))
        benefits = result.scalars().all()

        total_company = Decimal("0")
        total_employee = Decimal("0")
        by_type: dict = {}

        for b in benefits:
            cc = Decimal(str(b.company_contribution or 0))
            ec = Decimal(str(b.employee_contribution or 0))
            total_company += cc
            total_employee += ec
            btype = b.type or "other"
            if btype not in by_type:
                by_type[btype] = {"count": 0, "company_total": Decimal("0"), "employee_total": Decimal("0")}
            by_type[btype]["count"] += 1
            by_type[btype]["company_total"] += cc
            by_type[btype]["employee_total"] += ec

        return {
            "total_active_benefits": len(benefits),
            "total_company_cost_monthly": float(total_company),
            "total_employee_cost_monthly": float(total_employee),
            "by_type": {
                k: {
                    "count": v["count"],
                    "company_total": float(v["company_total"]),
                    "employee_total": float(v["employee_total"]),
                }
                for k, v in by_type.items()
            },
        }
