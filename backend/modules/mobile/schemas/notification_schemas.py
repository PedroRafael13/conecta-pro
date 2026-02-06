"""Schemas de notificações push."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PushNotificationCreate(BaseModel):
    """Schema para criar notificação push."""

    user_id: Optional[int] = Field(default=None, description="ID do usuário (ou broadcast)")
    title: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1, max_length=2000)
    notification_type: str = Field(default="info", description="system, alert, info, marketing")
    priority: str = Field(default="normal", description="low, normal, high, critical")
    data_payload: dict[str, Any] = Field(default_factory=dict)
    image_url: Optional[str] = Field(default=None, max_length=500)
    action_url: Optional[str] = Field(default=None, max_length=500)
    category: Optional[str] = Field(default=None, max_length=50)
    thread_id: Optional[str] = Field(default=None, max_length=100)
    collapse_key: Optional[str] = Field(default=None, max_length=100)
    scheduled_for: Optional[datetime] = Field(default=None, description="Agendamento futuro")
    ttl_seconds: int = Field(default=86400, ge=60, le=2419200, description="TTL em segundos")
    platforms: list[str] = Field(default=["android", "ios"], description="Plataformas alvo")

    model_config = {"from_attributes": True}


class PushNotificationResponse(BaseModel):
    """Response de notificação push."""

    id: UUID
    user_id: int
    title: str
    body: str
    notification_type: str
    priority: str
    data_payload: dict[str, Any] = {}
    image_url: Optional[str] = None
    action_url: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    external_id: Optional[str] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    """Lista de notificações."""

    notifications: list[PushNotificationResponse]
    total: int
    unread_count: int
    page: int = 1
    page_size: int = 20
    has_more: bool = False

    model_config = {"from_attributes": True}


class NotificationPreferences(BaseModel):
    """Preferências de notificação do usuário."""

    push_enabled: bool = Field(default=True, description="Notificações push habilitadas")
    email_enabled: bool = Field(default=True, description="Notificações por email")
    sms_enabled: bool = Field(default=False, description="Notificações por SMS")
    quiet_hours_enabled: bool = Field(default=False, description="Horário silencioso")
    quiet_hours_start: Optional[str] = Field(
        default="22:00",
        description="Início do horário silencioso (HH:MM)",
    )
    quiet_hours_end: Optional[str] = Field(
        default="07:00",
        description="Fim do horário silencioso (HH:MM)",
    )
    categories: dict[str, bool] = Field(
        default_factory=lambda: {
            "system": True,
            "alert": True,
            "info": True,
            "marketing": False,
            "reminder": True,
            "transaction": True,
            "message": True,
        },
        description="Categorias habilitadas",
    )
    sound_enabled: bool = Field(default=True)
    vibration_enabled: bool = Field(default=True)
    badge_enabled: bool = Field(default=True)

    model_config = {"from_attributes": True}


class NotificationPreferencesUpdate(BaseModel):
    """Update de preferências de notificação."""

    push_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    categories: Optional[dict[str, bool]] = None
    sound_enabled: Optional[bool] = None
    vibration_enabled: Optional[bool] = None
    badge_enabled: Optional[bool] = None

    model_config = {"from_attributes": True}


class NotificationStats(BaseModel):
    """Estatísticas de notificações."""

    total_sent: int = 0
    total_delivered: int = 0
    total_read: int = 0
    total_failed: int = 0
    delivery_rate: float = 0.0
    read_rate: float = 0.0
    avg_delivery_time_ms: float = 0.0

    model_config = {"from_attributes": True}


class BroadcastNotificationRequest(BaseModel):
    """Request para notificação broadcast."""

    title: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1, max_length=2000)
    notification_type: str = Field(default="info")
    priority: str = Field(default="normal")
    data_payload: dict[str, Any] = Field(default_factory=dict)
    target_users: Optional[list[int]] = Field(
        default=None,
        description="IDs de usuários específicos (None = todos)",
    )
    target_segments: Optional[list[str]] = Field(
        default=None,
        description="Segmentos de usuários",
    )
    target_platforms: list[str] = Field(default=["android", "ios"])
    scheduled_for: Optional[datetime] = None

    model_config = {"from_attributes": True}


class BroadcastNotificationResponse(BaseModel):
    """Response de notificação broadcast."""

    broadcast_id: str
    title: str
    body: str
    total_recipients: int
    sent_count: int
    failed_count: int
    scheduled_for: Optional[datetime] = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
