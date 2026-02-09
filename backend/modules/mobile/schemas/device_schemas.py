"""Schemas de dispositivo mobile."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DeviceTokenCreate(BaseModel):
    """Schema para criar/registrar token de dispositivo."""

    token: str = Field(..., min_length=10, max_length=500, description="Token FCM/APNs")
    platform: str = Field(..., description="android, ios, web")
    device_id: str | None = Field(default=None, max_length=100)
    device_name: str | None = Field(default=None, max_length=200)
    device_model: str | None = Field(default=None, max_length=100)
    os_version: str | None = Field(default=None, max_length=50)
    app_version: str | None = Field(default=None, max_length=50)
    app_build: str | None = Field(default=None, max_length=50)
    locale: str = Field(default="pt-BR", max_length=10)
    timezone: str | None = Field(default=None, max_length=50)

    model_config = {"from_attributes": True}


class DeviceTokenUpdate(BaseModel):
    """Schema para atualizar token de dispositivo."""

    token: str | None = Field(default=None, min_length=10, max_length=500)
    device_name: str | None = Field(default=None, max_length=200)
    os_version: str | None = Field(default=None, max_length=50)
    app_version: str | None = Field(default=None, max_length=50)
    app_build: str | None = Field(default=None, max_length=50)
    push_enabled: bool | None = None
    locale: str | None = Field(default=None, max_length=10)
    timezone: str | None = Field(default=None, max_length=50)

    model_config = {"from_attributes": True}


class DeviceTokenResponse(BaseModel):
    """Response de token de dispositivo."""

    id: UUID
    user_id: int
    platform: str
    device_id: str | None = None
    device_name: str | None = None
    device_model: str | None = None
    os_version: str | None = None
    app_version: str | None = None
    push_enabled: bool = True
    is_active: bool = True
    locale: str | None = None
    timezone: str | None = None
    last_used: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DeviceListResponse(BaseModel):
    """Lista de dispositivos do usuário."""

    devices: list[DeviceTokenResponse]
    total: int
    active_count: int

    model_config = {"from_attributes": True}


class DeviceStateUpdate(BaseModel):
    """Atualização de estado do dispositivo."""

    connection_type: str | None = Field(
        default=None,
        description="wifi, 4g, 3g, slow",
    )
    battery_level: int | None = Field(default=None, ge=0, le=100)
    storage_available_mb: int | None = Field(default=None, ge=0)
    is_charging: bool | None = None
    is_low_power_mode: bool | None = None

    model_config = {"from_attributes": True}
