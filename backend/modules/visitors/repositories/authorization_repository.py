"""Repository para VisitorAuthorization."""

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.visitors.models.authorization import (
    AuthorizationStatus,
    AuthorizationType,
    VisitorAuthorization,
)
from modules.visitors.schemas.authorization import (
    AuthorizationCreate,
    AuthorizationFilter,
    AuthorizationUpdate,
)

logger = logging.getLogger(__name__)


class AuthorizationRepository:
    """Repository para operações de VisitorAuthorization."""

    def __init__(self, session: AsyncSession):
        """Inicializa o repository."""
        self.session = session

    async def create(self, data: AuthorizationCreate) -> VisitorAuthorization:
        """Cria uma nova autorização."""
        auth = VisitorAuthorization(**data.model_dump(exclude_none=True))
        self.session.add(auth)
        await self.session.flush()
        await self.session.refresh(auth)
        logger.info(f"Autorização criada: {auth.code}")
        return auth

    async def get_by_id(
        self, auth_id: str | UUID
    ) -> Optional[VisitorAuthorization]:
        """Busca autorização por ID."""
        if isinstance(auth_id, str):
            auth_id = UUID(auth_id)

        result = await self.session.execute(
            select(VisitorAuthorization).where(
                and_(
                    VisitorAuthorization.id == auth_id,
                    VisitorAuthorization.is_deleted.is_(False),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[VisitorAuthorization]:
        """Busca autorização por código."""
        result = await self.session.execute(
            select(VisitorAuthorization).where(
                and_(
                    VisitorAuthorization.code == code,
                    VisitorAuthorization.is_deleted.is_(False),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_qr_code(self, qr_code: str) -> Optional[VisitorAuthorization]:
        """Busca autorização por QR Code."""
        result = await self.session.execute(
            select(VisitorAuthorization).where(
                and_(
                    VisitorAuthorization.qr_code == qr_code,
                    VisitorAuthorization.is_deleted.is_(False),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_access_code(
        self, access_code: str, condominium_id: str
    ) -> Optional[VisitorAuthorization]:
        """Busca autorização por código de acesso."""
        result = await self.session.execute(
            select(VisitorAuthorization).where(
                and_(
                    VisitorAuthorization.access_code == access_code,
                    VisitorAuthorization.condominium_id == condominium_id,
                    VisitorAuthorization.is_deleted.is_(False),
                )
            )
        )
        return result.scalar_one_or_none()

    async def update(
        self, auth_id: str | UUID, data: AuthorizationUpdate
    ) -> Optional[VisitorAuthorization]:
        """Atualiza uma autorização."""
        auth = await self.get_by_id(auth_id)
        if not auth:
            return None

        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        for field, value in update_data.items():
            setattr(auth, field, value)

        await self.session.flush()
        return auth

    async def delete(self, auth_id: str | UUID) -> bool:
        """Deleta uma autorização (soft delete)."""
        auth = await self.get_by_id(auth_id)
        if not auth:
            return False

        auth.soft_delete()
        await self.session.flush()
        return True

    async def list_with_filters(
        self,
        filters: Optional[AuthorizationFilter] = None,
        skip: int = 0,
        limit: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> tuple[list[VisitorAuthorization], int]:
        """Lista autorizações com filtros."""
        query = select(VisitorAuthorization).where(
            VisitorAuthorization.is_deleted.is_(False)
        )

        if filters:
            if filters.visitor_id:
                query = query.where(
                    VisitorAuthorization.visitor_id == filters.visitor_id
                )
            if filters.authorization_type:
                query = query.where(
                    VisitorAuthorization.authorization_type
                    == filters.authorization_type
                )
            if filters.status:
                query = query.where(
                    VisitorAuthorization.status == filters.status
                )
            if filters.condominium_id:
                query = query.where(
                    VisitorAuthorization.condominium_id == filters.condominium_id
                )
            if filters.unit_id:
                query = query.where(
                    VisitorAuthorization.unit_id == filters.unit_id
                )
            if filters.resident_id:
                query = query.where(
                    VisitorAuthorization.resident_id == filters.resident_id
                )
            if filters.valid_from:
                query = query.where(
                    VisitorAuthorization.valid_from >= filters.valid_from
                )
            if filters.valid_until:
                query = query.where(
                    VisitorAuthorization.valid_until <= filters.valid_until
                )
            if filters.is_expired is not None:
                now = datetime.utcnow()
                if filters.is_expired:
                    query = query.where(
                        VisitorAuthorization.valid_until < now
                    )
                else:
                    query = query.where(
                        or_(
                            VisitorAuthorization.valid_until.is_(None),
                            VisitorAuthorization.valid_until >= now,
                        )
                    )

        # Contar total
        count_result = await self.session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0

        # Ordenar
        order_column = getattr(
            VisitorAuthorization, order_by, VisitorAuthorization.created_at
        )
        if order_desc:
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        # Paginar
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def get_by_visitor(
        self,
        visitor_id: str | UUID,
        status: AuthorizationStatus = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[VisitorAuthorization]:
        """Lista autorizações de um visitante."""
        if isinstance(visitor_id, str):
            visitor_id = UUID(visitor_id)

        query = select(VisitorAuthorization).where(
            and_(
                VisitorAuthorization.visitor_id == visitor_id,
                VisitorAuthorization.is_deleted.is_(False),
            )
        )

        if status:
            query = query.where(VisitorAuthorization.status == status)

        query = query.order_by(VisitorAuthorization.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_pending(
        self, condominium_id: str = None, skip: int = 0, limit: int = 20
    ) -> list[VisitorAuthorization]:
        """Lista autorizações pendentes."""
        query = select(VisitorAuthorization).where(
            and_(
                VisitorAuthorization.status == AuthorizationStatus.PENDENTE,
                VisitorAuthorization.is_deleted.is_(False),
            )
        )

        if condominium_id:
            query = query.where(
                VisitorAuthorization.condominium_id == condominium_id
            )

        query = query.order_by(VisitorAuthorization.created_at.asc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_active(
        self, condominium_id: str = None, skip: int = 0, limit: int = 20
    ) -> list[VisitorAuthorization]:
        """Lista autorizações ativas."""
        now = datetime.utcnow()
        query = select(VisitorAuthorization).where(
            and_(
                VisitorAuthorization.status == AuthorizationStatus.APROVADA,
                VisitorAuthorization.is_deleted.is_(False),
                or_(
                    VisitorAuthorization.valid_until.is_(None),
                    VisitorAuthorization.valid_until >= now,
                ),
            )
        )

        if condominium_id:
            query = query.where(
                VisitorAuthorization.condominium_id == condominium_id
            )

        query = query.order_by(VisitorAuthorization.valid_until.asc().nulls_last())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_expiring_soon(
        self, days: int = 7, condominium_id: str = None
    ) -> list[VisitorAuthorization]:
        """Lista autorizações que expiram em breve."""
        from datetime import timedelta

        now = datetime.utcnow()
        limit_date = now + timedelta(days=days)

        query = select(VisitorAuthorization).where(
            and_(
                VisitorAuthorization.status == AuthorizationStatus.APROVADA,
                VisitorAuthorization.valid_until.isnot(None),
                VisitorAuthorization.valid_until >= now,
                VisitorAuthorization.valid_until <= limit_date,
                VisitorAuthorization.is_deleted.is_(False),
            )
        )

        if condominium_id:
            query = query.where(
                VisitorAuthorization.condominium_id == condominium_id
            )

        query = query.order_by(VisitorAuthorization.valid_until.asc())

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def approve(
        self,
        auth_id: str | UUID,
        approved_by_id: str = None,
        approved_by_name: str = None,
    ) -> Optional[VisitorAuthorization]:
        """Aprova uma autorização."""
        auth = await self.get_by_id(auth_id)
        if not auth:
            return None

        auth.approve(approved_by_id, approved_by_name)
        await self.session.flush()
        logger.info(f"Autorização aprovada: {auth.code}")
        return auth

    async def reject(
        self, auth_id: str | UUID, reason: str = None
    ) -> Optional[VisitorAuthorization]:
        """Rejeita uma autorização."""
        auth = await self.get_by_id(auth_id)
        if not auth:
            return None

        auth.reject(reason)
        await self.session.flush()
        logger.info(f"Autorização rejeitada: {auth.code}")
        return auth

    async def cancel(
        self, auth_id: str | UUID, reason: str = None
    ) -> Optional[VisitorAuthorization]:
        """Cancela uma autorização."""
        auth = await self.get_by_id(auth_id)
        if not auth:
            return None

        auth.cancel(reason)
        await self.session.flush()
        logger.info(f"Autorização cancelada: {auth.code}")
        return auth

    async def use(self, auth_id: str | UUID) -> Optional[VisitorAuthorization]:
        """Registra uso da autorização."""
        auth = await self.get_by_id(auth_id)
        if not auth:
            return None

        if auth.use():
            await self.session.flush()
            logger.info(f"Autorização usada: {auth.code} ({auth.uses_count})")
            return auth

        return None

    async def get_stats(
        self, condominium_id: str = None, date_from: datetime = None
    ) -> dict:
        """Retorna estatísticas de autorizações."""
        base_query = select(VisitorAuthorization).where(
            VisitorAuthorization.is_deleted.is_(False)
        )

        if condominium_id:
            base_query = base_query.where(
                VisitorAuthorization.condominium_id == condominium_id
            )
        if date_from:
            base_query = base_query.where(
                VisitorAuthorization.created_at >= date_from
            )

        # Contar total
        count_result = await self.session.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total = count_result.scalar() or 0

        # Por status
        status_query = (
            select(VisitorAuthorization.status, func.count())
            .where(VisitorAuthorization.is_deleted.is_(False))
            .group_by(VisitorAuthorization.status)
        )
        if condominium_id:
            status_query = status_query.where(
                VisitorAuthorization.condominium_id == condominium_id
            )

        status_result = await self.session.execute(status_query)
        by_status = {str(row[0].value): row[1] for row in status_result.all()}

        # Por tipo
        type_query = (
            select(VisitorAuthorization.authorization_type, func.count())
            .where(VisitorAuthorization.is_deleted.is_(False))
            .group_by(VisitorAuthorization.authorization_type)
        )
        if condominium_id:
            type_query = type_query.where(
                VisitorAuthorization.condominium_id == condominium_id
            )

        type_result = await self.session.execute(type_query)
        by_type = {str(row[0].value): row[1] for row in type_result.all()}

        # Total de usos
        uses_query = (
            select(func.sum(VisitorAuthorization.uses_count))
            .where(VisitorAuthorization.is_deleted.is_(False))
        )
        if condominium_id:
            uses_query = uses_query.where(
                VisitorAuthorization.condominium_id == condominium_id
            )

        uses_result = await self.session.execute(uses_query)
        total_uses = uses_result.scalar() or 0

        return {
            "total": total,
            "pending": by_status.get("pendente", 0),
            "approved": by_status.get("aprovada", 0),
            "rejected": by_status.get("rejeitada", 0),
            "expired": by_status.get("expirada", 0),
            "used": by_status.get("utilizada", 0),
            "by_type": by_type,
            "total_uses": int(total_uses),
        }

    async def validate(
        self,
        code: str = None,
        qr_code: str = None,
        access_code: str = None,
        condominium_id: str = None,
    ) -> Optional[VisitorAuthorization]:
        """Valida uma autorização."""
        auth = None

        if code:
            auth = await self.get_by_code(code)
        elif qr_code:
            auth = await self.get_by_qr_code(qr_code)
        elif access_code and condominium_id:
            auth = await self.get_by_access_code(access_code, condominium_id)

        if not auth:
            return None

        if condominium_id and auth.condominium_id != condominium_id:
            return None

        return auth if auth.can_use else None
