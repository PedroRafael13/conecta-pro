"""Skill IA: Payroll Master — Análise inteligente de folha de pagamento."""

import logging
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from modules.people_management.common.utils.clt_calculator import (
    SALARIO_MINIMO,
    TETO_INSS,
)
from modules.people_management.hr.services.payroll_service import PayrollService

logger = logging.getLogger(__name__)


class PayrollSkill:
    """Skill IA para análise avançada de folha de pagamento."""

    SKILL_NAME = "payroll_master"
    DESCRIPTION = "Análise inteligente de folha de pagamento com detecção de anomalias"

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.payroll_service = PayrollService(db)

    async def analyze_payroll(self, employee_id: str, month: int, year: int) -> dict:
        """Analisa folha com detecção de anomalias e sugestões."""
        calc = await self.payroll_service.calculate_employee_payroll(employee_id, month, year)
        anomalies = []
        suggestions = []

        salario = Decimal(str(calc["salario_base"]))
        liquido = Decimal(str(calc["salario_liquido"]))

        if salario < SALARIO_MINIMO:
            anomalies.append(
                {
                    "type": "below_minimum_wage",
                    "severity": "critical",
                    "message": f"Salário base R${salario} abaixo do mínimo R${SALARIO_MINIMO}",
                }
            )

        if liquido < 0:
            anomalies.append(
                {
                    "type": "negative_net_salary",
                    "severity": "critical",
                    "message": "Salário líquido negativo — verificar descontos",
                }
            )

        bruto = Decimal(str(calc["total_proventos"]))
        descontos = Decimal(str(calc["total_descontos"]))
        if bruto > 0 and (descontos / bruto) > Decimal("0.70"):
            anomalies.append(
                {
                    "type": "excessive_deductions",
                    "severity": "warning",
                    "message": f"Descontos representam {float(descontos / bruto * 100):.1f}% do bruto",
                }
            )

        if salario > TETO_INSS:
            suggestions.append(
                {
                    "type": "above_inss_ceiling",
                    "message": "Funcionário acima do teto INSS — considerar previdência complementar",
                }
            )

        return {
            **calc,
            "ai_analysis": {
                "anomalies": anomalies,
                "suggestions": suggestions,
                "risk_score": min(100, len(anomalies) * 30 + len(suggestions) * 10),
            },
        }

    async def compare_months(self, employee_id: str, month1: int, year1: int, month2: int, year2: int) -> dict:
        """Compara folha entre dois meses para detectar variações."""
        calc1 = await self.payroll_service.calculate_employee_payroll(employee_id, month1, year1)
        calc2 = await self.payroll_service.calculate_employee_payroll(employee_id, month2, year2)

        variations = []
        for key in ("total_proventos", "total_descontos", "salario_liquido"):
            v1, v2 = calc1[key], calc2[key]
            if v1 > 0:
                pct = ((v2 - v1) / v1) * 100
                if abs(pct) > 5:
                    variations.append({"field": key, "before": v1, "after": v2, "variation_pct": round(pct, 2)})

        return {
            "period_1": calc1["reference"],
            "period_2": calc2["reference"],
            "variations": variations,
            "has_significant_changes": len(variations) > 0,
        }
