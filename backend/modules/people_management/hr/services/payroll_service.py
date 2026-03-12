"""
Serviço de Folha de Pagamento — Departamento Pessoal.

Re-exporta funcionalidades do módulo hr/payroll_integration e adiciona
métodos para fechamento de folha e cálculo individual.
"""

import contextlib
import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.operacional.models.employee import Employee

logger = logging.getLogger(__name__)

# Re-export do serviço existente
try:
    from modules.hr.payroll_integration.services import PayrollService as HRPayrollService
except ImportError:
    HRPayrollService = None  # type: ignore[assignment, misc]


class PayrollService:
    """Serviço de Folha de Pagamento — visão DP."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._hr_service = None
        if HRPayrollService:
            with contextlib.suppress(Exception):
                self._hr_service = HRPayrollService(db)

    async def calculate_employee_payroll(
        self,
        employee_id: str | UUID,
        reference_month: int,
        reference_year: int,
    ) -> dict:
        """Calcula a folha de pagamento de um funcionário.

        Cálculos simplificados de INSS, IRRF e líquido.
        Para cálculos oficiais, usar integração com Domínio/TOTVS.

        Args:
            employee_id: ID do funcionário.
            reference_month: Mês de referência (1-12).
            reference_year: Ano de referência.

        Returns:
            Dicionário com detalhamento da folha.
        """
        result = await self.db.execute(select(Employee).where(Employee.id == str(employee_id)))
        employee = result.scalar_one_or_none()
        if not employee:
            raise ValueError(f"Funcionário {employee_id} não encontrado")

        salario_bruto = float(employee.salario_base or 0)

        # INSS 2026 (faixas simplificadas)
        inss = self._calc_inss(salario_bruto)

        # Base IRRF = bruto - INSS
        base_irrf = salario_bruto - inss
        irrf = self._calc_irrf(base_irrf)

        # Benefícios (buscar descontos do funcionário)
        from modules.people_management.hr.models.benefits import EmployeeBenefit

        ben_result = await self.db.execute(
            select(EmployeeBenefit).where(
                EmployeeBenefit.employee_id == str(employee_id),
                EmployeeBenefit.status == "active",
            )
        )
        benefits = ben_result.scalars().all()
        total_desconto_beneficios = sum(float(b.employee_contribution or 0) for b in benefits)

        total_descontos = inss + irrf + total_desconto_beneficios
        salario_liquido = salario_bruto - total_descontos

        return {
            "employee_id": str(employee_id),
            "employee_name": employee.nome,
            "reference": f"{reference_month:02d}/{reference_year}",
            "salario_bruto": round(salario_bruto, 2),
            "inss": round(inss, 2),
            "irrf": round(irrf, 2),
            "desconto_beneficios": round(total_desconto_beneficios, 2),
            "total_descontos": round(total_descontos, 2),
            "salario_liquido": round(salario_liquido, 2),
        }

    async def close_payroll(
        self,
        reference_month: int,
        reference_year: int,
    ) -> dict:
        """Fecha a folha de pagamento do mês para todos os funcionários ativos.

        Args:
            reference_month: Mês de referência (1-12).
            reference_year: Ano de referência.

        Returns:
            Dicionário com resumo do fechamento.
        """
        from sqlalchemy import func

        count_result = await self.db.execute(
            select(func.count()).select_from(Employee).where(Employee.status == "Ativo")
        )
        total_employees = count_result.scalar() or 0

        result = await self.db.execute(select(Employee).where(Employee.status == "Ativo"))
        employees = result.scalars().all()

        total_bruto = 0.0
        total_liquido = 0.0
        processed = 0

        for emp in employees:
            try:
                calc = await self.calculate_employee_payroll(str(emp.id), reference_month, reference_year)
                total_bruto += calc["salario_bruto"]
                total_liquido += calc["salario_liquido"]
                processed += 1
            except Exception as e:
                logger.warning("Erro ao calcular folha do funcionário %s: %s", emp.id, e)

        logger.info(
            "Folha %02d/%d fechada: %d funcionários processados",
            reference_month,
            reference_year,
            processed,
        )

        return {
            "reference": f"{reference_month:02d}/{reference_year}",
            "total_employees": total_employees,
            "processed": processed,
            "total_bruto": round(total_bruto, 2),
            "total_liquido": round(total_liquido, 2),
            "status": "closed",
        }

    @staticmethod
    def _calc_inss(salario: float) -> float:
        """Calcula INSS progressivo (tabela simplificada 2026)."""
        if salario <= 1412.00:
            return salario * 0.075
        elif salario <= 2666.68:
            return 1412.00 * 0.075 + (salario - 1412.00) * 0.09
        elif salario <= 4000.03:
            return 1412.00 * 0.075 + (2666.68 - 1412.00) * 0.09 + (salario - 2666.68) * 0.12
        elif salario <= 7786.02:
            return (
                1412.00 * 0.075
                + (2666.68 - 1412.00) * 0.09
                + (4000.03 - 2666.68) * 0.12
                + (min(salario, 7786.02) - 4000.03) * 0.14
            )
        else:
            return (
                1412.00 * 0.075 + (2666.68 - 1412.00) * 0.09 + (4000.03 - 2666.68) * 0.12 + (7786.02 - 4000.03) * 0.14
            )

    @staticmethod
    def _calc_irrf(base: float) -> float:
        """Calcula IRRF (tabela simplificada 2026)."""
        if base <= 2259.20:
            return 0.0
        elif base <= 2826.65:
            return base * 0.075 - 169.44
        elif base <= 3751.05:
            return base * 0.15 - 381.44
        elif base <= 4664.68:
            return base * 0.225 - 662.77
        else:
            return base * 0.275 - 896.00
