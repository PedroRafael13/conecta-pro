"""Service para ResidentVehicle."""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.residents.repositories.vehicle_repository import VehicleRepository
from modules.residents.schemas.vehicle import (
    VehicleCreate,
    VehicleUpdate,
    VehicleFilter,
    VehicleResponse,
    VehicleListResponse,
    VehicleStats,
)

logger = logging.getLogger(__name__)


class VehicleService:
    """Service para operações de ResidentVehicle."""

    def __init__(self, session: AsyncSession):
        """Inicializa o service."""
        self.session = session
        self.repository = VehicleRepository(session)

    async def create(self, data: VehicleCreate) -> VehicleResponse:
        """Cria um novo veículo."""
        # Verifica placa duplicada
        if data.plate:
            existing = await self.repository.get_by_plate(data.plate)
            if existing:
                raise ValueError(f"Já existe veículo com placa: {data.plate}")

        # Verifica RFID duplicado
        if data.rfid_tag:
            existing = await self.repository.get_by_rfid(data.rfid_tag)
            if existing:
                raise ValueError(f"Já existe veículo com RFID: {data.rfid_tag}")

        vehicle = await self.repository.create(data)
        await self.session.commit()
        logger.info("Veículo criado: {vehicle.id} - {vehicle.plate}")
        return VehicleResponse.model_validate(vehicle)

    async def get_by_id(self, vehicle_id: str | UUID) -> Optional[VehicleResponse]:
        """Busca veículo por ID."""
        vehicle = await self.repository.get_by_id(vehicle_id)
        if not vehicle:
            return None
        return VehicleResponse.model_validate(vehicle)

    async def get_by_plate(self, plate: str) -> Optional[VehicleResponse]:
        """Busca veículo por placa."""
        vehicle = await self.repository.get_by_plate(plate)
        if not vehicle:
            return None
        return VehicleResponse.model_validate(vehicle)

    async def get_by_rfid(self, rfid_tag: str) -> Optional[VehicleResponse]:
        """Busca veículo por RFID."""
        vehicle = await self.repository.get_by_rfid(rfid_tag)
        if not vehicle:
            return None
        return VehicleResponse.model_validate(vehicle)

    async def get_by_resident(
        self, resident_id: str | UUID, include_inactive: bool = False
    ) -> list[VehicleResponse]:
        """Busca veículos do morador."""
        vehicles = await self.repository.get_by_resident(resident_id, include_inactive)
        return [VehicleResponse.model_validate(v) for v in vehicles]

    async def update(
        self, vehicle_id: str | UUID, data: VehicleUpdate
    ) -> Optional[VehicleResponse]:
        """Atualiza um veículo."""
        # Verifica placa duplicada
        if data.plate:
            existing = await self.repository.get_by_plate(data.plate)
            if existing and str(existing.id) != str(vehicle_id):
                raise ValueError(f"Já existe veículo com placa: {data.plate}")

        # Verifica RFID duplicado
        if data.rfid_tag:
            existing = await self.repository.get_by_rfid(data.rfid_tag)
            if existing and str(existing.id) != str(vehicle_id):
                raise ValueError(f"Já existe veículo com RFID: {data.rfid_tag}")

        vehicle = await self.repository.update(vehicle_id, data)
        if not vehicle:
            return None
        await self.session.commit()
        logger.info("Veículo atualizado: {vehicle.id}")
        return VehicleResponse.model_validate(vehicle)

    async def delete(self, vehicle_id: str | UUID) -> bool:
        """Remove veículo (soft delete)."""
        result = await self.repository.soft_delete(vehicle_id)
        if result:
            await self.session.commit()
            logger.info("Veículo removido: {vehicle_id}")
        return result

    async def list(
        self,
        filters: Optional[VehicleFilter] = None,
        page: int = 1,
        page_size: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> VehicleListResponse:
        """Lista veículos com filtros e paginação."""
        skip = (page - 1) * page_size
        vehicles, total = await self.repository.list_with_filters(
            filters=filters,
            skip=skip,
            limit=page_size,
            order_by=order_by,
            order_desc=order_desc,
        )

        pages = (total + page_size - 1) // page_size if total > 0 else 0

        return VehicleListResponse(
            items=[VehicleResponse.model_validate(v) for v in vehicles],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    async def search(
        self, query: str, condominium_id: str = None, limit: int = 10
    ) -> list[VehicleResponse]:
        """Busca veículos."""
        vehicles = await self.repository.search(query, condominium_id, limit)
        return [VehicleResponse.model_validate(v) for v in vehicles]

    async def get_blocked(
        self, condominium_id: str = None, page: int = 1, page_size: int = 20
    ) -> list[VehicleResponse]:
        """Lista veículos bloqueados."""
        skip = (page - 1) * page_size
        vehicles = await self.repository.get_blocked(condominium_id, skip, page_size)
        return [VehicleResponse.model_validate(v) for v in vehicles]

    async def get_without_parking(
        self, condominium_id: str, page: int = 1, page_size: int = 20
    ) -> list[VehicleResponse]:
        """Lista veículos sem vaga."""
        skip = (page - 1) * page_size
        vehicles = await self.repository.get_without_parking(
            condominium_id, skip, page_size
        )
        return [VehicleResponse.model_validate(v) for v in vehicles]

    async def block(
        self, vehicle_id: str | UUID, reason: str, blocked_by: str
    ) -> Optional[VehicleResponse]:
        """Bloqueia veículo."""
        vehicle = await self.repository.block(vehicle_id, reason, blocked_by)
        if not vehicle:
            return None
        await self.session.commit()
        logger.info("Veículo bloqueado: {vehicle_id} - Motivo: {reason}")
        return VehicleResponse.model_validate(vehicle)

    async def unblock(self, vehicle_id: str | UUID) -> Optional[VehicleResponse]:
        """Desbloqueia veículo."""
        vehicle = await self.repository.unblock(vehicle_id)
        if not vehicle:
            return None
        await self.session.commit()
        logger.info("Veículo desbloqueado: {vehicle_id}")
        return VehicleResponse.model_validate(vehicle)

    async def assign_parking(
        self, vehicle_id: str | UUID, parking_spot: str
    ) -> Optional[VehicleResponse]:
        """Atribui vaga de estacionamento."""
        # Verifica se vaga já está ocupada
        vehicle = await self.repository.get_by_id(vehicle_id)
        if not vehicle:
            return None

        existing = await self.repository.get_by_parking_spot(
            vehicle.condominium_id, parking_spot
        )
        if existing and str(existing.id) != str(vehicle_id):
            raise ValueError(f"Vaga {parking_spot} já ocupada por outro veículo")

        vehicle = await self.repository.assign_parking(vehicle_id, parking_spot)
        if not vehicle:
            return None
        await self.session.commit()
        logger.info("Vaga atribuída: {vehicle_id} - Vaga: {parking_spot}")
        return VehicleResponse.model_validate(vehicle)

    async def remove_parking(self, vehicle_id: str | UUID) -> Optional[VehicleResponse]:
        """Remove vaga de estacionamento."""
        vehicle = await self.repository.remove_parking(vehicle_id)
        if not vehicle:
            return None
        await self.session.commit()
        logger.info("Vaga removida: {vehicle_id}")
        return VehicleResponse.model_validate(vehicle)

    async def mark_as_sold(self, vehicle_id: str | UUID) -> Optional[VehicleResponse]:
        """Marca veículo como vendido."""
        vehicle = await self.repository.mark_as_sold(vehicle_id)
        if not vehicle:
            return None
        await self.session.commit()
        logger.info("Veículo marcado como vendido: {vehicle_id}")
        return VehicleResponse.model_validate(vehicle)

    async def mark_as_stolen(
        self, vehicle_id: str | UUID, report_number: str = None
    ) -> Optional[VehicleResponse]:
        """Marca veículo como roubado."""
        vehicle = await self.repository.mark_as_stolen(vehicle_id, report_number)
        if not vehicle:
            return None
        await self.session.commit()
        logger.info("Veículo marcado como roubado: {vehicle_id} - BO: {report_number}")
        return VehicleResponse.model_validate(vehicle)

    async def get_stats(self, condominium_id: str = None) -> VehicleStats:
        """Retorna estatísticas."""
        stats = await self.repository.get_stats(condominium_id)
        return VehicleStats(**stats)

    async def validate_access(self, plate: str = None, rfid: str = None) -> dict:
        """Valida acesso de veículo por placa ou RFID."""
        vehicle = None

        if rfid:
            vehicle = await self.repository.get_by_rfid(rfid)
        elif plate:
            vehicle = await self.repository.get_by_plate(plate)

        if not vehicle:
            return {
                "allowed": False,
                "reason": "Veículo não encontrado",
                "vehicle": None,
            }

        if not vehicle.is_valid_for_access:
            reason = "Veículo bloqueado" if vehicle.is_blocked else "Veículo inativo"
            return {
                "allowed": False,
                "reason": reason,
                "vehicle": VehicleResponse.model_validate(vehicle),
            }

        return {
            "allowed": True,
            "reason": "Acesso permitido",
            "vehicle": VehicleResponse.model_validate(vehicle),
            "parking_spot": vehicle.parking_spot,
        }
