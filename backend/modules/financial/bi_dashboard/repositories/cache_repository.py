"""Repository de Cache de Analytics Financeiro."""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from modules.financial.bi_dashboard.models.analytics_cache import (
    AnalyticsCache,
    CacheStatus,
    CacheType,
)
from modules.financial.bi_dashboard.schemas.cache_schemas import (
    CacheStats,
)


class CacheRepository:
    """Repository para operacoes de Cache."""

    def __init__(self, db: Session):
        """Inicializa repository."""
        self.db = db

    def get_or_create(
        self,
        condominio_id: UUID,
        cache_key: str,
        tipo: CacheType = CacheType.QUERY,
        ttl_seconds: int = 300,
    ) -> AnalyticsCache:
        """Busca ou cria entrada de cache."""
        cache = self.get_by_key(cache_key, condominio_id)
        if cache:
            return cache

        cache = AnalyticsCache(
            condominio_id=condominio_id,
            cache_key=cache_key,
            tipo=tipo,
            data={},
            ttl_seconds=ttl_seconds,
            expires_at=datetime.utcnow() + timedelta(seconds=ttl_seconds),
        )
        self.db.add(cache)
        self.db.commit()
        self.db.refresh(cache)
        return cache

    def get_by_key(
        self,
        cache_key: str,
        condominio_id: UUID = None,
    ) -> AnalyticsCache | None:
        """Busca cache por chave."""
        query = self.db.query(AnalyticsCache).filter(AnalyticsCache.cache_key == cache_key)
        if condominio_id:
            query = query.filter(AnalyticsCache.condominio_id == condominio_id)
        return query.first()

    def get_by_id(
        self,
        cache_id: UUID,
        condominio_id: UUID = None,
    ) -> AnalyticsCache | None:
        """Busca cache por ID."""
        query = self.db.query(AnalyticsCache).filter(AnalyticsCache.id == cache_id)
        if condominio_id:
            query = query.filter(AnalyticsCache.condominio_id == condominio_id)
        return query.first()

    def set(
        self,
        condominio_id: UUID,
        cache_key: str,
        data: Any,
        tipo: CacheType = CacheType.QUERY,
        ttl_seconds: int = 300,
        entity_type: str = None,
        entity_id: UUID = None,
        parametros: dict = None,
    ) -> AnalyticsCache:
        """Define valor no cache."""
        cache = self.get_by_key(cache_key, condominio_id)

        if cache:
            cache.set_data(data, ttl_seconds)
            cache.entity_type = entity_type
            cache.entity_id = entity_id
            cache.parametros = parametros or {}
        else:
            cache = AnalyticsCache(
                condominio_id=condominio_id,
                cache_key=cache_key,
                tipo=tipo,
                entity_type=entity_type,
                entity_id=entity_id,
                parametros=parametros or {},
                data=data,
                ttl_seconds=ttl_seconds,
                expires_at=datetime.utcnow() + timedelta(seconds=ttl_seconds),
            )
            cache.set_data(data, ttl_seconds)
            self.db.add(cache)

        self.db.commit()
        self.db.refresh(cache)
        return cache

    def get(
        self,
        cache_key: str,
        condominio_id: UUID,
        record_stats: bool = True,
    ) -> Any | None:
        """Busca valor do cache."""
        cache = self.get_by_key(cache_key, condominio_id)

        if not cache:
            return None

        if record_stats:
            if cache.is_valid:
                cache.record_hit()
            else:
                cache.record_miss()
            self.db.commit()

        if cache.is_valid:
            return cache.data
        return None

    def invalidate(
        self,
        cache_key: str,
        condominio_id: UUID,
    ) -> bool:
        """Invalida entrada de cache."""
        cache = self.get_by_key(cache_key, condominio_id)
        if cache:
            cache.invalidate()
            self.db.commit()
            return True
        return False

    def invalidate_by_entity(
        self,
        entity_type: str,
        entity_id: UUID,
        condominio_id: UUID = None,
    ) -> int:
        """Invalida caches por entidade."""
        query = self.db.query(AnalyticsCache).filter(
            AnalyticsCache.entity_type == entity_type,
            AnalyticsCache.entity_id == entity_id,
        )
        if condominio_id:
            query = query.filter(AnalyticsCache.condominio_id == condominio_id)

        count = 0
        for cache in query.all():
            cache.invalidate()
            count += 1

        self.db.commit()
        return count

    def invalidate_by_type(
        self,
        tipo: CacheType,
        condominio_id: UUID,
    ) -> int:
        """Invalida caches por tipo."""
        count = 0
        for cache in (
            self.db.query(AnalyticsCache)
            .filter(
                AnalyticsCache.condominio_id == condominio_id,
                AnalyticsCache.tipo == tipo,
            )
            .all()
        ):
            cache.invalidate()
            count += 1

        self.db.commit()
        return count

    def invalidate_all(self, condominio_id: UUID) -> int:
        """Invalida todos os caches do condominio."""
        count = 0
        for cache in self.db.query(AnalyticsCache).filter(AnalyticsCache.condominio_id == condominio_id).all():
            cache.invalidate()
            count += 1

        self.db.commit()
        return count

    def cleanup_expired(
        self,
        condominio_id: UUID = None,
        older_than_hours: int = 24,
    ) -> int:
        """Remove caches expirados."""
        cutoff = datetime.utcnow() - timedelta(hours=older_than_hours)
        query = self.db.query(AnalyticsCache).filter(AnalyticsCache.expires_at < cutoff)
        if condominio_id:
            query = query.filter(AnalyticsCache.condominio_id == condominio_id)

        count = query.count()
        query.delete()
        self.db.commit()
        return count

    def get_stats(self, condominio_id: UUID) -> CacheStats:
        """Retorna estatisticas do cache."""
        base_query = self.db.query(AnalyticsCache).filter(AnalyticsCache.condominio_id == condominio_id)

        total_entries = base_query.count()
        valid_entries = base_query.filter(
            AnalyticsCache.status == CacheStatus.VALID,
            AnalyticsCache.expires_at > datetime.utcnow(),
        ).count()
        stale_entries = base_query.filter(AnalyticsCache.status == CacheStatus.STALE).count()
        expired_entries = base_query.filter(AnalyticsCache.status == CacheStatus.EXPIRED).count()
        error_entries = base_query.filter(AnalyticsCache.status == CacheStatus.ERROR).count()

        total_size_bytes = base_query.with_entities(func.sum(AnalyticsCache.data_size_bytes)).scalar() or 0
        total_hits = base_query.with_entities(func.sum(AnalyticsCache.hit_count)).scalar() or 0
        total_misses = base_query.with_entities(func.sum(AnalyticsCache.miss_count)).scalar() or 0

        overall_hit_rate = Decimal("0")
        total_requests = total_hits + total_misses
        if total_requests > 0:
            overall_hit_rate = Decimal(str((total_hits / total_requests) * 100))

        avg_ttl = base_query.with_entities(func.avg(AnalyticsCache.ttl_seconds)).scalar() or 0

        by_type = {}
        for tipo in CacheType:
            count = base_query.filter(AnalyticsCache.tipo == tipo).count()
            if count > 0:
                by_type[tipo.value] = count

        by_status = {}
        for status in CacheStatus:
            count = base_query.filter(AnalyticsCache.status == status).count()
            if count > 0:
                by_status[status.value] = count

        oldest = base_query.order_by(AnalyticsCache.created_at).first()
        newest = base_query.order_by(desc(AnalyticsCache.created_at)).first()

        return CacheStats(
            total_entries=total_entries,
            valid_entries=valid_entries,
            stale_entries=stale_entries,
            expired_entries=expired_entries,
            error_entries=error_entries,
            total_size_bytes=int(total_size_bytes),
            total_hits=int(total_hits),
            total_misses=int(total_misses),
            overall_hit_rate=overall_hit_rate,
            avg_ttl_seconds=int(avg_ttl),
            by_type=by_type,
            by_status=by_status,
            oldest_entry=oldest.created_at if oldest else None,
            newest_entry=newest.created_at if newest else None,
        )

    def extend_ttl(
        self,
        cache_key: str,
        condominio_id: UUID,
        extra_seconds: int,
    ) -> bool:
        """Estende TTL de cache."""
        cache = self.get_by_key(cache_key, condominio_id)
        if cache:
            cache.extend_ttl(extra_seconds)
            self.db.commit()
            return True
        return False

    def mark_stale(
        self,
        cache_key: str,
        condominio_id: UUID,
    ) -> bool:
        """Marca cache como obsoleto."""
        cache = self.get_by_key(cache_key, condominio_id)
        if cache:
            cache.mark_stale()
            self.db.commit()
            return True
        return False

    def list_by_entity_type(
        self,
        entity_type: str,
        condominio_id: UUID,
    ) -> list[AnalyticsCache]:
        """Lista caches por tipo de entidade."""
        return (
            self.db.query(AnalyticsCache)
            .filter(
                AnalyticsCache.condominio_id == condominio_id,
                AnalyticsCache.entity_type == entity_type,
            )
            .all()
        )

    def get_hot_entries(
        self,
        condominio_id: UUID,
        limit: int = 10,
    ) -> list[AnalyticsCache]:
        """Lista entradas mais acessadas."""
        return (
            self.db.query(AnalyticsCache)
            .filter(
                AnalyticsCache.condominio_id == condominio_id,
                AnalyticsCache.status == CacheStatus.VALID,
            )
            .order_by(desc(AnalyticsCache.hit_count))
            .limit(limit)
            .all()
        )
