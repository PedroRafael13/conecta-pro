"""Skill IA: Compliance Guardian — Conformidade trabalhista e eSocial."""

import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.operacional.models.employee import Employee
from modules.people_management.hr.models.contract import EmploymentContract

logger = logging.getLogger(__name__)


class ComplianceSkill:
    """Skill IA para verificação de conformidade trabalhista."""

    SKILL_NAME = "compliance_guardian"
    DESCRIPTION = "Verificação automática de conformidade CLT e eSocial"

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def check_employee_compliance(self, employee_id: str) -> dict:
        """Verifica conformidade completa de um funcionário."""
        result = await self.db.execute(select(Employee).where(Employee.id == employee_id))
        employee = result.scalar_one_or_none()
        if not employee:
            raise ValueError(f"Funcionário {employee_id} não encontrado")

        issues = []
        warnings = []

        if not employee.data_admissao:
            issues.append({"code": "CLT001", "severity": "critical", "message": "Data de admissão não informada"})

        from modules.people_management.common.utils.clt_calculator import SALARIO_MINIMO

        if not employee.salario_base or float(employee.salario_base) < float(SALARIO_MINIMO):
            issues.append({"code": "CLT002", "severity": "critical", "message": "Salário abaixo do mínimo legal"})

        contract_result = await self.db.execute(
            select(EmploymentContract).where(
                EmploymentContract.employee_id == employee_id,
                EmploymentContract.status == "active",
            )
        )
        contract = contract_result.scalar_one_or_none()
        if not contract:
            warnings.append(
                {"code": "CLT003", "severity": "warning", "message": "Sem contrato de trabalho ativo registrado"}
            )

        for field in ("cpf", "rg"):
            if not getattr(employee, field, None):
                warnings.append(
                    {"code": f"DOC_{field.upper()}", "severity": "warning", "message": f"{field.upper()} não informado"}
                )

        compliance_score = max(0, 100 - (len(issues) * 25) - (len(warnings) * 10))

        return {
            "employee_id": employee_id,
            "employee_name": employee.nome,
            "compliance_score": compliance_score,
            "status": "compliant" if not issues else "non_compliant",
            "issues": issues,
            "warnings": warnings,
            "checked_at": datetime.utcnow().isoformat(),
        }

    async def bulk_compliance_check(self) -> dict:
        """Verifica conformidade de todos os funcionários ativos."""
        result = await self.db.execute(select(Employee).where(Employee.status == "Ativo"))
        employees = result.scalars().all()

        results = []
        total_issues = 0
        for emp in employees:
            try:
                check = await self.check_employee_compliance(str(emp.id))
                results.append(check)
                total_issues += len(check["issues"])
            except Exception as e:
                logger.warning("Erro ao verificar conformidade de %s: %s", emp.id, e)

        compliant = sum(1 for r in results if r["status"] == "compliant")

        return {
            "total_employees": len(employees),
            "compliant": compliant,
            "non_compliant": len(employees) - compliant,
            "total_issues": total_issues,
            "compliance_rate": round(compliant / max(len(employees), 1) * 100, 1),
            "details": results,
        }
