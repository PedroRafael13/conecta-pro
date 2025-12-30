"""Repository para Visitor."""

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.visitors.models.visitor import Visitor, VisitorStatus, VisitorType
from modules.visitors.schemas.visitor import VisitorCreate, VisitorFilter, VisitorUpdate

logger = logging.getLogger(__name__)


class VisitorRepository:
    """Repository para operações de Visitor."""

    def __init__(self, session: AsyncSession):
        """Inicializa o repository."""
        self.session = session

    async def create(self, data: VisitorCreate) -> Visitor:
        """Cria um novo visitante."""
        visitor = Visitor(**data.model_dump(exclude_none=True))
        self.session.add(visitor)
        await self.session.flush()
        await self.session.refresh(visitor)
        logger.info(f"Visitante criado: {visitor.code} - {visitor.name}")
        return visitor

    async def get_by_id(self, visitor_id: str | UUID) -> Optional[Visitor]:
        """Busca visitante por ID."""
        if isinstance(visitor_id, str):
            visitor_id = UUID(visitor_id)

        result = await self.session.execute(
            select(Visitor).where(
                and_(Visitor.id == visitor_id, Visitor.is_deleted.is_(False))
            )
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[Visitor]:
        """Busca visitante por código."""
        result = await self.session.execute(
            select(Visitor).where(
                and_(Visitor.code == code, Visitor.is_deleted.is_(False))
            )
        )
        return result.scalar_one_or_none()

    async def get_by_cpf(self, cpf: str) -> Optional[Visitor]:
        """Busca visitante por CPF."""
        result = await self.session.execute(
            select(Visitor).where(
                and_(Visitor.cpf == cpf, Visitor.is_deleted.is_(False))
            )
        )
        return result.scalar_one_or_none()

    async def get_by_document(
        self, document_number: str
    ) -> Optional[Visitor]:
        """Busca visitante por documento."""
        result = await self.session.execute(
            select(Visitor).where(
                and_(
                    Visitor.document_number == document_number,
                    Visitor.is_deleted.is_(False),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_qr_code(self, qr_code: str) -> Optional[Visitor]:
        """Busca visitante por QR Code."""
        result = await self.session.execute(
            select(Visitor).where(
                and_(Visitor.qr_code == qr_code, Visitor.is_deleted.is_(False))
            )
        )
        return result.scalar_one_or_none()

    async def get_by_plate(self, plate: str) -> Optional[Visitor]:
        """Busca visitante por placa do veículo."""
        result = await self.session.execute(
            select(Visitor).where(
                and_(
                    Visitor.vehicle_plate == plate.upper(),
                    Visitor.is_deleted.is_(False),
                )
            )
        )
        return result.scalar_one_or_none()

    async def update(
        self, visitor_id: str | UUID, data: VisitorUpdate
    ) -> Optional[Visitor]:
        """Atualiza um visitante."""
        visitor = await self.get_by_id(visitor_id)
        if not visitor:
            return None

        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        for field, value in update_data.items():
            setattr(visitor, field, value)

        await self.session.flush()
        return visitor

    async def delete(self, visitor_id: str | UUID) -> bool:
        """Deleta um visitante (soft delete)."""
        visitor = await self.get_by_id(visitor_id)
        if not visitor:
            return False

        visitor.soft_delete()
        await self.session.flush()
        return True

    async def list_with_filters(
        self,
        filters: Optional[VisitorFilter] = None,
        skip: int = 0,
        limit: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> tuple[list[Visitor], int]:
        """Lista visitantes com filtros."""
        query = select(Visitor).where(Visitor.is_deleted.is_(False))

        if filters:
            if filters.name:
                query = query.where(Visitor.name.ilike(f"%{filters.name}%"))
            if filters.visitor_type:
                query = query.where(Visitor.visitor_type == filters.visitor_type)
            if filters.status:
                query = query.where(Visitor.status == filters.status)
            if filters.document_number:
                query = query.where(
                    Visitor.document_number == filters.document_number
                )
            if filters.cpf:
                query = query.where(Visitor.cpf == filters.cpf)
            if filters.phone:
                query = query.where(
                    or_(
                        Visitor.phone.ilike(f"%{filters.phone}%"),
                        Visitor.phone_secondary.ilike(f"%{filters.phone}%"),
                    )
                )
            if filters.company_name:
                query = query.where(
                    Visitor.company_name.ilike(f"%{filters.company_name}%")
                )
            if filters.vehicle_plate:
                query = query.where(
                    Visitor.vehicle_plate == filters.vehicle_plate.upper()
                )
            if filters.condominium_id:
                query = query.where(
                    Visitor.default_condominium_id == filters.condominium_id
                )
            if filters.is_blocked is not None:
                if filters.is_blocked:
                    query = query.where(Visitor.status == VisitorStatus.BLOQUEADO)
                else:
                    query = query.where(Visitor.status != VisitorStatus.BLOQUEADO)
            if filters.has_vehicle is not None:
                if filters.has_vehicle:
                    query = query.where(Visitor.vehicle_plate.isnot(None))
                else:
                    query = query.where(Visitor.vehicle_plate.is_(None))
            if filters.has_biometric is not None:
                if filters.has_biometric:
                    query = query.where(
                        or_(
                            Visitor.biometric_template.isnot(None),
                            Visitor.face_encoding.isnot(None),
                        )
                    )
            if filters.tags:
                for tag in filters.tags:
                    query = query.where(Visitor.tags.contains([tag]))
            if filters.created_from:
                query = query.where(Visitor.created_at >= filters.created_from)
            if filters.created_until:
                query = query.where(Visitor.created_at <= filters.created_until)

        # Contar total
        count_result = await self.session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0

        # Ordenar
        order_column = getattr(Visitor, order_by, Visitor.created_at)
        if order_desc:
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        # Paginar
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def search(
        self, query_str: str, condominium_id: str = None, limit: int = 10
    ) -> list[Visitor]:
        """Busca visitantes por termo."""
        query = select(Visitor).where(
            and_(
                Visitor.is_deleted.is_(False),
                or_(
                    Visitor.name.ilike(f"%{query_str}%"),
                    Visitor.cpf.ilike(f"%{query_str}%"),
                    Visitor.document_number.ilike(f"%{query_str}%"),
                    Visitor.phone.ilike(f"%{query_str}%"),
                    Visitor.vehicle_plate.ilike(f"%{query_str}%"),
                    Visitor.company_name.ilike(f"%{query_str}%"),
                ),
            )
        )

        if condominium_id:
            query = query.where(Visitor.default_condominium_id == condominium_id)

        query = query.order_by(Visitor.name).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_blocked(
        self, skip: int = 0, limit: int = 20
    ) -> list[Visitor]:
        """Lista visitantes bloqueados."""
        result = await self.session.execute(
            select(Visitor)
            .where(
                and_(
                    Visitor.status == VisitorStatus.BLOQUEADO,
                    Visitor.is_deleted.is_(False),
                )
            )
            .order_by(Visitor.blocked_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_vip(self, skip: int = 0, limit: int = 20) -> list[Visitor]:
        """Lista visitantes VIP."""
        result = await self.session.execute(
            select(Visitor)
            .where(
                and_(
                    Visitor.status == VisitorStatus.VIP,
                    Visitor.is_deleted.is_(False),
                )
            )
            .order_by(Visitor.name)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_frequent(
        self, min_visits: int = 10, skip: int = 0, limit: int = 20
    ) -> list[Visitor]:
        """Lista visitantes frequentes."""
        result = await self.session.execute(
            select(Visitor)
            .where(
                and_(
                    Visitor.visit_count >= min_visits,
                    Visitor.is_deleted.is_(False),
                )
            )
            .order_by(Visitor.visit_count.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_condominium(
        self, condominium_id: str, skip: int = 0, limit: int = 20
    ) -> list[Visitor]:
        """Lista visitantes de um condomínio."""
        result = await self.session.execute(
            select(Visitor)
            .where(
                and_(
                    Visitor.default_condominium_id == condominium_id,
                    Visitor.is_deleted.is_(False),
                )
            )
            .order_by(Visitor.name)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_stats(
        self, condominium_id: str = None, date_from: datetime = None
    ) -> dict:
        """Retorna estatísticas de visitantes."""
        base_query = select(Visitor).where(Visitor.is_deleted.is_(False))

        if condominium_id:
            base_query = base_query.where(
                Visitor.default_condominium_id == condominium_id
            )
        if date_from:
            base_query = base_query.where(Visitor.created_at >= date_from)

        # Contar total
        count_result = await self.session.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total = count_result.scalar() or 0

        # Por status
        status_query = (
            select(Visitor.status, func.count())
            .where(Visitor.is_deleted.is_(False))
            .group_by(Visitor.status)
        )
        if condominium_id:
            status_query = status_query.where(
                Visitor.default_condominium_id == condominium_id
            )

        status_result = await self.session.execute(status_query)
        by_status = {str(row[0].value): row[1] for row in status_result.all()}

        # Por tipo
        type_query = (
            select(Visitor.visitor_type, func.count())
            .where(Visitor.is_deleted.is_(False))
            .group_by(Visitor.visitor_type)
        )
        if condominium_id:
            type_query = type_query.where(
                Visitor.default_condominium_id == condominium_id
            )

        type_result = await self.session.execute(type_query)
        by_type = {str(row[0].value): row[1] for row in type_result.all()}

        # Com veículo
        vehicle_query = (
            select(func.count())
            .select_from(Visitor)
            .where(
                and_(
                    Visitor.vehicle_plate.isnot(None),
                    Visitor.is_deleted.is_(False),
                )
            )
        )
        if condominium_id:
            vehicle_query = vehicle_query.where(
                Visitor.default_condominium_id == condominium_id
            )
        vehicle_result = await self.session.execute(vehicle_query)
        with_vehicle = vehicle_result.scalar() or 0

        # Com biometria
        bio_query = (
            select(func.count())
            .select_from(Visitor)
            .where(
                and_(
                    or_(
                        Visitor.biometric_template.isnot(None),
                        Visitor.face_encoding.isnot(None),
                    ),
                    Visitor.is_deleted.is_(False),
                )
            )
        )
        if condominium_id:
            bio_query = bio_query.where(
                Visitor.default_condominium_id == condominium_id
            )
        bio_result = await self.session.execute(bio_query)
        with_biometric = bio_result.scalar() or 0

        # Média de visitas
        avg_query = (
            select(func.avg(Visitor.visit_count))
            .where(Visitor.is_deleted.is_(False))
        )
        if condominium_id:
            avg_query = avg_query.where(
                Visitor.default_condominium_id == condominium_id
            )
        avg_result = await self.session.execute(avg_query)
        avg_visits = avg_result.scalar() or 0

        # Total de visitas
        total_visits_query = (
            select(func.sum(Visitor.visit_count))
            .where(Visitor.is_deleted.is_(False))
        )
        if condominium_id:
            total_visits_query = total_visits_query.where(
                Visitor.default_condominium_id == condominium_id
            )
        total_visits_result = await self.session.execute(total_visits_query)
        total_visits = total_visits_result.scalar() or 0

        return {
            "total": total,
            "active": by_status.get("ativo", 0),
            "blocked": by_status.get("bloqueado", 0),
            "vip": by_status.get("vip", 0),
            "temporary": by_status.get("temporario", 0),
            "inactive": by_status.get("inativo", 0),
            "by_type": by_type,
            "with_vehicle": with_vehicle,
            "with_biometric": with_biometric,
            "avg_visits": float(avg_visits),
            "total_visits": int(total_visits),
        }

    async def block(
        self,
        visitor_id: str | UUID,
        reason: str,
        blocked_by_id: str = None,
        blocked_by_name: str = None,
        until: datetime = None,
    ) -> Optional[Visitor]:
        """Bloqueia um visitante."""
        visitor = await self.get_by_id(visitor_id)
        if not visitor:
            return None

        visitor.block(reason, blocked_by_id, blocked_by_name, until)
        await self.session.flush()
        logger.warning(f"Visitante bloqueado: {visitor.code} - {reason}")
        return visitor

    async def unblock(self, visitor_id: str | UUID) -> Optional[Visitor]:
        """Desbloqueia um visitante."""
        visitor = await self.get_by_id(visitor_id)
        if not visitor:
            return None

        visitor.unblock()
        await self.session.flush()
        logger.info(f"Visitante desbloqueado: {visitor.code}")
        return visitor

    async def set_vip(self, visitor_id: str | UUID) -> Optional[Visitor]:
        """Define visitante como VIP."""
        visitor = await self.get_by_id(visitor_id)
        if not visitor:
            return None

        visitor.set_vip()
        await self.session.flush()
        return visitor

    async def register_visit(
        self, visitor_id: str | UUID, duration_minutes: int = None
    ) -> Optional[Visitor]:
        """Registra uma visita."""
        visitor = await self.get_by_id(visitor_id)
        if not visitor:
            return None

        visitor.register_visit(duration_minutes)
        await self.session.flush()
        return visitor
