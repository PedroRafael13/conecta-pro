"""
Repository para operações de banco de dados com Substitution.
"""

from datetime import date, datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import logger
from modules.operations.models.substitution import Substitution, SubstitutionStatus
from modules.operations.schemas.substitution import (
    SubstitutionCreate,
    SubstitutionFilter,
    SubstitutionUpdate,
)


class SubstitutionRepository:
    """Repository para operações CRUD de Substitution."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self, data: SubstitutionCreate, requested_by: Optional[str] = None
    ) -> Substitution:
        """
        Cria uma nova substituição.

        Args:
            data: Dados da substituição
            requested_by: ID do solicitante

        Returns:
            Substitution criada
        """
        substitution = Substitution(
            id=str(uuid4()),
            shift_id=data.shift_id,
            post_id=data.post_id,
            original_employee_id=data.original_employee_id,
            substitute_employee_id=data.substitute_employee_id,
            reason=data.reason.value,
            status=SubstitutionStatus.PENDING.value,
            substitution_date=data.substitution_date,
            reason_details=data.reason_details,
            notes=data.notes,
            requested_by=requested_by,
        )

        self.db.add(substitution)
        await self.db.commit()
        await self.db.refresh(substitution)

        logger.info(f"Substitution criada: {substitution.id}")
        return substitution

    async def get_by_id(self, substitution_id: str) -> Optional[Substitution]:
        """
        Busca substituição por ID.

        Args:
            substitution_id: ID da substituição

        Returns:
            Substitution ou None
        """
        result = await self.db.execute(
            select(Substitution).where(
                Substitution.id == substitution_id,
                Substitution.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_shift(self, shift_id: str) -> Optional[Substitution]:
        """
        Busca substituição por turno.

        Args:
            shift_id: ID do turno

        Returns:
            Substitution ou None
        """
        result = await self.db.execute(
            select(Substitution).where(
                Substitution.shift_id == shift_id,
                Substitution.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        filters: Optional[SubstitutionFilter] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Substitution], int]:
        """
        Lista substituições com filtros e paginação.

        Args:
            filters: Filtros de busca
            page: Página atual
            page_size: Itens por página

        Returns:
            Tupla (substituições, total)
        """
        query = select(Substitution).where(Substitution.is_active.is_(True))

        if filters:
            query = self._apply_filters(query, filters)

        # Count total
        count_query = select(func.count(Substitution.id)).where(Substitution.is_active.is_(True))
        if filters:
            count_query = self._apply_filters(count_query, filters)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(Substitution.substitution_date.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        substitutions = list(result.scalars().all())

        return substitutions, total

    def _apply_filters(self, query, filters: SubstitutionFilter):
        """Aplica filtros à query."""
        if filters.shift_id:
            query = query.where(Substitution.shift_id == filters.shift_id)

        if filters.post_id:
            query = query.where(Substitution.post_id == filters.post_id)

        if filters.original_employee_id:
            query = query.where(Substitution.original_employee_id == filters.original_employee_id)

        if filters.substitute_employee_id:
            query = query.where(
                Substitution.substitute_employee_id == filters.substitute_employee_id
            )

        if filters.status:
            query = query.where(Substitution.status == filters.status.value)

        if filters.reason:
            query = query.where(Substitution.reason == filters.reason.value)

        if filters.start_date:
            query = query.where(Substitution.substitution_date >= filters.start_date)

        if filters.end_date:
            query = query.where(Substitution.substitution_date <= filters.end_date)

        if filters.is_pending:
            query = query.where(Substitution.status == SubstitutionStatus.PENDING.value)

        if filters.has_substitute is not None:
            if filters.has_substitute:
                query = query.where(Substitution.substitute_employee_id.isnot(None))
            else:
                query = query.where(Substitution.substitute_employee_id.is_(None))

        return query

    async def update(
        self, substitution_id: str, data: SubstitutionUpdate
    ) -> Optional[Substitution]:
        """
        Atualiza uma substituição.

        Args:
            substitution_id: ID da substituição
            data: Dados para atualização

        Returns:
            Substitution atualizada ou None
        """
        substitution = await self.get_by_id(substitution_id)
        if not substitution:
            return None

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field in ("status", "reason") and value:
                setattr(substitution, field, value.value)
            else:
                setattr(substitution, field, value)

        substitution.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(substitution)

        logger.info(f"Substitution atualizada: {substitution.id}")
        return substitution

    async def confirm(
        self,
        substitution_id: str,
        substitute_employee_id: str,
        approved_by: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Optional[Substitution]:
        """
        Confirma uma substituição.

        Args:
            substitution_id: ID da substituição
            substitute_employee_id: ID do substituto
            approved_by: ID do aprovador
            notes: Observações

        Returns:
            Substitution confirmada ou None
        """
        substitution = await self.get_by_id(substitution_id)
        if not substitution:
            return None

        if substitution.status != SubstitutionStatus.PENDING.value:
            logger.warning(f"Substituição não está pendente: {substitution_id}")
            return None

        substitution.substitute_employee_id = substitute_employee_id
        substitution.status = SubstitutionStatus.CONFIRMED.value
        substitution.confirmed_at = datetime.utcnow()
        substitution.approved_by = approved_by
        if notes:
            substitution.notes = f"{substitution.notes or ''}\n[Confirmação] {notes}".strip()
        substitution.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(substitution)

        logger.info(f"Substitution confirmada: {substitution.id}")
        return substitution

    async def reject(
        self,
        substitution_id: str,
        rejection_reason: str,
    ) -> Optional[Substitution]:
        """
        Rejeita uma substituição.

        Args:
            substitution_id: ID da substituição
            rejection_reason: Motivo da rejeição

        Returns:
            Substitution rejeitada ou None
        """
        substitution = await self.get_by_id(substitution_id)
        if not substitution:
            return None

        substitution.status = SubstitutionStatus.REJECTED.value
        substitution.rejection_reason = rejection_reason
        substitution.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(substitution)

        logger.info(f"Substitution rejeitada: {substitution.id}")
        return substitution

    async def complete(self, substitution_id: str) -> Optional[Substitution]:
        """
        Marca substituição como concluída.

        Args:
            substitution_id: ID da substituição

        Returns:
            Substitution concluída ou None
        """
        substitution = await self.get_by_id(substitution_id)
        if not substitution:
            return None

        if substitution.status not in (
            SubstitutionStatus.CONFIRMED.value,
            SubstitutionStatus.IN_PROGRESS.value,
        ):
            logger.warning(f"Substituição não pode ser concluída: {substitution_id}")
            return None

        substitution.status = SubstitutionStatus.COMPLETED.value
        substitution.completed_at = datetime.utcnow()
        substitution.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(substitution)

        logger.info(f"Substitution concluída: {substitution.id}")
        return substitution

    async def delete(self, substitution_id: str) -> bool:
        """
        Soft delete de substituição.

        Args:
            substitution_id: ID da substituição

        Returns:
            True se deletada
        """
        substitution = await self.get_by_id(substitution_id)
        if not substitution:
            return False

        substitution.is_active = False
        substitution.status = SubstitutionStatus.CANCELLED.value
        substitution.updated_at = datetime.utcnow()

        await self.db.commit()

        logger.info(f"Substitution deletada (soft): {substitution.id}")
        return True

    async def get_pending_count(self, post_id: Optional[str] = None) -> int:
        """
        Conta substituições pendentes.

        Args:
            post_id: ID do posto (opcional)

        Returns:
            Quantidade pendente
        """
        query = select(func.count(Substitution.id)).where(
            Substitution.status == SubstitutionStatus.PENDING.value,
            Substitution.is_active.is_(True),
        )

        if post_id:
            query = query.where(Substitution.post_id == post_id)

        result = await self.db.execute(query)
        return result.scalar() or 0
