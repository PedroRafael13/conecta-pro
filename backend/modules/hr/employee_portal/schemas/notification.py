"""Schemas para notificações do funcionário."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from modules.hr.employee_portal.models import (
    NotificationChannel,
    NotificationPriority,
    NotificationType,
)


class NotificationCreate(BaseModel):
    """Schema para criação de notificação."""

    employee_id: UUID
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.NORMAL

    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=5000)
    short_message: str | None = Field(None, max_length=200)

    icon: str | None = Field(None, max_length=50)
    color: str | None = Field(None, max_length=20)
    image_url: str | None = Field(None, max_length=500)

    action_url: str | None = Field(None, max_length=500)
    action_label: str | None = Field(None, max_length=50)
    action_type: str | None = Field(None, max_length=30)

    reference_type: str | None = Field(None, max_length=50)
    reference_id: UUID | None = None

    channels: list[NotificationChannel] = Field(default_factory=lambda: [NotificationChannel.PORTAL])

    scheduled_at: datetime | None = None
    expires_at: datetime | None = None

    is_recurring: bool = False
    recurrence_pattern: str | None = Field(None, max_length=50)

    extra_data: dict = Field(default_factory=dict)


class NotificationResponse(BaseModel):
    """Schema de resposta para notificação."""

    id: UUID
    condominio_id: UUID
    employee_id: UUID

    notification_type: str
    priority: str

    title: str
    message: str
    short_message: str | None

    icon: str | None
    color: str | None
    image_url: str | None

    action_url: str | None
    action_label: str | None
    action_type: str | None

    reference_type: str | None
    reference_id: UUID | None

    channels: list[str]
    delivered_channels: dict

    is_read: bool
    read_at: datetime | None
    clicked_at: datetime | None
    dismissed_at: datetime | None

    email_sent: bool
    email_sent_at: datetime | None
    email_opened: bool
    email_opened_at: datetime | None

    push_sent: bool
    push_sent_at: datetime | None
    push_clicked: bool
    push_clicked_at: datetime | None

    sms_sent: bool
    sms_sent_at: datetime | None
    sms_delivered: bool

    scheduled_at: datetime | None
    expires_at: datetime | None

    is_recurring: bool
    recurrence_pattern: str | None
    next_occurrence: datetime | None

    extra_data: dict

    is_active: bool
    is_archived: bool
    is_expired: bool
    is_pending_delivery: bool

    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class NotificationSummary(BaseModel):
    """Resumo da notificação para listagem."""

    id: UUID
    notification_type: str
    priority: str
    title: str
    short_message: str
    icon: str | None
    color: str | None
    action_url: str | None
    action_label: str | None
    is_read: bool
    created_at: datetime


class NotificationListResponse(BaseModel):
    """Lista paginada de notificações."""

    items: list[NotificationSummary]
    total: int
    page: int
    page_size: int
    pages: int
    unread_count: int


class NotificationMarkReadRequest(BaseModel):
    """Request para marcar notificações como lidas."""

    notification_ids: list[UUID] = Field(..., min_length=1, max_length=100)


class NotificationMarkReadResponse(BaseModel):
    """Resposta de marcação como lida."""

    marked_count: int
    remaining_unread: int


class NotificationDismissRequest(BaseModel):
    """Request para descartar notificações."""

    notification_ids: list[UUID] = Field(..., min_length=1, max_length=100)


class NotificationPreferencesUpdate(BaseModel):
    """Atualização de preferências de notificação."""

    # Portal
    notifications_enabled: bool | None = None
    notification_sound: bool | None = None
    notification_badge: bool | None = None

    # Email
    email_notifications_enabled: bool | None = None
    email_payslip: bool | None = None
    email_documents: bool | None = None
    email_vacation: bool | None = None
    email_announcements: bool | None = None
    email_birthday: bool | None = None
    email_digest: bool | None = None
    email_digest_time: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")

    # Push
    push_notifications_enabled: bool | None = None
    push_payslip: bool | None = None
    push_documents: bool | None = None
    push_vacation: bool | None = None
    push_announcements: bool | None = None
    push_time_entry: bool | None = None
    push_quiet_hours: bool | None = None
    push_quiet_start: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")
    push_quiet_end: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")

    # SMS
    sms_notifications_enabled: bool | None = None
    sms_urgent_only: bool | None = None

    # WhatsApp
    whatsapp_notifications_enabled: bool | None = None
    whatsapp_phone: str | None = Field(None, max_length=20)


class UnreadCountResponse(BaseModel):
    """Contagem de notificações não lidas."""

    total_unread: int
    by_type: dict  # {"payslip_available": 2, "document_available": 1, ...}
    by_priority: dict  # {"urgent": 1, "high": 2, "normal": 5, "low": 0}
    oldest_unread_at: datetime | None


class NotificationFilterRequest(BaseModel):
    """Filtros para busca de notificações."""

    employee_id: UUID | None = None
    notification_type: NotificationType | None = None
    priority: NotificationPriority | None = None
    is_read: bool | None = None
    is_active: bool | None = None
    is_archived: bool | None = None
    reference_type: str | None = None
    reference_id: UUID | None = None
    created_from: datetime | None = None
    created_to: datetime | None = None
    channel: NotificationChannel | None = None


class NotificationBulkCreateRequest(BaseModel):
    """Request para criação em lote de notificações."""

    employee_ids: list[UUID] = Field(..., min_length=1, max_length=1000)
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.NORMAL

    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=5000)
    short_message: str | None = Field(None, max_length=200)

    icon: str | None = Field(None, max_length=50)
    color: str | None = Field(None, max_length=20)

    action_url: str | None = Field(None, max_length=500)
    action_label: str | None = Field(None, max_length=50)

    channels: list[NotificationChannel] = Field(default_factory=lambda: [NotificationChannel.PORTAL])

    scheduled_at: datetime | None = None
    expires_at: datetime | None = None


class NotificationBulkCreateResponse(BaseModel):
    """Resposta de criação em lote."""

    total_requested: int
    total_created: int
    notification_ids: list[UUID]
