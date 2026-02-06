"""
Repository para GuardianSync.
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.remote_gatehouse.models.guardian_sync import (
    GuardianSync,
    SyncDirection,
    SyncStatus,
)
from modules.remote_gatehouse.schemas.guardian_sync import (
    GuardianSyncCreate,
    GuardianSyncFilter,
    GuardianSyncStats,
)


class GuardianSyncRepository:
    """Repository para operações com GuardianSync."""

    def __init__(self, db: AsyncSession) -> None:
        """Inicializa o repository."""
        self.db = db

    async def create(self, data: GuardianSyncCreate) -> GuardianSync:
        """Cria uma nova sincronização."""
        sync_code = f"SYNC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{str(uuid4())[:8].upper()}"

        sync = GuardianSync(
            sync_code=sync_code,
            direction=data.direction,
            entity_type=data.entity_type,
            entity_id=data.entity_id,
            external_id=data.external_id,
            client_id=data.client_id,
            contract_id=data.contract_id,
            post_id=data.post_id,
            payload=data.payload,
            metadata_extra=data.metadata_extra,
            status=SyncStatus.PENDING.value,
        )

        self.db.add(sync)
        await self.db.commit()
        await self.db.refresh(sync)
        return sync

    async def get_by_id(self, sync_id: str) -> Optional[GuardianSync]:
        """Busca sincronização por ID."""
        result = await self.db.execute(
            select(GuardianSync).where(
                GuardianSync.id == sync_id,
                GuardianSync.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, sync_code: str) -> Optional[GuardianSync]:
        """Busca sincronização por código."""
        result = await self.db.execute(
            select(GuardianSync).where(
                GuardianSync.sync_code == sync_code,
                GuardianSync.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_entity(
        self,
        entity_type: str,
        entity_id: str,
    ) -> Optional[GuardianSync]:
        """Busca última sincronização por entidade."""
        result = await self.db.execute(
            select(GuardianSync)
            .where(
                GuardianSync.entity_type == entity_type,
                GuardianSync.entity_id == entity_id,
                GuardianSync.is_active.is_(True),
            )
            .order_by(GuardianSync.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        filters: GuardianSyncFilter,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[GuardianSync], int]:
        """Lista sincronizações com filtros e paginação."""
        query = select(GuardianSync).where(GuardianSync.is_active.is_(True))

        # Aplicar filtros
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.where(
                or_(
                    GuardianSync.sync_code.ilike(search_term),
                    GuardianSync.entity_id.ilike(search_term),
                    GuardianSync.external_id.ilike(search_term),
                )
            )

        if filters.direction:
            query = query.where(GuardianSync.direction == filters.direction)

        if filters.entity_type:
            query = query.where(GuardianSync.entity_type == filters.entity_type)

        if filters.status:
            query = query.where(GuardianSync.status == filters.status)

        if filters.client_id:
            query = query.where(GuardianSync.client_id == filters.client_id)

        if filters.contract_id:
            query = query.where(GuardianSync.contract_id == filters.contract_id)

        if filters.can_retry is True:
            query = query.where(
                GuardianSync.status == SyncStatus.FAILED.value,
                GuardianSync.retry_count < GuardianSync.max_retries,
            )

        if filters.date_from:
            query = query.where(GuardianSync.created_at >= filters.date_from)

        if filters.date_to:
            query = query.where(GuardianSync.created_at <= filters.date_to)

        # Contar total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Aplicar paginação
        offset = (page - 1) * page_size
        query = query.order_by(GuardianSync.created_at.desc())
        query = query.offset(offset).limit(page_size)

        result = await self.db.execute(query)
        syncs = list(result.scalars().all())

        return syncs, total

    async def get_pending(self, limit: int = 100) -> list[GuardianSync]:
        """Busca sincronizações pendentes."""
        result = await self.db.execute(
            select(GuardianSync)
            .where(
                GuardianSync.status == SyncStatus.PENDING.value,
                GuardianSync.is_active.is_(True),
            )
            .order_by(GuardianSync.created_at)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_failed_for_retry(self, limit: int = 50) -> list[GuardianSync]:
        """Busca sincronizações falhas que podem ser reprocessadas."""
        now = datetime.utcnow()
        result = await self.db.execute(
            select(GuardianSync)
            .where(
                GuardianSync.status == SyncStatus.FAILED.value,
                GuardianSync.retry_count < GuardianSync.max_retries,
                or_(
                    GuardianSync.next_retry_at.is_(None),
                    GuardianSync.next_retry_at <= now,
                ),
                GuardianSync.is_active.is_(True),
            )
            .order_by(GuardianSync.last_retry_at)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def mark_in_progress(self, sync_id: str) -> Optional[GuardianSync]:
        """Marca sincronização como em andamento."""
        sync = await self.get_by_id(sync_id)
        if sync:
            sync.status = SyncStatus.IN_PROGRESS.value
            await self.db.commit()
            await self.db.refresh(sync)
        return sync

    async def mark_completed(
        self,
        sync_id: str,
        response: dict | None = None,
        external_id: str | None = None,
    ) -> Optional[GuardianSync]:
        """Marca sincronização como concluída."""
        sync = await self.get_by_id(sync_id)
        if sync:
            sync.mark_completed(response)
            if external_id:
                sync.external_id = external_id
            await self.db.commit()
            await self.db.refresh(sync)
        return sync

    async def mark_failed(
        self,
        sync_id: str,
        error: str,
        details: dict | None = None,
    ) -> Optional[GuardianSync]:
        """Marca sincronização como falha."""
        sync = await self.get_by_id(sync_id)
        if sync:
            sync.mark_failed(error, details)
            await self.db.commit()
            await self.db.refresh(sync)
        return sync

    async def retry(
        self,
        sync_id: str,
        notes: str | None = None,
    ) -> Optional[GuardianSync]:
        """Incrementa retentativa e reprocessa."""
        sync = await self.get_by_id(sync_id)
        if sync and sync.can_retry:
            sync.increment_retry()
            if notes:
                if not sync.metadata_extra:
                    sync.metadata_extra = {}
                sync.metadata_extra["retry_notes"] = notes
            await self.db.commit()
            await self.db.refresh(sync)
        return sync

    async def get_stats(
        self,
        client_id: str | None = None,
    ) -> GuardianSyncStats:
        """Retorna estatísticas de sincronização."""
        base_query = select(GuardianSync).where(GuardianSync.is_active.is_(True))

        if client_id:
            base_query = base_query.where(GuardianSync.client_id == client_id)

        # Contagem total
        total_result = await self.db.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total = total_result.scalar() or 0

        # Contagem por status
        status_counts = {}
        for status in SyncStatus:
            status_query = base_query.where(GuardianSync.status == status.value)
            count_result = await self.db.execute(
                select(func.count()).select_from(status_query.subquery())
            )
            status_counts[status.value] = count_result.scalar() or 0

        # Por direção
        direction_counts = {}
        for direction in SyncDirection:
            dir_query = base_query.where(GuardianSync.direction == direction.value)
            count_result = await self.db.execute(
                select(func.count()).select_from(dir_query.subquery())
            )
            direction_counts[direction.value] = count_result.scalar() or 0

        # Média de retentativas
        avg_result = await self.db.execute(
            select(func.avg(GuardianSync.retry_count)).select_from(
                base_query.subquery()
            )
        )
        avg_retry = avg_result.scalar() or 0.0

        # Última sincronização
        last_sync_result = await self.db.execute(
            select(GuardianSync.synced_at)
            .where(
                GuardianSync.status == SyncStatus.COMPLETED.value,
                GuardianSync.is_active.is_(True),
            )
            .order_by(GuardianSync.synced_at.desc())
            .limit(1)
        )
        last_sync = last_sync_result.scalar_one_or_none()

        completed = status_counts.get(SyncStatus.COMPLETED.value, 0)
        success_rate = (completed / total * 100) if total > 0 else 0.0

        return GuardianSyncStats(
            total=total,
            pending=status_counts.get(SyncStatus.PENDING.value, 0),
            in_progress=status_counts.get(SyncStatus.IN_PROGRESS.value, 0),
            completed=completed,
            failed=status_counts.get(SyncStatus.FAILED.value, 0),
            partial=status_counts.get(SyncStatus.PARTIAL.value, 0),
            success_rate=round(success_rate, 2),
            by_direction=direction_counts,
            by_entity_type={},
            avg_retry_count=round(float(avg_retry), 2),
            last_sync_at=last_sync,
        )

    async def delete(self, sync_id: str) -> bool:
        """Remove uma sincronização (soft delete)."""
        sync = await self.get_by_id(sync_id)
        if sync:
            sync.is_active = False
            await self.db.commit()
            return True
        return False
