"""Modelo REPSync - Controle de Sincronização.

Gerencia o histórico e status de sincronizações com dispositivos REP.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Integer,
    String,
    Text,
    Index,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base

if TYPE_CHECKING:
    from .rep_device import REPDevice


class SyncType(str, Enum):
    """Tipos de sincronização."""
    EVENTS_PULL = "events_pull"        # Buscar eventos do REP
    EVENTS_PUSH = "events_push"        # REP enviou eventos (webhook)
    USERS_PUSH = "users_push"          # Enviar usuários para REP
    USERS_PULL = "users_pull"          # Buscar usuários do REP
    TEMPLATES_PUSH = "templates_push"  # Enviar templates biométricos
    TEMPLATES_PULL = "templates_pull"  # Buscar templates biométricos
    TIME_SYNC = "time_sync"            # Sincronizar horário
    CONFIG_PUSH = "config_push"        # Enviar configurações
    STATUS_CHECK = "status_check"      # Verificar status
    FULL_SYNC = "full_sync"            # Sincronização completa


class SyncStatus(str, Enum):
    """Status da sincronização."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class SyncTrigger(str, Enum):
    """O que disparou a sincronização."""
    SCHEDULED = "scheduled"
    MANUAL = "manual"
    WEBHOOK = "webhook"
    STARTUP = "startup"
    RECOVERY = "recovery"
    API_REQUEST = "api_request"


class REPSync(Base):
    """Modelo de Sincronização com REP."""

    __tablename__ = "rep_syncs"

    # Identificação
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rep_devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    condominio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # Tipo e status
    sync_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default=SyncStatus.PENDING.value,
        index=True,
    )
    trigger: Mapped[str] = mapped_column(
        String(20),
        default=SyncTrigger.SCHEDULED.value,
    )

    # Timestamps
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )
    duration_seconds: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    # Progresso
    total_items: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    processed_items: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    success_items: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    error_items: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    skipped_items: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    # Para sync de eventos
    last_nsr_before: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Último NSR antes da sync",
    )
    last_nsr_after: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Último NSR após a sync",
    )
    events_from_datetime: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )
    events_to_datetime: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )

    # Erros
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    error_code: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    error_details: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )

    # Retries
    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    max_retries: Mapped[int] = mapped_column(
        Integer,
        default=3,
    )
    next_retry_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )

    # Logs e detalhes
    request_log: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Log das requisições HTTP",
    )
    response_log: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Log das respostas",
    )
    items_log: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Log dos itens processados (erros)",
    )

    # Métricas
    bytes_transferred: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    api_calls_made: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    # Quem disparou
    triggered_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    # Auditoria
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    __table_args__ = (
        Index("ix_rep_syncs_device_type", "device_id", "sync_type"),
        Index("ix_rep_syncs_device_created", "device_id", "created_at"),
        Index("ix_rep_syncs_status_pending", "status",
              postgresql_where="status IN ('pending', 'in_progress')"),
    )

    def __repr__(self) -> str:
        return f"<REPSync {self.sync_type} - {self.status}>"

    @property
    def is_running(self) -> bool:
        """Verifica se sync está em execução."""
        return self.status == SyncStatus.IN_PROGRESS.value

    @property
    def is_finished(self) -> bool:
        """Verifica se sync terminou."""
        return self.status in [
            SyncStatus.COMPLETED.value,
            SyncStatus.FAILED.value,
            SyncStatus.CANCELLED.value,
            SyncStatus.TIMEOUT.value,
        ]

    @property
    def success_rate(self) -> float:
        """Taxa de sucesso."""
        if self.processed_items == 0:
            return 0.0
        return (self.success_items / self.processed_items) * 100

    @property
    def progress_percent(self) -> float:
        """Percentual de progresso."""
        if self.total_items == 0:
            return 0.0
        return (self.processed_items / self.total_items) * 100

    def can_retry(self) -> bool:
        """Verifica se pode tentar novamente."""
        return (
            self.status == SyncStatus.FAILED.value and
            self.retry_count < self.max_retries
        )

    def start(self) -> None:
        """Inicia a sincronização."""
        self.status = SyncStatus.IN_PROGRESS.value
        self.started_at = datetime.utcnow()

    def complete(self, partial: bool = False) -> None:
        """Finaliza a sincronização."""
        self.status = SyncStatus.PARTIAL.value if partial else SyncStatus.COMPLETED.value
        self.completed_at = datetime.utcnow()
        if self.started_at:
            self.duration_seconds = int(
                (self.completed_at - self.started_at).total_seconds()
            )

    def fail(self, error_message: str, error_code: str = None) -> None:
        """Marca como falha."""
        self.status = SyncStatus.FAILED.value
        self.error_message = error_message
        self.error_code = error_code
        self.completed_at = datetime.utcnow()
        if self.started_at:
            self.duration_seconds = int(
                (self.completed_at - self.started_at).total_seconds()
            )

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "device_id": str(self.device_id),
            "sync_type": self.sync_type,
            "status": self.status,
            "trigger": self.trigger,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "total_items": self.total_items,
            "processed_items": self.processed_items,
            "success_items": self.success_items,
            "error_items": self.error_items,
            "progress_percent": self.progress_percent,
            "success_rate": self.success_rate,
            "error_message": self.error_message,
        }
