"""
Repository para operações de banco de dados com Allocation.
"""

from datetime import date, datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import logger
from modules.operations.models.allocation import Allocation, AllocationStatus
from modules.operations.schemas.allocation import (
    AllocationCreate,
    AllocationFilter,
    AllocationUpdate,
)


class AllocationRepository:
    """Repository para operações CRUD de Allocation."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, data: AllocationCreate, created_by: Optional[str] = None) -> Allocation:
        """
        Cria uma nova alocação.

        Args:
            data: Dados da alocação
            created_by: ID do usuário criador

        Returns:
            Allocation criada
        """
        allocation = Allocation(
            id=str(uuid4()),
            post_id=data.post_id,
            employee_id=data.employee_id,
            status=AllocationStatus.ACTIVE.value,
            start_date=data.start_date,
            end_date=data.end_date,
            is_primary=data.is_primary,
            is_temporary=data.is_temporary,
            hourly_rate=data.hourly_rate,
            monthly_salary=data.monthly_salary,
            additional_benefits=data.additional_benefits,
            role=data.role,
            qualifications=data.qualifications,
            notes=data.notes,
            created_by=created_by,
        )

        self.db.add(allocation)
        await self.db.commit()
        await self.db.refresh(allocation)

        logger.info(f"Allocation criada: {allocation.id}")
        return allocation

    async def get_by_id(self, allocation_id: str) -> Optional[Allocation]:
        """
        Busca alocação por ID.

        Args:
            allocation_id: ID da alocação

        Returns:
            Allocation ou None
        """
        result = await self.db.execute(
            select(Allocation).where(
                Allocation.id == allocation_id,
                Allocation.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def get_current_by_employee(self, employee_id: str) -> List[Allocation]:
        """
        Busca alocações atuais de um funcionário.

        Args:
            employee_id: ID do funcionário

        Returns:
            Lista de alocações
        """
        today = date.today()
        result = await self.db.execute(
            select(Allocation).where(
                Allocation.employee_id == employee_id,
                Allocation.status == AllocationStatus.ACTIVE.value,
                Allocation.start_date <= today,
                Allocation.is_active.is_(True),
            )
        )
        allocations = list(result.scalars().all())

        # Filtrar por end_date (pode ser null)
        return [a for a in allocations if a.end_date is None or a.end_date >= today]

    async def get_by_post(self, post_id: str) -> List[Allocation]:
        """
        Busca alocações de um posto.

        Args:
            post_id: ID do posto

        Returns:
            Lista de alocações
        """
        result = await self.db.execute(
            select(Allocation).where(
                Allocation.post_id == post_id,
                Allocation.status == AllocationStatus.ACTIVE.value,
                Allocation.is_active.is_(True),
            )
        )
        return list(result.scalars().all())

    async def list(
        self,
        filters: Optional[AllocationFilter] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Allocation], int]:
        """
        Lista alocações com filtros e paginação.

        Args:
            filters: Filtros de busca
            page: Página atual
            page_size: Itens por página

        Returns:
            Tupla (alocações, total)
        """
        query = select(Allocation).where(Allocation.is_active.is_(True))

        if filters:
            query = self._apply_filters(query, filters)

        # Count total
        count_query = select(func.count(Allocation.id)).where(Allocation.is_active.is_(True))
        if filters:
            count_query = self._apply_filters(count_query, filters)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(Allocation.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        allocations = list(result.scalars().all())

        return allocations, total

    def _apply_filters(self, query, filters: AllocationFilter):
        """Aplica filtros à query."""
        if filters.post_id:
            query = query.where(Allocation.post_id == filters.post_id)

        if filters.employee_id:
            query = query.where(Allocation.employee_id == filters.employee_id)

        if filters.status:
            query = query.where(Allocation.status == filters.status.value)

        if filters.is_primary is not None:
            query = query.where(Allocation.is_primary == filters.is_primary)

        if filters.is_temporary is not None:
            query = query.where(Allocation.is_temporary == filters.is_temporary)

        if filters.is_current:
            today = date.today()
            query = query.where(
                and_(
                    Allocation.status == AllocationStatus.ACTIVE.value,
                    Allocation.start_date <= today,
                )
            )

        if filters.start_date_from:
            query = query.where(Allocation.start_date >= filters.start_date_from)

        if filters.start_date_to:
            query = query.where(Allocation.start_date <= filters.start_date_to)

        return query

    async def update(self, allocation_id: str, data: AllocationUpdate) -> Optional[Allocation]:
        """
        Atualiza uma alocação.

        Args:
            allocation_id: ID da alocação
            data: Dados para atualização

        Returns:
            Allocation atualizada ou None
        """
        allocation = await self.get_by_id(allocation_id)
        if not allocation:
            return None

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field == "status" and value:
                setattr(allocation, field, value.value)
            else:
                setattr(allocation, field, value)

        allocation.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(allocation)

        logger.info(f"Allocation atualizada: {allocation.id}")
        return allocation

    async def terminate(
        self,
        allocation_id: str,
        end_date: date,
        reason: str,
        notes: Optional[str] = None,
    ) -> Optional[Allocation]:
        """
        Encerra uma alocação.

        Args:
            allocation_id: ID da alocação
            end_date: Data de encerramento
            reason: Motivo
            notes: Observações

        Returns:
            Allocation encerrada ou None
        """
        allocation = await self.get_by_id(allocation_id)
        if not allocation:
            return None

        allocation.status = AllocationStatus.TERMINATED.value
        allocation.end_date = end_date
        allocation.termination_reason = reason
        if notes:
            allocation.notes = f"{allocation.notes or ''}\n[Encerramento] {notes}".strip()
        allocation.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(allocation)

        logger.info(f"Allocation encerrada: {allocation.id}")
        return allocation

    async def delete(self, allocation_id: str) -> bool:
        """
        Soft delete de alocação.

        Args:
            allocation_id: ID da alocação

        Returns:
            True se deletada
        """
        allocation = await self.get_by_id(allocation_id)
        if not allocation:
            return False

        allocation.is_active = False
        allocation.updated_at = datetime.utcnow()

        await self.db.commit()

        logger.info(f"Allocation deletada (soft): {allocation.id}")
        return True

    async def get_available_employees(
        self, shift_date: date, post_id: Optional[str] = None
    ) -> List[str]:
        """
        Lista funcionários disponíveis em uma data.

        Args:
            shift_date: Data
            post_id: ID do posto (opcional, para priorizar)

        Returns:
            Lista de IDs de funcionários disponíveis
        """
        # Busca alocações ativas
        result = await self.db.execute(
            select(Allocation).where(
                Allocation.status == AllocationStatus.ACTIVE.value,
                Allocation.start_date <= shift_date,
                Allocation.is_active.is_(True),
            )
        )
        allocations = list(result.scalars().all())

        available = []
        for allocation in allocations:
            if allocation.end_date is None or allocation.end_date >= shift_date:
                available.append(allocation.employee_id)

        return list(set(available))
