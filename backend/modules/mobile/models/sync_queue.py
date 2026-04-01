"""Model de fila de sincronização offline."""

from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.models.base import Base


class SyncOperationType(StrEnum):
    """Tipos de operação de sincronização."""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    UPSERT = "upsert"


class SyncStatus(StrEnum):
    """Status da operação na fila."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"
    CANCELLED = "cancelled"


class ConflictResolution(StrEnum):
    """Estratégias de resolução de conflitos."""

    LAST_WRITE_WINS = "last_write_wins"
    SERVER_WINS = "server_wins"
    CLIENT_WINS = "client_wins"
    MERGE = "merge"
    USER_DECIDES = "user_decides"


class SyncQueueItem(Base):
    """
    Item na fila de sincronização offline.

    Armazena operações feitas offline que precisam
    ser sincronizadas com o servidor.
    """

    __tablename__ = "mobile_sync_queue"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    device_token_id = Column(
        UUID(as_uuid=True),
        ForeignKey("device_tokens.id", ondelete="SET NULL"),
        nullable=True,
    )
    operation_type = Column(
        String(20),
        nullable=False,
    )
    table_name = Column(
        String(100),
        nullable=False,
        comment="Tabela afetada pela operação",
    )
    record_id = Column(
        String(100),
        nullable=False,
        comment="ID do registro afetado",
    )
    data = Column(
        JSONB,
        default=dict,
        nullable=False,
        comment="Dados da operação",
    )
    changed_fields = Column(
        JSONB,
        default=list,
        nullable=False,
        comment="Lista de campos alterados",
    )
    client_timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="Timestamp do cliente quando operação foi feita",
    )
    server_version = Column(
        Integer,
        nullable=True,
        comment="Versão do registro no servidor antes da operação",
    )
    status = Column(
        String(20),
        default=SyncStatus.PENDING.value,
        nullable=False,
        index=True,
    )
    error_message = Column(
        Text,
        nullable=True,
    )
    retry_count = Column(
        Integer,
        default=0,
        nullable=False,
    )
    max_retries = Column(
        Integer,
        default=3,
        nullable=False,
    )
    priority = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Prioridade (maior = mais urgente)",
    )
    can_parallelize = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Se pode ser processado em paralelo",
    )
    depends_on = Column(
        UUID(as_uuid=True),
        nullable=True,
        comment="ID de operação que deve ser concluída antes",
    )
    conflict_resolution = Column(
        String(30),
        default="last_write_wins",
        nullable=False,
        comment="Estratégia de resolução de conflito",
    )
    conflict_data = Column(
        JSONB,
        nullable=True,
        comment="Dados do conflito se houver",
    )
    processed_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )
    extra_metadata = Column(
        JSONB,
        default=dict,
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relacionamentos
    user = relationship("User")
    device_token = relationship("DeviceToken")

    def __repr__(self) -> str:
        return f"<SyncQueueItem {self.id} {self.operation_type} {self.table_name}>"

    def mark_as_processing(self) -> None:
        """Marca como em processamento."""
        self.status = SyncStatus.PROCESSING.value

    def mark_as_completed(self) -> None:
        """Marca como concluída."""
        self.status = SyncStatus.COMPLETED.value
        self.processed_at = datetime.now(UTC)

    def mark_as_failed(self, error_message: str) -> None:
        """Marca como falha."""
        self.status = SyncStatus.FAILED.value
        self.error_message = error_message
        self.retry_count += 1

    def mark_as_conflict(self, conflict_data: dict) -> None:
        """Marca como conflito."""
        self.status = SyncStatus.CONFLICT.value
        self.conflict_data = conflict_data

    def can_retry(self) -> bool:
        """Verifica se pode tentar novamente."""
        return self.retry_count < self.max_retries

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "operation_type": self.operation_type,
            "table_name": self.table_name,
            "record_id": self.record_id,
            "data": self.data,
            "changed_fields": self.changed_fields,
            "client_timestamp": self.client_timestamp.isoformat() if self.client_timestamp else None,
            "status": self.status,
            "retry_count": self.retry_count,
            "can_parallelize": self.can_parallelize,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
