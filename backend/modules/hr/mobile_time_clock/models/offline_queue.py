"""Modelo OfflineQueue - Fila de registros offline.

Gerencia registros feitos offline que precisam ser sincronizados.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Boolean,
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


class QueueStatus(str, Enum):
    """Status do item na fila."""
    PENDING = "pending"            # Aguardando sync
    PROCESSING = "processing"      # Em processamento
    SYNCED = "synced"             # Sincronizado com sucesso
    FAILED = "failed"             # Falhou
    EXPIRED = "expired"           # Expirou (muito antigo)
    DUPLICATE = "duplicate"       # Duplicado detectado
    INVALID = "invalid"           # Dados inválidos


class QueuePriority(str, Enum):
    """Prioridade na fila."""
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class OfflineQueue(Base):
    """Modelo de fila offline."""

    __tablename__ = "offline_queue"

    # Identificação
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mobile_devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    condominio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # Identificador único do registro offline (gerado pelo app)
    offline_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    # Dados do registro
    checkin_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    checkin_type: Mapped[str] = mapped_column(String(20), nullable=False)
    device_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Geolocalização
    latitude: Mapped[Optional[float]] = mapped_column()
    longitude: Mapped[Optional[float]] = mapped_column()
    accuracy_meters: Mapped[Optional[float]] = mapped_column()

    # Validação local (feita no app)
    local_validation: Mapped[Optional[dict]] = mapped_column(JSONB)
    local_geofence_check: Mapped[bool] = mapped_column(Boolean, default=False)
    local_biometric_check: Mapped[bool] = mapped_column(Boolean, default=False)

    # Status e processamento
    status: Mapped[str] = mapped_column(
        String(20),
        default=QueueStatus.PENDING.value,
        index=True,
    )
    priority: Mapped[str] = mapped_column(
        String(20),
        default=QueuePriority.NORMAL.value,
    )

    # Resultado do sync
    checkin_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    sync_result: Mapped[Optional[dict]] = mapped_column(JSONB)

    # Erros e retry
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    error_code: Mapped[Optional[str]] = mapped_column(String(50))
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=5)
    next_retry_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_error_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Expiração
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_expired: Mapped[bool] = mapped_column(Boolean, default=False)

    # Metadados
    app_version: Mapped[Optional[str]] = mapped_column(String(20))
    device_info: Mapped[Optional[dict]] = mapped_column(JSONB)
    network_type: Mapped[Optional[str]] = mapped_column(String(20))  # wifi, 4g, 5g, offline

    # Timestamps
    queued_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    received_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Índices
    __table_args__ = (
        Index("ix_offline_queue_device_status", "device_id", "status"),
        Index("ix_offline_queue_employee_status", "employee_id", "status"),
        Index("ix_offline_queue_status_priority", "status", "priority"),
        Index("ix_offline_queue_expires", "expires_at"),
        Index("ix_offline_queue_offline_id", "offline_id"),
    )

    @property
    def can_retry(self) -> bool:
        """Verifica se pode tentar novamente."""
        if self.status != QueueStatus.FAILED.value:
            return False
        if self.is_expired:
            return False
        return self.retry_count < self.max_retries

    @property
    def is_processable(self) -> bool:
        """Verifica se pode ser processado."""
        if self.status != QueueStatus.PENDING.value:
            return False
        if self.is_expired:
            return False
        if datetime.utcnow() > self.expires_at:
            return False
        return True

    @property
    def age_hours(self) -> float:
        """Retorna idade em horas."""
        delta = datetime.utcnow() - self.device_timestamp
        return delta.total_seconds() / 3600

    def mark_processing(self) -> None:
        """Marca como em processamento."""
        self.status = QueueStatus.PROCESSING.value

    def mark_synced(self, checkin_id: uuid.UUID, result: dict = None) -> None:
        """Marca como sincronizado."""
        self.status = QueueStatus.SYNCED.value
        self.checkin_id = checkin_id
        self.synced_at = datetime.utcnow()
        self.processed_at = datetime.utcnow()
        self.sync_result = result or {}

    def mark_failed(self, error_message: str, error_code: str = None) -> None:
        """Marca como falho."""
        self.status = QueueStatus.FAILED.value
        self.error_message = error_message
        self.error_code = error_code
        self.last_error_at = datetime.utcnow()
        self.retry_count += 1

        # Calcular próximo retry com backoff exponencial
        if self.can_retry:
            from datetime import timedelta  # pylint: disable=import-outside-toplevel
            backoff_minutes = min(2 ** self.retry_count, 60)  # Max 1 hora
            self.next_retry_at = datetime.utcnow() + timedelta(minutes=backoff_minutes)
        else:
            self.next_retry_at = None

    def mark_expired(self) -> None:
        """Marca como expirado."""
        self.status = QueueStatus.EXPIRED.value
        self.is_expired = True
        self.processed_at = datetime.utcnow()

    def mark_duplicate(self) -> None:
        """Marca como duplicado."""
        self.status = QueueStatus.DUPLICATE.value
        self.processed_at = datetime.utcnow()

    def mark_invalid(self, reason: str) -> None:
        """Marca como inválido."""
        self.status = QueueStatus.INVALID.value
        self.error_message = reason
        self.processed_at = datetime.utcnow()

    def reset_for_retry(self) -> None:
        """Reseta para nova tentativa."""
        if self.can_retry:
            self.status = QueueStatus.PENDING.value
            self.error_message = None
            self.error_code = None

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "offline_id": self.offline_id,
            "device_id": str(self.device_id),
            "employee_id": str(self.employee_id),
            "checkin_type": self.checkin_type,
            "device_timestamp": self.device_timestamp.isoformat(),
            "status": self.status,
            "retry_count": self.retry_count,
            "age_hours": round(self.age_hours, 2),
            "can_retry": self.can_retry,
            "error_message": self.error_message,
        }
