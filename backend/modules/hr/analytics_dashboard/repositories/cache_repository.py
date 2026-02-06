"""Repository para AnalyticsCache."""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Any
from uuid import UUID

from sqlalchemy import select, update, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.analytics_dashboard.models import (
    AnalyticsCache,
    CacheType,
    CacheStatus,
)

logger = logging.getLogger(__name__)


class CacheRepository:
    """Repository para operações de cache."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_cache(
        self,
        cache_key: str,
        condominio_id: UUID,
    ) -> Optional[AnalyticsCache]:
        """Busca cache por chave."""
        query = select(AnalyticsCache).where(
            AnalyticsCache.cache_key == cache_key,
            AnalyticsCache.condominio_id == condominio_id,
            AnalyticsCache.is_active.is_(True),
        )
        result = await self.db.execute(query)
        cache = result.scalar_one_or_none()

        if cache and cache.is_expired:
            cache.status = CacheStatus.EXPIRED.value
            await self.db.commit()

        return cache

    async def get_valid_cache(
        self,
        cache_key: str,
        condominio_id: UUID,
    ) -> Optional[AnalyticsCache]:
        """Busca cache válido (não expirado)."""
        query = select(AnalyticsCache).where(
            AnalyticsCache.cache_key == cache_key,
            AnalyticsCache.condominio_id == condominio_id,
            AnalyticsCache.status == CacheStatus.VALID.value,
            AnalyticsCache.expires_at > datetime.utcnow(),
            AnalyticsCache.is_active.is_(True),
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def set_cache(
        self,
        condominio_id: UUID,
        cache_key: str,
        cache_type: CacheType,
        data: Any,
        ttl_seconds: int = 300,
        params: dict = None,
        kpi_code: str = None,
        widget_id: UUID = None,
        period_start: datetime = None,
        period_end: datetime = None,
        computation_time_ms: int = None,
    ) -> AnalyticsCache:
        """Cria ou atualiza cache."""
        # Verificar se já existe
        existing = await self.get_cache(cache_key, condominio_id)

        if existing:
            existing.refresh(data, ttl_seconds, computation_time_ms)
            await self.db.commit()
            await self.db.refresh(existing)
            return existing

        # Criar novo
        params_hash = AnalyticsCache.generate_params_hash(params or {})
        cache = AnalyticsCache(
            condominio_id=condominio_id,
            cache_key=cache_key,
            cache_type=cache_type.value,
            params_hash=params_hash,
            params=params,
            data=data,
            kpi_code=kpi_code,
            widget_id=widget_id,
            period_start=period_start,
            period_end=period_end,
            ttl_seconds=ttl_seconds,
            expires_at=datetime.utcnow() + timedelta(seconds=ttl_seconds),
            computation_time_ms=computation_time_ms,
            status=CacheStatus.VALID.value,
        )
        self.db.add(cache)
        await self.db.commit()
        await self.db.refresh(cache)
        return cache

    async def invalidate_cache(
        self,
        cache_key: str,
        condominio_id: UUID,
        reason: str = None,
    ) -> bool:
        """Invalida cache específico."""
        stmt = (
            update(AnalyticsCache)
            .where(
                AnalyticsCache.cache_key == cache_key,
                AnalyticsCache.condominio_id == condominio_id,
            )
            .values(
                status=CacheStatus.EXPIRED.value,
                invalidated_by=reason,
                expires_at=datetime.utcnow(),
            )
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    async def invalidate_by_kpi(
        self,
        kpi_code: str,
        condominio_id: UUID = None,
    ) -> int:
        """Invalida todos os caches de um KPI."""
        conditions = [AnalyticsCache.kpi_code == kpi_code]
        if condominio_id:
            conditions.append(AnalyticsCache.condominio_id == condominio_id)

        stmt = (
            update(AnalyticsCache)
            .where(and_(*conditions))
            .values(
                status=CacheStatus.EXPIRED.value,
                invalidated_by=f"KPI {kpi_code} invalidated",
                expires_at=datetime.utcnow(),
            )
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount

    async def invalidate_by_widget(
        self,
        widget_id: UUID,
    ) -> int:
        """Invalida cache de um widget."""
        stmt = (
            update(AnalyticsCache)
            .where(AnalyticsCache.widget_id == widget_id)
            .values(
                status=CacheStatus.EXPIRED.value,
                invalidated_by=f"Widget {widget_id} invalidated",
                expires_at=datetime.utcnow(),
            )
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount

    async def invalidate_all(
        self,
        condominio_id: UUID,
        cache_type: CacheType = None,
    ) -> int:
        """Invalida todos os caches de um condomínio."""
        conditions = [AnalyticsCache.condominio_id == condominio_id]
        if cache_type:
            conditions.append(AnalyticsCache.cache_type == cache_type.value)

        stmt = (
            update(AnalyticsCache)
            .where(and_(*conditions))
            .values(
                status=CacheStatus.EXPIRED.value,
                invalidated_by="Bulk invalidation",
                expires_at=datetime.utcnow(),
            )
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount

    async def record_hit(self, cache_id: UUID) -> None:
        """Registra hit no cache."""
        stmt = (
            update(AnalyticsCache)
            .where(AnalyticsCache.id == cache_id)
            .values(
                hit_count=AnalyticsCache.hit_count + 1,
                last_hit_at=datetime.utcnow(),
            )
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def cleanup_expired(
        self,
        older_than_hours: int = 24,
        dry_run: bool = True,
    ) -> dict:
        """Remove caches expirados antigos."""
        cutoff = datetime.utcnow() - timedelta(hours=older_than_hours)

        # Contar
        count_query = select(func.count(AnalyticsCache.id)).where(
            AnalyticsCache.expires_at < cutoff,
        )
        count_result = await self.db.execute(count_query)
        count = count_result.scalar()

        if not dry_run and count > 0:
            stmt = delete(AnalyticsCache).where(
                AnalyticsCache.expires_at < cutoff,
            )
            await self.db.execute(stmt)
            await self.db.commit()
            logger.info(f"Removidos {count} caches expirados")

        return {
            "expired_count": count,
            "deleted": not dry_run,
            "cutoff": cutoff.isoformat(),
        }

    async def get_statistics(  # pylint: disable=too-many-locals
        self,
        condominio_id: UUID = None,
    ) -> dict:
        """Retorna estatísticas de cache."""
        conditions = []
        if condominio_id:
            conditions.append(AnalyticsCache.condominio_id == condominio_id)

        # Total
        total_query = select(func.count(AnalyticsCache.id))
        if conditions:
            total_query = total_query.where(and_(*conditions))
        total_result = await self.db.execute(total_query)
        total = total_result.scalar()

        # Por status
        status_query = (
            select(
                AnalyticsCache.status,
                func.count(AnalyticsCache.id),
            )
            .group_by(AnalyticsCache.status)
        )
        if conditions:
            status_query = status_query.where(and_(*conditions))
        status_result = await self.db.execute(status_query)
        by_status = {row[0]: row[1] for row in status_result.all()}

        # Por tipo
        type_query = (
            select(
                AnalyticsCache.cache_type,
                func.count(AnalyticsCache.id),
            )
            .group_by(AnalyticsCache.cache_type)
        )
        if conditions:
            type_query = type_query.where(and_(*conditions))
        type_result = await self.db.execute(type_query)
        by_type = {row[0]: row[1] for row in type_result.all()}

        # Total hits
        hits_query = select(func.sum(AnalyticsCache.hit_count))
        if conditions:
            hits_query = hits_query.where(and_(*conditions))
        hits_result = await self.db.execute(hits_query)
        total_hits = hits_result.scalar() or 0

        # Tamanho total
        size_query = select(func.sum(AnalyticsCache.data_size_bytes))
        if conditions:
            size_query = size_query.where(and_(*conditions))
        size_result = await self.db.execute(size_query)
        total_size = size_result.scalar() or 0

        return {
            "total_entries": total,
            "by_status": by_status,
            "by_type": by_type,
            "total_hits": total_hits,
            "total_size_bytes": total_size,
            "hit_rate": round(total_hits / total * 100, 2) if total > 0 else 0,
        }

    async def get_hot_caches(
        self,
        condominio_id: UUID,
        limit: int = 10,
    ) -> List[AnalyticsCache]:
        """Retorna caches mais acessados."""
        query = (
            select(AnalyticsCache)
            .where(
                AnalyticsCache.condominio_id == condominio_id,
                AnalyticsCache.is_active.is_(True),
            )
            .order_by(AnalyticsCache.hit_count.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def extend_ttl(
        self,
        cache_key: str,
        condominio_id: UUID,
        additional_seconds: int,
    ) -> bool:
        """Estende TTL de um cache."""
        stmt = (
            update(AnalyticsCache)
            .where(
                AnalyticsCache.cache_key == cache_key,
                AnalyticsCache.condominio_id == condominio_id,
                AnalyticsCache.status == CacheStatus.VALID.value,
            )
            .values(
                expires_at=AnalyticsCache.expires_at + timedelta(seconds=additional_seconds),
            )
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
