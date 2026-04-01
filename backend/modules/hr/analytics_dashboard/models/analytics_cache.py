"""Modelo AnalyticsCache - Cache de métricas calculadas."""

import hashlib
import json
import uuid
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class CacheType(StrEnum):
    """Tipo de cache."""

    KPI = "kpi"  # Cache de KPI
    WIDGET = "widget"  # Cache de widget
    REPORT = "report"  # Cache de relatório
    AGGREGATION = "aggregation"  # Cache de agregação
    QUERY = "query"  # Cache de query


class CacheStatus(StrEnum):
    """Status do cache."""

    VALID = "valid"
    STALE = "stale"
    EXPIRED = "expired"
    COMPUTING = "computing"
    ERROR = "error"


class AnalyticsCache(Base):
    """Modelo de cache de analytics."""

    __tablename__ = "analytics_cache"

    # Identificação
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    condominio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # Chave de cache
    cache_key: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )  # SHA256 hash
    cache_type: Mapped[str] = mapped_column(
        String(20),
        default=CacheType.KPI.value,
    )

    # Referências
    kpi_code: Mapped[str | None] = mapped_column(String(50), index=True)
    widget_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    report_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))

    # Parâmetros usados para gerar o cache
    params_hash: Mapped[str] = mapped_column(String(64))
    params: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    # Período dos dados
    period_start: Mapped[datetime | None] = mapped_column(DateTime)
    period_end: Mapped[datetime | None] = mapped_column(DateTime)
    granularity: Mapped[str | None] = mapped_column(String(20))

    # Dados cacheados
    data: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    data_compressed: Mapped[str | None] = mapped_column(Text)
    is_compressed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Metadados do resultado
    row_count: Mapped[int | None] = mapped_column(Integer)
    data_size_bytes: Mapped[int | None] = mapped_column(Integer)

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        default=CacheStatus.VALID.value,
    )
    error_message: Mapped[str | None] = mapped_column(Text)

    # TTL e validade
    ttl_seconds: Mapped[int] = mapped_column(Integer, default=300)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    computation_time_ms: Mapped[int | None] = mapped_column(Integer)

    # Estatísticas de uso
    hit_count: Mapped[int] = mapped_column(Integer, default=0)
    last_hit_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Dependências (para invalidação em cascata)
    dependencies: Mapped[list | None] = mapped_column(JSONB, default=list)
    invalidated_by: Mapped[str | None] = mapped_column(String(100))

    # Auditoria
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Índices
    __table_args__ = (
        Index("ix_analytics_cache_key_condominio", "cache_key", "condominio_id"),
        Index("ix_analytics_cache_expires", "expires_at"),
        Index("ix_analytics_cache_kpi", "kpi_code"),
        Index("ix_analytics_cache_type_status", "cache_type", "status"),
    )

    @property
    def is_valid(self) -> bool:
        """Verifica se cache é válido."""
        return self.status == CacheStatus.VALID.value and self.expires_at > datetime.utcnow() and self.is_active

    @property
    def is_expired(self) -> bool:
        """Verifica se cache expirou."""
        return self.expires_at <= datetime.utcnow()

    @property
    def age_seconds(self) -> float:
        """Retorna idade do cache em segundos."""
        return (datetime.utcnow() - self.computed_at).total_seconds()

    @property
    def remaining_ttl_seconds(self) -> float:
        """Retorna TTL restante em segundos."""
        remaining = (self.expires_at - datetime.utcnow()).total_seconds()
        return max(0, remaining)

    @staticmethod
    def generate_cache_key(
        cache_type: str,
        identifier: str,
        params: dict = None,
    ) -> str:
        """Gera chave de cache única."""
        key_parts = [cache_type, identifier]
        if params:
            sorted_params = json.dumps(params, sort_keys=True)
            key_parts.append(sorted_params)

        key_string = "|".join(key_parts)
        return hashlib.sha256(key_string.encode()).hexdigest()

    @staticmethod
    def generate_params_hash(params: dict) -> str:
        """Gera hash dos parâmetros."""
        sorted_params = json.dumps(params, sort_keys=True)
        return hashlib.sha256(sorted_params.encode()).hexdigest()

    def record_hit(self) -> None:
        """Registra acesso ao cache."""
        self.hit_count += 1
        self.last_hit_at = datetime.utcnow()

    def invalidate(self, reason: str = None) -> None:
        """Invalida o cache."""
        self.status = CacheStatus.EXPIRED.value
        self.invalidated_by = reason
        self.expires_at = datetime.utcnow()

    def mark_stale(self) -> None:
        """Marca cache como stale (ainda usável, mas precisa atualizar)."""
        self.status = CacheStatus.STALE.value

    def refresh(
        self,
        data: Any,
        ttl_seconds: int = None,
        computation_time_ms: int = None,
    ) -> None:
        """Atualiza cache com novos dados."""
        self.data = data
        self.status = CacheStatus.VALID.value
        self.computed_at = datetime.utcnow()

        if ttl_seconds:
            self.ttl_seconds = ttl_seconds

        self.expires_at = datetime.utcnow() + timedelta(seconds=self.ttl_seconds)

        if computation_time_ms:
            self.computation_time_ms = computation_time_ms

        if isinstance(data, dict):
            self.data_size_bytes = len(json.dumps(data).encode())
        if isinstance(data, list):
            self.row_count = len(data)

    def extend_ttl(self, additional_seconds: int) -> None:
        """Estende TTL do cache."""
        self.expires_at = self.expires_at + timedelta(seconds=additional_seconds)

    def get_data(self) -> Any:
        """Retorna dados do cache."""
        self.record_hit()
        return self.data

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "cache_key": self.cache_key,
            "cache_type": self.cache_type,
            "status": self.status,
            "is_valid": self.is_valid,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "hit_count": self.hit_count,
            "age_seconds": self.age_seconds,
            "remaining_ttl": self.remaining_ttl_seconds,
        }
