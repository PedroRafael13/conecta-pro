"""Schemas para MobileDevice."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class MobileDeviceBase(BaseModel):
    """Schema base para dispositivo móvel."""
    device_name: str = Field(..., min_length=1, max_length=100)
    platform: str = Field(default="android")
    os_version: Optional[str] = Field(None, max_length=50)
    app_version: Optional[str] = Field(None, max_length=20)
    model: Optional[str] = Field(None, max_length=100)
    manufacturer: Optional[str] = Field(None, max_length=100)


class MobileDeviceRegister(MobileDeviceBase):
    """Schema para registrar novo dispositivo."""
    device_uuid: str = Field(..., min_length=10, max_length=100)
    push_token: Optional[str] = None
    push_provider: Optional[str] = Field(None, pattern="^(fcm|apns)$")
    biometric_capability: str = Field(default="none")
    device_info: Optional[dict] = Field(default_factory=dict)

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, v: str) -> str:
        allowed = ["android", "ios", "web"]
        if v.lower() not in allowed:
            raise ValueError(f"Platform must be one of: {allowed}")
        return v.lower()


class MobileDeviceUpdate(BaseModel):
    """Schema para atualizar dispositivo."""
    device_name: Optional[str] = Field(None, min_length=1, max_length=100)
    push_token: Optional[str] = None
    push_provider: Optional[str] = Field(None, pattern="^(fcm|apns)$")
    os_version: Optional[str] = Field(None, max_length=50)
    app_version: Optional[str] = Field(None, max_length=20)
    biometric_enabled: Optional[bool] = None
    location_permission: Optional[bool] = None
    background_location: Optional[bool] = None
    settings: Optional[dict] = None


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
    os_version: Optional[str]
    app_version: Optional[str]
    model: Optional[str]
    manufacturer: Optional[str]
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
    last_seen_at: Optional[datetime]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MobileDeviceList(BaseModel):
    """Schema de lista de dispositivos."""
    items: List[MobileDeviceResponse]
    total: int
    page: int
    page_size: int
    pages: int


class MobileDeviceFilter(BaseModel):
    """Filtros para busca de dispositivos."""
    employee_id: Optional[UUID] = None
    condominio_id: Optional[UUID] = None
    platform: Optional[str] = None
    status: Optional[str] = None
    is_trusted: Optional[bool] = None
    is_active: Optional[bool] = None


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
    battery_level: Optional[int] = Field(None, ge=0, le=100)
    network_type: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    accuracy_meters: Optional[float] = None


class DeviceLocationUpdate(BaseModel):
    """Schema para atualização de localização."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy_meters: Optional[float] = Field(None, ge=0)
    altitude: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None
