"""Schemas do módulo Push Notifications.

Sprint 37 - Push Notifications Mobile.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

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
    app_version: Optional[str] = Field(None, max_length=50)
    app_build: Optional[str] = Field(None, max_length=50)

    # Device info
    platform_version: Optional[str] = Field(None, max_length=50)
    device_model: Optional[str] = Field(None, max_length=100)
    device_manufacturer: Optional[str] = Field(None, max_length=100)
    device_name: Optional[str] = Field(None, max_length=200)
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
    subscribed_topics: List[str] = Field(default_factory=list)
    tags: Dict[str, Any] = Field(default_factory=dict)

    # Location (opcional)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    country: Optional[str] = Field(None, max_length=2)
    city: Optional[str] = Field(None, max_length=100)


class DeviceUpdateRequest(BaseModel):
    """Schema para atualização de dispositivo."""

    device_token: Optional[str] = None
    app_version: Optional[str] = Field(None, max_length=50)
    platform_version: Optional[str] = Field(None, max_length=50)

    notifications_enabled: Optional[bool] = None
    sound_enabled: Optional[bool] = None
    badge_enabled: Optional[bool] = None

    subscribed_topics: Optional[List[str]] = None
    tags: Optional[Dict[str, Any]] = None

    latitude: Optional[float] = None
    longitude: Optional[float] = None


class DeviceResponse(BaseModel):
    """Schema de resposta para dispositivo."""

    id: UUID
    tenant_id: UUID
    user_id: UUID
    device_id: str
    platform: DevicePlatform
    status: DeviceStatus

    app_id: str
    app_version: Optional[str] = None
    device_model: Optional[str] = None

    notifications_enabled: bool = True
    subscribed_topics: List[str] = Field(default_factory=list)

    last_active_at: Optional[datetime] = None
    total_notifications_sent: int = 0
    total_notifications_opened: int = 0
    engagement_score: Optional[float] = None

    active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DeviceListResponse(BaseModel):
    """Schema de lista de dispositivos."""

    items: List[DeviceResponse]
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
    icon: Optional[str] = Field(None, max_length=100)
    action: str = Field(..., min_length=1, max_length=200)  # URL or deep link


class CampaignCreateRequest(BaseModel):
    """Schema para criação de campanha."""

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    campaign_type: CampaignType = CampaignType.ONE_TIME

    # Conteúdo principal
    title: str = Field(..., min_length=1, max_length=100)
    body: str = Field(..., min_length=1, max_length=500)
    image_url: Optional[str] = Field(None, max_length=500)
    icon_url: Optional[str] = Field(None, max_length=500)

    # iOS específico
    ios_subtitle: Optional[str] = Field(None, max_length=100)
    ios_sound: str = Field(default="default", max_length=100)
    ios_badge: Optional[int] = None

    # Android específico
    android_channel_id: str = Field(default="default", max_length=100)
    android_color: Optional[str] = Field(None, max_length=10)
    android_priority: str = Field(default="high", max_length=10)

    # Ações
    click_action: Optional[str] = Field(None, max_length=200)
    action_buttons: List[ActionButtonSchema] = Field(default_factory=list)
    data_payload: Dict[str, Any] = Field(default_factory=dict)

    # Targeting
    target_type: TargetType = TargetType.ALL
    target_segment_id: Optional[UUID] = None
    target_users: List[UUID] = Field(default_factory=list)
    target_topics: List[str] = Field(default_factory=list)
    target_tags: Dict[str, List[str]] = Field(default_factory=dict)
    target_platforms: List[str] = Field(default=["ios", "android"])

    # Agendamento
    scheduled_at: Optional[datetime] = None
    timezone: str = Field(default="America/Sao_Paulo", max_length=50)
    optimal_time: bool = False

    # Configurações
    ttl_seconds: int = Field(default=86400, ge=60, le=2592000)  # 1min to 30 days
    rate_limit_per_second: int = Field(default=1000, ge=1)

    # Categoria
    category: Optional[str] = Field(None, max_length=50)
    tags: List[str] = Field(default_factory=list)


class CampaignUpdateRequest(BaseModel):
    """Schema para atualização de campanha."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None

    title: Optional[str] = Field(None, min_length=1, max_length=100)
    body: Optional[str] = Field(None, min_length=1, max_length=500)
    image_url: Optional[str] = Field(None, max_length=500)

    click_action: Optional[str] = Field(None, max_length=200)
    data_payload: Optional[Dict[str, Any]] = None

    scheduled_at: Optional[datetime] = None
    status: Optional[CampaignStatus] = None


class CampaignResponse(BaseModel):
    """Schema de resposta para campanha."""

    id: UUID
    tenant_id: UUID
    name: str
    description: Optional[str] = None

    campaign_type: CampaignType
    status: CampaignStatus

    title: str
    body: str
    image_url: Optional[str] = None
    click_action: Optional[str] = None

    target_type: TargetType
    target_platforms: List[str] = Field(default_factory=list)

    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    total_targeted: int = 0
    total_sent: int = 0
    total_delivered: int = 0
    total_opened: int = 0
    total_clicked: int = 0

    delivery_rate: Optional[float] = None
    open_rate: Optional[float] = None
    click_rate: Optional[float] = None

    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CampaignListResponse(BaseModel):
    """Schema de lista de campanhas."""

    items: List[CampaignResponse]
    total: int
    page: int
    page_size: int


# ============================================================================
# Notification Schemas
# ============================================================================


class SendPushRequest(BaseModel):
    """Schema para envio de push notification."""

    # Destinatários (um dos campos obrigatório)
    user_ids: List[UUID] = Field(default_factory=list)
    device_ids: List[UUID] = Field(default_factory=list)
    device_tokens: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)

    # Conteúdo
    title: str = Field(..., min_length=1, max_length=100)
    body: str = Field(..., min_length=1, max_length=500)
    subtitle: Optional[str] = Field(None, max_length=100)
    image_url: Optional[str] = Field(None, max_length=500)

    # Ações
    click_action: Optional[str] = Field(None, max_length=200)
    action_buttons: List[ActionButtonSchema] = Field(default_factory=list)
    data_payload: Dict[str, Any] = Field(default_factory=dict)

    # Configurações
    priority: NotificationPriority = NotificationPriority.HIGH
    ttl_seconds: int = Field(default=86400, ge=60)
    collapse_key: Optional[str] = Field(None, max_length=100)
    mutable_content: bool = False
    content_available: bool = False

    # Contexto
    category: Optional[str] = Field(None, max_length=50)
    source_type: Optional[str] = Field(None, max_length=50)
    source_id: Optional[UUID] = None

    @validator("user_ids", "device_ids", "device_tokens", "topics", pre=True, always=True)
    def at_least_one_target(cls, v, values):  # pylint: disable=no-self-argument
        """Valida que pelo menos um destinatário foi fornecido."""
        return v


class SendPushResponse(BaseModel):
    """Schema de resposta para envio de push."""

    success: bool
    message: str
    notification_ids: List[str] = Field(default_factory=list)
    total_targeted: int = 0
    total_queued: int = 0
    total_failed: int = 0
    failed_devices: List[str] = Field(default_factory=list)


class NotificationResponse(BaseModel):
    """Schema de resposta para notificação."""

    id: UUID
    notification_id: str
    tenant_id: UUID
    user_id: Optional[UUID] = None

    platform: str
    status: NotificationStatus
    priority: NotificationPriority

    title: str
    body: str
    image_url: Optional[str] = None

    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None

    opened: bool = False
    clicked: bool = False

    error_code: Optional[str] = None
    error_message: Optional[str] = None

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
    description: Optional[str] = None
    rules: List[SegmentRuleSchema] = Field(..., min_items=1)
    rules_logic: str = Field(default="AND", pattern=r"^(AND|OR)$")
    is_dynamic: bool = True


class SegmentResponse(BaseModel):
    """Schema de resposta para segmento."""

    id: UUID
    tenant_id: UUID
    name: str
    description: Optional[str] = None
    rules: List[Dict[str, Any]]
    rules_logic: str
    is_dynamic: bool
    cached_count: Optional[int] = None
    cached_at: Optional[datetime] = None
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
    platform: Optional[str] = None
    campaign_id: Optional[UUID] = None
    app_id: Optional[str] = None


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

    platform_breakdown: Dict[str, Dict[str, int]] = Field(default_factory=dict)


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

    avg_time_to_open_seconds: Optional[int] = None

    by_platform: Dict[str, Dict[str, int]] = Field(default_factory=dict)
    by_hour: Dict[str, Dict[str, int]] = Field(default_factory=dict)
    errors: Dict[str, int] = Field(default_factory=dict)


# ============================================================================
# Topic Schemas
# ============================================================================


class TopicSubscribeRequest(BaseModel):
    """Schema para inscrição em tópico."""

    topic: str = Field(..., min_length=1, max_length=100)
    device_ids: List[UUID] = Field(default_factory=list)
    user_ids: List[UUID] = Field(default_factory=list)


class TopicUnsubscribeRequest(BaseModel):
    """Schema para desinscrição de tópico."""

    topic: str = Field(..., min_length=1, max_length=100)
    device_ids: List[UUID] = Field(default_factory=list)
    user_ids: List[UUID] = Field(default_factory=list)


class TopicResponse(BaseModel):
    """Schema de resposta para tópico."""

    topic: str
    subscriber_count: int = 0
    last_notification_at: Optional[datetime] = None
