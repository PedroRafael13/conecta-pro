"""Service para VisitorAuthorization."""

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.visitors.repositories.authorization_repository import AuthorizationRepository
from modules.visitors.repositories.visitor_repository import VisitorRepository
from modules.visitors.schemas.authorization import (
    AuthorizationApprove,
    AuthorizationCreate,
    AuthorizationFilter,
    AuthorizationListResponse,
    AuthorizationReject,
    AuthorizationResponse,
    AuthorizationStats,
    AuthorizationUpdate,
    AuthorizationValidate,
    AuthorizationValidateResponse,
)

logger = logging.getLogger(__name__)


class AuthorizationService:
    """Service para operações de VisitorAuthorization."""

    def __init__(self, session: AsyncSession):
        """Inicializa o service."""
        self.session = session
        self.repository = AuthorizationRepository(session)
        self.visitor_repo = VisitorRepository(session)

    async def create(self, data: AuthorizationCreate) -> AuthorizationResponse:
        """Cria uma nova autorização."""
        auth = await self.repository.create(data)
        await self.session.commit()
        await self.session.refresh(auth)
        return AuthorizationResponse.model_validate(auth)

    async def get_by_id(
        self, auth_id: str | UUID
    ) -> Optional[AuthorizationResponse]:
        """Busca autorização por ID."""
        auth = await self.repository.get_by_id(auth_id)
        if not auth:
            return None
        return AuthorizationResponse.model_validate(auth)

    async def get_by_code(self, code: str) -> Optional[AuthorizationResponse]:
        """Busca autorização por código."""
        auth = await self.repository.get_by_code(code)
        if not auth:
            return None
        return AuthorizationResponse.model_validate(auth)

    async def update(
        self, auth_id: str | UUID, data: AuthorizationUpdate
    ) -> Optional[AuthorizationResponse]:
        """Atualiza uma autorização."""
        auth = await self.repository.update(auth_id, data)
        if not auth:
            return None
        await self.session.commit()
        return AuthorizationResponse.model_validate(auth)

    async def delete(self, auth_id: str | UUID) -> bool:
        """Deleta uma autorização."""
        result = await self.repository.delete(auth_id)
        if result:
            await self.session.commit()
        return result

    async def list(
        self,
        filters: Optional[AuthorizationFilter] = None,
        page: int = 1,
        page_size: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> AuthorizationListResponse:
        """Lista autorizações com filtros."""
        skip = (page - 1) * page_size
        auths, total = await self.repository.list_with_filters(
            filters, skip, page_size, order_by, order_desc
        )

        items = [AuthorizationResponse.model_validate(a) for a in auths]
        pages = (total + page_size - 1) // page_size

        return AuthorizationListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    async def get_by_visitor(
        self,
        visitor_id: str | UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> AuthorizationListResponse:
        """Lista autorizações de um visitante."""
        skip = (page - 1) * page_size
        auths = await self.repository.get_by_visitor(visitor_id, skip=skip, limit=page_size)
        items = [AuthorizationResponse.model_validate(a) for a in auths]
        return AuthorizationListResponse(
            items=items, total=len(items), page=page, page_size=page_size
        )

    async def get_pending(
        self, condominium_id: str = None, page: int = 1, page_size: int = 20
    ) -> AuthorizationListResponse:
        """Lista autorizações pendentes."""
        skip = (page - 1) * page_size
        auths = await self.repository.get_pending(condominium_id, skip, page_size)
        items = [AuthorizationResponse.model_validate(a) for a in auths]
        return AuthorizationListResponse(
            items=items, total=len(items), page=page, page_size=page_size
        )

    async def get_active(
        self, condominium_id: str = None, page: int = 1, page_size: int = 20
    ) -> AuthorizationListResponse:
        """Lista autorizações ativas."""
        skip = (page - 1) * page_size
        auths = await self.repository.get_active(condominium_id, skip, page_size)
        items = [AuthorizationResponse.model_validate(a) for a in auths]
        return AuthorizationListResponse(
            items=items, total=len(items), page=page, page_size=page_size
        )

    async def get_expiring_soon(
        self, days: int = 7, condominium_id: str = None
    ) -> list[AuthorizationResponse]:
        """Lista autorizações que expiram em breve."""
        auths = await self.repository.get_expiring_soon(days, condominium_id)
        return [AuthorizationResponse.model_validate(a) for a in auths]

    async def get_stats(
        self, condominium_id: str = None, date_from: datetime = None
    ) -> AuthorizationStats:
        """Retorna estatísticas."""
        stats = await self.repository.get_stats(condominium_id, date_from)
        return AuthorizationStats(**stats)

    async def approve(
        self, auth_id: str | UUID, data: AuthorizationApprove
    ) -> Optional[AuthorizationResponse]:
        """Aprova uma autorização."""
        auth = await self.repository.approve(
            auth_id, data.approved_by_id, data.approved_by_name
        )
        if not auth:
            return None
        await self.session.commit()
        return AuthorizationResponse.model_validate(auth)

    async def reject(
        self, auth_id: str | UUID, data: AuthorizationReject
    ) -> Optional[AuthorizationResponse]:
        """Rejeita uma autorização."""
        auth = await self.repository.reject(auth_id, data.reason)
        if not auth:
            return None
        await self.session.commit()
        return AuthorizationResponse.model_validate(auth)

    async def cancel(
        self, auth_id: str | UUID, reason: str = None
    ) -> Optional[AuthorizationResponse]:
        """Cancela uma autorização."""
        auth = await self.repository.cancel(auth_id, reason)
        if not auth:
            return None
        await self.session.commit()
        return AuthorizationResponse.model_validate(auth)

    async def use(self, auth_id: str | UUID) -> Optional[AuthorizationResponse]:
        """Registra uso da autorização."""
        auth = await self.repository.use(auth_id)
        if not auth:
            return None
        await self.session.commit()
        return AuthorizationResponse.model_validate(auth)

    async def validate(
        self, data: AuthorizationValidate
    ) -> AuthorizationValidateResponse:
        """Valida uma autorização."""
        auth = await self.repository.validate(
            data.code, data.qr_code, data.access_code, data.condominium_id
        )

        if not auth:
            return AuthorizationValidateResponse(
                valid=False,
                reason="Autorização não encontrada ou inválida",
            )

        # Buscar dados do visitante
        visitor = await self.visitor_repo.get_by_id(auth.visitor_id)

        if not auth.can_use:
            reason = "Autorização não pode ser utilizada"
            if not auth.is_valid:
                reason = "Autorização expirada"
            elif not auth.is_within_allowed_time:
                reason = "Fora do horário permitido"
            elif auth.max_uses and auth.uses_count >= auth.max_uses:
                reason = "Limite de usos atingido"

            return AuthorizationValidateResponse(
                valid=False,
                reason=reason,
                authorization=AuthorizationResponse.model_validate(auth),
                visitor_name=visitor.name if visitor else None,
                visitor_photo=visitor.photo_url if visitor else None,
            )

        return AuthorizationValidateResponse(
            valid=True,
            authorization=AuthorizationResponse.model_validate(auth),
            visitor_name=visitor.name if visitor else None,
            visitor_photo=visitor.photo_url if visitor else None,
            unit_number=auth.unit_number,
            resident_name=auth.resident_name,
        )

    async def extend_validity(
        self, auth_id: str | UUID, days: int
    ) -> Optional[AuthorizationResponse]:
        """Estende a validade de uma autorização."""
        auth = await self.repository.get_by_id(auth_id)
        if not auth:
            return None

        auth.extend_validity(days)
        await self.session.commit()
        return AuthorizationResponse.model_validate(auth)
