"""Service para Equipment."""

import base64
import json
import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from modules.equipment_management.repositories.equipment_repository import (
    EquipmentRepository,
)
from modules.equipment_management.schemas.equipment import (
    EquipmentCreate,
    EquipmentFilter,
    EquipmentListResponse,
    EquipmentResponse,
    EquipmentStats,
    EquipmentUpdate,
)

logger = logging.getLogger(__name__)


class EquipmentService:
    """Service para operações de Equipment."""

    def __init__(self, session: AsyncSession):
        """Inicializa o service."""
        self.session = session
        self.repository = EquipmentRepository(session)

    async def create(self, data: EquipmentCreate) -> EquipmentResponse:
        """Cria um novo equipamento."""
        # Verificar se serial já existe
        if data.serial_number:
            existing = await self.repository.get_by_serial_number(data.serial_number)
            if existing:
                raise ValueError(
                    f"Já existe equipamento com número de série: {data.serial_number}"
                )

        equipment = await self.repository.create(data)
        await self.session.commit()
        return EquipmentResponse.model_validate(equipment)

    async def get_by_id(self, equipment_id: str | UUID) -> Optional[EquipmentResponse]:
        """Busca equipamento por ID."""
        equipment = await self.repository.get_by_id(equipment_id)
        if not equipment:
            return None
        return EquipmentResponse.model_validate(equipment)

    async def get_by_code(self, code: str) -> Optional[EquipmentResponse]:
        """Busca equipamento por código."""
        equipment = await self.repository.get_by_code(code)
        if not equipment:
            return None
        return EquipmentResponse.model_validate(equipment)

    async def update(
        self, equipment_id: str | UUID, data: EquipmentUpdate
    ) -> Optional[EquipmentResponse]:
        """Atualiza um equipamento."""
        equipment = await self.repository.update(equipment_id, data)
        if not equipment:
            return None
        await self.session.commit()
        return EquipmentResponse.model_validate(equipment)

    async def delete(self, equipment_id: str | UUID) -> bool:
        """Remove um equipamento (soft delete)."""
        result = await self.repository.delete(equipment_id)
        if result:
            await self.session.commit()
        return result

    async def list_with_filters(
        self,
        filters: Optional[EquipmentFilter] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> EquipmentListResponse:
        """Lista equipamentos com filtros."""
        items, total = await self.repository.list_with_filters(
            filters=filters, page=page, page_size=page_size
        )

        total_pages = (total + page_size - 1) // page_size

        return EquipmentListResponse(
            items=[EquipmentResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def get_by_client(self, client_id: str) -> list[EquipmentResponse]:
        """Lista equipamentos de um cliente."""
        items = await self.repository.get_by_client(client_id)
        return [EquipmentResponse.model_validate(item) for item in items]

    async def get_by_contract(self, contract_id: str) -> list[EquipmentResponse]:
        """Lista equipamentos de um contrato."""
        items = await self.repository.get_by_contract(contract_id)
        return [EquipmentResponse.model_validate(item) for item in items]

    async def get_in_stock(self) -> list[EquipmentResponse]:
        """Lista equipamentos em estoque."""
        items = await self.repository.get_in_stock()
        return [EquipmentResponse.model_validate(item) for item in items]

    async def get_needing_maintenance(self) -> list[EquipmentResponse]:
        """Lista equipamentos que precisam de manutenção."""
        items = await self.repository.get_needing_maintenance()
        return [EquipmentResponse.model_validate(item) for item in items]

    async def get_offline(self) -> list[EquipmentResponse]:
        """Lista equipamentos offline."""
        items = await self.repository.get_offline()
        return [EquipmentResponse.model_validate(item) for item in items]

    async def get_expiring_warranty(self, days: int = 30) -> list[EquipmentResponse]:
        """Lista equipamentos com garantia expirando."""
        items = await self.repository.get_expiring_warranty(days)
        return [EquipmentResponse.model_validate(item) for item in items]

    async def get_stats(self, client_id: Optional[str] = None) -> EquipmentStats:
        """Obtém estatísticas de equipamentos."""
        return await self.repository.get_stats(client_id)

    async def install(
        self,
        equipment_id: str | UUID,
        client_id: str,
        client_name: str,
        contract_id: Optional[str] = None,
        installation_id: Optional[str] = None,
        location: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Optional[EquipmentResponse]:
        """Registra instalação de equipamento."""
        equipment = await self.repository.install(
            equipment_id=equipment_id,
            client_id=client_id,
            client_name=client_name,
            contract_id=contract_id,
            installation_id=installation_id,
            location=location,
            latitude=latitude,
            longitude=longitude,
        )
        if not equipment:
            return None
        await self.session.commit()
        return EquipmentResponse.model_validate(equipment)

    async def uninstall(self, equipment_id: str | UUID) -> Optional[EquipmentResponse]:
        """Desinstala equipamento."""
        equipment = await self.repository.uninstall(equipment_id)
        if not equipment:
            return None
        await self.session.commit()
        return EquipmentResponse.model_validate(equipment)

    async def update_online_status(
        self, equipment_id: str | UUID, is_online: bool
    ) -> Optional[EquipmentResponse]:
        """Atualiza status online/offline."""
        equipment = await self.repository.update_online_status(equipment_id, is_online)
        if not equipment:
            return None
        await self.session.commit()
        return EquipmentResponse.model_validate(equipment)

    async def bulk_update_online_status(
        self, equipment_ids: list[str], is_online: bool
    ) -> dict:
        """Atualiza status online/offline em massa."""
        count = await self.repository.bulk_update_online_status(equipment_ids, is_online)
        await self.session.commit()
        return {"updated": count, "total": len(equipment_ids)}

    async def generate_qr_code(self, equipment_id: str | UUID) -> Optional[str]:
        """Gera QR Code para equipamento."""
        equipment = await self.repository.get_by_id(equipment_id)
        if not equipment:
            return None

        # QR Code contém o código do equipamento
        qr_data = {
            "type": "equipment",
            "code": equipment.equipment_code,
            "id": str(equipment.id),
        }

        # Aqui seria gerado o QR Code real
        # Por enquanto retorna URL simulada
        encoded = base64.b64encode(json.dumps(qr_data).encode()).decode()
        qr_url = f"/api/v1/equipment/qr/{encoded}"

        # Atualizar equipamento com URL
        equipment.qr_code_url = qr_url
        await self.session.commit()

        return qr_url

    async def calculate_depreciation(
        self, equipment_id: str | UUID
    ) -> Optional[dict]:
        """Calcula depreciação atual do equipamento."""
        equipment = await self.repository.get_by_id(equipment_id)
        if not equipment:
            return None

        return {
            "equipment_id": str(equipment.id),
            "equipment_code": equipment.equipment_code,
            "purchase_value": equipment.purchase_value,
            "depreciation_rate": equipment.depreciation_rate,
            "current_value": equipment.current_value,
            "useful_life_months": equipment.useful_life_months,
            "age_months": equipment.age_months if hasattr(equipment, "age_months") else None,
        }
