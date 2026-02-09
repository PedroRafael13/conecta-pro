"""Modelo MobileDevice - Dispositivos móveis para registro de ponto.

Gerencia smartphones e tablets autorizados para registro de ponto.
"""

import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from .mobile_checkin import MobileCheckIn


class DevicePlatform(StrEnum):
    """Plataforma do dispositivo."""

    ANDROID = "android"
    IOS = "ios"
    WEB = "web"


class DeviceStatus(StrEnum):
    """Status do dispositivo."""

    PENDING = "pending"  # Aguardando aprovação
    ACTIVE = "active"  # Ativo e autorizado
    BLOCKED = "blocked"  # Bloqueado por admin
    REVOKED = "revoked"  # Autorização revogada
    LOST = "lost"  # Reportado como perdido


class BiometricCapability(StrEnum):
    """Capacidades biométricas do dispositivo."""

    NONE = "none"
    FINGERPRINT = "fingerprint"
    FACE_ID = "face_id"
    IRIS = "iris"
    BOTH = "both"  # Fingerprint + Face


class MobileDevice(Base):
    """Modelo de dispositivo móvel."""

    __tablename__ = "mobile_devices"

    # Identificação
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
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

    # Informações do dispositivo
    device_name: Mapped[str] = mapped_column(String(100), nullable=False)
    device_uuid: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    platform: Mapped[str] = mapped_column(
        String(20),
        default=DevicePlatform.ANDROID.value,
    )
    os_version: Mapped[str | None] = mapped_column(String(50))
    app_version: Mapped[str | None] = mapped_column(String(20))
    model: Mapped[str | None] = mapped_column(String(100))
    manufacturer: Mapped[str | None] = mapped_column(String(100))

    # Push notifications
    push_token: Mapped[str | None] = mapped_column(Text)
    push_provider: Mapped[str | None] = mapped_column(String(20))  # fcm, apns

    # Biometria
    biometric_capability: Mapped[str] = mapped_column(
        String(20),
        default=BiometricCapability.NONE.value,
    )
    biometric_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    biometric_enrolled_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Geolocalização
    location_permission: Mapped[bool] = mapped_column(Boolean, default=False)
    background_location: Mapped[bool] = mapped_column(Boolean, default=False)
    last_known_lat: Mapped[float | None] = mapped_column()
    last_known_lng: Mapped[float | None] = mapped_column()
    last_location_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Status e segurança
    status: Mapped[str] = mapped_column(
        String(20),
        default=DeviceStatus.PENDING.value,
        index=True,
    )
    is_trusted: Mapped[bool] = mapped_column(Boolean, default=False)
    trust_score: Mapped[int] = mapped_column(Integer, default=0)  # 0-100

    # Tokens e autenticação
    refresh_token_hash: Mapped[str | None] = mapped_column(String(256))
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Configurações
    allow_offline_checkin: Mapped[bool] = mapped_column(Boolean, default=True)
    max_offline_hours: Mapped[int] = mapped_column(Integer, default=24)
    require_photo: Mapped[bool] = mapped_column(Boolean, default=False)
    require_biometric: Mapped[bool] = mapped_column(Boolean, default=False)

    # Contadores
    checkin_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_failed_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Aprovação
    approved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime)
    blocked_reason: Mapped[str | None] = mapped_column(Text)
    blocked_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    blocked_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Metadados
    device_info: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    settings: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    # Timestamps
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime)
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

    # Relacionamentos
    checkins: Mapped[list["MobileCheckIn"]] = relationship(
        "MobileCheckIn",
        back_populates="device",
        lazy="dynamic",
    )

    # Índices
    __table_args__ = (
        Index("ix_mobile_devices_employee_status", "employee_id", "status"),
        Index("ix_mobile_devices_condominio_status", "condominio_id", "status"),
        Index("ix_mobile_devices_device_uuid", "device_uuid"),
    )

    @property
    def is_authorized(self) -> bool:
        """Verifica se dispositivo está autorizado."""
        return self.status == DeviceStatus.ACTIVE.value and self.is_active

    @property
    def can_checkin(self) -> bool:
        """Verifica se pode fazer check-in."""
        if not self.is_authorized:
            return False
        if self.failed_attempts >= 5:
            return False
        return True

    @property
    def needs_biometric(self) -> bool:
        """Verifica se precisa de biometria."""
        return self.require_biometric and self.biometric_enabled

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "employee_id": str(self.employee_id),
            "device_name": self.device_name,
            "platform": self.platform,
            "status": self.status,
            "is_trusted": self.is_trusted,
            "biometric_enabled": self.biometric_enabled,
            "checkin_count": self.checkin_count,
            "last_seen_at": self.last_seen_at.isoformat() if self.last_seen_at else None,
        }
