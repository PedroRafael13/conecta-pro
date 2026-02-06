"""Repository para REPSync."""

from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.rep_integration.models import (
    REPSync,
    SyncStatus,
)
from modules.hr.rep_integration.schemas import (
    REPSyncCreate,
    REPSyncUpdate,
    REPSyncFilter,
)


class REPSyncRepository:
    """Repository para operações de REPSync."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: REPSyncCreate) -> REPSync:
        """Cria nova sincronização."""
        sync = REPSync(
            device_id=data.device_id,
            condominio_id=data.condominio_id,
            sync_type=data.sync_type,
            trigger=data.trigger,
            triggered_by=data.triggered_by,
            events_from_datetime=data.events_from_datetime,
            events_to_datetime=data.events_to_datetime,
            status=SyncStatus.PENDING.value,
        )

        self.db.add(sync)
        await self.db.commit()
        await self.db.refresh(sync)
        return sync

    async def get_by_id(self, sync_id: UUID) -> Optional[REPSync]:
        """Busca sincronização por ID."""
        result = await self.db.execute(
            select(REPSync).where(REPSync.id == sync_id)
        )
        return result.scalar_one_or_none()

    async def update(
        self,
        sync_id: UUID,
        data: REPSyncUpdate,
    ) -> Optional[REPSync]:
        """Atualiza sincronização."""
        sync = await self.get_by_id(sync_id)
        if not sync:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(sync, field, value)

        await self.db.commit()
        await self.db.refresh(sync)
        return sync

    async def list_syncs(
        self,
        filters: REPSyncFilter,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[REPSync], int]:
        """Lista sincronizações com filtros e paginação."""
        query = select(REPSync)

        # Aplicar filtros
        if filters.device_id:
            query = query.where(REPSync.device_id == filters.device_id)
        if filters.condominio_id:
            query = query.where(REPSync.condominio_id == filters.condominio_id)
        if filters.sync_type:
            query = query.where(REPSync.sync_type == filters.sync_type)
        if filters.status:
            query = query.where(REPSync.status == filters.status)
        if filters.trigger:
            query = query.where(REPSync.trigger == filters.trigger)
        if filters.date_from:
            query = query.where(REPSync.created_at >= filters.date_from)
        if filters.date_to:
            query = query.where(REPSync.created_at <= filters.date_to)
        if filters.has_errors:
            if filters.has_errors:
                query = query.where(REPSync.error_items > 0)
            else:
                query = query.where(REPSync.error_items == 0)

        # Contagem total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginação
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        query = query.order_by(REPSync.created_at.desc())

        result = await self.db.execute(query)
        syncs = result.scalars().all()

        return list(syncs), total

    async def get_running_sync(self, device_id: UUID) -> Optional[REPSync]:
        """Verifica se há sync em andamento para o dispositivo."""
        result = await self.db.execute(
            select(REPSync).where(
                REPSync.device_id == device_id,
                REPSync.status == SyncStatus.IN_PROGRESS.value,
            )
        )
        return result.scalar_one_or_none()

    async def get_last_successful_sync(
        self,
        device_id: UUID,
        sync_type: str = None,
    ) -> Optional[REPSync]:
        """Retorna última sincronização bem-sucedida."""
        query = select(REPSync).where(
            REPSync.device_id == device_id,
            REPSync.status == SyncStatus.COMPLETED.value,
        )

        if sync_type:
            query = query.where(REPSync.sync_type == sync_type)

        query = query.order_by(REPSync.completed_at.desc()).limit(1)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def start_sync(self, sync_id: UUID) -> None:
        """Inicia uma sincronização."""
        await self.db.execute(
            update(REPSync)
            .where(REPSync.id == sync_id)
            .values(
                status=SyncStatus.IN_PROGRESS.value,
                started_at=datetime.utcnow(),
            )
        )
        await self.db.commit()

    async def complete_sync(
        self,
        sync_id: UUID,
        success_items: int,
        error_items: int,
        skipped_items: int,
        last_nsr: int = None,
    ) -> None:
        """Finaliza uma sincronização com sucesso."""
        sync = await self.get_by_id(sync_id)
        if not sync:
            return

        now = datetime.utcnow()
        duration = None
        if sync.started_at:
            duration = int((now - sync.started_at).total_seconds())

        total = success_items + error_items + skipped_items
        is_partial = error_items > 0

        await self.db.execute(
            update(REPSync)
            .where(REPSync.id == sync_id)
            .values(
                status=SyncStatus.PARTIAL.value if is_partial else SyncStatus.COMPLETED.value,
                completed_at=now,
                duration_seconds=duration,
                total_items=total,
                processed_items=total,
                success_items=success_items,
                error_items=error_items,
                skipped_items=skipped_items,
                last_nsr_after=last_nsr,
            )
        )
        await self.db.commit()

    async def fail_sync(
        self,
        sync_id: UUID,
        error_message: str,
        error_code: str = None,
        error_details: dict = None,
    ) -> None:
        """Marca sincronização como falha."""
        sync = await self.get_by_id(sync_id)
        if not sync:
            return

        now = datetime.utcnow()
        duration = None
        if sync.started_at:
            duration = int((now - sync.started_at).total_seconds())

        await self.db.execute(
            update(REPSync)
            .where(REPSync.id == sync_id)
            .values(
                status=SyncStatus.FAILED.value,
                completed_at=now,
                duration_seconds=duration,
                error_message=error_message,
                error_code=error_code,
                error_details=error_details,
                retry_count=sync.retry_count + 1,
            )
        )
        await self.db.commit()

    async def update_progress(
        self,
        sync_id: UUID,
        processed: int,
        success: int,
        errors: int,
        current_nsr: int = None,
    ) -> None:
        """Atualiza progresso da sincronização."""
        update_data = {
            "processed_items": processed,
            "success_items": success,
            "error_items": errors,
        }

        if current_nsr:
            update_data["last_nsr_after"] = current_nsr

        await self.db.execute(
            update(REPSync)
            .where(REPSync.id == sync_id)
            .values(**update_data)
        )
        await self.db.commit()

    async def cancel_stale_syncs(self, timeout_minutes: int = 30) -> int:
        """Cancela syncs travadas há muito tempo."""
        cutoff = datetime.utcnow() - timedelta(minutes=timeout_minutes)

        result = await self.db.execute(
            update(REPSync)
            .where(
                REPSync.status == SyncStatus.IN_PROGRESS.value,
                REPSync.started_at < cutoff,
            )
            .values(
                status=SyncStatus.TIMEOUT.value,
                completed_at=datetime.utcnow(),
                error_message=f"Timeout após {timeout_minutes} minutos",
            )
        )
        await self.db.commit()
        return result.rowcount

    async def get_statistics(  # pylint: disable=too-many-locals
        self,
        device_id: UUID = None,
        condominio_id: UUID = None,
        days: int = 30,
    ) -> dict:
        """Retorna estatísticas de sincronizações."""
        cutoff = datetime.utcnow() - timedelta(days=days)

        base_where = [REPSync.created_at >= cutoff]
        if device_id:
            base_where.append(REPSync.device_id == device_id)
        if condominio_id:
            base_where.append(REPSync.condominio_id == condominio_id)

        # Total
        total_result = await self.db.execute(
            select(func.count()).where(*base_where)
        )
        total = total_result.scalar() or 0

        # Por status
        status_result = await self.db.execute(
            select(
                REPSync.status,
                func.count(REPSync.id)
            )
            .where(*base_where)
            .group_by(REPSync.status)
        )
        by_status = {row[0]: row[1] for row in status_result.all()}

        # Por tipo
        type_result = await self.db.execute(
            select(
                REPSync.sync_type,
                func.count(REPSync.id)
            )
            .where(*base_where)
            .group_by(REPSync.sync_type)
        )
        by_type = {row[0]: row[1] for row in type_result.all()}

        # Média de duração
        avg_duration_result = await self.db.execute(
            select(func.avg(REPSync.duration_seconds)).where(
                *base_where,
                REPSync.duration_seconds.isnot(None),
            )
        )
        avg_duration = avg_duration_result.scalar() or 0

        # Total de itens
        items_result = await self.db.execute(
            select(
                func.sum(REPSync.success_items),
                func.sum(REPSync.error_items),
            ).where(*base_where)
        )
        items = items_result.one()

        success_rate = 0
        if total > 0:
            completed = by_status.get(SyncStatus.COMPLETED.value, 0)
            success_rate = (completed / total) * 100

        return {
            "total_syncs": total,
            "syncs_by_status": by_status,
            "syncs_by_type": by_type,
            "avg_duration_seconds": round(avg_duration, 2),
            "total_success_items": items[0] or 0,
            "total_error_items": items[1] or 0,
            "success_rate": round(success_rate, 2),
            "period_days": days,
        }
