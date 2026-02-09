"""
Repository para operações de banco de dados com TimeBank.
"""

from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import logger
from modules.operacional.models.time_bank import TimeBank, TimeBankStatus
from modules.operacional.schemas.time_bank import (
    TimeBankCreate,
    TimeBankFilter,
    TimeBankSummary,
    TimeBankUpdate,
)


class TimeBankRepository:
    """Repository para operações CRUD de TimeBank."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _get_current_balance(self, employee_id: str) -> float:
        """Calcula saldo atual do funcionário."""
        result = await self.db.execute(
            select(TimeBank).where(
                TimeBank.employee_id == employee_id,
                TimeBank.status == TimeBankStatus.APPROVED.value,
                TimeBank.is_active.is_(True),
            )
        )
        entries = list(result.scalars().all())

        balance = 0.0
        for entry in entries:
            balance += entry.signed_hours

        return balance

    async def create(self, data: TimeBankCreate, created_by: str | None = None) -> TimeBank:
        """
        Cria uma nova entrada no banco de horas.

        Args:
            data: Dados da entrada
            created_by: ID do usuário criador

        Returns:
            TimeBank criado
        """
        # Calcular saldo antes
        balance_before = await self._get_current_balance(data.employee_id)

        time_bank = TimeBank(
            id=str(uuid4()),
            employee_id=data.employee_id,
            entry_type=data.entry_type.value,
            status=TimeBankStatus.PENDING.value,
            hours=abs(data.hours),
            balance_before=balance_before,
            balance_after=balance_before,  # Será atualizado após aprovação
            reference_date=data.reference_date,
            expiration_date=data.expiration_date,
            shift_id=data.shift_id,
            post_id=data.post_id,
            description=data.description,
            reason=data.reason,
            created_by=created_by,
        )

        self.db.add(time_bank)
        await self.db.commit()
        await self.db.refresh(time_bank)

        logger.info(f"TimeBank criado: {time_bank.id}")
        return time_bank

    async def get_by_id(self, time_bank_id: str) -> TimeBank | None:
        """
        Busca entrada por ID.

        Args:
            time_bank_id: ID da entrada

        Returns:
            TimeBank ou None
        """
        result = await self.db.execute(
            select(TimeBank).where(
                TimeBank.id == time_bank_id,
                TimeBank.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        filters: TimeBankFilter | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[TimeBank], int]:
        """
        Lista entradas com filtros e paginação.

        Args:
            filters: Filtros de busca
            page: Página atual
            page_size: Itens por página

        Returns:
            Tupla (entradas, total)
        """
        query = select(TimeBank).where(TimeBank.is_active.is_(True))

        if filters:
            query = self._apply_filters(query, filters)

        # Count total
        count_query = select(func.count(TimeBank.id)).where(TimeBank.is_active.is_(True))
        if filters:
            count_query = self._apply_filters(count_query, filters)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(TimeBank.reference_date.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        entries = list(result.scalars().all())

        return entries, total

    def _apply_filters(self, query, filters: TimeBankFilter):
        """Aplica filtros à query."""
        if filters.employee_id:
            query = query.where(TimeBank.employee_id == filters.employee_id)

        if filters.entry_type:
            query = query.where(TimeBank.entry_type == filters.entry_type.value)

        if filters.status:
            query = query.where(TimeBank.status == filters.status.value)

        if filters.shift_id:
            query = query.where(TimeBank.shift_id == filters.shift_id)

        if filters.post_id:
            query = query.where(TimeBank.post_id == filters.post_id)

        if filters.start_date:
            query = query.where(TimeBank.reference_date >= filters.start_date)

        if filters.end_date:
            query = query.where(TimeBank.reference_date <= filters.end_date)

        if filters.is_expired:
            today = date.today()
            if filters.is_expired:
                query = query.where(
                    and_(
                        TimeBank.expiration_date.isnot(None),
                        TimeBank.expiration_date < today,
                    )
                )
            else:
                query = query.where(TimeBank.expiration_date.is_(None) | (TimeBank.expiration_date >= today))

        if filters.is_pending:
            query = query.where(TimeBank.status == TimeBankStatus.PENDING.value)

        return query

    async def update(self, time_bank_id: str, data: TimeBankUpdate) -> TimeBank | None:
        """
        Atualiza uma entrada.

        Args:
            time_bank_id: ID da entrada
            data: Dados para atualização

        Returns:
            TimeBank atualizado ou None
        """
        time_bank = await self.get_by_id(time_bank_id)
        if not time_bank:
            return None

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field in ("entry_type", "status") and value:
                setattr(time_bank, field, value.value)
            else:
                setattr(time_bank, field, value)

        time_bank.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(time_bank)

        logger.info(f"TimeBank atualizado: {time_bank.id}")
        return time_bank

    async def approve(
        self,
        time_bank_id: str,
        approved_by: str,
        notes: str | None = None,
    ) -> TimeBank | None:
        """
        Aprova uma entrada.

        Args:
            time_bank_id: ID da entrada
            approved_by: ID do aprovador
            notes: Observações

        Returns:
            TimeBank aprovado ou None
        """
        time_bank = await self.get_by_id(time_bank_id)
        if not time_bank:
            return None

        if time_bank.status != TimeBankStatus.PENDING.value:
            logger.warning(f"TimeBank não está pendente: {time_bank_id}")
            return None

        # Calcular novo saldo
        balance_before = await self._get_current_balance(time_bank.employee_id)
        balance_after = balance_before + time_bank.signed_hours

        time_bank.status = TimeBankStatus.APPROVED.value
        time_bank.approved_by = approved_by
        time_bank.approved_at = datetime.utcnow()
        time_bank.balance_before = balance_before
        time_bank.balance_after = balance_after
        if notes:
            time_bank.description = f"{time_bank.description or ''}\n[Aprovação] {notes}".strip()
        time_bank.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(time_bank)

        logger.info(f"TimeBank aprovado: {time_bank.id}")
        return time_bank

    async def reject(
        self,
        time_bank_id: str,
        rejection_reason: str,
        approved_by: str,
    ) -> TimeBank | None:
        """
        Rejeita uma entrada.

        Args:
            time_bank_id: ID da entrada
            rejection_reason: Motivo da rejeição
            approved_by: ID do rejeitador

        Returns:
            TimeBank rejeitado ou None
        """
        time_bank = await self.get_by_id(time_bank_id)
        if not time_bank:
            return None

        time_bank.status = TimeBankStatus.REJECTED.value
        time_bank.rejection_reason = rejection_reason
        time_bank.approved_by = approved_by
        time_bank.approved_at = datetime.utcnow()
        time_bank.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(time_bank)

        logger.info(f"TimeBank rejeitado: {time_bank.id}")
        return time_bank

    async def compensate(  # pylint: disable=too-many-arguments
        self,
        time_bank_id: str,
        hours: float = 0,  # pylint: disable=unused-argument
        compensation_date=None,  # pylint: disable=unused-argument
        compensation_shift_id: str | None = None,
        notes: str | None = None,  # pylint: disable=unused-argument
    ) -> TimeBank | None:
        """
        Marca entrada como compensada.

        Args:
            time_bank_id: ID da entrada (ou employee_id dependendo do contexto)
            hours: Horas a compensar
            compensation_date: Data da compensação
            compensation_shift_id: ID do turno de compensação
            notes: Observações

        Returns:
            TimeBank compensado ou None
        """
        time_bank = await self.get_by_id(time_bank_id)
        if not time_bank:
            return None

        if time_bank.status != TimeBankStatus.APPROVED.value:
            logger.warning(f"TimeBank não está aprovado: {time_bank_id}")
            return None

        time_bank.status = TimeBankStatus.USED.value
        time_bank.compensated_at = datetime.utcnow()
        time_bank.compensation_shift_id = compensation_shift_id
        time_bank.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(time_bank)

        logger.info(f"TimeBank compensado: {time_bank.id}")
        return time_bank

    async def delete(self, time_bank_id: str) -> bool:
        """
        Soft delete de entrada.

        Args:
            time_bank_id: ID da entrada

        Returns:
            True se deletado
        """
        time_bank = await self.get_by_id(time_bank_id)
        if not time_bank:
            return False

        time_bank.is_active = False
        time_bank.updated_at = datetime.utcnow()

        await self.db.commit()

        logger.info(f"TimeBank deletado (soft): {time_bank.id}")
        return True

    async def get_summary(self, employee_id: str) -> TimeBankSummary:
        """
        Obtém resumo do banco de horas de um funcionário.

        Args:
            employee_id: ID do funcionário

        Returns:
            Resumo
        """
        result = await self.db.execute(
            select(TimeBank).where(
                TimeBank.employee_id == employee_id,
                TimeBank.is_active.is_(True),
            )
        )
        entries = list(result.scalars().all())

        total_credit = 0.0
        total_debit = 0.0
        total_compensated = 0.0
        total_expired = 0.0
        pending_approval = 0.0
        expiring_soon = 0.0
        today = date.today()

        for entry in entries:
            if entry.status == TimeBankStatus.PENDING.value:
                pending_approval += entry.hours

            if entry.status == TimeBankStatus.APPROVED.value:
                if entry.is_credit:
                    total_credit += entry.hours
                else:
                    total_debit += entry.hours

                # Verificar expiração próxima (30 dias)
                if entry.expiration_date:
                    days_until = (entry.expiration_date - today).days
                    if 0 < days_until <= 30:
                        expiring_soon += entry.hours

            if entry.status == TimeBankStatus.USED.value:
                total_compensated += entry.hours

            if entry.status == TimeBankStatus.EXPIRED.value:
                total_expired += entry.hours

        current_balance = total_credit - total_debit - total_compensated

        return TimeBankSummary(
            employee_id=employee_id,
            total_credit=total_credit,
            total_debit=total_debit,
            total_compensated=total_compensated,
            total_expired=total_expired,
            current_balance=current_balance,
            pending_approval=pending_approval,
            expiring_soon=expiring_soon,
            entries_count=len(entries),
        )
