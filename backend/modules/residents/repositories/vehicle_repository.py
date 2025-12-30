"""Repository para ResidentVehicle."""

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.residents.models.vehicle import ResidentVehicle, VehicleStatus, VehicleType
from modules.residents.schemas.vehicle import VehicleCreate, VehicleFilter, VehicleUpdate

logger = logging.getLogger(__name__)


class VehicleRepository:
    """Repository para operações de ResidentVehicle."""

    def __init__(self, session: AsyncSession):
        """Inicializa o repository."""
        self.session = session

    async def create(self, data: VehicleCreate) -> ResidentVehicle:
        """Cria um novo veículo."""
        vehicle = ResidentVehicle(**data.model_dump(exclude_unset=True))
        self.session.add(vehicle)
        await self.session.flush()
        return vehicle

    async def get_by_id(self, vehicle_id: str | UUID) -> Optional[ResidentVehicle]:
        """Busca por ID."""
        query = select(ResidentVehicle).where(
            and_(ResidentVehicle.id == vehicle_id, ResidentVehicle.deleted_at.is_(None))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_plate(self, plate: str) -> Optional[ResidentVehicle]:
        """Busca por placa."""
        normalized_plate = plate.upper().replace("-", "").replace(" ", "")
        query = select(ResidentVehicle).where(
            and_(
                ResidentVehicle.plate == normalized_plate,
                ResidentVehicle.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_rfid(self, rfid_tag: str) -> Optional[ResidentVehicle]:
        """Busca por tag RFID."""
        query = select(ResidentVehicle).where(
            and_(
                ResidentVehicle.rfid_tag == rfid_tag,
                ResidentVehicle.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_resident(
        self, resident_id: str | UUID, include_inactive: bool = False
    ) -> list[ResidentVehicle]:
        """Busca veículos do morador."""
        query = select(ResidentVehicle).where(
            and_(
                ResidentVehicle.resident_id == resident_id,
                ResidentVehicle.deleted_at.is_(None),
            )
        )
        if not include_inactive:
            query = query.where(ResidentVehicle.status == VehicleStatus.ATIVO)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_parking_spot(
        self, condominium_id: str, parking_spot: str
    ) -> Optional[ResidentVehicle]:
        """Busca veículo pela vaga."""
        query = select(ResidentVehicle).where(
            and_(
                ResidentVehicle.condominium_id == condominium_id,
                ResidentVehicle.parking_spot == parking_spot,
                ResidentVehicle.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update(
        self, vehicle_id: str | UUID, data: VehicleUpdate
    ) -> Optional[ResidentVehicle]:
        """Atualiza um veículo."""
        vehicle = await self.get_by_id(vehicle_id)
        if not vehicle:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(vehicle, field, value)

        await self.session.flush()
        return vehicle

    async def soft_delete(self, vehicle_id: str | UUID) -> bool:
        """Soft delete de veículo."""
        vehicle = await self.get_by_id(vehicle_id)
        if not vehicle:
            return False

        vehicle.deleted_at = datetime.utcnow()
        vehicle.status = VehicleStatus.INATIVO
        await self.session.flush()
        return True

    async def list_with_filters(
        self,
        filters: Optional[VehicleFilter] = None,
        skip: int = 0,
        limit: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> tuple[list[ResidentVehicle], int]:
        """Lista veículos com filtros."""
        query = select(ResidentVehicle).where(ResidentVehicle.deleted_at.is_(None))

        if filters:
            if filters.resident_id:
                query = query.where(ResidentVehicle.resident_id == filters.resident_id)
            if filters.vehicle_type:
                query = query.where(ResidentVehicle.vehicle_type == filters.vehicle_type)
            if filters.status:
                query = query.where(ResidentVehicle.status == filters.status)
            if filters.brand:
                query = query.where(ResidentVehicle.brand.ilike(f"%{filters.brand}%"))
            if filters.model:
                query = query.where(ResidentVehicle.model.ilike(f"%{filters.model}%"))
            if filters.color:
                query = query.where(ResidentVehicle.color.ilike(f"%{filters.color}%"))
            if filters.plate:
                normalized = filters.plate.upper().replace("-", "").replace(" ", "")
                query = query.where(ResidentVehicle.plate.ilike(f"%{normalized}%"))
            if filters.is_blocked is not None:
                query = query.where(ResidentVehicle.is_blocked == filters.is_blocked)
            if filters.has_rfid is not None:
                if filters.has_rfid:
                    query = query.where(ResidentVehicle.rfid_tag.isnot(None))
                else:
                    query = query.where(ResidentVehicle.rfid_tag.is_(None))
            if filters.condominium_id:
                query = query.where(
                    ResidentVehicle.condominium_id == filters.condominium_id
                )

        # Contagem
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        # Ordenação
        order_column = getattr(ResidentVehicle, order_by, ResidentVehicle.created_at)
        if order_desc:
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)

        return list(result.scalars().all()), total

    async def search(
        self, query_str: str, condominium_id: str = None, limit: int = 10
    ) -> list[ResidentVehicle]:
        """Busca veículos."""
        query = select(ResidentVehicle).where(ResidentVehicle.deleted_at.is_(None))
        query = query.where(
            ResidentVehicle.plate.ilike(f"%{query_str}%")
            | ResidentVehicle.brand.ilike(f"%{query_str}%")
            | ResidentVehicle.model.ilike(f"%{query_str}%")
            | ResidentVehicle.color.ilike(f"%{query_str}%")
            | ResidentVehicle.rfid_tag.ilike(f"%{query_str}%")
        )

        if condominium_id:
            query = query.where(ResidentVehicle.condominium_id == condominium_id)

        query = query.limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_blocked(
        self, condominium_id: str = None, skip: int = 0, limit: int = 20
    ) -> list[ResidentVehicle]:
        """Lista veículos bloqueados."""
        query = select(ResidentVehicle).where(
            and_(
                ResidentVehicle.is_blocked.is_(True),
                ResidentVehicle.deleted_at.is_(None),
            )
        )
        if condominium_id:
            query = query.where(ResidentVehicle.condominium_id == condominium_id)
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_without_parking(
        self, condominium_id: str, skip: int = 0, limit: int = 20
    ) -> list[ResidentVehicle]:
        """Lista veículos sem vaga."""
        query = select(ResidentVehicle).where(
            and_(
                ResidentVehicle.condominium_id == condominium_id,
                ResidentVehicle.parking_spot.is_(None),
                ResidentVehicle.status == VehicleStatus.ATIVO,
                ResidentVehicle.deleted_at.is_(None),
            )
        )
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def block(
        self, vehicle_id: str | UUID, reason: str, blocked_by: str
    ) -> Optional[ResidentVehicle]:
        """Bloqueia veículo."""
        vehicle = await self.get_by_id(vehicle_id)
        if not vehicle:
            return None
        vehicle.block(reason, blocked_by)
        await self.session.flush()
        return vehicle

    async def unblock(self, vehicle_id: str | UUID) -> Optional[ResidentVehicle]:
        """Desbloqueia veículo."""
        vehicle = await self.get_by_id(vehicle_id)
        if not vehicle:
            return None
        vehicle.unblock()
        await self.session.flush()
        return vehicle

    async def assign_parking(
        self, vehicle_id: str | UUID, parking_spot: str
    ) -> Optional[ResidentVehicle]:
        """Atribui vaga."""
        vehicle = await self.get_by_id(vehicle_id)
        if not vehicle:
            return None
        vehicle.assign_parking_spot(parking_spot)
        await self.session.flush()
        return vehicle

    async def remove_parking(self, vehicle_id: str | UUID) -> Optional[ResidentVehicle]:
        """Remove vaga."""
        vehicle = await self.get_by_id(vehicle_id)
        if not vehicle:
            return None
        vehicle.remove_parking_spot()
        await self.session.flush()
        return vehicle

    async def mark_as_sold(self, vehicle_id: str | UUID) -> Optional[ResidentVehicle]:
        """Marca como vendido."""
        vehicle = await self.get_by_id(vehicle_id)
        if not vehicle:
            return None
        vehicle.mark_as_sold()
        await self.session.flush()
        return vehicle

    async def mark_as_stolen(
        self, vehicle_id: str | UUID, report_number: str = None
    ) -> Optional[ResidentVehicle]:
        """Marca como roubado."""
        vehicle = await self.get_by_id(vehicle_id)
        if not vehicle:
            return None
        vehicle.mark_as_stolen(report_number)
        await self.session.flush()
        return vehicle

    async def get_stats(self, condominium_id: str = None) -> dict:
        """Retorna estatísticas."""
        base_query = select(ResidentVehicle).where(
            ResidentVehicle.deleted_at.is_(None)
        )
        if condominium_id:
            base_query = base_query.where(
                ResidentVehicle.condominium_id == condominium_id
            )

        result = await self.session.execute(base_query)
        vehicles = list(result.scalars().all())

        stats = {
            "total": len(vehicles),
            "active": sum(1 for v in vehicles if v.status == VehicleStatus.ATIVO),
            "inactive": sum(1 for v in vehicles if v.status == VehicleStatus.INATIVO),
            "blocked": sum(1 for v in vehicles if v.is_blocked),
            "sold": sum(1 for v in vehicles if v.status == VehicleStatus.VENDIDO),
            "stolen": sum(1 for v in vehicles if v.status == VehicleStatus.ROUBADO),
            "by_type": {},
            "by_status": {},
            "with_rfid": sum(1 for v in vehicles if v.rfid_tag),
            "with_parking": sum(1 for v in vehicles if v.parking_spot),
            "without_parking": sum(
                1
                for v in vehicles
                if not v.parking_spot and v.status == VehicleStatus.ATIVO
            ),
        }

        for v in vehicles:
            stats["by_type"][v.vehicle_type.value] = (
                stats["by_type"].get(v.vehicle_type.value, 0) + 1
            )
            stats["by_status"][v.status.value] = (
                stats["by_status"].get(v.status.value, 0) + 1
            )

        return stats
