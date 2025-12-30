"""Repository para Resident."""

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.residents.models.resident import Resident, ResidentStatus, ResidentType
from modules.residents.schemas.resident import ResidentCreate, ResidentFilter, ResidentUpdate

logger = logging.getLogger(__name__)


class ResidentRepository:
    """Repository para operações de Resident."""

    def __init__(self, session: AsyncSession):
        """Inicializa o repository."""
        self.session = session

    async def create(self, data: ResidentCreate) -> Resident:
        """Cria um novo morador."""
        resident = Resident(**data.model_dump(exclude_unset=True))
        self.session.add(resident)
        await self.session.flush()
        return resident

    async def get_by_id(self, resident_id: str | UUID) -> Optional[Resident]:
        """Busca por ID."""
        query = select(Resident).where(
            and_(Resident.id == resident_id, Resident.deleted_at.is_(None))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[Resident]:
        """Busca por código."""
        query = select(Resident).where(
            and_(Resident.code == code, Resident.deleted_at.is_(None))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_cpf(self, cpf: str) -> Optional[Resident]:
        """Busca por CPF."""
        query = select(Resident).where(
            and_(Resident.cpf == cpf, Resident.deleted_at.is_(None))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_document(self, document_number: str) -> Optional[Resident]:
        """Busca por documento."""
        query = select(Resident).where(
            and_(Resident.document_number == document_number, Resident.deleted_at.is_(None))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_unit(
        self, condominium_id: str, unit_id: str
    ) -> list[Resident]:
        """Busca moradores da unidade."""
        query = select(Resident).where(
            and_(
                Resident.condominium_id == condominium_id,
                Resident.unit_id == unit_id,
                Resident.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(
        self, resident_id: str | UUID, data: ResidentUpdate
    ) -> Optional[Resident]:
        """Atualiza um morador."""
        resident = await self.get_by_id(resident_id)
        if not resident:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(resident, field, value)

        await self.session.flush()
        return resident

    async def soft_delete(self, resident_id: str | UUID) -> bool:
        """Soft delete de morador."""
        resident = await self.get_by_id(resident_id)
        if not resident:
            return False

        resident.deleted_at = datetime.utcnow()
        resident.status = ResidentStatus.INATIVO
        await self.session.flush()
        return True

    async def list_with_filters(
        self,
        filters: Optional[ResidentFilter] = None,
        skip: int = 0,
        limit: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> tuple[list[Resident], int]:
        """Lista moradores com filtros."""
        query = select(Resident).where(Resident.deleted_at.is_(None))

        if filters:
            if filters.name:
                query = query.where(Resident.name.ilike(f"%{filters.name}%"))
            if filters.resident_type:
                query = query.where(Resident.resident_type == filters.resident_type)
            if filters.status:
                query = query.where(Resident.status == filters.status)
            if filters.document_number:
                query = query.where(Resident.document_number == filters.document_number)
            if filters.cpf:
                query = query.where(Resident.cpf == filters.cpf)
            if filters.email:
                query = query.where(Resident.email.ilike(f"%{filters.email}%"))
            if filters.phone:
                query = query.where(Resident.phone.ilike(f"%{filters.phone}%"))
            if filters.condominium_id:
                query = query.where(Resident.condominium_id == filters.condominium_id)
            if filters.unit_id:
                query = query.where(Resident.unit_id == filters.unit_id)
            if filters.block:
                query = query.where(Resident.block == filters.block)
            if filters.is_blocked is not None:
                query = query.where(Resident.is_blocked == filters.is_blocked)
            if filters.is_defaulter is not None:
                query = query.where(Resident.is_defaulter == filters.is_defaulter)
            if filters.is_unit_owner is not None:
                query = query.where(Resident.is_unit_owner == filters.is_unit_owner)
            if filters.is_main_resident is not None:
                query = query.where(Resident.is_main_resident == filters.is_main_resident)

        # Contagem
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        # Ordenação
        order_column = getattr(Resident, order_by, Resident.created_at)
        if order_desc:
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)

        return list(result.scalars().all()), total

    async def search(
        self, query_str: str, condominium_id: str = None, limit: int = 10
    ) -> list[Resident]:
        """Busca moradores."""
        query = select(Resident).where(Resident.deleted_at.is_(None))
        query = query.where(
            Resident.name.ilike(f"%{query_str}%")
            | Resident.document_number.ilike(f"%{query_str}%")
            | Resident.cpf.ilike(f"%{query_str}%")
            | Resident.email.ilike(f"%{query_str}%")
            | Resident.phone.ilike(f"%{query_str}%")
            | Resident.unit_number.ilike(f"%{query_str}%")
        )

        if condominium_id:
            query = query.where(Resident.condominium_id == condominium_id)

        query = query.limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_blocked(
        self, condominium_id: str = None, skip: int = 0, limit: int = 20
    ) -> list[Resident]:
        """Lista moradores bloqueados."""
        query = select(Resident).where(
            and_(Resident.is_blocked.is_(True), Resident.deleted_at.is_(None))
        )
        if condominium_id:
            query = query.where(Resident.condominium_id == condominium_id)
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_defaulters(
        self, condominium_id: str = None, skip: int = 0, limit: int = 20
    ) -> list[Resident]:
        """Lista moradores inadimplentes."""
        query = select(Resident).where(
            and_(Resident.is_defaulter.is_(True), Resident.deleted_at.is_(None))
        )
        if condominium_id:
            query = query.where(Resident.condominium_id == condominium_id)
        query = query.order_by(Resident.debt_amount.desc())
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_owners(
        self, condominium_id: str, skip: int = 0, limit: int = 100
    ) -> list[Resident]:
        """Lista proprietários."""
        query = select(Resident).where(
            and_(
                Resident.condominium_id == condominium_id,
                Resident.resident_type == ResidentType.PROPRIETARIO,
                Resident.deleted_at.is_(None),
            )
        )
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def block(
        self, resident_id: str | UUID, reason: str, blocked_by: str
    ) -> Optional[Resident]:
        """Bloqueia morador."""
        resident = await self.get_by_id(resident_id)
        if not resident:
            return None
        resident.block(reason, blocked_by)
        await self.session.flush()
        return resident

    async def unblock(self, resident_id: str | UUID) -> Optional[Resident]:
        """Desbloqueia morador."""
        resident = await self.get_by_id(resident_id)
        if not resident:
            return None
        resident.unblock()
        await self.session.flush()
        return resident

    async def set_defaulter(
        self, resident_id: str | UUID, debt_amount: float = 0.0
    ) -> Optional[Resident]:
        """Marca como inadimplente."""
        resident = await self.get_by_id(resident_id)
        if not resident:
            return None
        resident.set_defaulter(debt_amount)
        await self.session.flush()
        return resident

    async def clear_defaulter(self, resident_id: str | UUID) -> Optional[Resident]:
        """Remove inadimplência."""
        resident = await self.get_by_id(resident_id)
        if not resident:
            return None
        resident.clear_defaulter()
        await self.session.flush()
        return resident

    async def get_stats(
        self, condominium_id: str = None
    ) -> dict:
        """Retorna estatísticas."""
        base_query = select(Resident).where(Resident.deleted_at.is_(None))
        if condominium_id:
            base_query = base_query.where(Resident.condominium_id == condominium_id)

        result = await self.session.execute(base_query)
        residents = list(result.scalars().all())

        stats = {
            "total": len(residents),
            "active": sum(1 for r in residents if r.status == ResidentStatus.ATIVO),
            "inactive": sum(1 for r in residents if r.status == ResidentStatus.INATIVO),
            "blocked": sum(1 for r in residents if r.is_blocked),
            "defaulters": sum(1 for r in residents if r.is_defaulter),
            "pending": sum(1 for r in residents if r.status == ResidentStatus.PENDENTE),
            "by_type": {},
            "by_status": {},
            "by_block": {},
            "with_biometric": sum(1 for r in residents if r.has_biometric),
            "with_access_card": sum(1 for r in residents if r.has_access_card),
            "owners": sum(1 for r in residents if r.resident_type == ResidentType.PROPRIETARIO),
            "tenants": sum(1 for r in residents if r.resident_type == ResidentType.INQUILINO),
            "total_debt": sum(r.debt_amount or 0 for r in residents if r.is_defaulter),
        }

        for r in residents:
            stats["by_type"][r.resident_type.value] = stats["by_type"].get(
                r.resident_type.value, 0
            ) + 1
            stats["by_status"][r.status.value] = stats["by_status"].get(
                r.status.value, 0
            ) + 1
            if r.block:
                stats["by_block"][r.block] = stats["by_block"].get(r.block, 0) + 1

        if stats["defaulters"] > 0:
            stats["avg_debt"] = stats["total_debt"] / stats["defaulters"]
        else:
            stats["avg_debt"] = 0.0

        return stats
