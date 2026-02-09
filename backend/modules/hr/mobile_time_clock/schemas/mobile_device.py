"""Schemas para MobileDevice."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class MobileDeviceBase(BaseModel):
    """Schema base para dispositivo móvel."""

    device_name: str = Field(..., min_length=1, max_length=100)
    platform: str = Field(default="android")
    os_version: str | None = Field(None, max_length=50)
    app_version: str | None = Field(None, max_length=20)
    model: str | None = Field(None, max_length=100)
    manufacturer: str | None = Field(None, max_length=100)


class MobileDeviceRegister(MobileDeviceBase):
    """Schema para registrar novo dispositivo."""

    device_uuid: str = Field(..., min_length=10, max_length=100)
    push_token: str | None = None
    push_provider: str | None = Field(None, pattern="^(fcm|apns)$")
    biometric_capability: str = Field(default="none")
    device_info: dict | None = Field(default_factory=dict)

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, v: str) -> str:
        """Valida plataforma."""
        allowed = ["android", "ios", "web"]
        if v.lower() not in allowed:
            raise ValueError(f"Platform must be one of: {allowed}")
        return v.lower()


class MobileDeviceUpdate(BaseModel):
    """Schema para atualizar dispositivo."""

    device_name: str | None = Field(None, min_length=1, max_length=100)
    push_token: str | None = None
    push_provider: str | None = Field(None, pattern="^(fcm|apns)$")
    os_version: str | None = Field(None, max_length=50)
    app_version: str | None = Field(None, max_length=20)
    biometric_enabled: bool | None = None
    location_permission: bool | None = None
    background_location: bool | None = None
    settings: dict | None = None


class MobileDeviceApprove(BaseModel):
    """Schema para aprovar dispositivo."""

    is_trusted: bool = Field(default=False)
    require_photo: bool = Field(default=False)
    require_biometric: bool = Field(default=False)
    allow_offline_checkin: bool = Field(default=True)
    max_offline_hours: int = Field(default=24, ge=1, le=168)


class MobileDeviceBlock(BaseModel):
    """Schema para bloquear dispositivo."""

    reason: str = Field(..., min_length=5, max_length=500)


class MobileDeviceResponse(BaseModel):
    """Schema de resposta para dispositivo."""

    id: UUID
    employee_id: UUID
    condominio_id: UUID
    device_name: str
    device_uuid: str
    platform: str
    os_version: str | None
    app_version: str | None
    model: str | None
    manufacturer: str | None
    biometric_capability: str
    biometric_enabled: bool
    location_permission: bool
    status: str
    is_trusted: bool
    trust_score: int
    checkin_count: int
    require_photo: bool
    require_biometric: bool
    allow_offline_checkin: bool
    first_seen_at: datetime
    last_seen_at: datetime | None
    is_active: bool
    created_at: datetime

    class Config:  # pylint: disable=too-few-public-methods
        """Configuracao do Pydantic."""

        from_attributes = True


class MobileDeviceList(BaseModel):
    """Schema de lista de dispositivos."""

    items: list[MobileDeviceResponse]
    total: int
    page: int
    page_size: int
    pages: int


class MobileDeviceFilter(BaseModel):
    """Filtros para busca de dispositivos."""

    employee_id: UUID | None = None
    condominio_id: UUID | None = None
    platform: str | None = None
    status: str | None = None
    is_trusted: bool | None = None
    is_active: bool | None = None


class MobileDeviceStats(BaseModel):
    """Estatísticas de dispositivos."""

    total_devices: int
    active_devices: int
    pending_approval: int
    blocked_devices: int
    by_platform: dict
    by_status: dict
    avg_trust_score: float
    devices_with_biometric: int
    devices_with_offline: int


class DeviceHeartbeat(BaseModel):
    """Schema para heartbeat do dispositivo."""

    app_version: str
    battery_level: int | None = Field(None, ge=0, le=100)
    network_type: str | None = None
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    accuracy_meters: float | None = None


class DeviceLocationUpdate(BaseModel):
    """Schema para atualização de localização."""

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy_meters: float | None = Field(None, ge=0)
    altitude: float | None = None
    speed: float | None = None
    heading: float | None = None
