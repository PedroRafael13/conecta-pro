"""Service para Visitor."""

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.visitors.repositories.visitor_repository import VisitorRepository
from modules.visitors.schemas.visitor import (
    VisitorBlock,
    VisitorCreate,
    VisitorFilter,
    VisitorListResponse,
    VisitorResponse,
    VisitorStats,
    VisitorUpdate,
)

logger = logging.getLogger(__name__)


class VisitorService:
    """Service para operações de Visitor."""

    def __init__(self, session: AsyncSession):
        """Inicializa o service."""
        self.session = session
        self.repository = VisitorRepository(session)

    async def create(self, data: VisitorCreate) -> VisitorResponse:
        """Cria um novo visitante."""
        # Verificar duplicidade por CPF
        if data.cpf:
            existing = await self.repository.get_by_cpf(data.cpf)
            if existing:
                logger.warning(f"Visitante já existe com CPF: {data.cpf}")
                return VisitorResponse.model_validate(existing)

        # Verificar duplicidade por documento
        if data.document_number:
            existing = await self.repository.get_by_document(data.document_number)
            if existing:
                logger.warning(
                    f"Visitante já existe com documento: {data.document_number}"
                )
                return VisitorResponse.model_validate(existing)

        visitor = await self.repository.create(data)
        await self.session.commit()
        await self.session.refresh(visitor)
        return VisitorResponse.model_validate(visitor)

    async def get_by_id(self, visitor_id: str | UUID) -> Optional[VisitorResponse]:
        """Busca visitante por ID."""
        visitor = await self.repository.get_by_id(visitor_id)
        if not visitor:
            return None
        return VisitorResponse.model_validate(visitor)

    async def get_by_code(self, code: str) -> Optional[VisitorResponse]:
        """Busca visitante por código."""
        visitor = await self.repository.get_by_code(code)
        if not visitor:
            return None
        return VisitorResponse.model_validate(visitor)

    async def get_by_cpf(self, cpf: str) -> Optional[VisitorResponse]:
        """Busca visitante por CPF."""
        visitor = await self.repository.get_by_cpf(cpf)
        if not visitor:
            return None
        return VisitorResponse.model_validate(visitor)

    async def get_by_document(self, document: str) -> Optional[VisitorResponse]:
        """Busca visitante por documento."""
        visitor = await self.repository.get_by_document(document)
        if not visitor:
            return None
        return VisitorResponse.model_validate(visitor)

    async def get_by_plate(self, plate: str) -> Optional[VisitorResponse]:
        """Busca visitante por placa."""
        visitor = await self.repository.get_by_plate(plate)
        if not visitor:
            return None
        return VisitorResponse.model_validate(visitor)

    async def get_by_qr_code(self, qr_code: str) -> Optional[VisitorResponse]:
        """Busca visitante por QR Code."""
        visitor = await self.repository.get_by_qr_code(qr_code)
        if not visitor:
            return None
        return VisitorResponse.model_validate(visitor)

    async def update(
        self, visitor_id: str | UUID, data: VisitorUpdate
    ) -> Optional[VisitorResponse]:
        """Atualiza um visitante."""
        visitor = await self.repository.update(visitor_id, data)
        if not visitor:
            return None
        await self.session.commit()
        return VisitorResponse.model_validate(visitor)

    async def delete(self, visitor_id: str | UUID) -> bool:
        """Deleta um visitante."""
        result = await self.repository.delete(visitor_id)
        if result:
            await self.session.commit()
        return result

    async def list(
        self,
        filters: Optional[VisitorFilter] = None,
        page: int = 1,
        page_size: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> VisitorListResponse:
        """Lista visitantes com filtros."""
        skip = (page - 1) * page_size
        visitors, total = await self.repository.list_with_filters(
            filters, skip, page_size, order_by, order_desc
        )

        items = [VisitorResponse.model_validate(v) for v in visitors]
        pages = (total + page_size - 1) // page_size

        return VisitorListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    async def search(
        self, query: str, condominium_id: str = None, limit: int = 10
    ) -> list[VisitorResponse]:
        """Busca visitantes por termo."""
        visitors = await self.repository.search(query, condominium_id, limit)
        return [VisitorResponse.model_validate(v) for v in visitors]

    async def get_blocked(
        self, page: int = 1, page_size: int = 20
    ) -> VisitorListResponse:
        """Lista visitantes bloqueados."""
        skip = (page - 1) * page_size
        visitors = await self.repository.get_blocked(skip, page_size)
        items = [VisitorResponse.model_validate(v) for v in visitors]
        return VisitorListResponse(
            items=items, total=len(items), page=page, page_size=page_size
        )

    async def get_vip(self, page: int = 1, page_size: int = 20) -> VisitorListResponse:
        """Lista visitantes VIP."""
        skip = (page - 1) * page_size
        visitors = await self.repository.get_vip(skip, page_size)
        items = [VisitorResponse.model_validate(v) for v in visitors]
        return VisitorListResponse(
            items=items, total=len(items), page=page, page_size=page_size
        )

    async def get_frequent(
        self, min_visits: int = 10, page: int = 1, page_size: int = 20
    ) -> VisitorListResponse:
        """Lista visitantes frequentes."""
        skip = (page - 1) * page_size
        visitors = await self.repository.get_frequent(min_visits, skip, page_size)
        items = [VisitorResponse.model_validate(v) for v in visitors]
        return VisitorListResponse(
            items=items, total=len(items), page=page, page_size=page_size
        )

    async def get_by_condominium(
        self, condominium_id: str, page: int = 1, page_size: int = 20
    ) -> VisitorListResponse:
        """Lista visitantes de um condomínio."""
        skip = (page - 1) * page_size
        visitors = await self.repository.get_by_condominium(
            condominium_id, skip, page_size
        )
        items = [VisitorResponse.model_validate(v) for v in visitors]
        return VisitorListResponse(
            items=items, total=len(items), page=page, page_size=page_size
        )

    async def get_stats(
        self, condominium_id: str = None, date_from: datetime = None
    ) -> VisitorStats:
        """Retorna estatísticas."""
        stats = await self.repository.get_stats(condominium_id, date_from)
        return VisitorStats(**stats)

    async def block(
        self, visitor_id: str | UUID, data: VisitorBlock
    ) -> Optional[VisitorResponse]:
        """Bloqueia um visitante."""
        visitor = await self.repository.block(
            visitor_id,
            data.reason,
            data.blocked_by_id,
            data.blocked_by_name,
            data.until,
        )
        if not visitor:
            return None
        await self.session.commit()
        return VisitorResponse.model_validate(visitor)

    async def unblock(self, visitor_id: str | UUID) -> Optional[VisitorResponse]:
        """Desbloqueia um visitante."""
        visitor = await self.repository.unblock(visitor_id)
        if not visitor:
            return None
        await self.session.commit()
        return VisitorResponse.model_validate(visitor)

    async def set_vip(self, visitor_id: str | UUID) -> Optional[VisitorResponse]:
        """Define visitante como VIP."""
        visitor = await self.repository.set_vip(visitor_id)
        if not visitor:
            return None
        await self.session.commit()
        return VisitorResponse.model_validate(visitor)

    async def register_visit(
        self, visitor_id: str | UUID, duration_minutes: int = None
    ) -> Optional[VisitorResponse]:
        """Registra uma visita."""
        visitor = await self.repository.register_visit(visitor_id, duration_minutes)
        if not visitor:
            return None
        await self.session.commit()
        return VisitorResponse.model_validate(visitor)

    async def generate_qr_code(self, visitor_id: str | UUID) -> Optional[str]:
        """Gera QR Code para visitante."""
        visitor = await self.repository.get_by_id(visitor_id)
        if not visitor:
            return None

        qr_code = visitor.generate_qr_code()
        await self.session.commit()
        return qr_code

    async def find_or_create(self, data: VisitorCreate) -> VisitorResponse:
        """Busca ou cria visitante."""
        # Tentar encontrar por CPF
        if data.cpf:
            existing = await self.repository.get_by_cpf(data.cpf)
            if existing:
                return VisitorResponse.model_validate(existing)

        # Tentar encontrar por documento
        if data.document_number:
            existing = await self.repository.get_by_document(data.document_number)
            if existing:
                return VisitorResponse.model_validate(existing)

        # Criar novo
        return await self.create(data)
