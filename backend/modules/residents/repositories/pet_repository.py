"""Repository para ResidentPet."""

import logging
from datetime import datetime, date
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.residents.models.pet import ResidentPet, PetStatus, PetType, PetSize
from modules.residents.schemas.pet import PetCreate, PetFilter, PetUpdate

logger = logging.getLogger(__name__)


class PetRepository:
    """Repository para operações de ResidentPet."""

    def __init__(self, session: AsyncSession):
        """Inicializa o repository."""
        self.session = session

    async def create(self, data: PetCreate) -> ResidentPet:
        """Cria um novo pet."""
        pet = ResidentPet(**data.model_dump(exclude_unset=True))
        self.session.add(pet)
        await self.session.flush()
        return pet

    async def get_by_id(self, pet_id: str | UUID) -> Optional[ResidentPet]:
        """Busca por ID."""
        query = select(ResidentPet).where(
            and_(ResidentPet.id == pet_id, ResidentPet.deleted_at.is_(None))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_microchip(self, microchip: str) -> Optional[ResidentPet]:
        """Busca por microchip."""
        query = select(ResidentPet).where(
            and_(
                ResidentPet.microchip_number == microchip,
                ResidentPet.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_resident(
        self, resident_id: str | UUID, include_inactive: bool = False
    ) -> list[ResidentPet]:
        """Busca pets do morador."""
        query = select(ResidentPet).where(
            and_(
                ResidentPet.resident_id == resident_id,
                ResidentPet.deleted_at.is_(None),
            )
        )
        if not include_inactive:
            query = query.where(ResidentPet.status == PetStatus.ATIVO)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(
        self, pet_id: str | UUID, data: PetUpdate
    ) -> Optional[ResidentPet]:
        """Atualiza um pet."""
        pet = await self.get_by_id(pet_id)
        if not pet:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(pet, field, value)

        await self.session.flush()
        return pet

    async def soft_delete(self, pet_id: str | UUID) -> bool:
        """Soft delete de pet."""
        pet = await self.get_by_id(pet_id)
        if not pet:
            return False

        pet.deleted_at = datetime.utcnow()
        pet.status = PetStatus.INATIVO
        await self.session.flush()
        return True

    async def list_with_filters(
        self,
        filters: Optional[PetFilter] = None,
        skip: int = 0,
        limit: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> tuple[list[ResidentPet], int]:
        """Lista pets com filtros."""
        query = select(ResidentPet).where(ResidentPet.deleted_at.is_(None))

        if filters:
            if filters.resident_id:
                query = query.where(ResidentPet.resident_id == filters.resident_id)
            if filters.pet_type:
                query = query.where(ResidentPet.pet_type == filters.pet_type)
            if filters.status:
                query = query.where(ResidentPet.status == filters.status)
            if filters.breed:
                query = query.where(ResidentPet.breed.ilike(f"%{filters.breed}%"))
            if filters.size:
                query = query.where(ResidentPet.size == filters.size)
            if filters.is_vaccinated is not None:
                query = query.where(ResidentPet.is_vaccinated == filters.is_vaccinated)
            if filters.is_neutered is not None:
                query = query.where(ResidentPet.is_neutered == filters.is_neutered)
            if filters.is_aggressive is not None:
                query = query.where(ResidentPet.is_aggressive == filters.is_aggressive)
            if filters.can_use_common_areas is not None:
                query = query.where(
                    ResidentPet.can_use_common_areas == filters.can_use_common_areas
                )
            if filters.condominium_id:
                query = query.where(ResidentPet.condominium_id == filters.condominium_id)

        # Contagem
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        # Ordenação
        order_column = getattr(ResidentPet, order_by, ResidentPet.created_at)
        if order_desc:
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)

        return list(result.scalars().all()), total

    async def search(
        self, query_str: str, condominium_id: str = None, limit: int = 10
    ) -> list[ResidentPet]:
        """Busca pets."""
        query = select(ResidentPet).where(ResidentPet.deleted_at.is_(None))
        query = query.where(
            ResidentPet.name.ilike(f"%{query_str}%")
            | ResidentPet.breed.ilike(f"%{query_str}%")
            | ResidentPet.microchip_number.ilike(f"%{query_str}%")
            | ResidentPet.registration_number.ilike(f"%{query_str}%")
        )

        if condominium_id:
            query = query.where(ResidentPet.condominium_id == condominium_id)

        query = query.limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_aggressive(
        self, condominium_id: str = None, skip: int = 0, limit: int = 20
    ) -> list[ResidentPet]:
        """Lista pets agressivos."""
        query = select(ResidentPet).where(
            and_(
                ResidentPet.is_aggressive.is_(True),
                ResidentPet.status == PetStatus.ATIVO,
                ResidentPet.deleted_at.is_(None),
            )
        )
        if condominium_id:
            query = query.where(ResidentPet.condominium_id == condominium_id)
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_not_vaccinated(
        self, condominium_id: str = None, skip: int = 0, limit: int = 20
    ) -> list[ResidentPet]:
        """Lista pets não vacinados."""
        query = select(ResidentPet).where(
            and_(
                ResidentPet.is_vaccinated.is_(False),
                ResidentPet.status == PetStatus.ATIVO,
                ResidentPet.deleted_at.is_(None),
            )
        )
        if condominium_id:
            query = query.where(ResidentPet.condominium_id == condominium_id)
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_vaccination_expiring(
        self, days: int = 30, condominium_id: str = None
    ) -> list[ResidentPet]:
        """Lista pets com vacina expirando."""
        today = date.today()
        expiry_limit = date(today.year, today.month, today.day)
        # Calcula data limite
        from datetime import timedelta

        expiry_limit = today + timedelta(days=days)

        query = select(ResidentPet).where(
            and_(
                ResidentPet.vaccination_expiry.isnot(None),
                ResidentPet.vaccination_expiry <= expiry_limit,
                ResidentPet.vaccination_expiry >= today,
                ResidentPet.status == PetStatus.ATIVO,
                ResidentPet.deleted_at.is_(None),
            )
        )
        if condominium_id:
            query = query.where(ResidentPet.condominium_id == condominium_id)
        query = query.order_by(ResidentPet.vaccination_expiry.asc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_vaccination(
        self, pet_id: str | UUID, vaccination_date: date, expiry_date: date
    ) -> Optional[ResidentPet]:
        """Atualiza vacinação."""
        pet = await self.get_by_id(pet_id)
        if not pet:
            return None
        pet.update_vaccination(vaccination_date, expiry_date)
        await self.session.flush()
        return pet

    async def deactivate(self, pet_id: str | UUID) -> Optional[ResidentPet]:
        """Desativa pet."""
        pet = await self.get_by_id(pet_id)
        if not pet:
            return None
        pet.deactivate()
        await self.session.flush()
        return pet

    async def mark_as_deceased(self, pet_id: str | UUID) -> Optional[ResidentPet]:
        """Marca como falecido."""
        pet = await self.get_by_id(pet_id)
        if not pet:
            return None
        pet.mark_as_deceased()
        await self.session.flush()
        return pet

    async def mark_as_donated(self, pet_id: str | UUID) -> Optional[ResidentPet]:
        """Marca como doado."""
        pet = await self.get_by_id(pet_id)
        if not pet:
            return None
        pet.mark_as_donated()
        await self.session.flush()
        return pet

    async def mark_as_lost(self, pet_id: str | UUID) -> Optional[ResidentPet]:
        """Marca como perdido."""
        pet = await self.get_by_id(pet_id)
        if not pet:
            return None
        pet.mark_as_lost()
        await self.session.flush()
        return pet

    async def restrict_areas(
        self, pet_id: str | UUID, areas: list[str]
    ) -> Optional[ResidentPet]:
        """Restringe áreas."""
        pet = await self.get_by_id(pet_id)
        if not pet:
            return None
        pet.restrict_areas(areas)
        await self.session.flush()
        return pet

    async def allow_areas(
        self, pet_id: str | UUID, areas: list[str]
    ) -> Optional[ResidentPet]:
        """Permite áreas."""
        pet = await self.get_by_id(pet_id)
        if not pet:
            return None
        pet.allow_areas(areas)
        await self.session.flush()
        return pet

    async def get_stats(self, condominium_id: str = None) -> dict:
        """Retorna estatísticas."""
        base_query = select(ResidentPet).where(ResidentPet.deleted_at.is_(None))
        if condominium_id:
            base_query = base_query.where(ResidentPet.condominium_id == condominium_id)

        result = await self.session.execute(base_query)
        pets = list(result.scalars().all())

        # Conta vacinas expirando nos próximos 30 dias
        today = date.today()
        from datetime import timedelta

        expiry_limit = today + timedelta(days=30)

        stats = {
            "total": len(pets),
            "active": sum(1 for p in pets if p.status == PetStatus.ATIVO),
            "by_type": {},
            "by_size": {},
            "vaccinated": sum(1 for p in pets if p.is_vaccinated),
            "not_vaccinated": sum(1 for p in pets if not p.is_vaccinated),
            "vaccination_expiring": sum(
                1
                for p in pets
                if p.vaccination_expiry
                and p.vaccination_expiry <= expiry_limit
                and p.vaccination_expiry >= today
            ),
            "neutered": sum(1 for p in pets if p.is_neutered),
            "aggressive": sum(1 for p in pets if p.is_aggressive),
            "with_special_needs": sum(1 for p in pets if p.has_special_needs),
            "deceased": sum(1 for p in pets if p.status == PetStatus.FALECIDO),
            "lost": sum(1 for p in pets if p.status == PetStatus.PERDIDO),
        }

        for p in pets:
            stats["by_type"][p.pet_type.value] = (
                stats["by_type"].get(p.pet_type.value, 0) + 1
            )
            if p.size:
                stats["by_size"][p.size.value] = (
                    stats["by_size"].get(p.size.value, 0) + 1
                )

        return stats
