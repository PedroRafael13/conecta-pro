"""Schemas Pydantic para REPDevice."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, ConfigDict
import re


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
    firmware_version: Optional[str] = Field(
        default=None,
        max_length=50,
    )
    mte_registration: Optional[str] = Field(
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
    description: Optional[str] = None
    location: Optional[str] = Field(
        default=None,
        max_length=200,
    )
    latitude: Optional[Decimal] = Field(
        default=None,
        ge=-90,
        le=90,
    )
    longitude: Optional[Decimal] = Field(
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
    ip_address: Optional[str] = Field(
        default=None,
        max_length=45,
    )
    port: int = Field(
        default=80,
        ge=1,
        le=65535,
    )
    mac_address: Optional[str] = Field(
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
    def validate_ip(cls, v: Optional[str]) -> Optional[str]:
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
    def validate_mac(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        mac_pattern = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
        if not re.match(mac_pattern, v):
            raise ValueError("MAC address inválido")
        return v.upper()


class REPDeviceCreate(REPDeviceBase):
    """Schema para criar REPDevice."""

    condominio_id: UUID
    auth_username: Optional[str] = None
    auth_password: Optional[str] = Field(
        default=None,
        description="Senha (será criptografada)",
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API Key (será criptografada)",
    )
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None
    endpoints_config: Optional[dict] = None
    vendor_config: Optional[dict] = None


class REPDeviceUpdate(BaseModel):
    """Schema para atualizar REPDevice."""

    device_name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = None
    location: Optional[str] = None
    firmware_version: Optional[str] = None
    ip_address: Optional[str] = None
    port: Optional[int] = None
    communication_protocol: Optional[str] = None
    auth_method: Optional[str] = None
    auth_username: Optional[str] = None
    auth_password: Optional[str] = None
    api_key: Optional[str] = None
    sync_enabled: Optional[bool] = None
    sync_interval_seconds: Optional[int] = None
    sync_mode: Optional[str] = None
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None
    endpoints_config: Optional[dict] = None
    vendor_config: Optional[dict] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    geofence_radius: Optional[int] = None
    timezone: Optional[str] = None
    is_active: Optional[bool] = None


class REPDeviceResponse(REPDeviceBase):
    """Schema de resposta para REPDevice."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    condominio_id: UUID
    status: str
    last_online: Optional[datetime] = None
    last_sync: Optional[datetime] = None
    last_error: Optional[str] = None
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

    items: List[REPDeviceResponse]
    total: int
    page: int
    page_size: int
    pages: int


class REPDeviceFilter(BaseModel):
    """Filtros para busca de dispositivos."""

    condominio_id: Optional[UUID] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None
    sync_enabled: Optional[bool] = None
    location: Optional[str] = None
    search: Optional[str] = Field(
        default=None,
        description="Busca em nome, serial, localização",
    )


class REPDeviceStatusUpdate(BaseModel):
    """Schema para atualizar status do dispositivo."""

    status: str
    error_message: Optional[str] = None


class REPDeviceCredentials(BaseModel):
    """Schema para credenciais do dispositivo."""

    auth_username: Optional[str] = None
    auth_password: Optional[str] = None
    api_key: Optional[str] = None
    certificate_path: Optional[str] = None


class REPDeviceTestConnection(BaseModel):
    """Schema para resultado de teste de conexão."""

    success: bool
    latency_ms: Optional[int] = None
    device_info: Optional[dict] = None
    error_message: Optional[str] = None
