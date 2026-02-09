"""Repository para OfflineQueue."""

from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.mobile_time_clock.models import (
    OfflineQueue,
    QueueStatus,
)
from modules.hr.mobile_time_clock.schemas import (
    OfflineQueueFilter,
    OfflineQueueItemCreate,
)


class OfflineQueueRepository:
    """Repository para operações com fila offline."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        data: OfflineQueueItemCreate,
        device_id: UUID,
        employee_id: UUID,
        condominio_id: UUID,
    ) -> OfflineQueue:
        """Cria novo item na fila."""
        item = OfflineQueue(
            device_id=device_id,
            employee_id=employee_id,
            condominio_id=condominio_id,
            offline_id=data.offline_id,
            checkin_data=data.checkin_data,
            checkin_type=data.checkin_type,
            device_timestamp=data.device_timestamp,
            latitude=data.latitude,
            longitude=data.longitude,
            accuracy_meters=data.accuracy_meters,
            local_validation=data.local_validation,
            local_geofence_check=data.local_geofence_check,
            local_biometric_check=data.local_biometric_check,
            app_version=data.app_version,
            device_info=data.device_info or {},
            network_type=data.network_type,
            queued_at=data.device_timestamp,
            received_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=data.expires_hours),
        )

        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def create_batch(
        self,
        items: list[OfflineQueueItemCreate],
        device_id: UUID,
        employee_id: UUID,
        condominio_id: UUID,
    ) -> list[OfflineQueue]:
        """Cria múltiplos itens na fila."""
        created = []
        for data in items:
            # Verificar duplicata
            existing = await self.get_by_offline_id(data.offline_id)
            if existing:
                continue

            item = await self.create(data, device_id, employee_id, condominio_id)
            created.append(item)

        return created

    async def get_by_id(self, item_id: UUID) -> OfflineQueue | None:
        """Busca item por ID."""
        result = await self.db.execute(select(OfflineQueue).where(OfflineQueue.id == item_id))
        return result.scalar_one_or_none()

    async def get_by_offline_id(self, offline_id: str) -> OfflineQueue | None:
        """Busca item por offline_id."""
        result = await self.db.execute(select(OfflineQueue).where(OfflineQueue.offline_id == offline_id))
        return result.scalar_one_or_none()

    async def get_pending(
        self,
        device_id: UUID = None,
        limit: int = 50,
    ) -> list[OfflineQueue]:
        """Busca itens pendentes para processamento."""
        query = select(OfflineQueue).where(
            OfflineQueue.status == QueueStatus.PENDING.value,
            OfflineQueue.is_expired.is_(False),
        )

        if device_id:
            query = query.where(OfflineQueue.device_id == device_id)

        # Verificar retry
        query = query.where((OfflineQueue.next_retry_at.is_(None)) | (OfflineQueue.next_retry_at <= datetime.utcnow()))

        result = await self.db.execute(
            query.order_by(
                OfflineQueue.priority.desc(),
                OfflineQueue.queued_at.asc(),
            ).limit(limit)
        )
        return list(result.scalars().all())

    async def get_failed_for_retry(
        self,
        limit: int = 20,
    ) -> list[OfflineQueue]:
        """Busca itens falhos elegíveis para retry."""
        now = datetime.utcnow()
        result = await self.db.execute(
            select(OfflineQueue)
            .where(OfflineQueue.status == QueueStatus.FAILED.value)
            .where(OfflineQueue.is_expired.is_(False))
            .where(OfflineQueue.retry_count < OfflineQueue.max_retries)
            .where(OfflineQueue.next_retry_at <= now)
            .order_by(OfflineQueue.next_retry_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def mark_processing(self, item_id: UUID) -> OfflineQueue | None:
        """Marca item como em processamento."""
        item = await self.get_by_id(item_id)
        if not item:
            return None

        item.mark_processing()
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def mark_synced(
        self,
        item_id: UUID,
        checkin_id: UUID,
    ) -> OfflineQueue | None:
        """Marca item como sincronizado."""
        item = await self.get_by_id(item_id)
        if not item:
            return None

        item.mark_synced(checkin_id)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def mark_failed(
        self,
        item_id: UUID,
        error_message: str,
        error_code: str = None,
    ) -> OfflineQueue | None:
        """Marca item como falho."""
        item = await self.get_by_id(item_id)
        if not item:
            return None

        item.mark_failed(error_message, error_code)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def mark_duplicate(self, item_id: UUID) -> OfflineQueue | None:
        """Marca item como duplicado."""
        item = await self.get_by_id(item_id)
        if not item:
            return None

        item.status = QueueStatus.DUPLICATE.value
        item.processed_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def mark_invalid(
        self,
        item_id: UUID,
        reason: str,
    ) -> OfflineQueue | None:
        """Marca item como inválido."""
        item = await self.get_by_id(item_id)
        if not item:
            return None

        item.status = QueueStatus.INVALID.value
        item.error_message = reason
        item.processed_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def mark_expired_items(self) -> int:
        """Marca itens expirados."""
        now = datetime.utcnow()
        result = await self.db.execute(
            update(OfflineQueue)
            .where(OfflineQueue.expires_at < now)
            .where(
                OfflineQueue.status.in_(
                    [
                        QueueStatus.PENDING.value,
                        QueueStatus.FAILED.value,
                    ]
                )
            )
            .values(
                status=QueueStatus.EXPIRED.value,
                is_expired=True,
                processed_at=now,
            )
        )
        await self.db.commit()
        return result.rowcount

    async def reset_for_retry(
        self,
        item_ids: list[UUID],
        force: bool = False,
    ) -> int:
        """Reseta itens para retry."""
        query = update(OfflineQueue).where(OfflineQueue.id.in_(item_ids))

        if not force:
            query = query.where(
                OfflineQueue.status.in_(
                    [
                        QueueStatus.FAILED.value,
                        QueueStatus.INVALID.value,
                    ]
                )
            )

        result = await self.db.execute(
            query.values(
                status=QueueStatus.PENDING.value,
                retry_count=0,
                next_retry_at=None,
                error_message=None,
                error_code=None,
            )
        )
        await self.db.commit()
        return result.rowcount

    async def list_items(
        self,
        filters: OfflineQueueFilter,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[OfflineQueue], int]:
        """Lista itens com filtros."""
        query = select(OfflineQueue)

        if filters.device_id:
            query = query.where(OfflineQueue.device_id == filters.device_id)
        if filters.employee_id:
            query = query.where(OfflineQueue.employee_id == filters.employee_id)
        if filters.condominio_id:
            query = query.where(OfflineQueue.condominio_id == filters.condominio_id)
        if filters.status:
            query = query.where(OfflineQueue.status == filters.status)
        if filters.priority:
            query = query.where(OfflineQueue.priority == filters.priority)
        if filters.is_expired is not None:
            query = query.where(OfflineQueue.is_expired == filters.is_expired)
        if filters.date_from:
            query = query.where(OfflineQueue.queued_at >= filters.date_from)
        if filters.date_to:
            query = query.where(OfflineQueue.queued_at <= filters.date_to)

        # Total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginação
        query = query.order_by(OfflineQueue.queued_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_statistics(
        self,
        condominio_id: UUID = None,
    ) -> dict:
        """Obtém estatísticas da fila."""
        query = select(OfflineQueue)
        if condominio_id:
            query = query.where(OfflineQueue.condominio_id == condominio_id)

        result = await self.db.execute(query)
        items = list(result.scalars().all())

        now = datetime.utcnow()
        by_status = {}
        by_priority = {}
        ages = []
        retries = []
        oldest_pending = None

        for item in items:
            by_status[item.status] = by_status.get(item.status, 0) + 1
            by_priority[item.priority] = by_priority.get(item.priority, 0) + 1

            age_hours = (now - item.queued_at).total_seconds() / 3600
            ages.append(age_hours)
            retries.append(item.retry_count)

            if item.status == QueueStatus.PENDING.value:
                if oldest_pending is None or item.queued_at < oldest_pending:
                    oldest_pending = item.queued_at

        return {
            "total_items": len(items),
            "pending_items": by_status.get(QueueStatus.PENDING.value, 0),
            "processing_items": by_status.get(QueueStatus.PROCESSING.value, 0),
            "synced_items": by_status.get(QueueStatus.SYNCED.value, 0),
            "failed_items": by_status.get(QueueStatus.FAILED.value, 0),
            "expired_items": by_status.get(QueueStatus.EXPIRED.value, 0),
            "by_status": by_status,
            "by_priority": by_priority,
            "avg_age_hours": sum(ages) / len(ages) if ages else 0,
            "avg_retry_count": sum(retries) / len(retries) if retries else 0,
            "oldest_pending": oldest_pending,
        }

    async def cleanup(
        self,
        older_than_hours: int = 72,
        statuses: list[str] = None,
        dry_run: bool = True,
    ) -> dict:
        """Limpa itens antigos da fila."""
        if statuses is None:
            statuses = [
                QueueStatus.SYNCED.value,
                QueueStatus.EXPIRED.value,
                QueueStatus.DUPLICATE.value,
                QueueStatus.INVALID.value,
            ]

        cutoff = datetime.utcnow() - timedelta(hours=older_than_hours)

        # Contar por status
        count_by_status = {}
        for status in statuses:
            count_result = await self.db.execute(
                select(func.count())
                .select_from(OfflineQueue)
                .where(OfflineQueue.status == status)
                .where(OfflineQueue.queued_at < cutoff)
            )
            count_by_status[status] = count_result.scalar() or 0

        total_to_delete = sum(count_by_status.values())

        if not dry_run and total_to_delete > 0:
            await self.db.execute(
                delete(OfflineQueue).where(OfflineQueue.status.in_(statuses)).where(OfflineQueue.queued_at < cutoff)
            )
            await self.db.commit()

        return {
            "deleted_count": total_to_delete if not dry_run else 0,
            "would_delete": total_to_delete,
            "by_status": count_by_status,
            "dry_run": dry_run,
        }

    async def get_device_queue_count(self, device_id: UUID) -> int:
        """Conta itens pendentes do dispositivo."""
        result = await self.db.execute(
            select(func.count())
            .select_from(OfflineQueue)
            .where(OfflineQueue.device_id == device_id)
            .where(
                OfflineQueue.status.in_(
                    [
                        QueueStatus.PENDING.value,
                        QueueStatus.PROCESSING.value,
                        QueueStatus.FAILED.value,
                    ]
                )
            )
        )
        return result.scalar() or 0

    async def delete(self, item_id: UUID) -> bool:
        """Remove item da fila."""
        item = await self.get_by_id(item_id)
        if not item:
            return False

        await self.db.delete(item)
        await self.db.commit()
        return True
