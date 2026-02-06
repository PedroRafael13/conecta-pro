"""Schemas de dispositivo mobile."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class DeviceTokenCreate(BaseModel):
    """Schema para criar/registrar token de dispositivo."""

    token: str = Field(..., min_length=10, max_length=500, description="Token FCM/APNs")
    platform: str = Field(..., description="android, ios, web")
    device_id: Optional[str] = Field(default=None, max_length=100)
    device_name: Optional[str] = Field(default=None, max_length=200)
    device_model: Optional[str] = Field(default=None, max_length=100)
    os_version: Optional[str] = Field(default=None, max_length=50)
    app_version: Optional[str] = Field(default=None, max_length=50)
    app_build: Optional[str] = Field(default=None, max_length=50)
    locale: str = Field(default="pt-BR", max_length=10)
    timezone: Optional[str] = Field(default=None, max_length=50)

    model_config = {"from_attributes": True}


class DeviceTokenUpdate(BaseModel):
    """Schema para atualizar token de dispositivo."""

    token: Optional[str] = Field(default=None, min_length=10, max_length=500)
    device_name: Optional[str] = Field(default=None, max_length=200)
    os_version: Optional[str] = Field(default=None, max_length=50)
    app_version: Optional[str] = Field(default=None, max_length=50)
    app_build: Optional[str] = Field(default=None, max_length=50)
    push_enabled: Optional[bool] = None
    locale: Optional[str] = Field(default=None, max_length=10)
    timezone: Optional[str] = Field(default=None, max_length=50)

    model_config = {"from_attributes": True}


class DeviceTokenResponse(BaseModel):
    """Response de token de dispositivo."""

    id: UUID
    user_id: int
    platform: str
    device_id: Optional[str] = None
    device_name: Optional[str] = None
    device_model: Optional[str] = None
    os_version: Optional[str] = None
    app_version: Optional[str] = None
    push_enabled: bool = True
    is_active: bool = True
    locale: Optional[str] = None
    timezone: Optional[str] = None
    last_used: Optional[datetime] = None
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

    connection_type: Optional[str] = Field(
        default=None,
        description="wifi, 4g, 3g, slow",
    )
    battery_level: Optional[int] = Field(default=None, ge=0, le=100)
    storage_available_mb: Optional[int] = Field(default=None, ge=0)
    is_charging: Optional[bool] = None
    is_low_power_mode: Optional[bool] = None

    model_config = {"from_attributes": True}
