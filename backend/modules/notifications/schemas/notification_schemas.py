"""Schemas do módulo de Notificações.

Sprint 36 - Notification Hub.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from modules.notifications.models.notification_channel import (
    ChannelProvider,
    ChannelStatus,
    ChannelType,
)
from modules.notifications.models.notification_log import LogEventType, LogLevel
from modules.notifications.models.notification_preference import DigestType, FrequencyType
from modules.notifications.models.notification_queue import QueuePriority, QueueStatus
from modules.notifications.models.notification_template import TemplateCategory, TemplateStatus

# ============================================================================
# Channel Schemas
# ============================================================================


class ChannelConfigBase(BaseModel):
    """Schema base para configuração de canal."""

    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    channel_type: ChannelType
    provider: ChannelProvider
    status: ChannelStatus = ChannelStatus.ACTIVE


class ChannelConfigCreate(ChannelConfigBase):
    """Schema para criação de canal."""

    provider_config: dict[str, Any] = Field(default_factory=dict)
    sender_config: dict[str, Any] = Field(default_factory=dict)
    rate_limit_per_second: int = Field(default=10, ge=1)
    rate_limit_per_minute: int = Field(default=100, ge=1)
    rate_limit_per_hour: int = Field(default=1000, ge=1)
    rate_limit_per_day: int = Field(default=10000, ge=1)
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delay_seconds: int = Field(default=60, ge=1)
    is_default: bool = False
    business_hours_only: bool = False
    cost_per_message: float = Field(default=0.0, ge=0)
    supported_categories: list[str] = Field(default_factory=list)


class ChannelConfigUpdate(BaseModel):
    """Schema para atualização de canal."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    status: ChannelStatus | None = None
    provider_config: dict[str, Any] | None = None
    sender_config: dict[str, Any] | None = None
    rate_limit_per_second: int | None = Field(None, ge=1)
    rate_limit_per_minute: int | None = Field(None, ge=1)
    rate_limit_per_hour: int | None = Field(None, ge=1)
    rate_limit_per_day: int | None = Field(None, ge=1)
    max_retries: int | None = Field(None, ge=0, le=10)
    is_default: bool | None = None
    active: bool | None = None


class ChannelConfigResponse(ChannelConfigBase):
    """Schema de resposta para canal."""

    id: UUID
    tenant_id: UUID
    total_sent: int = 0
    total_delivered: int = 0
    total_failed: int = 0
    delivery_rate: float | None = None
    active: bool = True
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


# ============================================================================
# Template Schemas
# ============================================================================


class TemplateVariableSchema(BaseModel):
    """Schema para variável de template."""

    name: str = Field(..., min_length=1, max_length=50)
    type: str = Field(default="string")  # string, number, date, boolean, object
    required: bool = False
    default: Any | None = None
    description: str | None = None


class TemplateBase(BaseModel):
    """Schema base para template."""

    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    category: TemplateCategory = TemplateCategory.NOTIFICATION
    status: TemplateStatus = TemplateStatus.DRAFT


class TemplateCreate(TemplateBase):
    """Schema para criação de template."""

    channel_id: UUID | None = None

    # Email
    email_subject: str | None = Field(None, max_length=500)
    email_body_html: str | None = None
    email_body_text: str | None = None
    email_from_name: str | None = Field(None, max_length=100)
    email_from_address: EmailStr | None = None
    email_reply_to: EmailStr | None = None

    # WhatsApp
    whatsapp_template_name: str | None = Field(None, max_length=200)
    whatsapp_body: str | None = None
    whatsapp_footer: str | None = Field(None, max_length=60)
    whatsapp_buttons: list[dict[str, Any]] = Field(default_factory=list)

    # SMS
    sms_body: str | None = Field(None, max_length=160)

    # Push
    push_title: str | None = Field(None, max_length=100)
    push_body: str | None = Field(None, max_length=500)
    push_image_url: str | None = None
    push_action_url: str | None = None

    # In-App
    in_app_title: str | None = Field(None, max_length=200)
    in_app_body: str | None = None
    in_app_icon: str | None = Field(None, max_length=50)
    in_app_action_url: str | None = None

    # Variables
    variables: list[TemplateVariableSchema] = Field(default_factory=list)
    sample_data: dict[str, Any] = Field(default_factory=dict)

    # Config
    locale: str = Field(default="pt_BR", max_length=10)
    requires_approval: bool = False
    tags: list[str] = Field(default_factory=list)


class TemplateUpdate(BaseModel):
    """Schema para atualização de template."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    category: TemplateCategory | None = None
    status: TemplateStatus | None = None

    email_subject: str | None = Field(None, max_length=500)
    email_body_html: str | None = None
    email_body_text: str | None = None

    whatsapp_body: str | None = None
    sms_body: str | None = Field(None, max_length=160)

    push_title: str | None = Field(None, max_length=100)
    push_body: str | None = Field(None, max_length=500)

    in_app_title: str | None = Field(None, max_length=200)
    in_app_body: str | None = None

    variables: list[TemplateVariableSchema] | None = None
    sample_data: dict[str, Any] | None = None
    active: bool | None = None


class TemplateResponse(TemplateBase):
    """Schema de resposta para template."""

    id: UUID
    tenant_id: UUID
    channel_id: UUID | None = None

    email_subject: str | None = None
    whatsapp_template_name: str | None = None
    sms_body: str | None = None
    push_title: str | None = None
    in_app_title: str | None = None

    variables: list[dict[str, Any]] = Field(default_factory=list)
    version: int = 1

    total_sent: int = 0
    total_opened: int = 0
    total_clicked: int = 0
    open_rate: float | None = None
    click_rate: float | None = None

    active: bool = True
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


# ============================================================================
# Preference Schemas
# ============================================================================


class CategoryPreferenceSchema(BaseModel):
    """Schema para preferência de categoria."""

    enabled: bool = True
    channels: list[str] = Field(default_factory=list)


class PreferenceBase(BaseModel):
    """Schema base para preferências."""

    notifications_enabled: bool = True
    quiet_hours_enabled: bool = False
    quiet_hours_start: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")
    quiet_hours_end: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")
    timezone: str = Field(default="America/Sao_Paulo", max_length=50)


class PreferenceCreate(PreferenceBase):
    """Schema para criação de preferências."""

    user_id: UUID
    user_email: EmailStr | None = None
    user_phone: str | None = Field(None, max_length=20)

    email_enabled: bool = True
    email_frequency: FrequencyType = FrequencyType.INSTANT
    email_digest: DigestType = DigestType.NONE

    whatsapp_enabled: bool = True
    whatsapp_frequency: FrequencyType = FrequencyType.INSTANT

    sms_enabled: bool = True
    sms_frequency: FrequencyType = FrequencyType.INSTANT

    push_enabled: bool = True
    push_sound_enabled: bool = True
    push_vibration_enabled: bool = True

    in_app_enabled: bool = True

    preferred_channels: list[str] = Field(default=["email", "push", "in_app"])
    category_preferences: dict[str, CategoryPreferenceSchema] = Field(default_factory=dict)

    marketing_consent: bool = False
    transactional_consent: bool = True


class PreferenceUpdate(BaseModel):
    """Schema para atualização de preferências."""

    notifications_enabled: bool | None = None
    quiet_hours_enabled: bool | None = None
    quiet_hours_start: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")
    quiet_hours_end: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")

    email_enabled: bool | None = None
    email_frequency: FrequencyType | None = None
    whatsapp_enabled: bool | None = None
    sms_enabled: bool | None = None
    push_enabled: bool | None = None
    in_app_enabled: bool | None = None

    preferred_channels: list[str] | None = None
    category_preferences: dict[str, CategoryPreferenceSchema] | None = None

    marketing_consent: bool | None = None


class PreferenceResponse(PreferenceBase):
    """Schema de resposta para preferências."""

    id: UUID
    tenant_id: UUID
    user_id: UUID
    user_email: str | None = None
    user_phone: str | None = None

    email_enabled: bool = True
    whatsapp_enabled: bool = True
    sms_enabled: bool = True
    push_enabled: bool = True
    in_app_enabled: bool = True

    preferred_channels: list[str] = Field(default_factory=list)
    global_unsubscribe: bool = False

    email_verified: bool = False
    phone_verified: bool = False

    marketing_consent: bool = False
    transactional_consent: bool = True

    total_received: int = 0
    total_opened: int = 0
    engagement_score: float | None = None

    active: bool = True
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


# ============================================================================
# Send Notification Schemas
# ============================================================================


class RecipientSchema(BaseModel):
    """Schema para destinatário de notificação."""

    user_id: UUID | None = None
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=20)
    device_token: str | None = None
    name: str | None = Field(None, max_length=200)

    @field_validator("email", "phone", "device_token", mode="before")
    @classmethod
    def at_least_one_address(cls, v: Any) -> Any:
        """Garante que pelo menos um endereço seja fornecido."""
        return v


class SendNotificationRequest(BaseModel):
    """Schema para envio de notificação."""

    # Destinatários
    recipients: list[RecipientSchema] = Field(..., min_items=1, max_items=1000)

    # Template ou conteúdo direto
    template_id: UUID | None = None
    template_slug: str | None = None
    template_variables: dict[str, Any] = Field(default_factory=dict)

    # Conteúdo direto (se não usar template)
    subject: str | None = Field(None, max_length=500)
    body: str | None = None
    body_html: str | None = None

    # Canais
    channels: list[ChannelType] = Field(default_factory=list)  # Se vazio, usa preferências
    channel_id: UUID | None = None  # Canal específico

    # Agendamento
    scheduled_at: datetime | None = None
    not_after: datetime | None = None  # Expiração

    # Prioridade
    priority: QueuePriority = QueuePriority.NORMAL

    # Contexto
    category: str | None = Field(None, max_length=50)
    tags: list[str] = Field(default_factory=list)
    source_entity_type: str | None = None
    source_entity_id: UUID | None = None

    # Config
    respect_preferences: bool = True  # Respeitar opt-out do usuário
    batch_id: UUID | None = None  # Agrupar envios
    idempotency_key: str | None = Field(None, max_length=100)

    @field_validator("template_id", "subject", mode="before")
    @classmethod
    def template_or_content(cls, v: Any) -> Any:
        """Garante que template ou conteúdo direto seja fornecido."""
        return v


class SendNotificationResponse(BaseModel):
    """Schema de resposta para envio de notificação."""

    success: bool
    message: str
    notification_ids: list[str] = Field(default_factory=list)
    batch_id: UUID | None = None
    queued_count: int = 0
    skipped_count: int = 0
    skipped_reasons: dict[str, int] = Field(default_factory=dict)


# ============================================================================
# Queue Schemas
# ============================================================================


class QueueItemResponse(BaseModel):
    """Schema de resposta para item da fila."""

    id: UUID
    notification_id: str
    tenant_id: UUID
    user_id: UUID | None = None
    recipient_address: str
    channel_type: str
    status: QueueStatus
    priority: QueuePriority
    subject: str | None = None

    scheduled_at: datetime | None = None
    sent_at: datetime | None = None
    delivered_at: datetime | None = None

    attempt: int = 0
    max_attempts: int = 3
    last_error: str | None = None

    opened: bool = False
    clicked: bool = False

    created_at: datetime

    class Config:
        from_attributes = True


class QueueStatsResponse(BaseModel):
    """Schema de estatísticas da fila."""

    total_pending: int = 0
    total_scheduled: int = 0
    total_processing: int = 0
    total_sent: int = 0
    total_delivered: int = 0
    total_failed: int = 0
    total_retry: int = 0

    by_channel: dict[str, int] = Field(default_factory=dict)
    by_priority: dict[str, int] = Field(default_factory=dict)

    oldest_pending_at: datetime | None = None
    avg_processing_time_ms: float | None = None


# ============================================================================
# Log Schemas
# ============================================================================


class LogEntryResponse(BaseModel):
    """Schema de resposta para entrada de log."""

    id: UUID
    notification_id: str | None = None
    channel_type: str | None = None
    event_type: LogEventType
    level: LogLevel
    message: str | None = None

    provider: str | None = None
    provider_status: str | None = None

    previous_status: str | None = None
    new_status: str | None = None

    processing_time_ms: int | None = None
    attempt_number: int | None = None

    created_at: datetime

    class Config:
        from_attributes = True


class MetricsSummaryResponse(BaseModel):
    """Schema de resumo de métricas."""

    period: str
    channel_type: str | None = None

    total_sent: int = 0
    total_delivered: int = 0
    total_opened: int = 0
    total_clicked: int = 0
    total_failed: int = 0

    delivery_rate: float = 0.0
    open_rate: float = 0.0
    click_rate: float = 0.0
    bounce_rate: float = 0.0

    avg_delivery_time_ms: float | None = None
    total_cost: float = 0.0
