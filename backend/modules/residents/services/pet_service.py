"""Service para ResidentPet."""

import logging
from datetime import date
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.residents.repositories.pet_repository import PetRepository
from modules.residents.schemas.pet import (
    PetCreate,
    PetUpdate,
    PetFilter,
    PetResponse,
    PetListResponse,
    PetStats,
)

logger = logging.getLogger(__name__)


class PetService:
    """Service para operações de ResidentPet."""

    def __init__(self, session: AsyncSession):
        """Inicializa o service."""
        self.session = session
        self.repository = PetRepository(session)

    async def create(self, data: PetCreate) -> PetResponse:
        """Cria um novo pet."""
        # Verifica microchip duplicado
        if data.microchip_number:
            existing = await self.repository.get_by_microchip(data.microchip_number)
            if existing:
                raise ValueError(
                    f"Já existe pet com microchip: {data.microchip_number}"
                )

        pet = await self.repository.create(data)
        await self.session.commit()
        logger.info("Pet criado: {pet.id} - {pet.name}")
        return PetResponse.model_validate(pet)

    async def get_by_id(self, pet_id: str | UUID) -> Optional[PetResponse]:
        """Busca pet por ID."""
        pet = await self.repository.get_by_id(pet_id)
        if not pet:
            return None
        return PetResponse.model_validate(pet)

    async def get_by_microchip(self, microchip: str) -> Optional[PetResponse]:
        """Busca pet por microchip."""
        pet = await self.repository.get_by_microchip(microchip)
        if not pet:
            return None
        return PetResponse.model_validate(pet)

    async def get_by_resident(
        self, resident_id: str | UUID, include_inactive: bool = False
    ) -> list[PetResponse]:
        """Busca pets do morador."""
        pets = await self.repository.get_by_resident(resident_id, include_inactive)
        return [PetResponse.model_validate(p) for p in pets]

    async def update(
        self, pet_id: str | UUID, data: PetUpdate
    ) -> Optional[PetResponse]:
        """Atualiza um pet."""
        # Verifica microchip duplicado
        if data.microchip_number:
            existing = await self.repository.get_by_microchip(data.microchip_number)
            if existing and str(existing.id) != str(pet_id):
                raise ValueError(
                    f"Já existe pet com microchip: {data.microchip_number}"
                )

        pet = await self.repository.update(pet_id, data)
        if not pet:
            return None
        await self.session.commit()
        logger.info("Pet atualizado: {pet.id}")
        return PetResponse.model_validate(pet)

    async def delete(self, pet_id: str | UUID) -> bool:
        """Remove pet (soft delete)."""
        result = await self.repository.soft_delete(pet_id)
        if result:
            await self.session.commit()
            logger.info("Pet removido: {pet_id}")
        return result

    async def list(
        self,
        filters: Optional[PetFilter] = None,
        page: int = 1,
        page_size: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> PetListResponse:
        """Lista pets com filtros e paginação."""
        skip = (page - 1) * page_size
        pets, total = await self.repository.list_with_filters(
            filters=filters,
            skip=skip,
            limit=page_size,
            order_by=order_by,
            order_desc=order_desc,
        )

        pages = (total + page_size - 1) // page_size if total > 0 else 0

        return PetListResponse(
            items=[PetResponse.model_validate(p) for p in pets],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    async def search(
        self, query: str, condominium_id: str = None, limit: int = 10
    ) -> list[PetResponse]:
        """Busca pets."""
        pets = await self.repository.search(query, condominium_id, limit)
        return [PetResponse.model_validate(p) for p in pets]

    async def get_aggressive(
        self, condominium_id: str = None, page: int = 1, page_size: int = 20
    ) -> list[PetResponse]:
        """Lista pets agressivos."""
        skip = (page - 1) * page_size
        pets = await self.repository.get_aggressive(condominium_id, skip, page_size)
        return [PetResponse.model_validate(p) for p in pets]

    async def get_not_vaccinated(
        self, condominium_id: str = None, page: int = 1, page_size: int = 20
    ) -> list[PetResponse]:
        """Lista pets não vacinados."""
        skip = (page - 1) * page_size
        pets = await self.repository.get_not_vaccinated(condominium_id, skip, page_size)
        return [PetResponse.model_validate(p) for p in pets]

    async def get_vaccination_expiring(
        self, days: int = 30, condominium_id: str = None
    ) -> list[PetResponse]:
        """Lista pets com vacina expirando."""
        pets = await self.repository.get_vaccination_expiring(days, condominium_id)
        return [PetResponse.model_validate(p) for p in pets]

    async def update_vaccination(
        self, pet_id: str | UUID, vaccination_date: date, expiry_date: date
    ) -> Optional[PetResponse]:
        """Atualiza vacinação."""
        pet = await self.repository.update_vaccination(
            pet_id, vaccination_date, expiry_date
        )
        if not pet:
            return None
        await self.session.commit()
        logger.info("Vacinação atualizada: {pet_id}")
        return PetResponse.model_validate(pet)

    async def deactivate(self, pet_id: str | UUID) -> Optional[PetResponse]:
        """Desativa pet."""
        pet = await self.repository.deactivate(pet_id)
        if not pet:
            return None
        await self.session.commit()
        logger.info("Pet desativado: {pet_id}")
        return PetResponse.model_validate(pet)

    async def mark_as_deceased(self, pet_id: str | UUID) -> Optional[PetResponse]:
        """Marca pet como falecido."""
        pet = await self.repository.mark_as_deceased(pet_id)
        if not pet:
            return None
        await self.session.commit()
        logger.info("Pet marcado como falecido: {pet_id}")
        return PetResponse.model_validate(pet)

    async def mark_as_donated(self, pet_id: str | UUID) -> Optional[PetResponse]:
        """Marca pet como doado."""
        pet = await self.repository.mark_as_donated(pet_id)
        if not pet:
            return None
        await self.session.commit()
        logger.info("Pet marcado como doado: {pet_id}")
        return PetResponse.model_validate(pet)

    async def mark_as_lost(self, pet_id: str | UUID) -> Optional[PetResponse]:
        """Marca pet como perdido."""
        pet = await self.repository.mark_as_lost(pet_id)
        if not pet:
            return None
        await self.session.commit()
        logger.info("Pet marcado como perdido: {pet_id}")
        return PetResponse.model_validate(pet)

    async def restrict_areas(
        self, pet_id: str | UUID, areas: list[str]
    ) -> Optional[PetResponse]:
        """Restringe áreas para o pet."""
        pet = await self.repository.restrict_areas(pet_id, areas)
        if not pet:
            return None
        await self.session.commit()
        logger.info("Áreas restritas para pet: {pet_id}")
        return PetResponse.model_validate(pet)

    async def allow_areas(
        self, pet_id: str | UUID, areas: list[str]
    ) -> Optional[PetResponse]:
        """Permite áreas para o pet."""
        pet = await self.repository.allow_areas(pet_id, areas)
        if not pet:
            return None
        await self.session.commit()
        logger.info("Áreas permitidas para pet: {pet_id}")
        return PetResponse.model_validate(pet)

    async def get_stats(self, condominium_id: str = None) -> PetStats:
        """Retorna estatísticas."""
        stats = await self.repository.get_stats(condominium_id)
        return PetStats(**stats)
