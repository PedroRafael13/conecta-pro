"""Skill IA: Smart Onboarder — Integração inteligente de novos colaboradores."""

import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.operacional.models.employee import Employee

logger = logging.getLogger(__name__)


class OnboarderSkill:
    """Skill IA para gestão inteligente de onboarding."""

    SKILL_NAME = "smart_onboarder"
    DESCRIPTION = "Gestão e automação do processo de onboarding"

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def generate_onboarding_checklist(self, employee_id: str) -> dict:
        """Gera checklist personalizado de onboarding."""
        result = await self.db.execute(select(Employee).where(Employee.id == employee_id))
        employee = result.scalar_one_or_none()
        if not employee:
            raise ValueError(f"Funcionário {employee_id} não encontrado")

        cargo = getattr(employee, "cargo", "") or ""
        is_security = "vigil" in cargo.lower() or "segur" in cargo.lower()

        checklist = [
            {"step": 1, "category": "docs", "task": "Coletar documentos pessoais (RG, CPF, CTPS)", "required": True},
            {"step": 2, "category": "docs", "task": "Assinar contrato de trabalho", "required": True},
            {"step": 3, "category": "docs", "task": "Cadastrar no eSocial (S-2200)", "required": True},
            {"step": 4, "category": "benefits", "task": "Incluir no plano de saúde", "required": False},
            {"step": 5, "category": "benefits", "task": "Cadastrar vale transporte", "required": True},
            {"step": 6, "category": "training", "task": "Treinamento de integração", "required": True},
            {"step": 7, "category": "it", "task": "Criar acesso ao portal do funcionário", "required": True},
            {"step": 8, "category": "ops", "task": "Definir escala e posto de trabalho", "required": True},
        ]

        if is_security:
            checklist.extend(
                [
                    {
                        "step": 9,
                        "category": "security",
                        "task": "Verificar CNV (Carteira Nacional de Vigilante)",
                        "required": True,
                    },
                    {
                        "step": 10,
                        "category": "security",
                        "task": "Treinamento de segurança obrigatório",
                        "required": True,
                    },
                    {
                        "step": 11,
                        "category": "security",
                        "task": "Entrega de uniforme e equipamentos",
                        "required": True,
                    },
                ]
            )

        return {
            "employee_id": employee_id,
            "employee_name": employee.nome,
            "cargo": cargo,
            "total_steps": len(checklist),
            "checklist": checklist,
            "generated_at": datetime.utcnow().isoformat(),
        }

    async def onboarding_status(self) -> dict:
        """Status geral dos processos de onboarding ativos."""
        from modules.people_management.hr.models.admission import AdmissionProcess

        result = await self.db.execute(
            select(AdmissionProcess).where(AdmissionProcess.status.in_(["pending", "in_progress", "documents_pending"]))
        )
        processes = result.scalars().all()

        return {
            "active_onboardings": len(processes),
            "processes": [
                {
                    "id": str(p.id),
                    "employee_id": str(p.employee_id) if p.employee_id else None,
                    "status": str(p.status),
                }
                for p in processes
            ],
            "checked_at": datetime.utcnow().isoformat(),
        }
