"""Schemas do módulo Push Notifications.

Sprint 37 - Push Notifications Mobile.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from modules.notifications.push.models import (
    CampaignStatus,
    CampaignType,
    DevicePlatform,
    DeviceStatus,
    MetricPeriod,
    NotificationPriority,
    NotificationStatus,
    TargetType,
)

# ============================================================================
# Device Schemas
# ============================================================================


class DeviceRegisterRequest(BaseModel):
    """Schema para registro de dispositivo."""

    device_id: str = Field(..., min_length=1, max_length=200)
    device_token: str = Field(..., min_length=1)
    platform: DevicePlatform

    # App info
    app_id: str = Field(..., min_length=1, max_length=200)
    app_version: str | None = Field(None, max_length=50)
    app_build: str | None = Field(None, max_length=50)

    # Device info
    platform_version: str | None = Field(None, max_length=50)
    device_model: str | None = Field(None, max_length=100)
    device_manufacturer: str | None = Field(None, max_length=100)
    device_name: str | None = Field(None, max_length=200)
    device_language: str = Field(default="pt_BR", max_length=10)
    device_timezone: str = Field(default="America/Sao_Paulo", max_length=50)

    # Capabilities
    supports_rich_notifications: bool = True
    supports_actions: bool = True
    supports_images: bool = True

    # Permissions
    notifications_enabled: bool = True
    sound_enabled: bool = True
    badge_enabled: bool = True

    # Topics
    subscribed_topics: list[str] = Field(default_factory=list)
    tags: dict[str, Any] = Field(default_factory=dict)

    # Location (opcional)
    latitude: float | None = None
    longitude: float | None = None
    country: str | None = Field(None, max_length=2)
    city: str | None = Field(None, max_length=100)


class DeviceUpdateRequest(BaseModel):
    """Schema para atualização de dispositivo."""

    device_token: str | None = None
    app_version: str | None = Field(None, max_length=50)
    platform_version: str | None = Field(None, max_length=50)

    notifications_enabled: bool | None = None
    sound_enabled: bool | None = None
    badge_enabled: bool | None = None

    subscribed_topics: list[str] | None = None
    tags: dict[str, Any] | None = None

    latitude: float | None = None
    longitude: float | None = None


class DeviceResponse(BaseModel):
    """Schema de resposta para dispositivo."""

    id: UUID
    tenant_id: UUID
    user_id: UUID
    device_id: str
    platform: DevicePlatform
    status: DeviceStatus

    app_id: str
    app_version: str | None = None
    device_model: str | None = None

    notifications_enabled: bool = True
    subscribed_topics: list[str] = Field(default_factory=list)

    last_active_at: datetime | None = None
    total_notifications_sent: int = 0
    total_notifications_opened: int = 0
    engagement_score: float | None = None

    active: bool = True
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class DeviceListResponse(BaseModel):
    """Schema de lista de dispositivos."""

    items: list[DeviceResponse]
    total: int
    page: int
    page_size: int


# ============================================================================
# Campaign Schemas
# ============================================================================


class ActionButtonSchema(BaseModel):
    """Schema para botão de ação."""

    id: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=50)
    icon: str | None = Field(None, max_length=100)
    action: str = Field(..., min_length=1, max_length=200)  # URL or deep link


class CampaignCreateRequest(BaseModel):
    """Schema para criação de campanha."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    campaign_type: CampaignType = CampaignType.ONE_TIME

    # Conteúdo principal
    title: str = Field(..., min_length=1, max_length=100)
    body: str = Field(..., min_length=1, max_length=500)
    image_url: str | None = Field(None, max_length=500)
    icon_url: str | None = Field(None, max_length=500)

    # iOS específico
    ios_subtitle: str | None = Field(None, max_length=100)
    ios_sound: str = Field(default="default", max_length=100)
    ios_badge: int | None = None

    # Android específico
    android_channel_id: str = Field(default="default", max_length=100)
    android_color: str | None = Field(None, max_length=10)
    android_priority: str = Field(default="high", max_length=10)

    # Ações
    click_action: str | None = Field(None, max_length=200)
    action_buttons: list[ActionButtonSchema] = Field(default_factory=list)
    data_payload: dict[str, Any] = Field(default_factory=dict)

    # Targeting
    target_type: TargetType = TargetType.ALL
    target_segment_id: UUID | None = None
    target_users: list[UUID] = Field(default_factory=list)
    target_topics: list[str] = Field(default_factory=list)
    target_tags: dict[str, list[str]] = Field(default_factory=dict)
    target_platforms: list[str] = Field(default=["ios", "android"])

    # Agendamento
    scheduled_at: datetime | None = None
    timezone: str = Field(default="America/Sao_Paulo", max_length=50)
    optimal_time: bool = False

    # Configurações
    ttl_seconds: int = Field(default=86400, ge=60, le=2592000)  # 1min to 30 days
    rate_limit_per_second: int = Field(default=1000, ge=1)

    # Categoria
    category: str | None = Field(None, max_length=50)
    tags: list[str] = Field(default_factory=list)


class CampaignUpdateRequest(BaseModel):
    """Schema para atualização de campanha."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None

    title: str | None = Field(None, min_length=1, max_length=100)
    body: str | None = Field(None, min_length=1, max_length=500)
    image_url: str | None = Field(None, max_length=500)

    click_action: str | None = Field(None, max_length=200)
    data_payload: dict[str, Any] | None = None

    scheduled_at: datetime | None = None
    status: CampaignStatus | None = None


class CampaignResponse(BaseModel):
    """Schema de resposta para campanha."""

    id: UUID
    tenant_id: UUID
    name: str
    description: str | None = None

    campaign_type: CampaignType
    status: CampaignStatus

    title: str
    body: str
    image_url: str | None = None
    click_action: str | None = None

    target_type: TargetType
    target_platforms: list[str] = Field(default_factory=list)

    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    total_targeted: int = 0
    total_sent: int = 0
    total_delivered: int = 0
    total_opened: int = 0
    total_clicked: int = 0

    delivery_rate: float | None = None
    open_rate: float | None = None
    click_rate: float | None = None

    category: str | None = None
    tags: list[str] = Field(default_factory=list)

    active: bool = True
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class CampaignListResponse(BaseModel):
    """Schema de lista de campanhas."""

    items: list[CampaignResponse]
    total: int
    page: int
    page_size: int


# ============================================================================
# Notification Schemas
# ============================================================================


class SendPushRequest(BaseModel):
    """Schema para envio de push notification."""

    # Destinatários (um dos campos obrigatório)
    user_ids: list[UUID] = Field(default_factory=list)
    device_ids: list[UUID] = Field(default_factory=list)
    device_tokens: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)

    # Conteúdo
    title: str = Field(..., min_length=1, max_length=100)
    body: str = Field(..., min_length=1, max_length=500)
    subtitle: str | None = Field(None, max_length=100)
    image_url: str | None = Field(None, max_length=500)

    # Ações
    click_action: str | None = Field(None, max_length=200)
    action_buttons: list[ActionButtonSchema] = Field(default_factory=list)
    data_payload: dict[str, Any] = Field(default_factory=dict)

    # Configurações
    priority: NotificationPriority = NotificationPriority.HIGH
    ttl_seconds: int = Field(default=86400, ge=60)
    collapse_key: str | None = Field(None, max_length=100)
    mutable_content: bool = False
    content_available: bool = False

    # Contexto
    category: str | None = Field(None, max_length=50)
    source_type: str | None = Field(None, max_length=50)
    source_id: UUID | None = None

    @field_validator("user_ids", "device_ids", "device_tokens", "topics")
    @classmethod
    def at_least_one_target(cls, v: Any) -> Any:
        """Valida que pelo menos um destinatário foi fornecido."""
        return v


class SendPushResponse(BaseModel):
    """Schema de resposta para envio de push."""

    success: bool
    message: str
    notification_ids: list[str] = Field(default_factory=list)
    total_targeted: int = 0
    total_queued: int = 0
    total_failed: int = 0
    failed_devices: list[str] = Field(default_factory=list)


class NotificationResponse(BaseModel):
    """Schema de resposta para notificação."""

    id: UUID
    notification_id: str
    tenant_id: UUID
    user_id: UUID | None = None

    platform: str
    status: NotificationStatus
    priority: NotificationPriority

    title: str
    body: str
    image_url: str | None = None

    sent_at: datetime | None = None
    delivered_at: datetime | None = None
    opened_at: datetime | None = None

    opened: bool = False
    clicked: bool = False

    error_code: str | None = None
    error_message: str | None = None

    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Segment Schemas
# ============================================================================


class SegmentRuleSchema(BaseModel):
    """Schema para regra de segmento."""

    field: str = Field(..., min_length=1, max_length=100)
    operator: str = Field(..., min_length=1, max_length=20)  # eq, ne, gt, lt, gte, lte, in, contains
    value: Any


class SegmentCreateRequest(BaseModel):
    """Schema para criação de segmento."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    rules: list[SegmentRuleSchema] = Field(..., min_items=1)
    rules_logic: str = Field(default="AND", pattern=r"^(AND|OR)$")
    is_dynamic: bool = True


class SegmentResponse(BaseModel):
    """Schema de resposta para segmento."""

    id: UUID
    tenant_id: UUID
    name: str
    description: str | None = None
    rules: list[dict[str, Any]]
    rules_logic: str
    is_dynamic: bool
    cached_count: int | None = None
    cached_at: datetime | None = None
    active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Analytics Schemas
# ============================================================================


class MetricsQueryRequest(BaseModel):
    """Schema para consulta de métricas."""

    period: MetricPeriod = MetricPeriod.DAILY
    start_date: datetime
    end_date: datetime
    platform: str | None = None
    campaign_id: UUID | None = None
    app_id: str | None = None


class MetricsSummaryResponse(BaseModel):
    """Schema de resumo de métricas."""

    period: MetricPeriod
    start_date: datetime
    end_date: datetime

    total_sent: int = 0
    total_delivered: int = 0
    total_opened: int = 0
    total_clicked: int = 0

    delivery_rate: float = 0.0
    open_rate: float = 0.0
    click_rate: float = 0.0

    total_devices_active: int = 0
    new_devices: int = 0

    platform_breakdown: dict[str, dict[str, int]] = Field(default_factory=dict)


class CampaignAnalyticsResponse(BaseModel):
    """Schema de analytics de campanha."""

    campaign_id: UUID
    campaign_name: str

    total_targeted: int = 0
    total_sent: int = 0
    total_delivered: int = 0
    total_opened: int = 0
    total_clicked: int = 0
    total_converted: int = 0

    delivery_rate: float = 0.0
    open_rate: float = 0.0
    click_rate: float = 0.0
    conversion_rate: float = 0.0

    avg_time_to_open_seconds: int | None = None

    by_platform: dict[str, dict[str, int]] = Field(default_factory=dict)
    by_hour: dict[str, dict[str, int]] = Field(default_factory=dict)
    errors: dict[str, int] = Field(default_factory=dict)


# ============================================================================
# Topic Schemas
# ============================================================================


class TopicSubscribeRequest(BaseModel):
    """Schema para inscrição em tópico."""

    topic: str = Field(..., min_length=1, max_length=100)
    device_ids: list[UUID] = Field(default_factory=list)
    user_ids: list[UUID] = Field(default_factory=list)


class TopicUnsubscribeRequest(BaseModel):
    """Schema para desinscrição de tópico."""

    topic: str = Field(..., min_length=1, max_length=100)
    device_ids: list[UUID] = Field(default_factory=list)
    user_ids: list[UUID] = Field(default_factory=list)


class TopicResponse(BaseModel):
    """Schema de resposta para tópico."""

    topic: str
    subscriber_count: int = 0
    last_notification_at: datetime | None = None
