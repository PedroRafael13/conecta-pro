"""
Serviço de Contratos de Trabalho — Departamento Pessoal.

CRUD de contratos de trabalho e geração de documento contratual.
"""

import logging
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.people_management.hr.models.contract import (
    ContractType,
    EmploymentContract,
)

logger = logging.getLogger(__name__)


class ContractService:
    """Serviço de Contratos de Trabalho — visão DP."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_contract(self, data: dict) -> EmploymentContract:
        """Cria um novo contrato de trabalho.

        Se houver contrato vigente, marca-o como não atual.

        Args:
            data: Dados do contrato (schema ContractCreate).

        Returns:
            Instância de EmploymentContract criada.
        """
        # Desativar contrato vigente anterior
        current_result = await self.db.execute(
            select(EmploymentContract).where(
                EmploymentContract.employee_id == data["employee_id"],
                EmploymentContract.is_current.is_(True),
            )
        )
        current_contract = current_result.scalar_one_or_none()

        previous_id = None
        if current_contract:
            current_contract.is_current = False
            previous_id = str(current_contract.id)

        contract = EmploymentContract(
            id=uuid4(),
            employee_id=data["employee_id"],
            type=data["type"],
            start_date=data["start_date"],
            end_date=data.get("end_date"),
            work_schedule=data.get("work_schedule"),
            weekly_hours=data.get("weekly_hours"),
            base_salary=data["base_salary"],
            hazard_pay_percent=data.get("hazard_pay_percent", 0),
            unhealthy_pay_percent=data.get("unhealthy_pay_percent", 0),
            night_shift_percent=data.get("night_shift_percent", 0),
            job_title=data.get("job_title"),
            department=data.get("department"),
            cost_center=data.get("cost_center"),
            workplace_id=data.get("workplace_id"),
            union_name=data.get("union_name"),
            union_code=data.get("union_code"),
            is_current=True,
            previous_contract_id=previous_id,
            notes=data.get("notes"),
        )
        self.db.add(contract)
        await self.db.flush()
        await self.db.refresh(contract)
        logger.info("Contrato criado: %s para employee %s", contract.id, contract.employee_id)
        return contract

    async def get_by_id(self, contract_id: str | UUID) -> EmploymentContract | None:
        """Busca contrato por ID."""
        result = await self.db.execute(select(EmploymentContract).where(EmploymentContract.id == str(contract_id)))
        return result.scalar_one_or_none()

    async def get_current_contract(self, employee_id: str | UUID) -> EmploymentContract | None:
        """Busca o contrato vigente de um funcionário."""
        result = await self.db.execute(
            select(EmploymentContract).where(
                EmploymentContract.employee_id == str(employee_id),
                EmploymentContract.is_current.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def list_by_employee(self, employee_id: str | UUID) -> list[EmploymentContract]:
        """Lista todos os contratos de um funcionário (histórico).

        Args:
            employee_id: ID do funcionário.

        Returns:
            Lista de contratos ordenados por data de início (desc).
        """
        result = await self.db.execute(
            select(EmploymentContract)
            .where(EmploymentContract.employee_id == str(employee_id))
            .order_by(EmploymentContract.start_date.desc())
        )
        return list(result.scalars().all())

    async def update_contract(self, contract_id: str | UUID, data: dict) -> EmploymentContract | None:
        """Atualiza dados de um contrato.

        Args:
            contract_id: ID do contrato.
            data: Campos a atualizar.

        Returns:
            Contrato atualizado ou None.
        """
        contract = await self.get_by_id(contract_id)
        if not contract:
            return None

        update_data = {k: v for k, v in data.items() if v is not None}
        for key, value in update_data.items():
            if hasattr(contract, key):
                setattr(contract, key, value)

        await self.db.flush()
        await self.db.refresh(contract)
        return contract

    def generate_contract_document(
        self,
        contract: EmploymentContract,
        employee_name: str,
        company_name: str = "Jordan Santos de Jesus Ltda",
        company_cnpj: str = "35.710.481/0001-03",
    ) -> dict:
        """Gera dados para documento de contrato de trabalho.

        Args:
            contract: Instância do contrato.
            employee_name: Nome do funcionário.
            company_name: Razão social da empresa.
            company_cnpj: CNPJ da empresa.

        Returns:
            Dicionário com dados do documento contratual.
        """
        contract_type_labels = {
            ContractType.CLT_INDETERMINATE: "Contrato por Prazo Indeterminado",
            ContractType.CLT_DETERMINATE: "Contrato por Prazo Determinado",
            ContractType.TEMPORARY: "Contrato Temporário",
            ContractType.INTERMITTENT: "Contrato Intermitente",
            ContractType.APPRENTICE: "Contrato de Aprendizagem",
            ContractType.INTERN: "Contrato de Estágio",
        }

        total_salary = float(contract.base_salary)
        if contract.hazard_pay_percent:
            total_salary += total_salary * (float(contract.hazard_pay_percent) / 100)
        if contract.unhealthy_pay_percent:
            total_salary += float(contract.base_salary) * (float(contract.unhealthy_pay_percent) / 100)

        return {
            "document_type": "employment_contract",
            "contract_id": str(contract.id),
            "company": {
                "name": company_name,
                "cnpj": company_cnpj,
            },
            "employee": {
                "name": employee_name,
                "employee_id": str(contract.employee_id),
            },
            "contract": {
                "type_label": contract_type_labels.get(ContractType(contract.type), contract.type),
                "start_date": contract.start_date.isoformat(),
                "end_date": contract.end_date.isoformat() if contract.end_date else None,
                "work_schedule": contract.work_schedule,
                "weekly_hours": float(contract.weekly_hours) if contract.weekly_hours else None,
                "base_salary": float(contract.base_salary),
                "hazard_pay_percent": float(contract.hazard_pay_percent or 0),
                "unhealthy_pay_percent": float(contract.unhealthy_pay_percent or 0),
                "night_shift_percent": float(contract.night_shift_percent or 0),
                "total_salary_estimate": round(total_salary, 2),
                "job_title": contract.job_title,
                "department": contract.department,
                "union_name": contract.union_name,
            },
            "generated_at": None,  # Será preenchido na geração do PDF
        }
