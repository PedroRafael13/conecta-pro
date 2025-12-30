"""Repository para VisitorLog."""

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, extract, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.visitors.models.log import (
    AccessMethod,
    AccessPoint,
    AccessType,
    DenialReason,
    VisitorLog,
)
from modules.visitors.schemas.log import LogDeny, LogEntry, LogExit, LogFilter

logger = logging.getLogger(__name__)


class LogRepository:
    """Repository para operações de VisitorLog."""

    def __init__(self, session: AsyncSession):
        """Inicializa o repository."""
        self.session = session

    async def create_entry(self, data: LogEntry) -> VisitorLog:
        """Cria registro de entrada."""
        log = VisitorLog(**data.model_dump(exclude_none=True))
        log.register_entry(
            method=data.access_method,
            point=data.access_point,
            operator_id=data.operator_id,
            operator_name=data.operator_name,
        )
        self.session.add(log)
        await self.session.flush()
        await self.session.refresh(log)
        logger.info(f"Entrada registrada: visitante {data.visitor_id}")
        return log

    async def create_exit(self, data: LogExit) -> Optional[VisitorLog]:
        """Cria registro de saída."""
        # Buscar entrada sem saída
        entry = await self.get_current_entry(
            data.visitor_id, data.condominium_id
        )

        if entry:
            entry.register_exit(
                method=data.access_method,
                point=data.access_point,
                operator_id=data.operator_id,
                operator_name=data.operator_name,
            )
            if data.notes:
                entry.notes = (
                    f"{entry.notes or ''}\n{data.notes}".strip()
                )
            await self.session.flush()
            logger.info(f"Saída registrada: visitante {data.visitor_id}")
            return entry

        # Se não há entrada, criar log de saída avulso
        log = VisitorLog(
            visitor_id=data.visitor_id,
            condominium_id=data.condominium_id,
            access_type=AccessType.SAIDA,
            access_method=data.access_method,
            access_point=data.access_point,
            exit_at=datetime.utcnow(),
            timestamp=datetime.utcnow(),
            operator_id=data.operator_id,
            operator_name=data.operator_name,
            notes=data.notes,
        )
        self.session.add(log)
        await self.session.flush()
        await self.session.refresh(log)
        return log

    async def create_denial(self, data: LogDeny) -> VisitorLog:
        """Cria registro de negativa."""
        log = VisitorLog(**data.model_dump(exclude_none=True))
        log.deny_access(
            reason=data.denial_reason,
            notes=data.denial_notes,
            operator_id=data.operator_id,
        )
        self.session.add(log)
        await self.session.flush()
        await self.session.refresh(log)
        logger.warning(
            f"Acesso negado: visitante {data.visitor_id} - {data.denial_reason}"
        )
        return log

    async def get_by_id(self, log_id: str | UUID) -> Optional[VisitorLog]:
        """Busca log por ID."""
        if isinstance(log_id, str):
            log_id = UUID(log_id)

        result = await self.session.execute(
            select(VisitorLog).where(
                and_(VisitorLog.id == log_id, VisitorLog.is_deleted.is_(False))
            )
        )
        return result.scalar_one_or_none()

    async def get_current_entry(
        self, visitor_id: str | UUID, condominium_id: str
    ) -> Optional[VisitorLog]:
        """Busca entrada atual (sem saída) do visitante."""
        if isinstance(visitor_id, str):
            visitor_id = UUID(visitor_id)

        result = await self.session.execute(
            select(VisitorLog)
            .where(
                and_(
                    VisitorLog.visitor_id == visitor_id,
                    VisitorLog.condominium_id == condominium_id,
                    VisitorLog.access_type == AccessType.ENTRADA,
                    VisitorLog.exit_at.is_(None),
                    VisitorLog.is_deleted.is_(False),
                )
            )
            .order_by(VisitorLog.entry_at.desc())
        )
        return result.scalar_one_or_none()

    async def list_with_filters(
        self,
        filters: Optional[LogFilter] = None,
        skip: int = 0,
        limit: int = 20,
        order_by: str = "timestamp",
        order_desc: bool = True,
    ) -> tuple[list[VisitorLog], int]:
        """Lista logs com filtros."""
        query = select(VisitorLog).where(VisitorLog.is_deleted.is_(False))

        if filters:
            if filters.visitor_id:
                query = query.where(VisitorLog.visitor_id == filters.visitor_id)
            if filters.condominium_id:
                query = query.where(
                    VisitorLog.condominium_id == filters.condominium_id
                )
            if filters.unit_id:
                query = query.where(VisitorLog.unit_id == filters.unit_id)
            if filters.resident_id:
                query = query.where(VisitorLog.resident_id == filters.resident_id)
            if filters.access_type:
                query = query.where(VisitorLog.access_type == filters.access_type)
            if filters.access_method:
                query = query.where(
                    VisitorLog.access_method == filters.access_method
                )
            if filters.access_point:
                query = query.where(VisitorLog.access_point == filters.access_point)
            if filters.denied is not None:
                query = query.where(VisitorLog.denied == filters.denied)
            if filters.denial_reason:
                query = query.where(
                    VisitorLog.denial_reason == filters.denial_reason
                )
            if filters.has_vehicle is not None:
                if filters.has_vehicle:
                    query = query.where(VisitorLog.vehicle_plate.isnot(None))
                else:
                    query = query.where(VisitorLog.vehicle_plate.is_(None))
            if filters.has_companions is not None:
                if filters.has_companions:
                    query = query.where(VisitorLog.companions_count > 0)
                else:
                    query = query.where(VisitorLog.companions_count == 0)
            if filters.operator_id:
                query = query.where(VisitorLog.operator_id == filters.operator_id)
            if filters.device_id:
                query = query.where(VisitorLog.device_id == filters.device_id)
            if filters.timestamp_from:
                query = query.where(VisitorLog.timestamp >= filters.timestamp_from)
            if filters.timestamp_until:
                query = query.where(VisitorLog.timestamp <= filters.timestamp_until)
            if filters.is_still_inside is not None:
                if filters.is_still_inside:
                    query = query.where(
                        and_(
                            VisitorLog.access_type == AccessType.ENTRADA,
                            VisitorLog.exit_at.is_(None),
                        )
                    )
                else:
                    query = query.where(VisitorLog.exit_at.isnot(None))

        # Contar total
        count_result = await self.session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0

        # Ordenar
        order_column = getattr(VisitorLog, order_by, VisitorLog.timestamp)
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
        skip: int = 0,
        limit: int = 50,
    ) -> list[VisitorLog]:
        """Lista logs de um visitante."""
        if isinstance(visitor_id, str):
            visitor_id = UUID(visitor_id)

        result = await self.session.execute(
            select(VisitorLog)
            .where(
                and_(
                    VisitorLog.visitor_id == visitor_id,
                    VisitorLog.is_deleted.is_(False),
                )
            )
            .order_by(VisitorLog.timestamp.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_inside(
        self, condominium_id: str, skip: int = 0, limit: int = 100
    ) -> list[VisitorLog]:
        """Lista visitantes atualmente dentro."""
        result = await self.session.execute(
            select(VisitorLog)
            .where(
                and_(
                    VisitorLog.condominium_id == condominium_id,
                    VisitorLog.access_type == AccessType.ENTRADA,
                    VisitorLog.exit_at.is_(None),
                    VisitorLog.is_deleted.is_(False),
                )
            )
            .order_by(VisitorLog.entry_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_denied(
        self, condominium_id: str = None, skip: int = 0, limit: int = 50
    ) -> list[VisitorLog]:
        """Lista acessos negados."""
        query = select(VisitorLog).where(
            and_(
                VisitorLog.denied.is_(True),
                VisitorLog.is_deleted.is_(False),
            )
        )

        if condominium_id:
            query = query.where(VisitorLog.condominium_id == condominium_id)

        query = query.order_by(VisitorLog.timestamp.desc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_date_range(
        self,
        condominium_id: str,
        date_from: datetime,
        date_until: datetime,
        access_type: AccessType = None,
    ) -> list[VisitorLog]:
        """Lista logs por período."""
        query = select(VisitorLog).where(
            and_(
                VisitorLog.condominium_id == condominium_id,
                VisitorLog.timestamp >= date_from,
                VisitorLog.timestamp <= date_until,
                VisitorLog.is_deleted.is_(False),
            )
        )

        if access_type:
            query = query.where(VisitorLog.access_type == access_type)

        query = query.order_by(VisitorLog.timestamp.asc())

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_stats(
        self, condominium_id: str = None, date_from: datetime = None
    ) -> dict:
        """Retorna estatísticas de logs."""
        base_cond = [VisitorLog.is_deleted.is_(False)]

        if condominium_id:
            base_cond.append(VisitorLog.condominium_id == condominium_id)
        if date_from:
            base_cond.append(VisitorLog.timestamp >= date_from)

        # Total
        total_result = await self.session.execute(
            select(func.count()).select_from(VisitorLog).where(and_(*base_cond))
        )
        total = total_result.scalar() or 0

        # Por tipo de acesso
        type_query = (
            select(VisitorLog.access_type, func.count())
            .where(and_(*base_cond))
            .group_by(VisitorLog.access_type)
        )
        type_result = await self.session.execute(type_query)
        by_type = {str(row[0].value): row[1] for row in type_result.all()}

        # Por método
        method_query = (
            select(VisitorLog.access_method, func.count())
            .where(and_(*base_cond))
            .group_by(VisitorLog.access_method)
        )
        method_result = await self.session.execute(method_query)
        by_method = {str(row[0].value): row[1] for row in method_result.all()}

        # Por ponto
        point_query = (
            select(VisitorLog.access_point, func.count())
            .where(and_(*base_cond))
            .group_by(VisitorLog.access_point)
        )
        point_result = await self.session.execute(point_query)
        by_point = {str(row[0].value): row[1] for row in point_result.all()}

        # Por hora
        hour_query = (
            select(extract("hour", VisitorLog.timestamp), func.count())
            .where(and_(*base_cond))
            .group_by(extract("hour", VisitorLog.timestamp))
        )
        hour_result = await self.session.execute(hour_query)
        by_hour = {str(int(row[0])): row[1] for row in hour_result.all()}

        # Por dia da semana
        dow_query = (
            select(extract("dow", VisitorLog.timestamp), func.count())
            .where(and_(*base_cond))
            .group_by(extract("dow", VisitorLog.timestamp))
        )
        dow_result = await self.session.execute(dow_query)
        by_dow = {str(int(row[0])): row[1] for row in dow_result.all()}

        # Negados
        denied_result = await self.session.execute(
            select(func.count())
            .select_from(VisitorLog)
            .where(and_(*base_cond, VisitorLog.denied.is_(True)))
        )
        denied = denied_result.scalar() or 0

        # Ainda dentro
        inside_cond = base_cond + [
            VisitorLog.access_type == AccessType.ENTRADA,
            VisitorLog.exit_at.is_(None),
        ]
        inside_result = await self.session.execute(
            select(func.count()).select_from(VisitorLog).where(and_(*inside_cond))
        )
        still_inside = inside_result.scalar() or 0

        # Média duração
        avg_duration_result = await self.session.execute(
            select(func.avg(VisitorLog.duration_minutes))
            .where(and_(*base_cond, VisitorLog.duration_minutes.isnot(None)))
        )
        avg_duration = avg_duration_result.scalar() or 0

        # Com veículo
        vehicle_result = await self.session.execute(
            select(func.count())
            .select_from(VisitorLog)
            .where(and_(*base_cond, VisitorLog.vehicle_plate.isnot(None)))
        )
        with_vehicle = vehicle_result.scalar() or 0

        # Com acompanhantes
        companions_result = await self.session.execute(
            select(func.count())
            .select_from(VisitorLog)
            .where(and_(*base_cond, VisitorLog.companions_count > 0))
        )
        with_companions = companions_result.scalar() or 0

        # Total acompanhantes
        total_companions_result = await self.session.execute(
            select(func.sum(VisitorLog.companions_count)).where(and_(*base_cond))
        )
        total_companions = total_companions_result.scalar() or 0

        # Motivos de negativa
        denial_query = (
            select(VisitorLog.denial_reason, func.count())
            .where(and_(*base_cond, VisitorLog.denied.is_(True)))
            .group_by(VisitorLog.denial_reason)
        )
        denial_result = await self.session.execute(denial_query)
        denial_reasons = {
            str(row[0].value) if row[0] else "outro": row[1]
            for row in denial_result.all()
        }

        return {
            "total": total,
            "entries": by_type.get("entrada", 0),
            "exits": by_type.get("saida", 0),
            "denied": denied,
            "still_inside": still_inside,
            "by_access_type": by_type,
            "by_access_method": by_method,
            "by_access_point": by_point,
            "by_hour": by_hour,
            "by_day_of_week": by_dow,
            "avg_duration_minutes": float(avg_duration),
            "with_vehicle": with_vehicle,
            "with_companions": with_companions,
            "total_companions": int(total_companions),
            "denial_reasons": denial_reasons,
        }

    async def notify_resident(self, log_id: str | UUID) -> Optional[VisitorLog]:
        """Marca morador como notificado."""
        log = await self.get_by_id(log_id)
        if not log:
            return None

        log.notify_resident()
        await self.session.flush()
        return log

    async def count_inside(self, condominium_id: str) -> int:
        """Conta visitantes dentro."""
        result = await self.session.execute(
            select(func.count())
            .select_from(VisitorLog)
            .where(
                and_(
                    VisitorLog.condominium_id == condominium_id,
                    VisitorLog.access_type == AccessType.ENTRADA,
                    VisitorLog.exit_at.is_(None),
                    VisitorLog.is_deleted.is_(False),
                )
            )
        )
        return result.scalar() or 0
