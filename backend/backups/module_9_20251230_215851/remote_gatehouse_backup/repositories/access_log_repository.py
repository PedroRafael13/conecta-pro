"""
Repository para AccessLog.
"""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.remote_gatehouse.models.access_log import AccessLog, AccessLogType
from modules.remote_gatehouse.schemas.access_log import (
    AccessLogCreate,
    AccessLogFilter,
    AccessLogStats,
)


class AccessLogRepository:
    """Repository para operações com AccessLog."""

    def __init__(self, db: AsyncSession) -> None:
        """Inicializa o repository."""
        self.db = db

    async def create(self, data: AccessLogCreate) -> AccessLog:
        """Cria um novo log de acesso."""
        log = AccessLog(
            guardian_id=data.guardian_id,
            log_type=data.log_type,
            client_id=data.client_id,
            contract_id=data.contract_id,
            post_id=data.post_id,
            person_name=data.person_name,
            person_document=data.person_document,
            person_type=data.person_type,
            person_id=data.person_id,
            unit_code=data.unit_code,
            unit_block=data.unit_block,
            access_point=data.access_point,
            access_point_id=data.access_point_id,
            access_method=data.access_method,
            device_id=data.device_id,
            device_name=data.device_name,
            vehicle_plate=data.vehicle_plate,
            vehicle_model=data.vehicle_model,
            vehicle_color=data.vehicle_color,
            operator_id=data.operator_id,
            operator_name=data.operator_name,
            authorization_type=data.authorization_type,
            photos=data.photos,
            video_clip_url=data.video_clip_url,
            notes=data.notes,
            denial_reason=data.denial_reason,
            event_timestamp=data.event_timestamp,
            latitude=data.latitude,
            longitude=data.longitude,
            guardian_metadata=data.guardian_metadata,
        )

        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def create_batch(self, data_list: list[AccessLogCreate]) -> list[AccessLog]:
        """Cria múltiplos logs de acesso."""
        logs = []
        for data in data_list:
            log = AccessLog(
                guardian_id=data.guardian_id,
                log_type=data.log_type,
                client_id=data.client_id,
                contract_id=data.contract_id,
                post_id=data.post_id,
                person_name=data.person_name,
                person_document=data.person_document,
                person_type=data.person_type,
                person_id=data.person_id,
                unit_code=data.unit_code,
                unit_block=data.unit_block,
                access_point=data.access_point,
                access_point_id=data.access_point_id,
                access_method=data.access_method,
                device_id=data.device_id,
                device_name=data.device_name,
                vehicle_plate=data.vehicle_plate,
                vehicle_model=data.vehicle_model,
                vehicle_color=data.vehicle_color,
                operator_id=data.operator_id,
                operator_name=data.operator_name,
                authorization_type=data.authorization_type,
                photos=data.photos,
                video_clip_url=data.video_clip_url,
                notes=data.notes,
                denial_reason=data.denial_reason,
                event_timestamp=data.event_timestamp,
                latitude=data.latitude,
                longitude=data.longitude,
                guardian_metadata=data.guardian_metadata,
            )
            logs.append(log)
            self.db.add(log)

        await self.db.commit()
        for log in logs:
            await self.db.refresh(log)
        return logs

    async def get_by_id(self, log_id: str) -> Optional[AccessLog]:
        """Busca log por ID."""
        result = await self.db.execute(
            select(AccessLog).where(
                AccessLog.id == log_id,
                AccessLog.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_guardian_id(self, guardian_id: str) -> Optional[AccessLog]:
        """Busca log por ID do Guardian."""
        result = await self.db.execute(
            select(AccessLog).where(
                AccessLog.guardian_id == guardian_id,
                AccessLog.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        filters: AccessLogFilter,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[AccessLog], int]:
        """Lista logs com filtros e paginação."""
        query = select(AccessLog).where(AccessLog.is_active.is_(True))

        # Aplicar filtros
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.where(
                or_(
                    AccessLog.person_name.ilike(search_term),
                    AccessLog.person_document.ilike(search_term),
                    AccessLog.vehicle_plate.ilike(search_term),
                    AccessLog.unit_code.ilike(search_term),
                )
            )

        if filters.log_type:
            query = query.where(AccessLog.log_type == filters.log_type)

        if filters.client_id:
            query = query.where(AccessLog.client_id == filters.client_id)

        if filters.post_id:
            query = query.where(AccessLog.post_id == filters.post_id)

        if filters.person_type:
            query = query.where(AccessLog.person_type == filters.person_type)

        if filters.access_method:
            query = query.where(AccessLog.access_method == filters.access_method)

        if filters.unit_code:
            query = query.where(AccessLog.unit_code == filters.unit_code)

        if filters.vehicle_plate:
            query = query.where(AccessLog.vehicle_plate.ilike(f"%{filters.vehicle_plate}%"))

        if filters.date_from:
            query = query.where(AccessLog.event_timestamp >= filters.date_from)

        if filters.date_to:
            query = query.where(AccessLog.event_timestamp <= filters.date_to)

        if filters.is_denied is True:
            query = query.where(AccessLog.log_type == AccessLogType.DENIED.value)
        elif filters.is_denied is False:
            query = query.where(AccessLog.log_type != AccessLogType.DENIED.value)

        # Contar total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Aplicar paginação
        offset = (page - 1) * page_size
        query = query.order_by(AccessLog.event_timestamp.desc())
        query = query.offset(offset).limit(page_size)

        result = await self.db.execute(query)
        logs = list(result.scalars().all())

        return logs, total

    async def get_by_person(
        self,
        person_document: str,
        limit: int = 50,
    ) -> list[AccessLog]:
        """Busca logs por documento da pessoa."""
        result = await self.db.execute(
            select(AccessLog)
            .where(
                AccessLog.person_document == person_document,
                AccessLog.is_active.is_(True),
            )
            .order_by(AccessLog.event_timestamp.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_vehicle(
        self,
        vehicle_plate: str,
        limit: int = 50,
    ) -> list[AccessLog]:
        """Busca logs por placa do veículo."""
        result = await self.db.execute(
            select(AccessLog)
            .where(
                AccessLog.vehicle_plate == vehicle_plate.upper(),
                AccessLog.is_active.is_(True),
            )
            .order_by(AccessLog.event_timestamp.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_stats(
        self,
        client_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> AccessLogStats:
        """Retorna estatísticas de logs de acesso."""
        if not date_from:
            date_from = datetime.utcnow() - timedelta(days=30)
        if not date_to:
            date_to = datetime.utcnow()

        base_query = select(AccessLog).where(
            AccessLog.is_active.is_(True),
            AccessLog.event_timestamp >= date_from,
            AccessLog.event_timestamp <= date_to,
        )

        if client_id:
            base_query = base_query.where(AccessLog.client_id == client_id)

        # Contagem total
        total_result = await self.db.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total = total_result.scalar() or 0

        # Contagem por tipo
        type_counts = {}
        for log_type in AccessLogType:
            type_query = base_query.where(AccessLog.log_type == log_type.value)
            count_result = await self.db.execute(
                select(func.count()).select_from(type_query.subquery())
            )
            type_counts[log_type.value] = count_result.scalar() or 0

        # Calcular dias no período
        days = (date_to - date_from).days or 1
        avg_daily = total / days

        return AccessLogStats(
            total=total,
            entries=type_counts.get(AccessLogType.ENTRY.value, 0),
            exits=type_counts.get(AccessLogType.EXIT.value, 0),
            denied=type_counts.get(AccessLogType.DENIED.value, 0),
            visitors=type_counts.get(AccessLogType.VISITOR.value, 0),
            deliveries=type_counts.get(AccessLogType.DELIVERY.value, 0),
            by_access_method={},
            by_access_point={},
            by_hour={},
            by_day_of_week={},
            peak_hours=[],
            avg_daily=round(avg_daily, 2),
        )

    async def delete(self, log_id: str) -> bool:
        """Remove um log (soft delete)."""
        log = await self.get_by_id(log_id)
        if log:
            log.is_active = False
            await self.db.commit()
            return True
        return False
