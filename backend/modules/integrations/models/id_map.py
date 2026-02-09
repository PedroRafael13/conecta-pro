"""
IDMap Model - Mapeamento de IDs Externos para Internos
Sprint 33: Integration Framework
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID

from core.database import Base


class IDMap(Base):
    """
    Model para mapeamento de IDs entre sistemas.
    Mantém a relação ID externo <-> ID interno por entidade.
    Essencial para idempotência e reconciliação.
    """

    __tablename__ = "id_maps"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Referências
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    account_id = Column(
        UUID(as_uuid=True), ForeignKey("integration_accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Sistema e Entidade
    connector_type = Column(String(50), nullable=False)
    entity_type = Column(String(100), nullable=False)  # "product", "client", etc.

    # IDs
    external_id = Column(String(500), nullable=False)  # ID no sistema externo
    internal_id = Column(UUID(as_uuid=True), nullable=False)  # ID no Conecta PRO

    # IDs alternativos (alguns sistemas têm múltiplos identificadores)
    external_code = Column(String(200), nullable=True)  # Código/SKU
    external_reference = Column(String(200), nullable=True)  # Referência alternativa

    # Hash para detectar mudanças
    data_hash = Column(String(64), nullable=True)  # SHA-256 dos dados
    last_data_hash = Column(String(64), nullable=True)  # Hash anterior

    # Timestamps de sync
    first_synced_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_synced_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_modified_external_at = Column(DateTime, nullable=True)  # Quando mudou no externo
    last_modified_internal_at = Column(DateTime, nullable=True)  # Quando mudou no interno

    # Direção do último sync
    last_sync_direction = Column(String(20), nullable=True)  # "inbound" ou "outbound"

    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    is_synced = Column(Boolean, nullable=False, default=True)
    needs_update = Column(Boolean, nullable=False, default=False)
    has_conflict = Column(Boolean, nullable=False, default=False)

    # Conflito (se houver)
    conflict_data = Column(JSONB, nullable=True)
    conflict_resolved_at = Column(DateTime, nullable=True)
    conflict_resolved_by = Column(UUID(as_uuid=True), nullable=True)

    # Metadados extras
    extra_metadata = Column(JSONB, nullable=True)  # renamed from "metadata" (reserved)
    notes = Column(Text, nullable=True)

    # Auditoria
    ativo = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Índices e constraints
    __table_args__ = (
        # Unicidade: tenant + account + entity + external_id
        UniqueConstraint("tenant_id", "account_id", "entity_type", "external_id", name="uq_id_map_external"),
        # Unicidade: tenant + account + entity + internal_id
        UniqueConstraint("tenant_id", "account_id", "entity_type", "internal_id", name="uq_id_map_internal"),
        Index("ix_id_maps_tenant_id", "tenant_id"),
        Index("ix_id_maps_account_id", "account_id"),
        Index("ix_id_maps_entity_type", "entity_type"),
        Index("ix_id_maps_external_id", "external_id"),
        Index("ix_id_maps_internal_id", "internal_id"),
        Index("ix_id_maps_connector_type", "connector_type"),
        Index("ix_id_maps_external_code", "external_code"),
        Index("ix_id_maps_tenant_entity", "tenant_id", "entity_type"),
        Index("ix_id_maps_account_entity", "account_id", "entity_type"),
        Index("ix_id_maps_needs_update", "needs_update"),
        Index("ix_id_maps_has_conflict", "has_conflict"),
        Index("ix_id_maps_ativo", "ativo"),
    )

    def __repr__(self) -> str:
        return f"<IDMap {self.entity_type} ext={self.external_id} int={self.internal_id}>"

    def mark_synced(self, direction: str = "inbound", data_hash: str | None = None) -> None:
        """Marca como sincronizado."""
        self.last_synced_at = datetime.utcnow()
        self.last_sync_direction = direction
        self.is_synced = True
        self.needs_update = False
        if data_hash:
            self.last_data_hash = self.data_hash
            self.data_hash = data_hash
        self.updated_at = datetime.utcnow()

    def mark_needs_update(self, direction: str = "outbound") -> None:
        """Marca que precisa de atualização."""
        self.needs_update = True
        self.is_synced = False
        self.updated_at = datetime.utcnow()

    def mark_conflict(self, conflict_data: dict) -> None:
        """Marca conflito de dados."""
        self.has_conflict = True
        self.conflict_data = conflict_data
        self.is_synced = False
        self.updated_at = datetime.utcnow()

    def resolve_conflict(self, resolved_by: str | None = None, keep_external: bool = True) -> None:
        """Resolve conflito."""
        self.has_conflict = False
        self.conflict_resolved_at = datetime.utcnow()
        if resolved_by:
            self.conflict_resolved_by = resolved_by
        if self.conflict_data:
            resolution = "external" if keep_external else "internal"
            self.conflict_data["resolution"] = resolution
            self.conflict_data["resolved_at"] = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow()

    def deactivate(self, reason: str | None = None) -> None:
        """Desativa o mapeamento."""
        self.is_active = False
        if reason:
            self.notes = f"Desativado: {reason}"
        self.updated_at = datetime.utcnow()

    def reactivate(self) -> None:
        """Reativa o mapeamento."""
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def update_external_modified(self, modified_at: datetime) -> None:
        """Atualiza timestamp de modificação externa."""
        self.last_modified_external_at = modified_at
        self.updated_at = datetime.utcnow()

    def update_internal_modified(self, modified_at: datetime) -> None:
        """Atualiza timestamp de modificação interna."""
        self.last_modified_internal_at = modified_at
        self.updated_at = datetime.utcnow()

    def has_changed(self, new_hash: str) -> bool:
        """Verifica se dados mudaram baseado no hash."""
        return self.data_hash != new_hash

    @property
    def is_stale(self) -> bool:
        """Verifica se está desatualizado (não sincronizado há muito tempo)."""
        if not self.last_synced_at:
            return True
        delta = datetime.utcnow() - self.last_synced_at
        # Considera stale após 24 horas sem sync
        return delta.total_seconds() > 86400

    @property
    def sync_age_hours(self) -> float:
        """Horas desde último sync."""
        if not self.last_synced_at:
            return float("inf")
        delta = datetime.utcnow() - self.last_synced_at
        return delta.total_seconds() / 3600

    @classmethod
    def create_mapping(
        cls,
        tenant_id: str,
        account_id: str,
        connector_type: str,
        entity_type: str,
        external_id: str,
        internal_id: str,
        external_code: str | None = None,
        data_hash: str | None = None,
        extra_metadata: dict | None = None,
    ) -> "IDMap":
        """Factory method para criar mapeamento."""
        return cls(
            tenant_id=tenant_id,
            account_id=account_id,
            connector_type=connector_type,
            entity_type=entity_type,
            external_id=external_id,
            internal_id=internal_id,
            external_code=external_code,
            data_hash=data_hash,
            extra_metadata=extra_metadata,
            first_synced_at=datetime.utcnow(),
            last_synced_at=datetime.utcnow(),
            is_active=True,
            is_synced=True,
        )
