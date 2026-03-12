"""
Serviço de Banco de Horas — Departamento Pessoal.

Re-exporta o modelo TimeBank do operacional e adiciona
métodos de crédito, débito e consulta de saldo.
"""

import logging
from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.operacional.models.time_bank import (
    TimeBank,
    TimeBankEntryType,
    TimeBankStatus,
)

logger = logging.getLogger(__name__)


class OvertimeBankService:
    """Serviço de Banco de Horas — visão DP."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def credit(
        self,
        employee_id: str | UUID,
        hours: float,
        reference_date: date,
        description: str | None = None,
        created_by_id: str | UUID | None = None,
    ) -> TimeBank:
        """Credita horas no banco de horas do funcionário.

        Args:
            employee_id: ID do funcionário.
            hours: Quantidade de horas a creditar.
            reference_date: Data de referência.
            description: Descrição do crédito.
            created_by_id: ID do usuário que criou.

        Returns:
            Instância de TimeBank criada.
        """
        entry = TimeBank(
            id=uuid4(),
            employee_id=str(employee_id),
            entry_type=TimeBankEntryType.CREDIT,
            hours=hours,
            reference_date=reference_date,
            description=description or "Crédito de horas extras",
            status=TimeBankStatus.APPROVED,
            created_by_id=str(created_by_id) if created_by_id else None,
        )
        self.db.add(entry)
        await self.db.flush()
        await self.db.refresh(entry)
        logger.info(
            "Crédito de %.1fh no banco de horas: employee=%s",
            hours,
            employee_id,
        )
        return entry

    async def debit(
        self,
        employee_id: str | UUID,
        hours: float,
        reference_date: date,
        description: str | None = None,
        created_by_id: str | UUID | None = None,
    ) -> TimeBank:
        """Debita horas do banco de horas do funcionário.

        Args:
            employee_id: ID do funcionário.
            hours: Quantidade de horas a debitar.
            reference_date: Data de referência.
            description: Descrição do débito.
            created_by_id: ID do usuário que criou.

        Returns:
            Instância de TimeBank criada.
        """
        entry = TimeBank(
            id=uuid4(),
            employee_id=str(employee_id),
            entry_type=TimeBankEntryType.DEBIT,
            hours=hours,
            reference_date=reference_date,
            description=description or "Débito de compensação",
            status=TimeBankStatus.APPROVED,
            created_by_id=str(created_by_id) if created_by_id else None,
        )
        self.db.add(entry)
        await self.db.flush()
        await self.db.refresh(entry)
        logger.info(
            "Débito de %.1fh no banco de horas: employee=%s",
            hours,
            employee_id,
        )
        return entry

    async def get_balance(self, employee_id: str | UUID) -> dict:
        """Retorna o saldo atual do banco de horas do funcionário.

        Args:
            employee_id: ID do funcionário.

        Returns:
            Dicionário com saldo total, créditos e débitos.
        """
        # Créditos aprovados
        credit_result = await self.db.execute(
            select(func.coalesce(func.sum(TimeBank.hours), 0)).where(
                TimeBank.employee_id == str(employee_id),
                TimeBank.entry_type == TimeBankEntryType.CREDIT,
                TimeBank.status == TimeBankStatus.APPROVED,
            )
        )
        total_credits = float(credit_result.scalar() or 0)

        # Débitos e compensações aprovados
        debit_result = await self.db.execute(
            select(func.coalesce(func.sum(TimeBank.hours), 0)).where(
                TimeBank.employee_id == str(employee_id),
                TimeBank.entry_type.in_(
                    [
                        TimeBankEntryType.DEBIT,
                        TimeBankEntryType.COMPENSATION,
                    ]
                ),
                TimeBank.status == TimeBankStatus.APPROVED,
            )
        )
        total_debits = float(debit_result.scalar() or 0)

        balance = total_credits - total_debits

        return {
            "employee_id": str(employee_id),
            "total_credits": round(total_credits, 2),
            "total_debits": round(total_debits, 2),
            "balance": round(balance, 2),
            "unit": "hours",
        }
