"""Repository para ResidentEmergencyContact."""

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.residents.models.emergency_contact import (
    ResidentEmergencyContact,
    ContactRelationship,
)
from modules.residents.schemas.emergency_contact import (
    EmergencyContactCreate,
    EmergencyContactFilter,
    EmergencyContactUpdate,
)

logger = logging.getLogger(__name__)


class EmergencyContactRepository:
    """Repository para operações de ResidentEmergencyContact."""

    def __init__(self, session: AsyncSession):
        """Inicializa o repository."""
        self.session = session

    async def create(self, data: EmergencyContactCreate) -> ResidentEmergencyContact:
        """Cria um novo contato de emergência."""
        contact = ResidentEmergencyContact(**data.model_dump(exclude_unset=True))
        self.session.add(contact)
        await self.session.flush()
        return contact

    async def get_by_id(
        self, contact_id: str | UUID
    ) -> Optional[ResidentEmergencyContact]:
        """Busca por ID."""
        query = select(ResidentEmergencyContact).where(
            and_(
                ResidentEmergencyContact.id == contact_id,
                ResidentEmergencyContact.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_resident(
        self, resident_id: str | UUID, include_inactive: bool = False
    ) -> list[ResidentEmergencyContact]:
        """Busca contatos do morador."""
        query = select(ResidentEmergencyContact).where(
            and_(
                ResidentEmergencyContact.resident_id == resident_id,
                ResidentEmergencyContact.deleted_at.is_(None),
            )
        )
        if not include_inactive:
            query = query.where(ResidentEmergencyContact.is_active.is_(True))
        query = query.order_by(ResidentEmergencyContact.priority.asc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_primary_by_resident(
        self, resident_id: str | UUID
    ) -> Optional[ResidentEmergencyContact]:
        """Busca contato principal do morador."""
        query = select(ResidentEmergencyContact).where(
            and_(
                ResidentEmergencyContact.resident_id == resident_id,
                ResidentEmergencyContact.is_primary.is_(True),
                ResidentEmergencyContact.is_active.is_(True),
                ResidentEmergencyContact.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update(
        self, contact_id: str | UUID, data: EmergencyContactUpdate
    ) -> Optional[ResidentEmergencyContact]:
        """Atualiza um contato."""
        contact = await self.get_by_id(contact_id)
        if not contact:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(contact, field, value)

        await self.session.flush()
        return contact

    async def soft_delete(self, contact_id: str | UUID) -> bool:
        """Soft delete de contato."""
        contact = await self.get_by_id(contact_id)
        if not contact:
            return False

        contact.deleted_at = datetime.utcnow()
        contact.is_active = False
        await self.session.flush()
        return True

    async def list_with_filters(
        self,
        filters: Optional[EmergencyContactFilter] = None,
        skip: int = 0,
        limit: int = 20,
        order_by: str = "priority",
        order_desc: bool = False,
    ) -> tuple[list[ResidentEmergencyContact], int]:
        """Lista contatos com filtros."""
        query = select(ResidentEmergencyContact).where(
            ResidentEmergencyContact.deleted_at.is_(None)
        )

        if filters:
            if filters.resident_id:
                query = query.where(
                    ResidentEmergencyContact.resident_id == filters.resident_id
                )
            if filters.relationship:
                query = query.where(
                    ResidentEmergencyContact.relationship == filters.relationship
                )
            if filters.is_primary is not None:
                query = query.where(
                    ResidentEmergencyContact.is_primary == filters.is_primary
                )
            if filters.is_active is not None:
                query = query.where(
                    ResidentEmergencyContact.is_active == filters.is_active
                )

        # Contagem
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        # Ordenação
        order_column = getattr(
            ResidentEmergencyContact, order_by, ResidentEmergencyContact.priority
        )
        if order_desc:
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)

        return list(result.scalars().all()), total

    async def set_as_primary(
        self, contact_id: str | UUID
    ) -> Optional[ResidentEmergencyContact]:
        """Define como contato principal."""
        contact = await self.get_by_id(contact_id)
        if not contact:
            return None

        # Remove primary de outros contatos do mesmo morador
        other_contacts = await self.get_by_resident(contact.resident_id)
        for other in other_contacts:
            if other.id != contact.id and other.is_primary:
                other.is_primary = False

        contact.set_as_primary()
        await self.session.flush()
        return contact

    async def deactivate(
        self, contact_id: str | UUID
    ) -> Optional[ResidentEmergencyContact]:
        """Desativa contato."""
        contact = await self.get_by_id(contact_id)
        if not contact:
            return None
        contact.deactivate()
        await self.session.flush()
        return contact

    async def activate(
        self, contact_id: str | UUID
    ) -> Optional[ResidentEmergencyContact]:
        """Ativa contato."""
        contact = await self.get_by_id(contact_id)
        if not contact:
            return None
        contact.activate()
        await self.session.flush()
        return contact

    async def update_priority(
        self, contact_id: str | UUID, priority: int
    ) -> Optional[ResidentEmergencyContact]:
        """Atualiza prioridade."""
        contact = await self.get_by_id(contact_id)
        if not contact:
            return None
        contact.priority = priority
        await self.session.flush()
        return contact

    async def get_by_relationship(
        self,
        resident_id: str | UUID,
        relationship: ContactRelationship,
    ) -> list[ResidentEmergencyContact]:
        """Busca contatos por relacionamento."""
        query = select(ResidentEmergencyContact).where(
            and_(
                ResidentEmergencyContact.resident_id == resident_id,
                ResidentEmergencyContact.relationship == relationship,
                ResidentEmergencyContact.is_active.is_(True),
                ResidentEmergencyContact.deleted_at.is_(None),
            )
        )
        query = query.order_by(ResidentEmergencyContact.priority.asc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_by_resident(self, resident_id: str | UUID) -> int:
        """Conta contatos do morador."""
        query = select(func.count()).where(
            and_(
                ResidentEmergencyContact.resident_id == resident_id,
                ResidentEmergencyContact.is_active.is_(True),
                ResidentEmergencyContact.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_stats_by_resident(self, resident_id: str | UUID) -> dict:
        """Retorna estatísticas de contatos do morador."""
        contacts = await self.get_by_resident(resident_id, include_inactive=True)

        stats = {
            "total": len(contacts),
            "active": sum(1 for c in contacts if c.is_active),
            "inactive": sum(1 for c in contacts if not c.is_active),
            "has_primary": any(c.is_primary for c in contacts),
            "by_relationship": {},
        }

        for c in contacts:
            stats["by_relationship"][c.relationship.value] = (
                stats["by_relationship"].get(c.relationship.value, 0) + 1
            )

        return stats
