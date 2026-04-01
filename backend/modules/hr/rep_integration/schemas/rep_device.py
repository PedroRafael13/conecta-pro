"""Schemas Pydantic para REPDevice."""

import re
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class REPDeviceBase(BaseModel):
    """Schema base para REPDevice."""

    manufacturer: str = Field(
        default="control_id",
        description="Fabricante do REP",
    )
    model: str = Field(
        default="generic",
        description="Modelo do REP",
    )
    firmware_version: str | None = Field(
        default=None,
        max_length=50,
    )
    mte_registration: str | None = Field(
        default=None,
        max_length=20,
        description="Número de registro no MTE",
    )
    serial_number: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Número de série do equipamento",
    )
    device_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nome identificador do dispositivo",
    )
    description: str | None = None
    location: str | None = Field(
        default=None,
        max_length=200,
    )
    latitude: Decimal | None = Field(
        default=None,
        ge=-90,
        le=90,
    )
    longitude: Decimal | None = Field(
        default=None,
        ge=-180,
        le=180,
    )
    geofence_radius: int = Field(
        default=100,
        ge=10,
        le=10000,
        description="Raio de geofence em metros",
    )
    ip_address: str | None = Field(
        default=None,
        max_length=45,
    )
    port: int = Field(
        default=80,
        ge=1,
        le=65535,
    )
    mac_address: str | None = Field(
        default=None,
        max_length=17,
    )
    communication_protocol: str = Field(
        default="http_rest",
    )
    auth_method: str = Field(
        default="token",
    )
    sync_enabled: bool = Field(default=True)
    sync_interval_seconds: int = Field(
        default=300,
        ge=60,
        le=86400,
    )
    sync_mode: str = Field(
        default="pull",
        pattern="^(pull|push)$",
    )
    supports_biometric: bool = Field(default=True)
    supports_facial: bool = Field(default=False)
    supports_rfid: bool = Field(default=True)
    supports_password: bool = Field(default=True)
    supports_qrcode: bool = Field(default=False)
    timezone: str = Field(default="America/Sao_Paulo")

    @field_validator("ip_address")
    @classmethod
    def validate_ip(cls, v: str | None) -> str | None:
        """Valida formato de endereço IP."""
        if v is None:
            return v
        # Valida IPv4 ou IPv6
        ipv4_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
        ipv6_pattern = r"^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$"
        if not (re.match(ipv4_pattern, v) or re.match(ipv6_pattern, v)):
            raise ValueError("IP inválido")
        return v

    @field_validator("mac_address")
    @classmethod
    def validate_mac(cls, v: str | None) -> str | None:
        """Valida formato de MAC address."""
        if v is None:
            return v
        mac_pattern = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
        if not re.match(mac_pattern, v):
            raise ValueError("MAC address inválido")
        return v.upper()


class REPDeviceCreate(REPDeviceBase):
    """Schema para criar REPDevice."""

    condominio_id: UUID
    auth_username: str | None = None
    auth_password: str | None = Field(
        default=None,
        description="Senha (será criptografada)",
    )
    api_key: str | None = Field(
        default=None,
        description="API Key (será criptografada)",
    )
    webhook_url: str | None = None
    webhook_secret: str | None = None
    endpoints_config: dict | None = None
    vendor_config: dict | None = None


class REPDeviceUpdate(BaseModel):
    """Schema para atualizar REPDevice."""

    device_name: str | None = Field(default=None, max_length=100)
    description: str | None = None
    location: str | None = None
    firmware_version: str | None = None
    ip_address: str | None = None
    port: int | None = None
    communication_protocol: str | None = None
    auth_method: str | None = None
    auth_username: str | None = None
    auth_password: str | None = None
    api_key: str | None = None
    sync_enabled: bool | None = None
    sync_interval_seconds: int | None = None
    sync_mode: str | None = None
    webhook_url: str | None = None
    webhook_secret: str | None = None
    endpoints_config: dict | None = None
    vendor_config: dict | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    geofence_radius: int | None = None
    timezone: str | None = None
    is_active: bool | None = None


class REPDeviceResponse(REPDeviceBase):
    """Schema de resposta para REPDevice."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    condominio_id: UUID
    status: str
    last_online: datetime | None = None
    last_sync: datetime | None = None
    last_error: str | None = None
    consecutive_errors: int = 0
    registered_users: int = 0
    registered_fingerprints: int = 0
    registered_faces: int = 0
    events_count: int = 0
    events_pending_sync: int = 0
    is_active: bool
    created_at: datetime
    updated_at: datetime


class REPDeviceList(BaseModel):
    """Schema para lista de dispositivos."""

    items: list[REPDeviceResponse]
    total: int
    page: int
    page_size: int
    pages: int


class REPDeviceFilter(BaseModel):
    """Filtros para busca de dispositivos."""

    condominio_id: UUID | None = None
    manufacturer: str | None = None
    model: str | None = None
    status: str | None = None
    is_active: bool | None = None
    sync_enabled: bool | None = None
    location: str | None = None
    search: str | None = Field(
        default=None,
        description="Busca em nome, serial, localização",
    )


class REPDeviceStatusUpdate(BaseModel):
    """Schema para atualizar status do dispositivo."""

    status: str
    error_message: str | None = None


class REPDeviceCredentials(BaseModel):
    """Schema para credenciais do dispositivo."""

    auth_username: str | None = None
    auth_password: str | None = None
    api_key: str | None = None
    certificate_path: str | None = None


class REPDeviceTestConnection(BaseModel):
    """Schema para resultado de teste de conexão."""

    success: bool
    latency_ms: int | None = None
    device_info: dict | None = None
    error_message: str | None = None
