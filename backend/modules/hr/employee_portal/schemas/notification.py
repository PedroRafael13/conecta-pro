"""Schemas para notificações do funcionário."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field

from modules.hr.employee_portal.models import (
    NotificationType,
    NotificationPriority,
    NotificationChannel,
)


class NotificationCreate(BaseModel):
    """Schema para criação de notificação."""

    employee_id: UUID
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.NORMAL

    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=5000)
    short_message: Optional[str] = Field(None, max_length=200)

    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=20)
    image_url: Optional[str] = Field(None, max_length=500)

    action_url: Optional[str] = Field(None, max_length=500)
    action_label: Optional[str] = Field(None, max_length=50)
    action_type: Optional[str] = Field(None, max_length=30)

    reference_type: Optional[str] = Field(None, max_length=50)
    reference_id: Optional[UUID] = None

    channels: List[NotificationChannel] = Field(
        default_factory=lambda: [NotificationChannel.PORTAL]
    )

    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    is_recurring: bool = False
    recurrence_pattern: Optional[str] = Field(None, max_length=50)

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
    short_message: Optional[str]

    icon: Optional[str]
    color: Optional[str]
    image_url: Optional[str]

    action_url: Optional[str]
    action_label: Optional[str]
    action_type: Optional[str]

    reference_type: Optional[str]
    reference_id: Optional[UUID]

    channels: List[str]
    delivered_channels: dict

    is_read: bool
    read_at: Optional[datetime]
    clicked_at: Optional[datetime]
    dismissed_at: Optional[datetime]

    email_sent: bool
    email_sent_at: Optional[datetime]
    email_opened: bool
    email_opened_at: Optional[datetime]

    push_sent: bool
    push_sent_at: Optional[datetime]
    push_clicked: bool
    push_clicked_at: Optional[datetime]

    sms_sent: bool
    sms_sent_at: Optional[datetime]
    sms_delivered: bool

    scheduled_at: Optional[datetime]
    expires_at: Optional[datetime]

    is_recurring: bool
    recurrence_pattern: Optional[str]
    next_occurrence: Optional[datetime]

    extra_data: dict

    is_active: bool
    is_archived: bool
    is_expired: bool
    is_pending_delivery: bool

    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class NotificationSummary(BaseModel):
    """Resumo da notificação para listagem."""

    id: UUID
    notification_type: str
    priority: str
    title: str
    short_message: str
    icon: Optional[str]
    color: Optional[str]
    action_url: Optional[str]
    action_label: Optional[str]
    is_read: bool
    created_at: datetime


class NotificationListResponse(BaseModel):
    """Lista paginada de notificações."""

    items: List[NotificationSummary]
    total: int
    page: int
    page_size: int
    pages: int
    unread_count: int


class NotificationMarkReadRequest(BaseModel):
    """Request para marcar notificações como lidas."""

    notification_ids: List[UUID] = Field(..., min_length=1, max_length=100)


class NotificationMarkReadResponse(BaseModel):
    """Resposta de marcação como lida."""

    marked_count: int
    remaining_unread: int


class NotificationDismissRequest(BaseModel):
    """Request para descartar notificações."""

    notification_ids: List[UUID] = Field(..., min_length=1, max_length=100)


class NotificationPreferencesUpdate(BaseModel):
    """Atualização de preferências de notificação."""

    # Portal
    notifications_enabled: Optional[bool] = None
    notification_sound: Optional[bool] = None
    notification_badge: Optional[bool] = None

    # Email
    email_notifications_enabled: Optional[bool] = None
    email_payslip: Optional[bool] = None
    email_documents: Optional[bool] = None
    email_vacation: Optional[bool] = None
    email_announcements: Optional[bool] = None
    email_birthday: Optional[bool] = None
    email_digest: Optional[bool] = None
    email_digest_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")

    # Push
    push_notifications_enabled: Optional[bool] = None
    push_payslip: Optional[bool] = None
    push_documents: Optional[bool] = None
    push_vacation: Optional[bool] = None
    push_announcements: Optional[bool] = None
    push_time_entry: Optional[bool] = None
    push_quiet_hours: Optional[bool] = None
    push_quiet_start: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    push_quiet_end: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")

    # SMS
    sms_notifications_enabled: Optional[bool] = None
    sms_urgent_only: Optional[bool] = None

    # WhatsApp
    whatsapp_notifications_enabled: Optional[bool] = None
    whatsapp_phone: Optional[str] = Field(None, max_length=20)


class UnreadCountResponse(BaseModel):
    """Contagem de notificações não lidas."""

    total_unread: int
    by_type: dict  # {"payslip_available": 2, "document_available": 1, ...}
    by_priority: dict  # {"urgent": 1, "high": 2, "normal": 5, "low": 0}
    oldest_unread_at: Optional[datetime]


class NotificationFilterRequest(BaseModel):
    """Filtros para busca de notificações."""

    employee_id: Optional[UUID] = None
    notification_type: Optional[NotificationType] = None
    priority: Optional[NotificationPriority] = None
    is_read: Optional[bool] = None
    is_active: Optional[bool] = None
    is_archived: Optional[bool] = None
    reference_type: Optional[str] = None
    reference_id: Optional[UUID] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    channel: Optional[NotificationChannel] = None


class NotificationBulkCreateRequest(BaseModel):
    """Request para criação em lote de notificações."""

    employee_ids: List[UUID] = Field(..., min_length=1, max_length=1000)
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.NORMAL

    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=5000)
    short_message: Optional[str] = Field(None, max_length=200)

    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=20)

    action_url: Optional[str] = Field(None, max_length=500)
    action_label: Optional[str] = Field(None, max_length=50)

    channels: List[NotificationChannel] = Field(
        default_factory=lambda: [NotificationChannel.PORTAL]
    )

    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class NotificationBulkCreateResponse(BaseModel):
    """Resposta de criação em lote."""

    total_requested: int
    total_created: int
    notification_ids: List[UUID]
