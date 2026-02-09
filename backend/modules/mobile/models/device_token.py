"""Model de Device Token para push notifications."""

from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID

from core.models.base import Base


class DevicePlatform(StrEnum):
    """Plataformas de dispositivo suportadas."""

    ANDROID = "android"
    IOS = "ios"
    WEB = "web"


class DeviceToken(Base):
    """
    Token de dispositivo para push notifications.

    Armazena tokens FCM (Android) e APNs (iOS) para envio
    de notificações push aos dispositivos dos usuários.
    """

    __tablename__ = "device_tokens"

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
    token = Column(
        String(500),
        nullable=False,
        unique=True,
        index=True,
    )
    platform = Column(
        String(20),
        nullable=False,
    )
    device_id = Column(
        String(100),
        nullable=True,
        comment="Identificador único do dispositivo",
    )
    device_name = Column(
        String(200),
        nullable=True,
        comment="Nome do dispositivo (ex: iPhone de João)",
    )
    device_model = Column(
        String(100),
        nullable=True,
        comment="Modelo do dispositivo",
    )
    os_version = Column(
        String(50),
        nullable=True,
        comment="Versão do sistema operacional",
    )
    app_version = Column(
        String(50),
        nullable=True,
        comment="Versão do app instalado",
    )
    app_build = Column(
        String(50),
        nullable=True,
        comment="Build number do app",
    )
    push_enabled = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Se push está habilitado no dispositivo",
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )
    locale = Column(
        String(10),
        nullable=True,
        default="pt-BR",
        comment="Idioma do dispositivo",
    )
    timezone = Column(
        String(50),
        nullable=True,
        comment="Timezone do dispositivo",
    )
    extra_metadata = Column(
        JSONB,
        default=dict,
        nullable=False,
        comment="Metadados adicionais do dispositivo",
    )
    last_used = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        comment="Última vez que o token foi usado",
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
    # user = relationship("User", back_populates="device_tokens")  # TODO: Adicionar device_tokens no modelo User

    def __repr__(self) -> str:
        return f"<DeviceToken {self.id} platform={self.platform}>"

    def update_last_used(self) -> None:
        """Atualiza timestamp de último uso."""
        self.last_used = datetime.now(UTC)

    def deactivate(self) -> None:
        """Desativa o token."""
        self.is_active = False
        self.updated_at = datetime.now(UTC)

    def activate(self) -> None:
        """Ativa o token."""
        self.is_active = True
        self.updated_at = datetime.now(UTC)

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "platform": self.platform,
            "device_name": self.device_name,
            "device_model": self.device_model,
            "os_version": self.os_version,
            "app_version": self.app_version,
            "push_enabled": self.push_enabled,
            "is_active": self.is_active,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
