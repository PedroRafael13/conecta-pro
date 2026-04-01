"""Service para EquipmentComodato."""

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.equipment_management.models.equipment import EquipmentStatus
from modules.equipment_management.repositories.comodato_repository import (
    ComodatoRepository,
)
from modules.equipment_management.repositories.equipment_repository import (
    EquipmentRepository,
)
from modules.equipment_management.schemas.comodato import (
    ComodatoCreate,
    ComodatoFilter,
    ComodatoListResponse,
    ComodatoResponse,
    ComodatoUpdate,
)

logger = logging.getLogger(__name__)


class ComodatoService:
    """Service para operações de EquipmentComodato."""

    def __init__(self, session: AsyncSession):
        """Inicializa o service."""
        self.session = session
        self.repository = ComodatoRepository(session)
        self.equipment_repository = EquipmentRepository(session)

    async def create(self, data: ComodatoCreate) -> ComodatoResponse:
        """Cria um novo comodato."""
        # Verificar se equipamento existe e está disponível
        equipment = await self.equipment_repository.get_by_id(data.equipment_id)
        if not equipment:
            raise ValueError(f"Equipamento não encontrado: {data.equipment_id}")

        if equipment.status != EquipmentStatus.ESTOQUE:
            raise ValueError(f"Equipamento {equipment.equipment_code} não está disponível para comodato")

        # Verificar se já não existe comodato ativo para este equipamento
        existing = await self.repository.get_by_equipment(data.equipment_id)
        if existing:
            raise ValueError(f"Já existe comodato ativo para equipamento: {data.equipment_code}")

        comodato = await self.repository.create(data)
        await self.session.commit()
        return ComodatoResponse.model_validate(comodato)

    async def get_by_id(self, comodato_id: str | UUID) -> ComodatoResponse | None:
        """Busca comodato por ID."""
        comodato = await self.repository.get_by_id(comodato_id)
        if not comodato:
            return None
        return ComodatoResponse.model_validate(comodato)

    async def get_by_code(self, code: str) -> ComodatoResponse | None:
        """Busca comodato por código."""
        comodato = await self.repository.get_by_code(code)
        if not comodato:
            return None
        return ComodatoResponse.model_validate(comodato)

    async def update(self, comodato_id: str | UUID, data: ComodatoUpdate) -> ComodatoResponse | None:
        """Atualiza um comodato."""
        comodato = await self.repository.update(comodato_id, data)
        if not comodato:
            return None
        await self.session.commit()
        return ComodatoResponse.model_validate(comodato)

    async def delete(self, comodato_id: str | UUID) -> bool:
        """Remove um comodato (soft delete)."""
        result = await self.repository.delete(comodato_id)
        if result:
            await self.session.commit()
        return result

    async def list_with_filters(
        self,
        filters: ComodatoFilter | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ComodatoListResponse:
        """Lista comodatos com filtros."""
        items, total = await self.repository.list_with_filters(filters=filters, page=page, page_size=page_size)

        total_pages = (total + page_size - 1) // page_size

        return ComodatoListResponse(
            items=[ComodatoResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def get_by_client(self, client_id: str) -> list[ComodatoResponse]:
        """Lista comodatos de um cliente."""
        items = await self.repository.get_by_client(client_id)
        return [ComodatoResponse.model_validate(item) for item in items]

    async def get_active(self, client_id: str | None = None) -> list[ComodatoResponse]:
        """Lista comodatos ativos."""
        items = await self.repository.get_active(client_id)
        return [ComodatoResponse.model_validate(item) for item in items]

    async def get_pending_signature(self) -> list[ComodatoResponse]:
        """Lista comodatos aguardando assinatura."""
        items = await self.repository.get_pending_signature()
        return [ComodatoResponse.model_validate(item) for item in items]

    async def get_pending_delivery(self) -> list[ComodatoResponse]:
        """Lista comodatos aguardando entrega."""
        items = await self.repository.get_pending_delivery()
        return [ComodatoResponse.model_validate(item) for item in items]

    async def get_pending_return(self) -> list[ComodatoResponse]:
        """Lista comodatos com devolução pendente."""
        items = await self.repository.get_pending_return()
        return [ComodatoResponse.model_validate(item) for item in items]

    async def get_expiring(self, days: int = 30) -> list[ComodatoResponse]:
        """Lista comodatos expirando em X dias."""
        items = await self.repository.get_expiring(days)
        return [ComodatoResponse.model_validate(item) for item in items]

    async def get_expired(self) -> list[ComodatoResponse]:
        """Lista comodatos expirados não devolvidos."""
        items = await self.repository.get_expired()
        return [ComodatoResponse.model_validate(item) for item in items]

    async def sign(
        self,
        comodato_id: str | UUID,
        signed_by_client: str,
        signed_by_company: str,
    ) -> ComodatoResponse | None:
        """Registra assinatura do contrato."""
        comodato = await self.repository.sign(comodato_id, signed_by_client, signed_by_company)
        if not comodato:
            return None

        # Atualizar status do equipamento para comodato
        equipment = await self.equipment_repository.get_by_id(comodato.equipment_id)
        if equipment:
            equipment.status = EquipmentStatus.COMODATO

        await self.session.commit()
        return ComodatoResponse.model_validate(comodato)

    async def deliver(
        self,
        comodato_id: str | UUID,
        delivered_by: str,
        received_by: str,
        notes: str | None = None,
        photos: list | None = None,
    ) -> ComodatoResponse | None:
        """Registra entrega do equipamento."""
        comodato = await self.repository.deliver(comodato_id, delivered_by, received_by, notes, photos)
        if not comodato:
            return None
        await self.session.commit()
        return ComodatoResponse.model_validate(comodato)

    async def request_return(self, comodato_id: str | UUID) -> ComodatoResponse | None:
        """Solicita devolução."""
        comodato = await self.repository.request_return(comodato_id)
        if not comodato:
            return None
        await self.session.commit()
        return ComodatoResponse.model_validate(comodato)

    async def schedule_return(self, comodato_id: str | UUID, scheduled_date: datetime) -> ComodatoResponse | None:
        """Agenda devolução."""
        comodato = await self.repository.schedule_return(comodato_id, scheduled_date)
        if not comodato:
            return None
        await self.session.commit()
        return ComodatoResponse.model_validate(comodato)

    async def register_return(
        self,
        comodato_id: str | UUID,
        returned_by: str,
        condition: str,
        notes: str | None = None,
        photos: list | None = None,
    ) -> ComodatoResponse | None:
        """Registra devolução e retorna equipamento ao estoque."""
        comodato = await self.repository.get_by_id(comodato_id)
        if not comodato:
            return None

        # Registrar devolução
        comodato = await self.repository.register_return(comodato_id, returned_by, condition, notes, photos)

        # Retornar equipamento ao estoque
        equipment = await self.equipment_repository.get_by_id(comodato.equipment_id)
        if equipment:
            equipment.status = EquipmentStatus.ESTOQUE
            equipment.client_id = None
            equipment.client_name = None
            equipment.contract_id = None

        await self.session.commit()
        return ComodatoResponse.model_validate(comodato)

    async def register_damage(
        self,
        comodato_id: str | UUID,
        description: str,
        cost: float,
    ) -> ComodatoResponse | None:
        """Registra dano no equipamento."""
        comodato = await self.repository.register_damage(comodato_id, description, cost)
        if not comodato:
            return None
        await self.session.commit()
        return ComodatoResponse.model_validate(comodato)

    async def mark_as_lost(self, comodato_id: str | UUID) -> ComodatoResponse | None:
        """Marca equipamento como perdido e aplica penalidade."""
        comodato = await self.repository.get_by_id(comodato_id)
        if not comodato:
            return None

        comodato = await self.repository.mark_as_lost(comodato_id)

        # Marcar equipamento como baixa
        equipment = await self.equipment_repository.get_by_id(comodato.equipment_id)
        if equipment:
            equipment.decommission()

        await self.session.commit()
        return ComodatoResponse.model_validate(comodato)

    async def terminate(self, comodato_id: str | UUID, reason: str) -> ComodatoResponse | None:
        """Encerra contrato de comodato."""
        comodato = await self.repository.terminate(comodato_id, reason)
        if not comodato:
            return None
        await self.session.commit()
        return ComodatoResponse.model_validate(comodato)

    async def transfer(
        self,
        comodato_id: str | UUID,
        new_client_id: str,
        new_client_name: str,
        reason: str,
    ) -> ComodatoResponse | None:
        """Transfere comodato para outro cliente."""
        comodato = await self.repository.transfer(comodato_id, new_client_id, reason)
        if not comodato:
            return None

        # Atualizar cliente no equipamento
        equipment = await self.equipment_repository.get_by_id(comodato.equipment_id)
        if equipment:
            equipment.client_id = new_client_id
            equipment.client_name = new_client_name

        await self.session.commit()
        return ComodatoResponse.model_validate(comodato)

    async def get_stats(self, client_id: str | None = None) -> dict:
        """Obtém estatísticas de comodatos."""
        return await self.repository.get_stats(client_id)

    async def generate_contract_pdf(self, comodato_id: str | UUID) -> str | None:
        """Gera PDF do contrato de comodato."""
        comodato = await self.repository.get_by_id(comodato_id)
        if not comodato:
            return None

        # Aqui seria gerado o PDF real
        # Por enquanto retorna URL simulada
        pdf_url = f"/api/v1/comodatos/{comodato_id}/contract.pdf"

        # Atualizar comodato com URL do PDF
        comodato.contract_pdf_url = pdf_url
        await self.session.commit()

        return pdf_url

    async def generate_delivery_term(self, comodato_id: str | UUID) -> str | None:
        """Gera termo de entrega."""
        comodato = await self.repository.get_by_id(comodato_id)
        if not comodato:
            return None

        # Aqui seria gerado o PDF real
        pdf_url = f"/api/v1/comodatos/{comodato_id}/delivery_term.pdf"

        comodato.delivery_term_url = pdf_url
        await self.session.commit()

        return pdf_url

    async def generate_return_term(self, comodato_id: str | UUID) -> str | None:
        """Gera termo de devolução."""
        comodato = await self.repository.get_by_id(comodato_id)
        if not comodato:
            return None

        # Aqui seria gerado o PDF real
        pdf_url = f"/api/v1/comodatos/{comodato_id}/return_term.pdf"

        comodato.return_term_url = pdf_url
        await self.session.commit()

        return pdf_url
