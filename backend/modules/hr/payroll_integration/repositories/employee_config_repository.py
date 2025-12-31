"""Repository para configuração de folha por funcionário."""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.payroll_integration.models import (
    EmployeePayrollConfig,
    ContractType,
    OvertimeRule,
)
from modules.hr.payroll_integration.schemas import (
    EmployeePayrollConfigCreate,
    EmployeePayrollConfigUpdate,
)

logger = logging.getLogger(__name__)


class EmployeePayrollConfigRepository:
    """Repository para configurações de folha por funcionário."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        data: EmployeePayrollConfigCreate,
        condominio_id: UUID,
        *,
        created_by: UUID = None,
    ) -> EmployeePayrollConfig:
        """Cria nova configuração de folha."""
        config = EmployeePayrollConfig(
            condominio_id=condominio_id,
            employee_id=data.employee_id,
            contract_type=data.contract_type.value,
            admission_date=data.admission_date,
            termination_date=data.termination_date,
            experience_end_date=data.experience_end_date,
            base_salary=data.base_salary,
            salary_type=data.salary_type,
            hourly_rate=data.hourly_rate,
            daily_rate=data.daily_rate,
            work_schedule_type=data.work_schedule_type.value,
            weekly_hours=data.weekly_hours,
            daily_hours=data.daily_hours,
            monthly_hours=data.monthly_hours,
            work_start=data.work_start,
            work_end=data.work_end,
            lunch_start=data.lunch_start,
            lunch_end=data.lunch_end,
            lunch_duration_minutes=data.lunch_duration_minutes,
            overtime_rule=data.overtime_rule.value,
            overtime_rate_50=data.overtime_rate_50,
            overtime_rate_100=data.overtime_rate_100,
            overtime_threshold=data.overtime_threshold,
            night_shift_rate=data.night_shift_rate,
            night_shift_start=data.night_shift_start,
            night_shift_end=data.night_shift_end,
            night_hour_reduction=data.night_hour_reduction,
            bank_hours_enabled=data.bank_hours_enabled,
            bank_hours_policy=(
                data.bank_hours_policy.value if data.bank_hours_policy else None
            ),
            bank_hours_balance=data.bank_hours_balance,
            bank_hours_limit=data.bank_hours_limit,
            bank_hours_hybrid_threshold=data.bank_hours_hybrid_threshold,
            hazard_pay_rate=data.hazard_pay_rate,
            unhealthy_pay_rate=data.unhealthy_pay_rate,
            unhealthy_pay_base=data.unhealthy_pay_base,
            benefits=self._serialize_benefits(data.benefits),
            loans=[loan.model_dump() for loan in (data.loans or [])],
            alimony=[alimony.model_dump() for alimony in (data.alimony or [])],
            dependents=[dep.model_dump() for dep in (data.dependents or [])],
            dependents_count=data.dependents_count,
            union_id=data.union_id,
            union_contribution_enabled=data.union_contribution_enabled,
            union_contribution_type=data.union_contribution_type,
            union_contribution_value=data.union_contribution_value,
            calculation_config=(
                data.calculation_config.model_dump()
                if data.calculation_config
                else {}
            ),
            external_codes=(
                data.external_codes.model_dump() if data.external_codes else {}
            ),
            created_by=created_by,
        )

        self.db.add(config)
        await self.db.commit()
        await self.db.refresh(config)

        logger.info("Configuração de folha criada para: %s", data.employee_id)
        return config

    def _serialize_benefits(self, benefits: list) -> dict:
        """Serializa benefícios para armazenamento."""
        if not benefits:
            return {}
        return {b.benefit_type: b.model_dump() for b in benefits}

    async def get_by_id(
        self,
        config_id: UUID,
    ) -> Optional[EmployeePayrollConfig]:
        """Busca configuração por ID."""
        query = select(EmployeePayrollConfig).where(
            and_(
                EmployeePayrollConfig.id == config_id,
                EmployeePayrollConfig.ativo.is_(True),
            )
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_employee(
        self,
        employee_id: UUID,
        condominio_id: UUID,
    ) -> Optional[EmployeePayrollConfig]:
        """Busca configuração por funcionário."""
        query = select(EmployeePayrollConfig).where(
            and_(
                EmployeePayrollConfig.employee_id == employee_id,
                EmployeePayrollConfig.condominio_id == condominio_id,
                EmployeePayrollConfig.ativo.is_(True),
            )
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_configs(
        self,
        condominio_id: UUID,
        *,
        contract_type: ContractType = None,
        active_only: bool = True,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[EmployeePayrollConfig], int]:
        """Lista configurações com filtros."""
        conditions = [
            EmployeePayrollConfig.condominio_id == condominio_id,
            EmployeePayrollConfig.ativo.is_(True),
        ]

        if contract_type:
            conditions.append(
                EmployeePayrollConfig.contract_type == contract_type.value
            )
        if active_only:
            conditions.append(EmployeePayrollConfig.termination_date.is_(None))

        # Count
        count_query = select(func.count(EmployeePayrollConfig.id)).where(
            and_(*conditions)
        )
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Fetch
        query = (
            select(EmployeePayrollConfig)
            .where(and_(*conditions))
            .order_by(EmployeePayrollConfig.admission_date.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await self.db.execute(query)
        configs = list(result.scalars().all())

        return configs, total

    async def update(
        self,
        config_id: UUID,
        data: EmployeePayrollConfigUpdate,
    ) -> Optional[EmployeePayrollConfig]:
        """Atualiza configuração."""
        config = await self.get_by_id(config_id)
        if not config:
            return None

        update_data = data.model_dump(exclude_unset=True)

        # Handle nested objects
        if "benefits" in update_data and update_data["benefits"]:
            update_data["benefits"] = self._serialize_benefits(update_data["benefits"])
        if "loans" in update_data and update_data["loans"]:
            update_data["loans"] = [l.model_dump() for l in update_data["loans"]]
        if "alimony" in update_data and update_data["alimony"]:
            update_data["alimony"] = [a.model_dump() for a in update_data["alimony"]]
        if "dependents" in update_data and update_data["dependents"]:
            update_data["dependents"] = [
                d.model_dump() for d in update_data["dependents"]
            ]
        if "calculation_config" in update_data and update_data["calculation_config"]:
            update_data["calculation_config"] = update_data[
                "calculation_config"
            ].model_dump()
        if "external_codes" in update_data and update_data["external_codes"]:
            update_data["external_codes"] = update_data["external_codes"].model_dump()

        # Handle enums
        if "work_schedule_type" in update_data and update_data["work_schedule_type"]:
            update_data["work_schedule_type"] = update_data[
                "work_schedule_type"
            ].value
        if "overtime_rule" in update_data and update_data["overtime_rule"]:
            update_data["overtime_rule"] = update_data["overtime_rule"].value
        if "bank_hours_policy" in update_data and update_data["bank_hours_policy"]:
            update_data["bank_hours_policy"] = update_data["bank_hours_policy"].value

        for field, value in update_data.items():
            if value is not None:
                setattr(config, field, value)

        config.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(config)

        return config

    async def update_salary(
        self,
        config_id: UUID,
        new_salary: Decimal,
        *,
        new_hourly_rate: Decimal = None,
    ) -> Optional[EmployeePayrollConfig]:
        """Atualiza salário."""
        config = await self.get_by_id(config_id)
        if not config:
            return None

        config.base_salary = new_salary
        if new_hourly_rate:
            config.hourly_rate = new_hourly_rate
        config.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(config)

        return config

    async def update_bank_hours_balance(
        self,
        config_id: UUID,
        adjustment: Decimal,
        *,
        adjustment_type: str = "credit",
    ) -> Optional[EmployeePayrollConfig]:
        """Atualiza saldo do banco de horas."""
        config = await self.get_by_id(config_id)
        if not config:
            return None

        if adjustment_type == "credit":
            config.bank_hours_balance = (config.bank_hours_balance or Decimal("0")) + adjustment
        elif adjustment_type == "debit":
            config.bank_hours_balance = (config.bank_hours_balance or Decimal("0")) - adjustment
        elif adjustment_type == "reset":
            config.bank_hours_balance = Decimal("0")

        config.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(config)

        return config

    async def terminate(
        self,
        config_id: UUID,
        termination_date,
    ) -> Optional[EmployeePayrollConfig]:
        """Registra demissão."""
        config = await self.get_by_id(config_id)
        if not config:
            return None

        config.termination_date = termination_date
        config.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(config)

        return config

    async def delete(self, config_id: UUID) -> bool:
        """Soft delete da configuração."""
        config = await self.get_by_id(config_id)
        if not config:
            return False

        config.ativo = False
        config.updated_at = datetime.utcnow()
        await self.db.commit()

        return True

    async def get_active_employees(
        self,
        condominio_id: UUID,
    ) -> List[EmployeePayrollConfig]:
        """Retorna funcionários ativos."""
        query = select(EmployeePayrollConfig).where(
            and_(
                EmployeePayrollConfig.condominio_id == condominio_id,
                EmployeePayrollConfig.ativo.is_(True),
                EmployeePayrollConfig.termination_date.is_(None),
            )
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_employees_with_bank_hours(
        self,
        condominio_id: UUID,
    ) -> List[EmployeePayrollConfig]:
        """Retorna funcionários com banco de horas ativo."""
        query = select(EmployeePayrollConfig).where(
            and_(
                EmployeePayrollConfig.condominio_id == condominio_id,
                EmployeePayrollConfig.ativo.is_(True),
                EmployeePayrollConfig.termination_date.is_(None),
                EmployeePayrollConfig.bank_hours_enabled.is_(True),
            )
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_by_contract_type(
        self,
        condominio_id: UUID,
    ) -> dict:
        """Conta funcionários por tipo de contrato."""
        query = (
            select(
                EmployeePayrollConfig.contract_type,
                func.count(EmployeePayrollConfig.id),
            )
            .where(
                and_(
                    EmployeePayrollConfig.condominio_id == condominio_id,
                    EmployeePayrollConfig.ativo.is_(True),
                    EmployeePayrollConfig.termination_date.is_(None),
                )
            )
            .group_by(EmployeePayrollConfig.contract_type)
        )

        result = await self.db.execute(query)
        return {row[0]: row[1] for row in result.fetchall()}
