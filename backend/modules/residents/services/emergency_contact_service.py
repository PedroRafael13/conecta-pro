"""Service para ResidentEmergencyContact."""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.residents.repositories.emergency_contact_repository import (
    EmergencyContactRepository,
)
from modules.residents.models.emergency_contact import ContactRelationship
from modules.residents.schemas.emergency_contact import (
    EmergencyContactCreate,
    EmergencyContactUpdate,
    EmergencyContactFilter,
    EmergencyContactResponse,
    EmergencyContactListResponse,
)

logger = logging.getLogger(__name__)


class EmergencyContactService:
    """Service para operações de ResidentEmergencyContact."""

    def __init__(self, session: AsyncSession):
        """Inicializa o service."""
        self.session = session
        self.repository = EmergencyContactRepository(session)

    async def create(self, data: EmergencyContactCreate) -> EmergencyContactResponse:
        """Cria um novo contato de emergência."""
        # Se é o primeiro contato, define como principal automaticamente
        count = await self.repository.count_by_resident(data.resident_id)
        if count == 0:
            data_dict = data.model_dump()
            data_dict["is_primary"] = True
            data = EmergencyContactCreate(**data_dict)

        contact = await self.repository.create(data)
        await self.session.commit()
        logger.info("Contato de emergência criado: {contact.id} - {contact.name}")
        return EmergencyContactResponse.model_validate(contact)

    async def get_by_id(
        self, contact_id: str | UUID
    ) -> Optional[EmergencyContactResponse]:
        """Busca contato por ID."""
        contact = await self.repository.get_by_id(contact_id)
        if not contact:
            return None
        return EmergencyContactResponse.model_validate(contact)

    async def get_by_resident(
        self, resident_id: str | UUID, include_inactive: bool = False
    ) -> list[EmergencyContactResponse]:
        """Busca contatos do morador."""
        contacts = await self.repository.get_by_resident(resident_id, include_inactive)
        return [EmergencyContactResponse.model_validate(c) for c in contacts]

    async def get_primary_by_resident(
        self, resident_id: str | UUID
    ) -> Optional[EmergencyContactResponse]:
        """Busca contato principal do morador."""
        contact = await self.repository.get_primary_by_resident(resident_id)
        if not contact:
            return None
        return EmergencyContactResponse.model_validate(contact)

    async def update(
        self, contact_id: str | UUID, data: EmergencyContactUpdate
    ) -> Optional[EmergencyContactResponse]:
        """Atualiza um contato."""
        contact = await self.repository.update(contact_id, data)
        if not contact:
            return None
        await self.session.commit()
        logger.info("Contato de emergência atualizado: {contact.id}")
        return EmergencyContactResponse.model_validate(contact)

    async def delete(self, contact_id: str | UUID) -> bool:
        """Remove contato (soft delete)."""
        # Verifica se é o contato principal
        contact = await self.repository.get_by_id(contact_id)
        if not contact:
            return False

        if contact.is_primary:
            # Busca outros contatos para definir novo principal
            contacts = await self.repository.get_by_resident(contact.resident_id)
            other_contacts = [c for c in contacts if str(c.id) != str(contact_id)]
            if other_contacts:
                # Define o próximo como principal
                await self.repository.set_as_primary(other_contacts[0].id)

        result = await self.repository.soft_delete(contact_id)
        if result:
            await self.session.commit()
            logger.info("Contato de emergência removido: {contact_id}")
        return result

    async def list(
        self,
        filters: Optional[EmergencyContactFilter] = None,
        page: int = 1,
        page_size: int = 20,
        order_by: str = "priority",
        order_desc: bool = False,
    ) -> EmergencyContactListResponse:
        """Lista contatos com filtros e paginação."""
        skip = (page - 1) * page_size
        contacts, total = await self.repository.list_with_filters(
            filters=filters,
            skip=skip,
            limit=page_size,
            order_by=order_by,
            order_desc=order_desc,
        )

        pages = (total + page_size - 1) // page_size if total > 0 else 0

        return EmergencyContactListResponse(
            items=[EmergencyContactResponse.model_validate(c) for c in contacts],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    async def set_as_primary(
        self, contact_id: str | UUID
    ) -> Optional[EmergencyContactResponse]:
        """Define como contato principal."""
        contact = await self.repository.set_as_primary(contact_id)
        if not contact:
            return None
        await self.session.commit()
        logger.info("Contato definido como principal: {contact_id}")
        return EmergencyContactResponse.model_validate(contact)

    async def deactivate(
        self, contact_id: str | UUID
    ) -> Optional[EmergencyContactResponse]:
        """Desativa contato."""
        contact = await self.repository.deactivate(contact_id)
        if not contact:
            return None
        await self.session.commit()
        logger.info("Contato desativado: {contact_id}")
        return EmergencyContactResponse.model_validate(contact)

    async def activate(
        self, contact_id: str | UUID
    ) -> Optional[EmergencyContactResponse]:
        """Ativa contato."""
        contact = await self.repository.activate(contact_id)
        if not contact:
            return None
        await self.session.commit()
        logger.info("Contato ativado: {contact_id}")
        return EmergencyContactResponse.model_validate(contact)

    async def update_priority(
        self, contact_id: str | UUID, priority: int
    ) -> Optional[EmergencyContactResponse]:
        """Atualiza prioridade do contato."""
        if priority < 1 or priority > 10:
            raise ValueError("Prioridade deve ser entre 1 e 10")

        contact = await self.repository.update_priority(contact_id, priority)
        if not contact:
            return None
        await self.session.commit()
        logger.info("Prioridade atualizada: {contact_id} - {priority}")
        return EmergencyContactResponse.model_validate(contact)

    async def get_by_relationship(
        self,
        resident_id: str | UUID,
        relationship: str,
    ) -> list[EmergencyContactResponse]:
        """Busca contatos por relacionamento."""
        rel = ContactRelationship(relationship)
        contacts = await self.repository.get_by_relationship(resident_id, rel)
        return [EmergencyContactResponse.model_validate(c) for c in contacts]

    async def get_stats_by_resident(self, resident_id: str | UUID) -> dict:
        """Retorna estatísticas de contatos do morador."""
        return await self.repository.get_stats_by_resident(resident_id)

    async def reorder_priorities(
        self, resident_id: str | UUID, contact_ids: list[str]
    ) -> list[EmergencyContactResponse]:
        """Reordena prioridades dos contatos."""
        updated_contacts = []
        for priority, contact_id in enumerate(contact_ids, start=1):
            contact = await self.repository.update_priority(contact_id, priority)
            if contact:
                updated_contacts.append(contact)

        await self.session.commit()
        logger.info("Prioridades reordenadas para morador: {resident_id}")
        return [EmergencyContactResponse.model_validate(c) for c in updated_contacts]
