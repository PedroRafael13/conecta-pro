"""Model de sessão mobile."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.models.base import Base


class MobileSession(Base):
    """
    Sessão de usuário em dispositivo móvel.

    Armazena informações da sessão mobile incluindo
    token de sincronização e estado do cache.
    """

    __tablename__ = "mobile_sessions"

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
        ForeignKey("device_tokens.id", ondelete="CASCADE"),
        nullable=False,
    )
    sync_token = Column(
        String(100),
        nullable=False,
        unique=True,
        comment="Token para sincronização incremental",
    )
    last_sync_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Última sincronização bem sucedida",
    )
    last_activity_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    cached_modules = Column(
        JSONB,
        default=list,
        nullable=False,
        comment="Lista de módulos cacheados no dispositivo",
    )
    cache_version = Column(
        Integer,
        default=1,
        nullable=False,
        comment="Versão do cache local",
    )
    offline_data_size = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Tamanho estimado dos dados offline em bytes",
    )
    pending_operations = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Número de operações pendentes de sync",
    )
    connection_quality = Column(
        String(20),
        nullable=True,
        comment="Qualidade da conexão (wifi, 4g, 3g, slow)",
    )
    battery_level = Column(
        Integer,
        nullable=True,
        comment="Nível de bateria (0-100)",
    )
    storage_available = Column(
        Integer,
        nullable=True,
        comment="Armazenamento disponível em MB",
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )
    preferences = Column(
        JSONB,
        default=dict,
        nullable=False,
        comment="Preferências de sincronização",
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
        return f"<MobileSession {self.id}>"

    def update_activity(self) -> None:
        """Atualiza timestamp de atividade."""
        self.last_activity_at = datetime.now(UTC)

    def update_sync_token(self, new_token: str) -> None:
        """Atualiza token de sincronização."""
        self.sync_token = new_token
        self.last_sync_at = datetime.now(UTC)

    def increment_cache_version(self) -> None:
        """Incrementa versão do cache."""
        self.cache_version += 1

    def update_device_state(
        self,
        connection_quality: str | None = None,
        battery_level: int | None = None,
        storage_available: int | None = None,
    ) -> None:
        """Atualiza estado do dispositivo."""
        if connection_quality:
            self.connection_quality = connection_quality
        if battery_level is not None:
            self.battery_level = battery_level
        if storage_available is not None:
            self.storage_available = storage_available

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "sync_token": self.sync_token,
            "last_sync_at": self.last_sync_at.isoformat() if self.last_sync_at else None,
            "cached_modules": self.cached_modules,
            "cache_version": self.cache_version,
            "pending_operations": self.pending_operations,
            "connection_quality": self.connection_quality,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
