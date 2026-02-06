"""Schemas do módulo de Notificações.

Sprint 36 - Notification Hub.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator

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
    description: Optional[str] = Field(None, max_length=500)
    channel_type: ChannelType
    provider: ChannelProvider
    status: ChannelStatus = ChannelStatus.ACTIVE


class ChannelConfigCreate(ChannelConfigBase):
    """Schema para criação de canal."""

    provider_config: Dict[str, Any] = Field(default_factory=dict)
    sender_config: Dict[str, Any] = Field(default_factory=dict)
    rate_limit_per_second: int = Field(default=10, ge=1)
    rate_limit_per_minute: int = Field(default=100, ge=1)
    rate_limit_per_hour: int = Field(default=1000, ge=1)
    rate_limit_per_day: int = Field(default=10000, ge=1)
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delay_seconds: int = Field(default=60, ge=1)
    is_default: bool = False
    business_hours_only: bool = False
    cost_per_message: float = Field(default=0.0, ge=0)
    supported_categories: List[str] = Field(default_factory=list)


class ChannelConfigUpdate(BaseModel):
    """Schema para atualização de canal."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[ChannelStatus] = None
    provider_config: Optional[Dict[str, Any]] = None
    sender_config: Optional[Dict[str, Any]] = None
    rate_limit_per_second: Optional[int] = Field(None, ge=1)
    rate_limit_per_minute: Optional[int] = Field(None, ge=1)
    rate_limit_per_hour: Optional[int] = Field(None, ge=1)
    rate_limit_per_day: Optional[int] = Field(None, ge=1)
    max_retries: Optional[int] = Field(None, ge=0, le=10)
    is_default: Optional[bool] = None
    active: Optional[bool] = None


class ChannelConfigResponse(ChannelConfigBase):
    """Schema de resposta para canal."""

    id: UUID
    tenant_id: UUID
    total_sent: int = 0
    total_delivered: int = 0
    total_failed: int = 0
    delivery_rate: Optional[float] = None
    active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

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
    default: Optional[Any] = None
    description: Optional[str] = None


class TemplateBase(BaseModel):
    """Schema base para template."""

    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: TemplateCategory = TemplateCategory.NOTIFICATION
    status: TemplateStatus = TemplateStatus.DRAFT


class TemplateCreate(TemplateBase):
    """Schema para criação de template."""

    channel_id: Optional[UUID] = None

    # Email
    email_subject: Optional[str] = Field(None, max_length=500)
    email_body_html: Optional[str] = None
    email_body_text: Optional[str] = None
    email_from_name: Optional[str] = Field(None, max_length=100)
    email_from_address: Optional[EmailStr] = None
    email_reply_to: Optional[EmailStr] = None

    # WhatsApp
    whatsapp_template_name: Optional[str] = Field(None, max_length=200)
    whatsapp_body: Optional[str] = None
    whatsapp_footer: Optional[str] = Field(None, max_length=60)
    whatsapp_buttons: List[Dict[str, Any]] = Field(default_factory=list)

    # SMS
    sms_body: Optional[str] = Field(None, max_length=160)

    # Push
    push_title: Optional[str] = Field(None, max_length=100)
    push_body: Optional[str] = Field(None, max_length=500)
    push_image_url: Optional[str] = None
    push_action_url: Optional[str] = None

    # In-App
    in_app_title: Optional[str] = Field(None, max_length=200)
    in_app_body: Optional[str] = None
    in_app_icon: Optional[str] = Field(None, max_length=50)
    in_app_action_url: Optional[str] = None

    # Variables
    variables: List[TemplateVariableSchema] = Field(default_factory=list)
    sample_data: Dict[str, Any] = Field(default_factory=dict)

    # Config
    locale: str = Field(default="pt_BR", max_length=10)
    requires_approval: bool = False
    tags: List[str] = Field(default_factory=list)


class TemplateUpdate(BaseModel):
    """Schema para atualização de template."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[TemplateCategory] = None
    status: Optional[TemplateStatus] = None

    email_subject: Optional[str] = Field(None, max_length=500)
    email_body_html: Optional[str] = None
    email_body_text: Optional[str] = None

    whatsapp_body: Optional[str] = None
    sms_body: Optional[str] = Field(None, max_length=160)

    push_title: Optional[str] = Field(None, max_length=100)
    push_body: Optional[str] = Field(None, max_length=500)

    in_app_title: Optional[str] = Field(None, max_length=200)
    in_app_body: Optional[str] = None

    variables: Optional[List[TemplateVariableSchema]] = None
    sample_data: Optional[Dict[str, Any]] = None
    active: Optional[bool] = None


class TemplateResponse(TemplateBase):
    """Schema de resposta para template."""

    id: UUID
    tenant_id: UUID
    channel_id: Optional[UUID] = None

    email_subject: Optional[str] = None
    whatsapp_template_name: Optional[str] = None
    sms_body: Optional[str] = None
    push_title: Optional[str] = None
    in_app_title: Optional[str] = None

    variables: List[Dict[str, Any]] = Field(default_factory=list)
    version: int = 1

    total_sent: int = 0
    total_opened: int = 0
    total_clicked: int = 0
    open_rate: Optional[float] = None
    click_rate: Optional[float] = None

    active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# Preference Schemas
# ============================================================================


class CategoryPreferenceSchema(BaseModel):
    """Schema para preferência de categoria."""

    enabled: bool = True
    channels: List[str] = Field(default_factory=list)


class PreferenceBase(BaseModel):
    """Schema base para preferências."""

    notifications_enabled: bool = True
    quiet_hours_enabled: bool = False
    quiet_hours_start: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    quiet_hours_end: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    timezone: str = Field(default="America/Sao_Paulo", max_length=50)


class PreferenceCreate(PreferenceBase):
    """Schema para criação de preferências."""

    user_id: UUID
    user_email: Optional[EmailStr] = None
    user_phone: Optional[str] = Field(None, max_length=20)

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

    preferred_channels: List[str] = Field(default=["email", "push", "in_app"])
    category_preferences: Dict[str, CategoryPreferenceSchema] = Field(default_factory=dict)

    marketing_consent: bool = False
    transactional_consent: bool = True


class PreferenceUpdate(BaseModel):
    """Schema para atualização de preferências."""

    notifications_enabled: Optional[bool] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    quiet_hours_end: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")

    email_enabled: Optional[bool] = None
    email_frequency: Optional[FrequencyType] = None
    whatsapp_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None

    preferred_channels: Optional[List[str]] = None
    category_preferences: Optional[Dict[str, CategoryPreferenceSchema]] = None

    marketing_consent: Optional[bool] = None


class PreferenceResponse(PreferenceBase):
    """Schema de resposta para preferências."""

    id: UUID
    tenant_id: UUID
    user_id: UUID
    user_email: Optional[str] = None
    user_phone: Optional[str] = None

    email_enabled: bool = True
    whatsapp_enabled: bool = True
    sms_enabled: bool = True
    push_enabled: bool = True
    in_app_enabled: bool = True

    preferred_channels: List[str] = Field(default_factory=list)
    global_unsubscribe: bool = False

    email_verified: bool = False
    phone_verified: bool = False

    marketing_consent: bool = False
    transactional_consent: bool = True

    total_received: int = 0
    total_opened: int = 0
    engagement_score: Optional[float] = None

    active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# Send Notification Schemas
# ============================================================================


class RecipientSchema(BaseModel):
    """Schema para destinatário de notificação."""

    user_id: Optional[UUID] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    device_token: Optional[str] = None
    name: Optional[str] = Field(None, max_length=200)

    @validator("email", "phone", "device_token", pre=True, always=True)
    def at_least_one_address(cls, v, values):  # pylint: disable=no-self-argument
        """Garante que pelo menos um endereço seja fornecido."""
        return v


class SendNotificationRequest(BaseModel):
    """Schema para envio de notificação."""

    # Destinatários
    recipients: List[RecipientSchema] = Field(..., min_items=1, max_items=1000)

    # Template ou conteúdo direto
    template_id: Optional[UUID] = None
    template_slug: Optional[str] = None
    template_variables: Dict[str, Any] = Field(default_factory=dict)

    # Conteúdo direto (se não usar template)
    subject: Optional[str] = Field(None, max_length=500)
    body: Optional[str] = None
    body_html: Optional[str] = None

    # Canais
    channels: List[ChannelType] = Field(default_factory=list)  # Se vazio, usa preferências
    channel_id: Optional[UUID] = None  # Canal específico

    # Agendamento
    scheduled_at: Optional[datetime] = None
    not_after: Optional[datetime] = None  # Expiração

    # Prioridade
    priority: QueuePriority = QueuePriority.NORMAL

    # Contexto
    category: Optional[str] = Field(None, max_length=50)
    tags: List[str] = Field(default_factory=list)
    source_entity_type: Optional[str] = None
    source_entity_id: Optional[UUID] = None

    # Config
    respect_preferences: bool = True  # Respeitar opt-out do usuário
    batch_id: Optional[UUID] = None  # Agrupar envios
    idempotency_key: Optional[str] = Field(None, max_length=100)

    @validator("template_id", "subject", pre=True, always=True)
    def template_or_content(cls, v, values):  # pylint: disable=no-self-argument
        """Garante que template ou conteúdo direto seja fornecido."""
        return v


class SendNotificationResponse(BaseModel):
    """Schema de resposta para envio de notificação."""

    success: bool
    message: str
    notification_ids: List[str] = Field(default_factory=list)
    batch_id: Optional[UUID] = None
    queued_count: int = 0
    skipped_count: int = 0
    skipped_reasons: Dict[str, int] = Field(default_factory=dict)


# ============================================================================
# Queue Schemas
# ============================================================================


class QueueItemResponse(BaseModel):
    """Schema de resposta para item da fila."""

    id: UUID
    notification_id: str
    tenant_id: UUID
    user_id: Optional[UUID] = None
    recipient_address: str
    channel_type: str
    status: QueueStatus
    priority: QueuePriority
    subject: Optional[str] = None

    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

    attempt: int = 0
    max_attempts: int = 3
    last_error: Optional[str] = None

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

    by_channel: Dict[str, int] = Field(default_factory=dict)
    by_priority: Dict[str, int] = Field(default_factory=dict)

    oldest_pending_at: Optional[datetime] = None
    avg_processing_time_ms: Optional[float] = None


# ============================================================================
# Log Schemas
# ============================================================================


class LogEntryResponse(BaseModel):
    """Schema de resposta para entrada de log."""

    id: UUID
    notification_id: Optional[str] = None
    channel_type: Optional[str] = None
    event_type: LogEventType
    level: LogLevel
    message: Optional[str] = None

    provider: Optional[str] = None
    provider_status: Optional[str] = None

    previous_status: Optional[str] = None
    new_status: Optional[str] = None

    processing_time_ms: Optional[int] = None
    attempt_number: Optional[int] = None

    created_at: datetime

    class Config:
        from_attributes = True


class MetricsSummaryResponse(BaseModel):
    """Schema de resumo de métricas."""

    period: str
    channel_type: Optional[str] = None

    total_sent: int = 0
    total_delivered: int = 0
    total_opened: int = 0
    total_clicked: int = 0
    total_failed: int = 0

    delivery_rate: float = 0.0
    open_rate: float = 0.0
    click_rate: float = 0.0
    bounce_rate: float = 0.0

    avg_delivery_time_ms: Optional[float] = None
    total_cost: float = 0.0
