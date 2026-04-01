"""Schemas de Cache de Analytics Financeiro."""

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from modules.financial.bi_dashboard.models.analytics_cache import (
    CacheStatus,
    CacheType,
)


class CacheEntry(BaseModel):
    """Entrada de cache."""

    id: UUID
    condominio_id: UUID
    cache_key: str
    tipo: CacheType
    status: CacheStatus
    entity_type: str | None = None
    entity_id: UUID | None = None
    data: Any
    data_size_bytes: int | None = None
    row_count: int | None = None
    parametros: dict = Field(default_factory=dict)
    periodo_inicio: datetime | None = None
    periodo_fim: datetime | None = None
    ttl_seconds: int = 300
    expires_at: datetime
    is_expired: bool = False
    hit_count: int = 0
    miss_count: int = 0
    last_hit_at: datetime | None = None
    last_refresh_at: datetime | None = None
    refresh_count: int = 0
    refresh_duration_ms: int | None = None
    last_error: str | None = None
    error_count: int = 0
    is_valid: bool = True
    hit_rate: Decimal = Decimal("0")
    age_seconds: int = 0
    time_to_live: int = 0
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class CacheStats(BaseModel):
    """Estatisticas do cache."""

    total_entries: int = 0
    valid_entries: int = 0
    stale_entries: int = 0
    expired_entries: int = 0
    error_entries: int = 0
    total_size_bytes: int = 0
    total_hits: int = 0
    total_misses: int = 0
    overall_hit_rate: Decimal = Decimal("0")
    avg_ttl_seconds: int = 0
    avg_age_seconds: int = 0
    by_type: dict = Field(default_factory=dict)
    by_status: dict = Field(default_factory=dict)
    oldest_entry: datetime | None = None
    newest_entry: datetime | None = None


class CacheInvalidate(BaseModel):
    """Solicitacao de invalidacao de cache."""

    cache_keys: list[str] | None = None
    entity_type: str | None = None
    entity_ids: list[UUID] | None = None
    tipo: CacheType | None = None
    invalidate_all: bool = Field(default=False)
    condominio_only: bool = Field(default=True)


class CacheRefresh(BaseModel):
    """Solicitacao de refresh de cache."""

    cache_keys: list[str] | None = None
    entity_type: str | None = None
    entity_ids: list[UUID] | None = None
    force: bool = Field(default=False)


class CacheWarmup(BaseModel):
    """Solicitacao de warmup de cache."""

    entity_types: list[str] = Field(default_factory=list)
    period_days: int = Field(default=30, ge=1, le=365)
    priority_entities: list[UUID] = Field(default_factory=list)


class CacheConfig(BaseModel):
    """Configuracao de cache."""

    default_ttl_seconds: int = Field(default=300, ge=60, le=86400)
    max_entries: int = Field(default=10000, ge=100, le=1000000)
    max_size_mb: int = Field(default=100, ge=1, le=10000)
    auto_cleanup_enabled: bool = Field(default=True)
    cleanup_interval_minutes: int = Field(default=60, ge=5, le=1440)
    warmup_enabled: bool = Field(default=True)
    warmup_schedule: str = Field(default="0 6 * * *")


class CacheCleanupResult(BaseModel):
    """Resultado de limpeza de cache."""

    entries_removed: int = 0
    bytes_freed: int = 0
    entries_remaining: int = 0
    duration_ms: int = 0
    executed_at: datetime


class CacheHitResult(BaseModel):
    """Resultado de consulta ao cache."""

    hit: bool
    data: Any | None = None
    cache_key: str
    ttl_remaining: int = 0
    age_seconds: int = 0
    from_stale: bool = False
