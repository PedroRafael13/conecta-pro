"""Service para EquipmentInstallation."""

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.equipment_management.repositories.equipment_repository import (
    EquipmentRepository,
)
from modules.equipment_management.repositories.installation_repository import (
    InstallationRepository,
)
from modules.equipment_management.schemas.installation import (
    InstallationCreate,
    InstallationFilter,
    InstallationListResponse,
    InstallationResponse,
    InstallationUpdate,
)

logger = logging.getLogger(__name__)


class InstallationService:
    """Service para operações de EquipmentInstallation."""

    def __init__(self, session: AsyncSession):
        """Inicializa o service."""
        self.session = session
        self.repository = InstallationRepository(session)
        self.equipment_repository = EquipmentRepository(session)

    async def create(self, data: InstallationCreate) -> InstallationResponse:
        """Cria uma nova instalação."""
        # Verificar se equipamentos existem e estão disponíveis
        for eq_id in data.equipment_ids:
            equipment = await self.equipment_repository.get_by_id(eq_id)
            if not equipment:
                raise ValueError(f"Equipamento não encontrado: {eq_id}")
            if equipment.status.value != "estoque":
                raise ValueError(f"Equipamento {equipment.equipment_code} não está disponível para instalação")

        installation = await self.repository.create(data)
        await self.session.commit()
        return InstallationResponse.model_validate(installation)

    async def get_by_id(self, installation_id: str | UUID) -> InstallationResponse | None:
        """Busca instalação por ID."""
        installation = await self.repository.get_by_id(installation_id)
        if not installation:
            return None
        return InstallationResponse.model_validate(installation)

    async def get_by_code(self, code: str) -> InstallationResponse | None:
        """Busca instalação por código."""
        installation = await self.repository.get_by_code(code)
        if not installation:
            return None
        return InstallationResponse.model_validate(installation)

    async def update(self, installation_id: str | UUID, data: InstallationUpdate) -> InstallationResponse | None:
        """Atualiza uma instalação."""
        installation = await self.repository.update(installation_id, data)
        if not installation:
            return None
        await self.session.commit()
        return InstallationResponse.model_validate(installation)

    async def delete(self, installation_id: str | UUID) -> bool:
        """Remove uma instalação (soft delete)."""
        result = await self.repository.delete(installation_id)
        if result:
            await self.session.commit()
        return result

    async def list_with_filters(
        self,
        filters: InstallationFilter | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> InstallationListResponse:
        """Lista instalações com filtros."""
        items, total = await self.repository.list_with_filters(filters=filters, page=page, page_size=page_size)

        total_pages = (total + page_size - 1) // page_size

        return InstallationListResponse(
            items=[InstallationResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def get_by_client(self, client_id: str) -> list[InstallationResponse]:
        """Lista instalações de um cliente."""
        items = await self.repository.get_by_client(client_id)
        return [InstallationResponse.model_validate(item) for item in items]

    async def get_by_technician(
        self, technician_id: str, include_completed: bool = False
    ) -> list[InstallationResponse]:
        """Lista instalações de um técnico."""
        items = await self.repository.get_by_technician(technician_id, include_completed)
        return [InstallationResponse.model_validate(item) for item in items]

    async def get_scheduled_for_date(self, date: datetime) -> list[InstallationResponse]:
        """Lista instalações agendadas para uma data."""
        items = await self.repository.get_scheduled_for_date(date)
        return [InstallationResponse.model_validate(item) for item in items]

    async def get_overdue(self) -> list[InstallationResponse]:
        """Lista instalações atrasadas."""
        items = await self.repository.get_overdue()
        return [InstallationResponse.model_validate(item) for item in items]

    async def get_pending_acceptance(self) -> list[InstallationResponse]:
        """Lista instalações aguardando aceite."""
        items = await self.repository.get_pending_acceptance()
        return [InstallationResponse.model_validate(item) for item in items]

    async def start(self, installation_id: str | UUID) -> InstallationResponse | None:
        """Inicia uma instalação."""
        installation = await self.repository.start(installation_id)
        if not installation:
            return None
        await self.session.commit()
        return InstallationResponse.model_validate(installation)

    async def complete(
        self,
        installation_id: str | UUID,
        technical_report: str | None = None,
    ) -> InstallationResponse | None:
        """Conclui uma instalação e atualiza equipamentos."""
        installation = await self.repository.get_by_id(installation_id)
        if not installation:
            return None

        # Marcar equipamentos como instalados
        for eq_id in installation.equipment_ids:
            await self.equipment_repository.install(
                equipment_id=eq_id,
                client_id=installation.client_id,
                client_name=installation.client_name,
                contract_id=installation.contract_id,
                installation_id=str(installation.id),
                location=installation.address,
                latitude=installation.gps_latitude,
                longitude=installation.gps_longitude,
            )

        # Concluir instalação
        installation = await self.repository.complete(installation_id, technical_report)
        await self.session.commit()
        return InstallationResponse.model_validate(installation)

    async def cancel(self, installation_id: str | UUID, reason: str) -> InstallationResponse | None:
        """Cancela uma instalação."""
        installation = await self.repository.cancel(installation_id, reason)
        if not installation:
            return None
        await self.session.commit()
        return InstallationResponse.model_validate(installation)

    async def reschedule(
        self,
        installation_id: str | UUID,
        new_date: datetime,
        reason: str | None = None,
    ) -> InstallationResponse | None:
        """Reagenda uma instalação."""
        installation = await self.repository.reschedule(installation_id, new_date, reason)
        if not installation:
            return None
        await self.session.commit()
        return InstallationResponse.model_validate(installation)

    async def accept_by_client(self, installation_id: str | UUID, accepted_by: str) -> InstallationResponse | None:
        """Registra aceite do cliente."""
        installation = await self.repository.accept_by_client(installation_id, accepted_by)
        if not installation:
            return None
        await self.session.commit()
        return InstallationResponse.model_validate(installation)

    async def add_photo(
        self,
        installation_id: str | UUID,
        photo_url: str,
        photo_type: str = "after",
    ) -> InstallationResponse | None:
        """Adiciona foto à instalação."""
        installation = await self.repository.add_photo(installation_id, photo_url, photo_type)
        if not installation:
            return None
        await self.session.commit()
        return InstallationResponse.model_validate(installation)

    async def get_stats_by_period(self, date_from: datetime, date_to: datetime) -> dict:
        """Estatísticas de instalações por período."""
        return await self.repository.get_stats_by_period(date_from, date_to)

    async def assign_technician(
        self,
        installation_id: str | UUID,
        technician_id: str,
        technician_name: str,
    ) -> InstallationResponse | None:
        """Atribui técnico à instalação."""
        update_data = InstallationUpdate(
            technician_id=technician_id,
            technician_name=technician_name,
        )
        installation = await self.repository.update(installation_id, update_data)
        if not installation:
            return None
        await self.session.commit()
        return InstallationResponse.model_validate(installation)

    async def get_technician_schedule(self, technician_id: str, date: datetime) -> list[InstallationResponse]:
        """Obtém agenda do técnico para uma data."""
        all_installations = await self.repository.get_scheduled_for_date(date)
        technician_installations = [inst for inst in all_installations if inst.technician_id == technician_id]
        return [InstallationResponse.model_validate(item) for item in technician_installations]
