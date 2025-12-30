"""Repository para ResidentDependent."""

import logging
from datetime import datetime, date
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.residents.models.dependent import (
    ResidentDependent,
    DependentStatus,
    RelationshipType,
)
from modules.residents.schemas.dependent import (
    DependentCreate,
    DependentFilter,
    DependentUpdate,
)

logger = logging.getLogger(__name__)


class DependentRepository:
    """Repository para operações de ResidentDependent."""

    def __init__(self, session: AsyncSession):
        """Inicializa o repository."""
        self.session = session

    async def create(self, data: DependentCreate) -> ResidentDependent:
        """Cria um novo dependente."""
        dependent = ResidentDependent(**data.model_dump(exclude_unset=True))
        self.session.add(dependent)
        await self.session.flush()
        return dependent

    async def get_by_id(self, dependent_id: str | UUID) -> Optional[ResidentDependent]:
        """Busca por ID."""
        query = select(ResidentDependent).where(
            and_(
                ResidentDependent.id == dependent_id,
                ResidentDependent.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_cpf(self, cpf: str) -> Optional[ResidentDependent]:
        """Busca por CPF."""
        query = select(ResidentDependent).where(
            and_(ResidentDependent.cpf == cpf, ResidentDependent.deleted_at.is_(None))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_document(self, document_number: str) -> Optional[ResidentDependent]:
        """Busca por documento."""
        query = select(ResidentDependent).where(
            and_(
                ResidentDependent.document_number == document_number,
                ResidentDependent.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_resident(
        self, resident_id: str | UUID, include_inactive: bool = False
    ) -> list[ResidentDependent]:
        """Busca dependentes do morador."""
        query = select(ResidentDependent).where(
            and_(
                ResidentDependent.resident_id == resident_id,
                ResidentDependent.deleted_at.is_(None),
            )
        )
        if not include_inactive:
            query = query.where(ResidentDependent.status == DependentStatus.ATIVO)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_minors_by_resident(
        self, resident_id: str | UUID
    ) -> list[ResidentDependent]:
        """Busca dependentes menores do morador."""
        today = date.today()
        query = select(ResidentDependent).where(
            and_(
                ResidentDependent.resident_id == resident_id,
                ResidentDependent.birth_date.isnot(None),
                ResidentDependent.status == DependentStatus.ATIVO,
                ResidentDependent.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(query)
        dependents = list(result.scalars().all())
        # Filtra menores de 18 anos
        return [d for d in dependents if d.is_minor]

    async def update(
        self, dependent_id: str | UUID, data: DependentUpdate
    ) -> Optional[ResidentDependent]:
        """Atualiza um dependente."""
        dependent = await self.get_by_id(dependent_id)
        if not dependent:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(dependent, field, value)

        await self.session.flush()
        return dependent

    async def soft_delete(self, dependent_id: str | UUID) -> bool:
        """Soft delete de dependente."""
        dependent = await self.get_by_id(dependent_id)
        if not dependent:
            return False

        dependent.deleted_at = datetime.utcnow()
        dependent.status = DependentStatus.INATIVO
        await self.session.flush()
        return True

    async def list_with_filters(
        self,
        filters: Optional[DependentFilter] = None,
        skip: int = 0,
        limit: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> tuple[list[ResidentDependent], int]:
        """Lista dependentes com filtros."""
        query = select(ResidentDependent).where(ResidentDependent.deleted_at.is_(None))

        if filters:
            if filters.resident_id:
                query = query.where(
                    ResidentDependent.resident_id == filters.resident_id
                )
            if filters.relationship_type:
                query = query.where(
                    ResidentDependent.relationship_type == filters.relationship_type
                )
            if filters.status:
                query = query.where(ResidentDependent.status == filters.status)
            if filters.is_minor is not None:
                # Precisa calcular em memória
                pass
            if filters.is_employee is not None:
                employee_types = [
                    RelationshipType.EMPREGADO_DOMESTICO,
                    RelationshipType.DIARISTA,
                    RelationshipType.MOTORISTA,
                    RelationshipType.CUIDADOR,
                ]
                if filters.is_employee:
                    query = query.where(
                        ResidentDependent.relationship_type.in_(employee_types)
                    )
                else:
                    query = query.where(
                        ~ResidentDependent.relationship_type.in_(employee_types)
                    )
            if filters.has_access is not None:
                query = query.where(
                    ResidentDependent.has_access == filters.has_access
                )
            if filters.is_blocked is not None:
                query = query.where(
                    ResidentDependent.is_blocked == filters.is_blocked
                )
            if filters.condominium_id:
                query = query.where(
                    ResidentDependent.condominium_id == filters.condominium_id
                )

        # Contagem
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        # Ordenação
        order_column = getattr(
            ResidentDependent, order_by, ResidentDependent.created_at
        )
        if order_desc:
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)

        dependents = list(result.scalars().all())

        # Filtra menores em memória se necessário
        if filters and filters.is_minor is not None:
            if filters.is_minor:
                dependents = [d for d in dependents if d.is_minor]
            else:
                dependents = [d for d in dependents if not d.is_minor]

        return dependents, total

    async def search(
        self, query_str: str, condominium_id: str = None, limit: int = 10
    ) -> list[ResidentDependent]:
        """Busca dependentes."""
        query = select(ResidentDependent).where(ResidentDependent.deleted_at.is_(None))
        query = query.where(
            ResidentDependent.name.ilike(f"%{query_str}%")
            | ResidentDependent.social_name.ilike(f"%{query_str}%")
            | ResidentDependent.cpf.ilike(f"%{query_str}%")
            | ResidentDependent.document_number.ilike(f"%{query_str}%")
            | ResidentDependent.email.ilike(f"%{query_str}%")
            | ResidentDependent.phone.ilike(f"%{query_str}%")
        )

        if condominium_id:
            query = query.where(ResidentDependent.condominium_id == condominium_id)

        query = query.limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_blocked(
        self, condominium_id: str = None, skip: int = 0, limit: int = 20
    ) -> list[ResidentDependent]:
        """Lista dependentes bloqueados."""
        query = select(ResidentDependent).where(
            and_(
                ResidentDependent.is_blocked.is_(True),
                ResidentDependent.deleted_at.is_(None),
            )
        )
        if condominium_id:
            query = query.where(ResidentDependent.condominium_id == condominium_id)
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_employees(
        self, condominium_id: str = None, skip: int = 0, limit: int = 20
    ) -> list[ResidentDependent]:
        """Lista funcionários domésticos."""
        employee_types = [
            RelationshipType.EMPREGADO_DOMESTICO,
            RelationshipType.DIARISTA,
            RelationshipType.MOTORISTA,
            RelationshipType.CUIDADOR,
        ]
        query = select(ResidentDependent).where(
            and_(
                ResidentDependent.relationship_type.in_(employee_types),
                ResidentDependent.status == DependentStatus.ATIVO,
                ResidentDependent.deleted_at.is_(None),
            )
        )
        if condominium_id:
            query = query.where(ResidentDependent.condominium_id == condominium_id)
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_temporary_expiring(
        self, days: int = 30, condominium_id: str = None
    ) -> list[ResidentDependent]:
        """Lista temporários expirando."""
        today = date.today()
        from datetime import timedelta

        expiry_limit = today + timedelta(days=days)

        query = select(ResidentDependent).where(
            and_(
                ResidentDependent.valid_until.isnot(None),
                ResidentDependent.valid_until <= expiry_limit,
                ResidentDependent.valid_until >= today,
                ResidentDependent.status == DependentStatus.ATIVO,
                ResidentDependent.deleted_at.is_(None),
            )
        )
        if condominium_id:
            query = query.where(ResidentDependent.condominium_id == condominium_id)
        query = query.order_by(ResidentDependent.valid_until.asc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def block(
        self, dependent_id: str | UUID, reason: str
    ) -> Optional[ResidentDependent]:
        """Bloqueia dependente."""
        dependent = await self.get_by_id(dependent_id)
        if not dependent:
            return None
        dependent.block(reason)
        await self.session.flush()
        return dependent

    async def unblock(self, dependent_id: str | UUID) -> Optional[ResidentDependent]:
        """Desbloqueia dependente."""
        dependent = await self.get_by_id(dependent_id)
        if not dependent:
            return None
        dependent.unblock()
        await self.session.flush()
        return dependent

    async def deactivate(self, dependent_id: str | UUID) -> Optional[ResidentDependent]:
        """Desativa dependente."""
        dependent = await self.get_by_id(dependent_id)
        if not dependent:
            return None
        dependent.deactivate()
        await self.session.flush()
        return dependent

    async def activate(self, dependent_id: str | UUID) -> Optional[ResidentDependent]:
        """Ativa dependente."""
        dependent = await self.get_by_id(dependent_id)
        if not dependent:
            return None
        dependent.activate()
        await self.session.flush()
        return dependent

    async def set_temporary(
        self, dependent_id: str | UUID, valid_from: date, valid_until: date
    ) -> Optional[ResidentDependent]:
        """Define como temporário."""
        dependent = await self.get_by_id(dependent_id)
        if not dependent:
            return None
        dependent.set_temporary(valid_from, valid_until)
        await self.session.flush()
        return dependent

    async def add_authorized_pickup(
        self, dependent_id: str | UUID, person_name: str, person_phone: str, document: str = None
    ) -> Optional[ResidentDependent]:
        """Adiciona pessoa autorizada a buscar."""
        dependent = await self.get_by_id(dependent_id)
        if not dependent:
            return None
        dependent.add_authorized_pickup(person_name, person_phone, document)
        await self.session.flush()
        return dependent

    async def remove_authorized_pickup(
        self, dependent_id: str | UUID, person_name: str
    ) -> Optional[ResidentDependent]:
        """Remove pessoa autorizada a buscar."""
        dependent = await self.get_by_id(dependent_id)
        if not dependent:
            return None
        dependent.remove_authorized_pickup(person_name)
        await self.session.flush()
        return dependent

    async def set_work_schedule(
        self, dependent_id: str | UUID, schedule: dict
    ) -> Optional[ResidentDependent]:
        """Define horário de trabalho."""
        dependent = await self.get_by_id(dependent_id)
        if not dependent:
            return None
        dependent.set_work_schedule(schedule)
        await self.session.flush()
        return dependent

    async def get_stats(self, condominium_id: str = None) -> dict:
        """Retorna estatísticas."""
        base_query = select(ResidentDependent).where(
            ResidentDependent.deleted_at.is_(None)
        )
        if condominium_id:
            base_query = base_query.where(
                ResidentDependent.condominium_id == condominium_id
            )

        result = await self.session.execute(base_query)
        dependents = list(result.scalars().all())

        employee_types = [
            RelationshipType.EMPREGADO_DOMESTICO,
            RelationshipType.DIARISTA,
            RelationshipType.MOTORISTA,
            RelationshipType.CUIDADOR,
        ]

        stats = {
            "total": len(dependents),
            "active": sum(1 for d in dependents if d.status == DependentStatus.ATIVO),
            "blocked": sum(1 for d in dependents if d.is_blocked),
            "minors": sum(1 for d in dependents if d.is_minor),
            "employees": sum(
                1 for d in dependents if d.relationship_type in employee_types
            ),
            "temporary": sum(1 for d in dependents if d.valid_until is not None),
            "by_relationship": {},
            "with_access": sum(1 for d in dependents if d.has_access),
            "with_biometric": sum(1 for d in dependents if d.has_biometric),
            "with_special_needs": sum(1 for d in dependents if d.has_special_needs),
        }

        for d in dependents:
            stats["by_relationship"][d.relationship_type.value] = (
                stats["by_relationship"].get(d.relationship_type.value, 0) + 1
            )

        return stats
