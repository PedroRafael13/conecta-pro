"""Service para EquipmentMaintenance."""

import logging
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.equipment_management.models.maintenance import (
    MaintenancePriority,
    MaintenanceStatus,
    MaintenanceType,
)
from modules.equipment_management.repositories.equipment_repository import (
    EquipmentRepository,
)
from modules.equipment_management.repositories.maintenance_repository import (
    MaintenanceRepository,
)
from modules.equipment_management.schemas.maintenance import (
    MaintenanceCreate,
    MaintenanceFilter,
    MaintenanceListResponse,
    MaintenanceResponse,
    MaintenanceStats,
    MaintenanceUpdate,
)

logger = logging.getLogger(__name__)


class MaintenanceService:
    """Service para operações de EquipmentMaintenance."""

    def __init__(self, session: AsyncSession):
        """Inicializa o service."""
        self.session = session
        self.repository = MaintenanceRepository(session)
        self.equipment_repository = EquipmentRepository(session)

    async def create(self, data: MaintenanceCreate) -> MaintenanceResponse:
        """Cria uma nova manutenção."""
        # Verificar se equipamento existe
        equipment = await self.equipment_repository.get_by_id(data.equipment_id)
        if not equipment:
            raise ValueError(f"Equipamento não encontrado: {data.equipment_id}")

        maintenance = await self.repository.create(data)
        await self.session.commit()
        return MaintenanceResponse.model_validate(maintenance)

    async def get_by_id(
        self, maintenance_id: str | UUID
    ) -> Optional[MaintenanceResponse]:
        """Busca manutenção por ID."""
        maintenance = await self.repository.get_by_id(maintenance_id)
        if not maintenance:
            return None
        return MaintenanceResponse.model_validate(maintenance)

    async def get_by_code(self, code: str) -> Optional[MaintenanceResponse]:
        """Busca manutenção por código."""
        maintenance = await self.repository.get_by_code(code)
        if not maintenance:
            return None
        return MaintenanceResponse.model_validate(maintenance)

    async def update(
        self, maintenance_id: str | UUID, data: MaintenanceUpdate
    ) -> Optional[MaintenanceResponse]:
        """Atualiza uma manutenção."""
        maintenance = await self.repository.update(maintenance_id, data)
        if not maintenance:
            return None
        await self.session.commit()
        return MaintenanceResponse.model_validate(maintenance)

    async def delete(self, maintenance_id: str | UUID) -> bool:
        """Remove uma manutenção (soft delete)."""
        result = await self.repository.delete(maintenance_id)
        if result:
            await self.session.commit()
        return result

    async def list_with_filters(
        self,
        filters: Optional[MaintenanceFilter] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> MaintenanceListResponse:
        """Lista manutenções com filtros."""
        items, total = await self.repository.list_with_filters(
            filters=filters, page=page, page_size=page_size
        )

        total_pages = (total + page_size - 1) // page_size

        return MaintenanceListResponse(
            items=[MaintenanceResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def get_by_equipment(self, equipment_id: str) -> list[MaintenanceResponse]:
        """Lista manutenções de um equipamento."""
        items = await self.repository.get_by_equipment(equipment_id)
        return [MaintenanceResponse.model_validate(item) for item in items]

    async def get_by_client(self, client_id: str) -> list[MaintenanceResponse]:
        """Lista manutenções de um cliente."""
        items = await self.repository.get_by_client(client_id)
        return [MaintenanceResponse.model_validate(item) for item in items]

    async def get_by_technician(
        self, technician_id: str, include_completed: bool = False
    ) -> list[MaintenanceResponse]:
        """Lista manutenções de um técnico."""
        items = await self.repository.get_by_technician(
            technician_id, include_completed
        )
        return [MaintenanceResponse.model_validate(item) for item in items]

    async def get_scheduled_for_date(
        self, date: datetime
    ) -> list[MaintenanceResponse]:
        """Lista manutenções agendadas para uma data."""
        items = await self.repository.get_scheduled_for_date(date)
        return [MaintenanceResponse.model_validate(item) for item in items]

    async def get_overdue(self) -> list[MaintenanceResponse]:
        """Lista manutenções atrasadas."""
        items = await self.repository.get_overdue()
        return [MaintenanceResponse.model_validate(item) for item in items]

    async def get_waiting_parts(self) -> list[MaintenanceResponse]:
        """Lista manutenções aguardando peças."""
        items = await self.repository.get_waiting_parts()
        return [MaintenanceResponse.model_validate(item) for item in items]

    async def get_needing_followup(self) -> list[MaintenanceResponse]:
        """Lista manutenções que precisam de follow-up."""
        items = await self.repository.get_needing_followup()
        return [MaintenanceResponse.model_validate(item) for item in items]

    async def start(
        self, maintenance_id: str | UUID
    ) -> Optional[MaintenanceResponse]:
        """Inicia uma manutenção e atualiza status do equipamento."""
        maintenance = await self.repository.get_by_id(maintenance_id)
        if not maintenance:
            return None

        # Atualizar status do equipamento para manutenção
        equipment = await self.equipment_repository.get_by_id(
            maintenance.equipment_id
        )
        if equipment:
            equipment.send_to_maintenance()

        maintenance = await self.repository.start(maintenance_id)
        await self.session.commit()
        return MaintenanceResponse.model_validate(maintenance)

    async def complete(
        self,
        maintenance_id: str | UUID,
        problem_resolved: bool = True,
        equipment_status_after: Optional[str] = None,
    ) -> Optional[MaintenanceResponse]:
        """Conclui uma manutenção e atualiza equipamento."""
        maintenance = await self.repository.get_by_id(maintenance_id)
        if not maintenance:
            return None

        # Retornar equipamento da manutenção
        equipment = await self.equipment_repository.get_by_id(
            maintenance.equipment_id
        )
        if equipment:
            equipment.return_from_maintenance()
            if maintenance.next_maintenance_date:
                equipment.next_maintenance_at = maintenance.next_maintenance_date
            equipment.last_maintenance_at = datetime.utcnow()
            equipment.total_maintenances = (equipment.total_maintenances or 0) + 1

        maintenance = await self.repository.complete(
            maintenance_id, problem_resolved, equipment_status_after
        )

        # Se é recorrente, criar próxima manutenção
        if maintenance.is_recurring:
            await self.repository.create_recurring(maintenance_id)

        await self.session.commit()
        return MaintenanceResponse.model_validate(maintenance)

    async def cancel(
        self, maintenance_id: str | UUID
    ) -> Optional[MaintenanceResponse]:
        """Cancela uma manutenção."""
        maintenance = await self.repository.get_by_id(maintenance_id)
        if not maintenance:
            return None

        # Se equipamento estava em manutenção, retornar
        if maintenance.status == MaintenanceStatus.IN_PROGRESS:
            equipment = await self.equipment_repository.get_by_id(
                maintenance.equipment_id
            )
            if equipment:
                equipment.return_from_maintenance()

        maintenance = await self.repository.cancel(maintenance_id)
        await self.session.commit()
        return MaintenanceResponse.model_validate(maintenance)

    async def mark_waiting_parts(
        self, maintenance_id: str | UUID, parts_requested: list
    ) -> Optional[MaintenanceResponse]:
        """Marca como aguardando peças."""
        maintenance = await self.repository.mark_waiting_parts(
            maintenance_id, parts_requested
        )
        if not maintenance:
            return None
        await self.session.commit()
        return MaintenanceResponse.model_validate(maintenance)

    async def add_part_replaced(
        self,
        maintenance_id: str | UUID,
        part_name: str,
        part_code: Optional[str] = None,
        quantity: int = 1,
        unit_cost: float = 0.0,
    ) -> Optional[MaintenanceResponse]:
        """Adiciona peça substituída."""
        maintenance = await self.repository.add_part_replaced(
            maintenance_id, part_name, part_code, quantity, unit_cost
        )
        if not maintenance:
            return None
        await self.session.commit()
        return MaintenanceResponse.model_validate(maintenance)

    async def sign_by_client(
        self, maintenance_id: str | UUID, signed_by: str, signature: str
    ) -> Optional[MaintenanceResponse]:
        """Registra assinatura do cliente."""
        maintenance = await self.repository.sign_by_client(
            maintenance_id, signed_by, signature
        )
        if not maintenance:
            return None
        await self.session.commit()
        return MaintenanceResponse.model_validate(maintenance)

    async def get_stats(
        self,
        client_id: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> MaintenanceStats:
        """Obtém estatísticas de manutenções."""
        return await self.repository.get_stats(client_id, date_from, date_to)

    async def assign_technician(
        self,
        maintenance_id: str | UUID,
        technician_id: str,
        technician_name: str,
    ) -> Optional[MaintenanceResponse]:
        """Atribui técnico à manutenção."""
        update_data = MaintenanceUpdate(
            technician_id=technician_id,
            technician_name=technician_name,
        )
        maintenance = await self.repository.update(maintenance_id, update_data)
        if not maintenance:
            return None
        await self.session.commit()
        return MaintenanceResponse.model_validate(maintenance)

    async def schedule_preventive(
        self, equipment_id: str, interval_days: int, checklist_template_id: Optional[str] = None
    ) -> Optional[MaintenanceResponse]:
        """Agenda manutenção preventiva para equipamento."""
        equipment = await self.equipment_repository.get_by_id(equipment_id)
        if not equipment:
            return None

        # Criar manutenção preventiva
        data = MaintenanceCreate(
            maintenance_type=MaintenanceType.PREVENTIVA,
            priority=MaintenancePriority.MEDIUM,
            equipment_id=str(equipment.id),
            equipment_code=equipment.equipment_code,
            equipment_name=equipment.name,
            equipment_type=equipment.equipment_type.value,
            serial_number=equipment.serial_number,
            client_id=equipment.client_id,
            client_name=equipment.client_name,
            contract_id=equipment.contract_id,
            title=f"Manutenção Preventiva - {equipment.name}",
            description="Manutenção preventiva programada",
            scheduled_date=datetime.utcnow() + timedelta(days=interval_days),
            checklist_template_id=checklist_template_id,
            is_recurring=True,
            recurrence_interval_days=interval_days,
        )

        maintenance = await self.repository.create(data)
        await self.session.commit()
        return MaintenanceResponse.model_validate(maintenance)

    async def get_equipment_maintenance_history(
        self, equipment_id: str, limit: int = 10
    ) -> list[MaintenanceResponse]:
        """Obtém histórico de manutenções de um equipamento."""
        items = await self.repository.get_by_equipment(equipment_id)
        return [MaintenanceResponse.model_validate(item) for item in items[:limit]]
