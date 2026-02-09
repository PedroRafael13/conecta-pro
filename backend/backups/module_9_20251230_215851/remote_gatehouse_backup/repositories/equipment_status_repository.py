"""
Repository para EquipmentStatus.
"""

from datetime import datetime, timedelta

from modules.remote_gatehouse.models.equipment_status import (
    EquipmentStatus,
    EquipmentStatusType,
)
from modules.remote_gatehouse.schemas.equipment_status import (
    EquipmentStatusCreate,
    EquipmentStatusFilter,
    EquipmentStatusStats,
    EquipmentStatusUpdate,
)
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession


class EquipmentStatusRepository:
    """Repository para operações com EquipmentStatus."""

    def __init__(self, db: AsyncSession) -> None:
        """Inicializa o repository."""
        self.db = db

    async def create(self, data: EquipmentStatusCreate) -> EquipmentStatus:
        """Cria um novo status de equipamento."""
        equipment = EquipmentStatus(
            guardian_id=data.guardian_id,
            equipment_id=data.equipment_id,
            equipment_type=data.equipment_type,
            equipment_name=data.equipment_name,
            equipment_model=data.equipment_model,
            equipment_brand=data.equipment_brand,
            serial_number=data.serial_number,
            firmware_version=data.firmware_version,
            status=data.status,
            status_message=data.status_message,
            status_code=data.status_code,
            client_id=data.client_id,
            contract_id=data.contract_id,
            post_id=data.post_id,
            location=data.location,
            location_details=data.location_details,
            ip_address=data.ip_address,
            mac_address=data.mac_address,
            port=data.port,
            last_ping_at=data.last_ping_at,
            ping_latency_ms=data.ping_latency_ms,
            uptime_percentage=data.uptime_percentage,
            metrics=data.metrics,
            has_alerts=data.has_alerts,
            active_alerts=data.active_alerts,
            next_maintenance_at=data.next_maintenance_at,
            maintenance_notes=data.maintenance_notes,
            guardian_metadata=data.guardian_metadata,
        )

        self.db.add(equipment)
        await self.db.commit()
        await self.db.refresh(equipment)
        return equipment

    async def get_by_id(self, equipment_id: str) -> EquipmentStatus | None:
        """Busca equipamento por ID."""
        result = await self.db.execute(
            select(EquipmentStatus).where(
                EquipmentStatus.id == equipment_id,
                EquipmentStatus.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_guardian_id(
        self,
        guardian_id: str,
    ) -> EquipmentStatus | None:
        """Busca equipamento por ID do Guardian."""
        result = await self.db.execute(
            select(EquipmentStatus).where(
                EquipmentStatus.guardian_id == guardian_id,
                EquipmentStatus.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_equipment_id(
        self,
        equipment_id: str,
        client_id: str,
    ) -> EquipmentStatus | None:
        """Busca por equipment_id e client_id."""
        result = await self.db.execute(
            select(EquipmentStatus).where(
                EquipmentStatus.equipment_id == equipment_id,
                EquipmentStatus.client_id == client_id,
                EquipmentStatus.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        filters: EquipmentStatusFilter,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[EquipmentStatus], int]:
        """Lista equipamentos com filtros e paginação."""
        query = select(EquipmentStatus).where(EquipmentStatus.is_active.is_(True))

        # Aplicar filtros
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.where(
                or_(
                    EquipmentStatus.equipment_name.ilike(search_term),
                    EquipmentStatus.equipment_id.ilike(search_term),
                    EquipmentStatus.ip_address.ilike(search_term),
                    EquipmentStatus.location.ilike(search_term),
                )
            )

        if filters.equipment_type:
            query = query.where(EquipmentStatus.equipment_type == filters.equipment_type)

        if filters.status:
            query = query.where(EquipmentStatus.status == filters.status)

        if filters.client_id:
            query = query.where(EquipmentStatus.client_id == filters.client_id)

        if filters.post_id:
            query = query.where(EquipmentStatus.post_id == filters.post_id)

        if filters.is_online is True:
            query = query.where(EquipmentStatus.status == EquipmentStatusType.ONLINE.value)
        elif filters.is_online is False:
            query = query.where(EquipmentStatus.status != EquipmentStatusType.ONLINE.value)

        if filters.has_alerts is not None:
            query = query.where(EquipmentStatus.has_alerts == filters.has_alerts)

        if filters.has_issues is True:
            query = query.where(
                EquipmentStatus.status.in_(
                    [
                        EquipmentStatusType.WARNING.value,
                        EquipmentStatusType.ERROR.value,
                    ]
                )
            )

        if filters.needs_maintenance is True:
            now = datetime.utcnow()
            query = query.where(EquipmentStatus.next_maintenance_at <= now + timedelta(days=7))

        # Contar total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Aplicar paginação
        offset = (page - 1) * page_size
        query = query.order_by(
            EquipmentStatus.status,
            EquipmentStatus.equipment_name,
        )
        query = query.offset(offset).limit(page_size)

        result = await self.db.execute(query)
        equipments = list(result.scalars().all())

        return equipments, total

    async def update(
        self,
        equipment_id: str,
        data: EquipmentStatusUpdate,
    ) -> EquipmentStatus | None:
        """Atualiza status de um equipamento."""
        equipment = await self.get_by_id(equipment_id)
        if not equipment:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(equipment, field, value)

        await self.db.commit()
        await self.db.refresh(equipment)
        return equipment

    async def update_by_guardian_id(
        self,
        guardian_id: str,
        data: EquipmentStatusUpdate,
    ) -> EquipmentStatus | None:
        """Atualiza status pelo ID do Guardian."""
        equipment = await self.get_by_guardian_id(guardian_id)
        if not equipment:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(equipment, field, value)

        # Atualizar timestamps de status
        if data.status == EquipmentStatusType.ONLINE:
            equipment.last_online_at = datetime.utcnow()
        elif data.status == EquipmentStatusType.OFFLINE:
            equipment.last_offline_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(equipment)
        return equipment

    async def get_offline(
        self,
        client_id: str | None = None,
        limit: int = 100,
    ) -> list[EquipmentStatus]:  # noqa: A003
        """Busca equipamentos offline."""
        query = select(EquipmentStatus).where(
            EquipmentStatus.status == EquipmentStatusType.OFFLINE.value,
            EquipmentStatus.is_active.is_(True),
        )

        if client_id:
            query = query.where(EquipmentStatus.client_id == client_id)

        query = query.order_by(EquipmentStatus.last_offline_at).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_with_alerts(
        self,
        client_id: str | None = None,
        limit: int = 100,
    ) -> list[EquipmentStatus]:  # noqa: A003
        """Busca equipamentos com alertas."""
        query = select(EquipmentStatus).where(
            EquipmentStatus.has_alerts.is_(True),
            EquipmentStatus.is_active.is_(True),
        )

        if client_id:
            query = query.where(EquipmentStatus.client_id == client_id)

        query = query.order_by(EquipmentStatus.alert_count.desc()).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_needs_maintenance(
        self,
        days_ahead: int = 7,
        client_id: str | None = None,
    ) -> list[EquipmentStatus]:  # noqa: A003
        """Busca equipamentos que precisam de manutenção."""
        cutoff = datetime.utcnow() + timedelta(days=days_ahead)

        query = select(EquipmentStatus).where(
            EquipmentStatus.next_maintenance_at <= cutoff,
            EquipmentStatus.is_active.is_(True),
        )

        if client_id:
            query = query.where(EquipmentStatus.client_id == client_id)

        query = query.order_by(EquipmentStatus.next_maintenance_at)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_stats(
        self,
        client_id: str | None = None,
    ) -> EquipmentStatusStats:
        """Retorna estatísticas de equipamentos."""
        base_query = select(EquipmentStatus).where(EquipmentStatus.is_active.is_(True))

        if client_id:
            base_query = base_query.where(EquipmentStatus.client_id == client_id)

        # Contagem total
        total_result = await self.db.execute(select(func.count()).select_from(base_query.subquery()))
        total = total_result.scalar() or 0

        # Contagem por status
        status_counts = {}
        for status in EquipmentStatusType:
            status_query = base_query.where(EquipmentStatus.status == status.value)
            count_result = await self.db.execute(select(func.count()).select_from(status_query.subquery()))
            status_counts[status.value] = count_result.scalar() or 0

        # Com alertas
        alerts_result = await self.db.execute(
            select(func.count()).select_from(base_query.where(EquipmentStatus.has_alerts.is_(True)).subquery())
        )
        with_alerts = alerts_result.scalar() or 0

        # Precisa manutenção
        cutoff = datetime.utcnow() + timedelta(days=7)
        maintenance_result = await self.db.execute(
            select(func.count()).select_from(base_query.where(EquipmentStatus.next_maintenance_at <= cutoff).subquery())
        )
        needs_maintenance = maintenance_result.scalar() or 0

        # Médias
        avg_uptime_result = await self.db.execute(
            select(func.avg(EquipmentStatus.uptime_percentage)).select_from(base_query.subquery())
        )
        avg_uptime = avg_uptime_result.scalar() or 0.0

        avg_latency_result = await self.db.execute(
            select(func.avg(EquipmentStatus.ping_latency_ms)).where(
                EquipmentStatus.is_active.is_(True),
                EquipmentStatus.ping_latency_ms.isnot(None),
            )
        )
        avg_latency = avg_latency_result.scalar() or 0.0

        online = status_counts.get(EquipmentStatusType.ONLINE.value, 0)
        availability_rate = (online / total * 100) if total > 0 else 0.0

        return EquipmentStatusStats(
            total=total,
            online=online,
            offline=status_counts.get(EquipmentStatusType.OFFLINE.value, 0),
            warning=status_counts.get(EquipmentStatusType.WARNING.value, 0),
            error=status_counts.get(EquipmentStatusType.ERROR.value, 0),
            maintenance=status_counts.get(EquipmentStatusType.MAINTENANCE.value, 0),
            disabled=status_counts.get(EquipmentStatusType.DISABLED.value, 0),
            availability_rate=round(availability_rate, 2),
            by_type={},
            by_client={},
            with_alerts=with_alerts,
            needs_maintenance=needs_maintenance,
            avg_uptime_percentage=round(float(avg_uptime), 2),
            avg_ping_latency_ms=round(float(avg_latency), 2),
        )

    async def delete(self, equipment_id: str) -> bool:
        """Remove um equipamento (soft delete)."""
        equipment = await self.get_by_id(equipment_id)
        if equipment:
            equipment.is_active = False
            await self.db.commit()
            return True
        return False
