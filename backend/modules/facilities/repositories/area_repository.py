"""
Repository para operações de banco de dados com Area.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import logger
from modules.facilities.models.area import Area, AreaStatus, AreaType
from modules.facilities.schemas.area import AreaCreate, AreaFilter, AreaStats, AreaUpdate


class AreaRepository:
    """Repository para operações CRUD de Area."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _generate_code(self) -> str:
        """Gera código único para área."""
        result = await self.db.execute(
            select(func.count(Area.id)).where(Area.is_active.is_(True))
        )
        count = result.scalar() or 0
        return f"AREA-{count + 1:04d}"

    async def create(self, data: AreaCreate, created_by: Optional[str] = None) -> Area:
        """
        Cria uma nova área.

        Args:
            data: Dados da área
            created_by: ID do usuário criador

        Returns:
            Area criada
        """
        code = data.code or await self._generate_code()

        area = Area(
            id=str(uuid4()),
            code=code,
            name=data.name,
            description=data.description,
            area_type=data.area_type.value,
            status=AreaStatus.ACTIVE.value,
            parent_id=data.parent_id,
            client_id=data.client_id,
            condominium_id=data.condominium_id,
            floor=data.floor,
            building=data.building,
            area_m2=data.area_m2,
            capacity=data.capacity,
            location_details=data.location_details,
            latitude=data.latitude,
            longitude=data.longitude,
            equipment=data.equipment,
            access_restrictions=data.access_restrictions,
            responsible_id=data.responsible_id,
            requires_reservation=data.requires_reservation,
            is_rentable=data.is_rentable,
            rental_price=data.rental_price,
            created_by=created_by,
        )

        self.db.add(area)
        await self.db.commit()
        await self.db.refresh(area)

        logger.info(f"Area criada: {area.id} - {area.code}")
        return area

    async def get_by_id(self, area_id: str) -> Optional[Area]:
        """
        Busca área por ID.

        Args:
            area_id: ID da área

        Returns:
            Area ou None
        """
        result = await self.db.execute(
            select(Area).where(
                Area.id == area_id,
                Area.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[Area]:
        """
        Busca área por código.

        Args:
            code: Código da área

        Returns:
            Area ou None
        """
        result = await self.db.execute(
            select(Area).where(
                Area.code == code.upper(),
                Area.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        filters: Optional[AreaFilter] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[Area], int]:
        """
        Lista áreas com filtros e paginação.

        Args:
            filters: Filtros de busca
            page: Página atual
            page_size: Itens por página

        Returns:
            Tupla (áreas, total)
        """
        query = select(Area).where(Area.is_active.is_(True))

        if filters:
            query = self._apply_filters(query, filters)

        # Count total
        count_query = select(func.count(Area.id)).where(Area.is_active.is_(True))
        if filters:
            count_query = self._apply_filters(count_query, filters)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(Area.name.asc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        areas = list(result.scalars().all())

        return areas, total

    def _apply_filters(self, query, filters: AreaFilter):
        """Aplica filtros à query."""
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.where(
                or_(
                    Area.name.ilike(search_term),
                    Area.code.ilike(search_term),
                    Area.description.ilike(search_term),
                )
            )

        if filters.area_type:
            query = query.where(Area.area_type == filters.area_type.value)

        if filters.status:
            query = query.where(Area.status == filters.status.value)

        if filters.parent_id:
            query = query.where(Area.parent_id == filters.parent_id)

        if filters.client_id:
            query = query.where(Area.client_id == filters.client_id)

        if filters.condominium_id:
            query = query.where(Area.condominium_id == filters.condominium_id)

        if filters.building:
            query = query.where(Area.building == filters.building)

        if filters.floor:
            query = query.where(Area.floor == filters.floor)

        if filters.requires_reservation is not None:
            query = query.where(Area.requires_reservation == filters.requires_reservation)

        if filters.is_rentable is not None:
            query = query.where(Area.is_rentable == filters.is_rentable)

        return query

    async def update(self, area_id: str, data: AreaUpdate) -> Optional[Area]:
        """
        Atualiza uma área.

        Args:
            area_id: ID da área
            data: Dados para atualização

        Returns:
            Area atualizada ou None
        """
        area = await self.get_by_id(area_id)
        if not area:
            return None

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field in ("area_type", "status") and value:
                setattr(area, field, value.value)
            else:
                setattr(area, field, value)

        area.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(area)

        logger.info(f"Area atualizada: {area.id}")
        return area

    async def delete(self, area_id: str) -> bool:
        """
        Soft delete de área.

        Args:
            area_id: ID da área

        Returns:
            True se deletada
        """
        area = await self.get_by_id(area_id)
        if not area:
            return False

        area.is_active = False
        area.updated_at = datetime.utcnow()

        await self.db.commit()

        logger.info(f"Area deletada (soft): {area.id}")
        return True

    async def get_children(self, parent_id: str) -> List[Area]:
        """
        Busca subáreas de uma área.

        Args:
            parent_id: ID da área pai

        Returns:
            Lista de subáreas
        """
        result = await self.db.execute(
            select(Area).where(
                Area.parent_id == parent_id,
                Area.is_active.is_(True),
            ).order_by(Area.name.asc())
        )
        return list(result.scalars().all())

    async def get_hierarchy(self, area_id: str) -> List[Area]:
        """
        Busca hierarquia de uma área (ancestrais).

        Args:
            area_id: ID da área

        Returns:
            Lista de ancestrais (do mais próximo ao mais distante)
        """
        hierarchy = []
        current = await self.get_by_id(area_id)

        while current and current.parent_id:
            parent = await self.get_by_id(current.parent_id)
            if parent:
                hierarchy.append(parent)
                current = parent
            else:
                break

        return hierarchy

    async def get_stats(
        self,
        client_id: Optional[str] = None,
        condominium_id: Optional[str] = None,
    ) -> AreaStats:
        """
        Obtém estatísticas de áreas.

        Args:
            client_id: Filtrar por cliente
            condominium_id: Filtrar por condomínio

        Returns:
            Estatísticas
        """
        base_filter = [Area.is_active.is_(True)]
        if client_id:
            base_filter.append(Area.client_id == client_id)
        if condominium_id:
            base_filter.append(Area.condominium_id == condominium_id)

        # Total
        total_result = await self.db.execute(
            select(func.count(Area.id)).where(and_(*base_filter))
        )
        total = total_result.scalar() or 0

        # Por tipo
        by_type: Dict[str, int] = {}
        for area_type in AreaType:
            type_result = await self.db.execute(
                select(func.count(Area.id)).where(
                    and_(*base_filter, Area.area_type == area_type.value)
                )
            )
            count = type_result.scalar() or 0
            if count > 0:
                by_type[area_type.value] = count

        # Por status
        by_status: Dict[str, int] = {}
        for status in AreaStatus:
            status_result = await self.db.execute(
                select(func.count(Area.id)).where(
                    and_(*base_filter, Area.status == status.value)
                )
            )
            count = status_result.scalar() or 0
            if count > 0:
                by_status[status.value] = count

        # Área total m²
        area_result = await self.db.execute(
            select(func.sum(Area.area_m2)).where(and_(*base_filter))
        )
        total_area_m2 = area_result.scalar() or 0.0

        # Capacidade total
        capacity_result = await self.db.execute(
            select(func.sum(Area.capacity)).where(and_(*base_filter))
        )
        total_capacity = capacity_result.scalar() or 0

        # Precisando de inspeção
        needing_inspection_result = await self.db.execute(
            select(func.count(Area.id)).where(
                and_(
                    *base_filter,
                    or_(
                        Area.next_inspection_date.is_(None),
                        Area.next_inspection_date <= datetime.now(),
                    ),
                )
            )
        )
        needing_inspection = needing_inspection_result.scalar() or 0

        # Rentáveis
        rentable_result = await self.db.execute(
            select(func.count(Area.id)).where(
                and_(*base_filter, Area.is_rentable.is_(True))
            )
        )
        rentable_count = rentable_result.scalar() or 0

        return AreaStats(
            total=total,
            by_type=by_type,
            by_status=by_status,
            total_area_m2=float(total_area_m2),
            total_capacity=int(total_capacity),
            needing_inspection=needing_inspection,
            with_pending_maintenance=0,  # Calculado via join com maintenances
            rentable_count=rentable_count,
        )
