"""
SyncState Model - Estado Incremental de Sincronização
Sprint 33: Integration Framework
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID

from core.database import Base


class SyncState(Base):
    """
    Model para armazenar estado incremental de sincronização.
    Permite retomar syncs de onde pararam e fazer delta sync.
    """

    __tablename__ = "sync_states"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Referências
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    account_id = Column(
        UUID(as_uuid=True), ForeignKey("integration_accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Identificação única: tenant + account + entity
    connector_type = Column(String(50), nullable=False)
    entity_type = Column(String(100), nullable=False)  # "products", "clients", etc.

    # Cursor/Pagination
    # Diferentes APIs usam diferentes estratégias
    last_cursor = Column(String(500), nullable=True)  # Para APIs com cursor
    last_page = Column(Integer, nullable=True)  # Para APIs com paginação
    last_offset = Column(Integer, nullable=True)  # Para APIs com offset

    # Timestamp-based sync
    last_sync_timestamp = Column(DateTime, nullable=True)  # updated_at > este valor
    last_created_at = Column(DateTime, nullable=True)
    last_modified_at = Column(DateTime, nullable=True)

    # ID-based sync
    last_synced_id = Column(String(200), nullable=True)  # Último ID processado
    last_synced_external_id = Column(String(200), nullable=True)

    # ETag/Version (para APIs que suportam)
    etag = Column(String(200), nullable=True)
    version = Column(String(100), nullable=True)

    # Estatísticas
    total_items_synced = Column(Integer, nullable=False, default=0)
    total_syncs = Column(Integer, nullable=False, default=0)
    last_sync_items = Column(Integer, nullable=False, default=0)

    # Full sync control
    last_full_sync_at = Column(DateTime, nullable=True)
    full_sync_required = Column(Boolean, nullable=False, default=False)
    full_sync_reason = Column(String(500), nullable=True)

    # Checkpoint para recovery
    checkpoint_data = Column(JSONB, nullable=True)

    # Timing
    first_sync_at = Column(DateTime, nullable=True)
    last_sync_at = Column(DateTime, nullable=True)
    last_sync_duration_ms = Column(Integer, nullable=True)

    # Erros
    consecutive_failures = Column(Integer, nullable=False, default=0)
    last_error = Column(Text, nullable=True)
    last_error_at = Column(DateTime, nullable=True)

    # Hash para detectar mudanças de schema
    schema_hash = Column(String(64), nullable=True)

    # Metadados extras
    extra_state = Column(JSONB, nullable=True)

    # Auditoria
    ativo = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Índices e constraints
    __table_args__ = (
        UniqueConstraint("tenant_id", "account_id", "entity_type", name="uq_sync_state_tenant_account_entity"),
        Index("ix_sync_states_tenant_id", "tenant_id"),
        Index("ix_sync_states_account_id", "account_id"),
        Index("ix_sync_states_entity_type", "entity_type"),
        Index("ix_sync_states_connector_type", "connector_type"),
        Index("ix_sync_states_last_sync_at", "last_sync_at"),
        Index("ix_sync_states_tenant_account", "tenant_id", "account_id"),
        Index("ix_sync_states_ativo", "ativo"),
    )

    def __repr__(self) -> str:
        return f"<SyncState {self.connector_type}/{self.entity_type}>"

    def update_cursor(self, cursor: str | None = None, page: int | None = None, offset: int | None = None) -> None:
        """Atualiza cursor de paginação."""
        if cursor is not None:
            self.last_cursor = cursor
        if page is not None:
            self.last_page = page
        if offset is not None:
            self.last_offset = offset
        self.updated_at = datetime.utcnow()

    def update_timestamp(
        self,
        sync_timestamp: datetime | None = None,
        created_at: datetime | None = None,
        modified_at: datetime | None = None,
    ) -> None:
        """Atualiza timestamps de sync."""
        if sync_timestamp is not None:
            self.last_sync_timestamp = sync_timestamp
        if created_at is not None:
            self.last_created_at = created_at
        if modified_at is not None:
            self.last_modified_at = modified_at
        self.updated_at = datetime.utcnow()

    def update_last_id(self, internal_id: str | None = None, external_id: str | None = None) -> None:
        """Atualiza último ID processado."""
        if internal_id is not None:
            self.last_synced_id = internal_id
        if external_id is not None:
            self.last_synced_external_id = external_id
        self.updated_at = datetime.utcnow()

    def complete_sync(self, items_synced: int, duration_ms: int, cursor: str | None = None) -> None:
        """Marca sync como completo."""
        now = datetime.utcnow()
        if not self.first_sync_at:
            self.first_sync_at = now
        self.last_sync_at = now
        self.last_sync_items = items_synced
        self.last_sync_duration_ms = duration_ms
        self.total_items_synced += items_synced
        self.total_syncs += 1
        self.consecutive_failures = 0
        if cursor is not None:
            self.last_cursor = cursor
        self.updated_at = now

    def complete_full_sync(self, items_synced: int, duration_ms: int) -> None:
        """Marca full sync como completo."""
        self.complete_sync(items_synced, duration_ms)
        self.last_full_sync_at = datetime.utcnow()
        self.full_sync_required = False
        self.full_sync_reason = None
        # Reset cursors após full sync
        self.last_cursor = None
        self.last_page = None
        self.last_offset = None

    def mark_failure(self, error_message: str) -> None:
        """Marca falha na sync."""
        self.consecutive_failures += 1
        self.last_error = error_message
        self.last_error_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def require_full_sync(self, reason: str) -> None:
        """Marca que precisa de full sync."""
        self.full_sync_required = True
        self.full_sync_reason = reason
        self.updated_at = datetime.utcnow()

    def reset(self) -> None:
        """Reseta estado para começar do zero."""
        self.last_cursor = None
        self.last_page = None
        self.last_offset = None
        self.last_sync_timestamp = None
        self.last_created_at = None
        self.last_modified_at = None
        self.last_synced_id = None
        self.last_synced_external_id = None
        self.etag = None
        self.version = None
        self.checkpoint_data = None
        self.full_sync_required = True
        self.full_sync_reason = "Estado resetado manualmente"
        self.updated_at = datetime.utcnow()

    def save_checkpoint(self, data: dict) -> None:
        """Salva checkpoint para recovery."""
        self.checkpoint_data = data
        self.updated_at = datetime.utcnow()

    def clear_checkpoint(self) -> None:
        """Limpa checkpoint."""
        self.checkpoint_data = None
        self.updated_at = datetime.utcnow()

    @property
    def needs_full_sync(self) -> bool:
        """Verifica se precisa de full sync."""
        if self.full_sync_required:
            return True
        # Se nunca fez sync, precisa de full
        if not self.first_sync_at:
            return True
        return False

    @property
    def has_valid_cursor(self) -> bool:
        """Verifica se tem cursor válido para incremental."""
        return bool(
            self.last_cursor or self.last_page or self.last_offset or self.last_sync_timestamp or self.last_synced_id
        )

    @property
    def is_healthy(self) -> bool:
        """Verifica se está saudável (sem muitas falhas)."""
        return self.consecutive_failures < 3

    @property
    def days_since_full_sync(self) -> int | None:
        """Dias desde último full sync."""
        if not self.last_full_sync_at:
            return None
        delta = datetime.utcnow() - self.last_full_sync_at
        return delta.days

    def get_incremental_params(self) -> dict:
        """Retorna parâmetros para sync incremental."""
        params = {}
        if self.last_cursor:
            params["cursor"] = self.last_cursor
        if self.last_page:
            params["page"] = self.last_page + 1
        if self.last_offset:
            params["offset"] = self.last_offset
        if self.last_sync_timestamp:
            params["updated_since"] = self.last_sync_timestamp.isoformat()
        if self.last_synced_external_id:
            params["after_id"] = self.last_synced_external_id
        if self.etag:
            params["if_none_match"] = self.etag
        return params
