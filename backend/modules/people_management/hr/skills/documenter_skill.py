"""Skill IA: Smart Documenter — Geração inteligente de documentos trabalhistas."""

import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.operacional.models.employee import Employee

logger = logging.getLogger(__name__)


class DocumenterSkill:
    """Skill IA para geração de documentos trabalhistas e eventos eSocial."""

    SKILL_NAME = "smart_documenter"
    DESCRIPTION = "Geração automática de documentos trabalhistas e eventos eSocial"

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def generate_esocial_s2200(self, employee_id: str) -> dict:
        """Gera evento S-2200 (Cadastramento Inicial / Admissão) do eSocial."""
        result = await self.db.execute(select(Employee).where(Employee.id == employee_id))
        employee = result.scalar_one_or_none()
        if not employee:
            raise ValueError(f"Funcionário {employee_id} não encontrado")

        xml_data = {
            "evento": "S-2200",
            "tipo": "Cadastramento Inicial do Vínculo",
            "cpfTrab": getattr(employee, "cpf", ""),
            "nmTrab": employee.nome,
            "dtNascto": str(getattr(employee, "data_nascimento", "")),
            "dtAdm": str(employee.data_admissao) if employee.data_admissao else "",
            "tpRegTrab": 1,
            "tpRegPrev": 1,
            "vrSalFx": float(employee.salario_base or 0),
            "undSalFixo": 5,
        }

        return {
            "event_type": "S-2200",
            "employee_id": employee_id,
            "status": "generated",
            "data": xml_data,
            "generated_at": datetime.utcnow().isoformat(),
            "message": "Evento S-2200 gerado — pronto para transmissão",
        }

    async def generate_esocial_s2299(self, employee_id: str, termination_date: str) -> dict:
        """Gera evento S-2299 (Desligamento) do eSocial."""
        result = await self.db.execute(select(Employee).where(Employee.id == employee_id))
        employee = result.scalar_one_or_none()
        if not employee:
            raise ValueError(f"Funcionário {employee_id} não encontrado")

        xml_data = {
            "evento": "S-2299",
            "tipo": "Desligamento",
            "cpfTrab": getattr(employee, "cpf", ""),
            "nmTrab": employee.nome,
            "dtDeslig": termination_date,
            "vrSalFx": float(employee.salario_base or 0),
        }

        return {
            "event_type": "S-2299",
            "employee_id": employee_id,
            "status": "generated",
            "data": xml_data,
            "generated_at": datetime.utcnow().isoformat(),
        }

    async def generate_payslip_data(self, employee_id: str, month: int, year: int) -> dict:
        """Gera dados do contracheque para impressão/PDF."""
        from modules.people_management.hr.services.payroll_service import PayrollService

        svc = PayrollService(self.db)
        calc = await svc.calculate_employee_payroll(employee_id, month, year)

        return {
            "document_type": "contracheque",
            "employee_id": employee_id,
            "reference": calc["reference"],
            "data": calc,
            "generated_at": datetime.utcnow().isoformat(),
        }
