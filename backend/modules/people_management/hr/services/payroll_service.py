"""
Serviço de Folha de Pagamento — Departamento Pessoal.

Calcula folha com INSS progressivo, IRRF, adicionais legais
e integração com benefícios. Usa clt_calculator para precisão Decimal.
"""

import contextlib
import logging
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.operacional.models.employee import Employee
from modules.people_management.common.utils.clt_calculator import (
    calcular_adicional_noturno,
    calcular_dsr_sobre_extras,
    calcular_fgts_mensal,
    calcular_hora_extra_50,
    calcular_hora_extra_100,
    calcular_hora_normal,
    calcular_inss,
    calcular_irrf,
    calcular_periculosidade,
    calcular_vale_transporte_desconto,
)

logger = logging.getLogger(__name__)

# Re-export do serviço existente
try:
    from modules.hr.payroll_integration.services import PayrollService as HRPayrollService
except ImportError:
    HRPayrollService = None  # type: ignore[assignment, misc]


def _d(v) -> Decimal:
    """Converte para Decimal de forma segura."""
    if v is None:
        return Decimal("0")
    return Decimal(str(v))


class PayrollService:
    """Serviço de Folha de Pagamento — visão DP com cálculos CLT reais."""

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
        """Calcula a folha de pagamento de um funcionário com CLT real.

        Args:
            employee_id: ID do funcionário.
            reference_month: Mês de referência (1-12).
            reference_year: Ano de referência.

        Returns:
            Dicionário com detalhamento completo da folha.
        """
        result = await self.db.execute(select(Employee).where(Employee.id == str(employee_id)))
        employee = result.scalar_one_or_none()
        if not employee:
            raise ValueError(f"Funcionário {employee_id} não encontrado")

        salario_base = _d(employee.salario_base)
        valor_hora = calcular_hora_normal(salario_base)

        # --- PROVENTOS ---
        proventos = []

        # 1. Salário base
        proventos.append({"codigo": "001", "descricao": "Salário Base", "ref": "30d", "valor": salario_base})

        # 2. Adicional de Periculosidade (30%)
        ad_periculosidade = Decimal("0")
        if getattr(employee, "adicional_periculosidade", None):
            ad_periculosidade = calcular_periculosidade(salario_base)
            proventos.append(
                {"codigo": "010", "descricao": "Periculosidade 30%", "ref": "30%", "valor": ad_periculosidade}
            )

        # 3. Adicional Noturno (20%) — placeholder para integração com time_records
        ad_noturno = Decimal("0")
        horas_noturnas = Decimal("0")
        if getattr(employee, "adicional_noturno", None) and horas_noturnas > 0:
            ad_noturno = calcular_adicional_noturno(valor_hora, horas_noturnas)
            proventos.append(
                {"codigo": "020", "descricao": "Ad. Noturno 20%", "ref": f"{horas_noturnas}h", "valor": ad_noturno}
            )

        # 4. Horas extras — placeholder para integração com time_records
        he_50 = Decimal("0")
        he_100 = Decimal("0")
        horas_extras_50 = Decimal("0")
        horas_extras_100 = Decimal("0")
        if horas_extras_50 > 0:
            he_50 = calcular_hora_extra_50(valor_hora, horas_extras_50)
            proventos.append(
                {"codigo": "030", "descricao": "Hora Extra 50%", "ref": f"{horas_extras_50}h", "valor": he_50}
            )
        if horas_extras_100 > 0:
            he_100 = calcular_hora_extra_100(valor_hora, horas_extras_100)
            proventos.append(
                {"codigo": "031", "descricao": "Hora Extra 100%", "ref": f"{horas_extras_100}h", "valor": he_100}
            )

        # 5. DSR sobre extras
        total_extras = he_50 + he_100
        dsr = Decimal("0")
        if total_extras > 0:
            dsr = calcular_dsr_sobre_extras(total_extras, dias_uteis=22, domingos_feriados=8)
            proventos.append({"codigo": "040", "descricao": "DSR s/ Extras", "ref": "", "valor": dsr})

        total_proventos = sum(p["valor"] for p in proventos)

        # --- DESCONTOS ---
        descontos = []

        # 1. INSS Progressivo
        inss = calcular_inss(total_proventos)
        descontos.append({"codigo": "201", "descricao": "INSS Progressivo", "ref": "", "valor": inss})

        # 2. IRRF
        base_irrf = total_proventos - inss
        dependentes = 0  # TODO: buscar dependentes do employee
        irrf = calcular_irrf(base_irrf, dependentes=dependentes)
        if irrf > 0:
            descontos.append({"codigo": "202", "descricao": "IRRF", "ref": "", "valor": irrf})

        # 3. Vale Transporte (6%)
        vt_desconto = Decimal("0")
        if getattr(employee, "vale_transporte", None):
            vt_desconto = calcular_vale_transporte_desconto(salario_base)
            descontos.append({"codigo": "210", "descricao": "VT 6%", "ref": "6%", "valor": vt_desconto})

        # 4. Benefícios (plano saúde, odonto, etc.)
        from modules.people_management.hr.models.benefits import EmployeeBenefit

        ben_result = await self.db.execute(
            select(EmployeeBenefit).where(
                EmployeeBenefit.employee_id == str(employee_id),
                EmployeeBenefit.status == "active",
            )
        )
        benefits = ben_result.scalars().all()
        for b in benefits:
            contrib = _d(b.employee_contribution)
            if contrib > 0:
                descontos.append(
                    {
                        "codigo": "220",
                        "descricao": f"Benefício: {b.type}",
                        "ref": b.plan_name or "",
                        "valor": contrib,
                    }
                )

        total_descontos = sum(d["valor"] for d in descontos)
        salario_liquido = total_proventos - total_descontos

        # FGTS (informativo, não desconta do funcionário)
        fgts = calcular_fgts_mensal(total_proventos)

        # Serializar Decimals para float no retorno
        def _f(v: Decimal) -> float:
            return float(v)

        return {
            "employee_id": str(employee_id),
            "employee_name": employee.nome,
            "cargo": getattr(employee, "cargo", ""),
            "reference": f"{reference_month:02d}/{reference_year}",
            "salario_base": _f(salario_base),
            "valor_hora": _f(valor_hora),
            "proventos": [{**p, "valor": _f(p["valor"])} for p in proventos],
            "descontos": [{**d, "valor": _f(d["valor"])} for d in descontos],
            "total_proventos": _f(total_proventos),
            "total_descontos": _f(total_descontos),
            "salario_liquido": _f(salario_liquido),
            "fgts_8_pct": _f(fgts),
            "base_inss": _f(total_proventos),
            "base_irrf": _f(base_irrf),
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

        total_bruto = Decimal("0")
        total_liquido = Decimal("0")
        total_fgts = Decimal("0")
        processed = 0
        errors = []

        for emp in employees:
            try:
                calc = await self.calculate_employee_payroll(str(emp.id), reference_month, reference_year)
                total_bruto += _d(calc["total_proventos"])
                total_liquido += _d(calc["salario_liquido"])
                total_fgts += _d(calc["fgts_8_pct"])
                processed += 1
            except Exception as e:
                logger.warning("Erro ao calcular folha do funcionário %s: %s", emp.id, e)
                errors.append({"employee_id": str(emp.id), "error": str(e)})

        logger.info(
            "Folha %02d/%d fechada: %d/%d funcionários processados",
            reference_month,
            reference_year,
            processed,
            total_employees,
        )

        return {
            "reference": f"{reference_month:02d}/{reference_year}",
            "total_employees": total_employees,
            "processed": processed,
            "errors": len(errors),
            "error_details": errors[:10],
            "total_bruto": float(total_bruto),
            "total_liquido": float(total_liquido),
            "total_fgts": float(total_fgts),
            "status": "closed",
        }

    async def mark_payslip_viewed(self, employee_id: str | UUID, month: int, year: int) -> dict:
        """Marca contracheque como visualizado pelo funcionário.

        Args:
            employee_id: ID do funcionário.
            month: Mês.
            year: Ano.

        Returns:
            Confirmação.
        """
        logger.info("Contracheque %02d/%d visualizado por %s", month, year, employee_id)
        return {"status": "viewed", "employee_id": str(employee_id), "reference": f"{month:02d}/{year}"}
