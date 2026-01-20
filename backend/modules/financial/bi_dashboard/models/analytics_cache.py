"""Model de Cache de Analytics Financeiro."""

import hashlib
import json
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID

from core.models.base import Base


class CacheStatus(str, Enum):
    """Status do cache."""

    VALID = "VALID"
    STALE = "STALE"
    EXPIRED = "EXPIRED"
    REFRESHING = "REFRESHING"
    ERROR = "ERROR"


class CacheType(str, Enum):
    """Tipo de cache."""

    WIDGET = "WIDGET"
    KPI = "KPI"
    DASHBOARD = "DASHBOARD"
    REPORT = "REPORT"
    QUERY = "QUERY"
    AGGREGATION = "AGGREGATION"


class AnalyticsCache(Base):
    """Cache de dados de Analytics Financeiro."""

    __tablename__ = "financial_analytics_cache"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=False,
        index=True,
    )

    # Identificacao
    cache_key = Column(String(255), nullable=False, index=True)
    tipo = Column(
        SQLEnum(CacheType, name="cache_type_enum"),
        default=CacheType.QUERY,
        nullable=False,
    )
    status = Column(
        SQLEnum(CacheStatus, name="cache_status_enum"),
        default=CacheStatus.VALID,
        nullable=False,
    )

    # Referencia
    entity_type = Column(String(100))
    entity_id = Column(PGUUID(as_uuid=True))
    query_hash = Column(String(64))

    # Dados
    data = Column(JSONB, nullable=False)
    data_size_bytes = Column(Integer)
    row_count = Column(Integer)

    # Parametros
    parametros = Column(JSONB, default=dict)
    periodo_inicio = Column(DateTime)
    periodo_fim = Column(DateTime)

    # TTL e Expiracao
    ttl_seconds = Column(Integer, default=300, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_expired = Column(Boolean, default=False)

    # Estatisticas
    hit_count = Column(Integer, default=0, nullable=False)
    miss_count = Column(Integer, default=0, nullable=False)
    last_hit_at = Column(DateTime)
    last_refresh_at = Column(DateTime)
    refresh_count = Column(Integer, default=0)
    refresh_duration_ms = Column(Integer)

    # Erro
    last_error = Column(Text)
    error_count = Column(Integer, default=0)

    # Metadados
    tags = Column(JSONB, default=list)
    extra_metadata = Column(JSONB, default=dict)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        """Representacao do cache."""
        return f"<AnalyticsCache {self.cache_key}: {self.status.value}>"

    @property
    def is_valid(self) -> bool:
        """Verifica se cache eh valido."""
        if self.status != CacheStatus.VALID:
            return False
        return datetime.utcnow() < self.expires_at

    @property
    def is_stale(self) -> bool:
        """Verifica se cache esta obsoleto."""
        return self.status == CacheStatus.STALE

    @property
    def hit_rate(self) -> Decimal:
        """Calcula taxa de acerto."""
        total = self.hit_count + self.miss_count
        if total == 0:
            return Decimal("0")
        return Decimal(str((self.hit_count / total) * 100))

    @property
    def age_seconds(self) -> int:
        """Idade do cache em segundos."""
        if not self.last_refresh_at:
            return (datetime.utcnow() - self.created_at).total_seconds()
        return (datetime.utcnow() - self.last_refresh_at).total_seconds()

    @property
    def time_to_live(self) -> int:
        """Tempo restante de vida em segundos."""
        if self.is_expired:
            return 0
        remaining = (self.expires_at - datetime.utcnow()).total_seconds()
        return max(0, int(remaining))

    def set_data(self, data: Any, ttl: int = None) -> None:
        """Define dados no cache."""
        self.data = data
        self.status = CacheStatus.VALID
        self.last_refresh_at = datetime.utcnow()
        self.refresh_count += 1

        if ttl:
            self.ttl_seconds = ttl
        self.expires_at = datetime.utcnow() + timedelta(seconds=self.ttl_seconds)
        self.is_expired = False

        # Calcula tamanho aproximado
        json_str = json.dumps(data, default=str)
        self.data_size_bytes = len(json_str.encode("utf-8"))

        if isinstance(data, list):
            self.row_count = len(data)
        elif isinstance(data, dict) and "items" in data:
            self.row_count = len(data["items"])

    def record_hit(self) -> None:
        """Registra acerto de cache."""
        self.hit_count += 1
        self.last_hit_at = datetime.utcnow()

    def record_miss(self) -> None:
        """Registra erro de cache."""
        self.miss_count += 1

    def mark_stale(self) -> None:
        """Marca cache como obsoleto."""
        self.status = CacheStatus.STALE

    def mark_expired(self) -> None:
        """Marca cache como expirado."""
        self.status = CacheStatus.EXPIRED
        self.is_expired = True

    def mark_refreshing(self) -> None:
        """Marca cache como em atualizacao."""
        self.status = CacheStatus.REFRESHING

    def set_error(self, error: str) -> None:
        """Define erro no cache."""
        self.status = CacheStatus.ERROR
        self.last_error = error
        self.error_count += 1

    def invalidate(self) -> None:
        """Invalida o cache."""
        self.status = CacheStatus.EXPIRED
        self.is_expired = True
        self.expires_at = datetime.utcnow()

    def extend_ttl(self, extra_seconds: int) -> None:
        """Estende tempo de vida do cache."""
        self.expires_at = self.expires_at + timedelta(seconds=extra_seconds)
        if self.status == CacheStatus.EXPIRED:
            self.status = CacheStatus.VALID
            self.is_expired = False

    @classmethod
    def generate_key(
        cls,
        entity_type: str,
        entity_id: str,
        params: dict = None,
    ) -> str:
        """Gera chave de cache."""
        key = f"{entity_type}:{entity_id}"
        if params:
            param_str = json.dumps(params, sort_keys=True)
            param_hash = hashlib.md5(param_str.encode()).hexdigest()[:8]
            key = f"{key}:{param_hash}"
        return key
