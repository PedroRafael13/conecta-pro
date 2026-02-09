"""Modelo REPDevice - Registrador Eletrônico de Ponto.

Gerencia dispositivos REP homologados conforme Portaria 671 MTE.
Suporta: Control iD, Intelbras, Henry, Dimep, Madis, etc.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base

if TYPE_CHECKING:
    pass


class DeviceManufacturer(StrEnum):
    """Fabricantes de REP homologados."""

    CONTROL_ID = "control_id"
    INTELBRAS = "intelbras"
    HENRY = "henry"
    DIMEP = "dimep"
    MADIS = "madis"
    TOPDATA = "topdata"
    TRIX = "trix"
    SECULLUM = "secullum"
    OUTROS = "outros"


class DeviceModel(StrEnum):
    """Modelos de REP."""

    # Control iD
    IDCLASS = "idclass"
    IDFLEX = "idflex"
    IDFACE = "idface"
    IDONLINE = "idonline"
    # Intelbras
    SS_411 = "ss_411"
    SS_610 = "ss_610"
    SS_710 = "ss_710"
    # Henry
    SUPER_EASY = "super_easy"
    ORION_6 = "orion_6"
    PRISMA_SF = "prisma_sf"
    # Dimep
    SMART_POINT = "smart_point"
    BIO_POINT = "bio_point"
    # Genérico
    GENERIC = "generic"


class DeviceStatus(StrEnum):
    """Status do dispositivo."""

    ONLINE = "online"
    OFFLINE = "offline"
    SYNCING = "syncing"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    DISABLED = "disabled"


class CommunicationProtocol(StrEnum):
    """Protocolos de comunicação."""

    HTTP_REST = "http_rest"
    TCP_SOCKET = "tcp_socket"
    SOAP = "soap"
    SERIAL = "serial"
    USB = "usb"


class AuthMethod(StrEnum):
    """Métodos de autenticação."""

    NONE = "none"
    BASIC = "basic"
    TOKEN = "token"  # noqa: S105
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    CERTIFICATE = "certificate"


class REPDevice(Base):
    """Modelo de Registrador Eletrônico de Ponto."""

    __tablename__ = "rep_devices"

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

    # Dados do fabricante
    manufacturer: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=DeviceManufacturer.CONTROL_ID.value,
    )
    model: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=DeviceModel.GENERIC.value,
    )
    firmware_version: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    # Número de registro MTE
    mte_registration: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Número de registro no MTE",
    )

    # Identificação do dispositivo
    serial_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )
    device_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Localização
    location: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Local de instalação (ex: Portaria Principal)",
    )
    latitude: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 8),
        nullable=True,
    )
    longitude: Mapped[Decimal | None] = mapped_column(
        Numeric(11, 8),
        nullable=True,
    )
    geofence_radius: Mapped[int] = mapped_column(
        Integer,
        default=100,
        comment="Raio de geofence em metros",
    )

    # Conexão
    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )
    port: Mapped[int] = mapped_column(
        Integer,
        default=80,
    )
    mac_address: Mapped[str | None] = mapped_column(
        String(17),
        nullable=True,
    )
    communication_protocol: Mapped[str] = mapped_column(
        String(20),
        default=CommunicationProtocol.HTTP_REST.value,
    )

    # Autenticação
    auth_method: Mapped[str] = mapped_column(
        String(20),
        default=AuthMethod.TOKEN.value,
    )
    auth_username: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    auth_password_encrypted: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Senha criptografada AES-256",
    )
    api_key_encrypted: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="API Key criptografada",
    )
    certificate_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Endpoints customizados
    endpoints_config: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Configuração de endpoints da API",
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        default=DeviceStatus.OFFLINE.value,
        index=True,
    )
    last_online: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
    last_sync: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    last_error_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
    consecutive_errors: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    # Configuração de sync
    sync_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )
    sync_interval_seconds: Mapped[int] = mapped_column(
        Integer,
        default=300,
        comment="Intervalo de sincronização em segundos",
    )
    sync_mode: Mapped[str] = mapped_column(
        String(20),
        default="pull",
        comment="pull (busca no REP) ou push (REP envia)",
    )
    webhook_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="URL de webhook para modo push",
    )
    webhook_secret: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Capacidades do dispositivo
    supports_biometric: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )
    supports_facial: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )
    supports_rfid: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )
    supports_password: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )
    supports_qrcode: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )
    max_users: Mapped[int] = mapped_column(
        Integer,
        default=10000,
    )
    max_fingerprints: Mapped[int] = mapped_column(
        Integer,
        default=20000,
    )
    max_faces: Mapped[int] = mapped_column(
        Integer,
        default=3000,
    )
    max_events_storage: Mapped[int] = mapped_column(
        Integer,
        default=100000,
    )

    # Contadores
    registered_users: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    registered_fingerprints: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    registered_faces: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    events_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    events_pending_sync: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    # Configurações adicionais
    timezone: Mapped[str] = mapped_column(
        String(50),
        default="America/Sao_Paulo",
    )
    ntp_server: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    auto_adjust_time: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )
    time_drift_tolerance_seconds: Mapped[int] = mapped_column(
        Integer,
        default=30,
        comment="Tolerância de drift de horário em segundos",
    )

    # Configurações específicas do fabricante
    vendor_config: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Configurações específicas do fabricante",
    )

    # Auditoria
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    __table_args__ = (
        Index("ix_rep_devices_condominio_status", "condominio_id", "status"),
        Index("ix_rep_devices_manufacturer", "manufacturer"),
        Index("ix_rep_devices_serial", "serial_number"),
    )

    def __repr__(self) -> str:
        return f"<REPDevice {self.device_name} ({self.serial_number})>"

    @property
    def is_online(self) -> bool:
        """Verifica se dispositivo está online."""
        return self.status == DeviceStatus.ONLINE.value

    @property
    def needs_sync(self) -> bool:
        """Verifica se precisa sincronizar."""
        if not self.sync_enabled or not self.is_active:
            return False
        if not self.last_sync:
            return True
        elapsed = (datetime.utcnow() - self.last_sync).total_seconds()
        return elapsed >= self.sync_interval_seconds

    @property
    def connection_url(self) -> str:
        """Retorna URL de conexão."""
        if self.communication_protocol == CommunicationProtocol.HTTP_REST.value:
            protocol = "https" if self.port == 443 else "http"
            return f"{protocol}://{self.ip_address}:{self.port}"
        return f"{self.ip_address}:{self.port}"

    def to_dict(self) -> dict:
        """Converte para dicionário (sem dados sensíveis)."""
        return {
            "id": str(self.id),
            "condominio_id": str(self.condominio_id),
            "manufacturer": self.manufacturer,
            "model": self.model,
            "serial_number": self.serial_number,
            "device_name": self.device_name,
            "location": self.location,
            "status": self.status,
            "last_online": self.last_online.isoformat() if self.last_online else None,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "sync_enabled": self.sync_enabled,
            "is_active": self.is_active,
            "supports_biometric": self.supports_biometric,
            "supports_facial": self.supports_facial,
            "supports_rfid": self.supports_rfid,
            "registered_users": self.registered_users,
            "events_pending_sync": self.events_pending_sync,
        }
