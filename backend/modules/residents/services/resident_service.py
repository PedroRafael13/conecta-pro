"""Service para Resident."""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.residents.models.resident import Resident, ResidentStatus
from modules.residents.repositories.resident_repository import ResidentRepository
from modules.residents.schemas.resident import (
    ResidentCreate,
    ResidentUpdate,
    ResidentFilter,
    ResidentResponse,
    ResidentListResponse,
    ResidentStats,
)

logger = logging.getLogger(__name__)


class ResidentService:
    """Service para operações de Resident."""

    def __init__(self, session: AsyncSession):
        """Inicializa o service."""
        self.session = session
        self.repository = ResidentRepository(session)

    async def create(self, data: ResidentCreate) -> ResidentResponse:
        """Cria um novo morador."""
        # Verifica CPF duplicado
        if data.cpf:
            existing = await self.repository.get_by_cpf(data.cpf)
            if existing:
                raise ValueError(f"Já existe morador com CPF: {data.cpf}")

        # Verifica documento duplicado
        if data.document_number:
            existing = await self.repository.get_by_document(data.document_number)
            if existing:
                raise ValueError(
                    f"Já existe morador com documento: {data.document_number}"
                )

        resident = await self.repository.create(data)
        await self.session.commit()
        logger.info("Morador criado: {resident.id} - {resident.name}")
        return ResidentResponse.model_validate(resident)

    async def get_by_id(self, resident_id: str | UUID) -> Optional[ResidentResponse]:
        """Busca morador por ID."""
        resident = await self.repository.get_by_id(resident_id)
        if not resident:
            return None
        return ResidentResponse.model_validate(resident)

    async def get_by_code(self, code: str) -> Optional[ResidentResponse]:
        """Busca morador por código."""
        resident = await self.repository.get_by_code(code)
        if not resident:
            return None
        return ResidentResponse.model_validate(resident)

    async def get_by_cpf(self, cpf: str) -> Optional[ResidentResponse]:
        """Busca morador por CPF."""
        resident = await self.repository.get_by_cpf(cpf)
        if not resident:
            return None
        return ResidentResponse.model_validate(resident)

    async def get_by_unit(
        self, condominium_id: str, unit_id: str
    ) -> list[ResidentResponse]:
        """Busca moradores da unidade."""
        residents = await self.repository.get_by_unit(condominium_id, unit_id)
        return [ResidentResponse.model_validate(r) for r in residents]

    async def update(
        self, resident_id: str | UUID, data: ResidentUpdate
    ) -> Optional[ResidentResponse]:
        """Atualiza um morador."""
        # Verifica CPF duplicado
        if data.cpf:
            existing = await self.repository.get_by_cpf(data.cpf)
            if existing and str(existing.id) != str(resident_id):
                raise ValueError(f"Já existe morador com CPF: {data.cpf}")

        # Verifica documento duplicado
        if data.document_number:
            existing = await self.repository.get_by_document(data.document_number)
            if existing and str(existing.id) != str(resident_id):
                raise ValueError(
                    f"Já existe morador com documento: {data.document_number}"
                )

        resident = await self.repository.update(resident_id, data)
        if not resident:
            return None
        await self.session.commit()
        logger.info("Morador atualizado: {resident.id}")
        return ResidentResponse.model_validate(resident)

    async def delete(self, resident_id: str | UUID) -> bool:
        """Remove morador (soft delete)."""
        result = await self.repository.soft_delete(resident_id)
        if result:
            await self.session.commit()
            logger.info("Morador removido: {resident_id}")
        return result

    async def list(
        self,
        filters: Optional[ResidentFilter] = None,
        page: int = 1,
        page_size: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> ResidentListResponse:
        """Lista moradores com filtros e paginação."""
        skip = (page - 1) * page_size
        residents, total = await self.repository.list_with_filters(
            filters=filters,
            skip=skip,
            limit=page_size,
            order_by=order_by,
            order_desc=order_desc,
        )

        pages = (total + page_size - 1) // page_size if total > 0 else 0

        return ResidentListResponse(
            items=[ResidentResponse.model_validate(r) for r in residents],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    async def search(
        self, query: str, condominium_id: str = None, limit: int = 10
    ) -> list[ResidentResponse]:
        """Busca moradores."""
        residents = await self.repository.search(query, condominium_id, limit)
        return [ResidentResponse.model_validate(r) for r in residents]

    async def get_blocked(
        self, condominium_id: str = None, page: int = 1, page_size: int = 20
    ) -> list[ResidentResponse]:
        """Lista moradores bloqueados."""
        skip = (page - 1) * page_size
        residents = await self.repository.get_blocked(condominium_id, skip, page_size)
        return [ResidentResponse.model_validate(r) for r in residents]

    async def get_defaulters(
        self, condominium_id: str = None, page: int = 1, page_size: int = 20
    ) -> list[ResidentResponse]:
        """Lista moradores inadimplentes."""
        skip = (page - 1) * page_size
        residents = await self.repository.get_defaulters(
            condominium_id, skip, page_size
        )
        return [ResidentResponse.model_validate(r) for r in residents]

    async def get_owners(
        self, condominium_id: str, page: int = 1, page_size: int = 100
    ) -> list[ResidentResponse]:
        """Lista proprietários."""
        skip = (page - 1) * page_size
        residents = await self.repository.get_owners(condominium_id, skip, page_size)
        return [ResidentResponse.model_validate(r) for r in residents]

    async def block(
        self, resident_id: str | UUID, reason: str, blocked_by: str
    ) -> Optional[ResidentResponse]:
        """Bloqueia morador."""
        resident = await self.repository.block(resident_id, reason, blocked_by)
        if not resident:
            return None
        await self.session.commit()
        logger.info("Morador bloqueado: {resident_id} - Motivo: {reason}")
        return ResidentResponse.model_validate(resident)

    async def unblock(self, resident_id: str | UUID) -> Optional[ResidentResponse]:
        """Desbloqueia morador."""
        resident = await self.repository.unblock(resident_id)
        if not resident:
            return None
        await self.session.commit()
        logger.info("Morador desbloqueado: {resident_id}")
        return ResidentResponse.model_validate(resident)

    async def set_defaulter(
        self, resident_id: str | UUID, debt_amount: float = 0.0
    ) -> Optional[ResidentResponse]:
        """Marca como inadimplente."""
        resident = await self.repository.set_defaulter(resident_id, debt_amount)
        if not resident:
            return None
        await self.session.commit()
        logger.info(
            f"Morador marcado como inadimplente: {resident_id} - Débito: {debt_amount}"
        )
        return ResidentResponse.model_validate(resident)

    async def clear_defaulter(
        self, resident_id: str | UUID
    ) -> Optional[ResidentResponse]:
        """Remove inadimplência."""
        resident = await self.repository.clear_defaulter(resident_id)
        if not resident:
            return None
        await self.session.commit()
        logger.info("Inadimplência removida: {resident_id}")
        return ResidentResponse.model_validate(resident)

    async def move_out(
        self, resident_id: str | UUID, move_out_date: str = None
    ) -> Optional[ResidentResponse]:
        """Registra mudança do morador."""
        resident = await self.repository.get_by_id(resident_id)
        if not resident:
            return None

        from datetime import datetime, date

        if move_out_date:
            parsed_date = datetime.strptime(move_out_date, "%Y-%m-%d").date()
        else:
            parsed_date = date.today()

        resident.move_out(parsed_date)
        await self.session.commit()
        logger.info("Morador mudou-se: {resident_id}")
        return ResidentResponse.model_validate(resident)

    async def transfer_unit(
        self,
        resident_id: str | UUID,
        new_unit_id: str,
        new_unit_number: str,
        new_block: str = None,
    ) -> Optional[ResidentResponse]:
        """Transfere morador para nova unidade."""
        resident = await self.repository.get_by_id(resident_id)
        if not resident:
            return None

        resident.unit_id = new_unit_id
        resident.unit_number = new_unit_number
        resident.block = new_block
        resident.status = ResidentStatus.ATIVO
        await self.session.commit()
        logger.info("Morador transferido: {resident_id} para unidade {new_unit_number}")
        return ResidentResponse.model_validate(resident)

    async def enable_access(
        self,
        resident_id: str | UUID,
        method: str,
        identifier: str = None,
    ) -> Optional[ResidentResponse]:
        """Habilita método de acesso."""
        resident = await self.repository.get_by_id(resident_id)
        if not resident:
            return None

        from modules.residents.models.resident import AccessMethod

        access_method = AccessMethod(method)
        resident.enable_access_method(access_method, identifier)
        await self.session.commit()
        logger.info("Acesso habilitado: {resident_id} - {method}")
        return ResidentResponse.model_validate(resident)

    async def disable_access(
        self, resident_id: str | UUID, method: str
    ) -> Optional[ResidentResponse]:
        """Desabilita método de acesso."""
        resident = await self.repository.get_by_id(resident_id)
        if not resident:
            return None

        from modules.residents.models.resident import AccessMethod

        access_method = AccessMethod(method)
        resident.disable_access_method(access_method)
        await self.session.commit()
        logger.info("Acesso desabilitado: {resident_id} - {method}")
        return ResidentResponse.model_validate(resident)

    async def get_stats(self, condominium_id: str = None) -> ResidentStats:
        """Retorna estatísticas."""
        stats = await self.repository.get_stats(condominium_id)
        return ResidentStats(**stats)

    async def generate_qr_code(self, resident_id: str | UUID) -> Optional[str]:
        """Gera QR Code para morador."""
        resident = await self.repository.get_by_id(resident_id)
        if not resident:
            return None
        return resident.generate_qr_code()
