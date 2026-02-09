"""Schemas para preferências do funcionário."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from modules.hr.employee_portal.models import LanguagePreference, ThemePreference


class ThemeConfigSchema(BaseModel):
    """Configuração de tema."""

    theme: ThemePreference = ThemePreference.SYSTEM
    font_size: str = Field(default="medium", pattern="^(small|medium|large)$")
    compact_mode: bool = False
    animations_enabled: bool = True


class NotificationConfigSchema(BaseModel):
    """Configuração de notificações."""

    # Portal
    notifications_enabled: bool = True
    notification_sound: bool = True
    notification_badge: bool = True

    # Email
    email_notifications_enabled: bool = True
    email_payslip: bool = True
    email_documents: bool = True
    email_vacation: bool = True
    email_announcements: bool = True
    email_birthday: bool = True
    email_digest: bool = False
    email_digest_time: str = Field(default="08:00", pattern=r"^\d{2}:\d{2}$")

    # Push
    push_notifications_enabled: bool = True
    push_payslip: bool = True
    push_documents: bool = True
    push_vacation: bool = True
    push_announcements: bool = True
    push_time_entry: bool = True
    push_quiet_hours: bool = True
    push_quiet_start: str = Field(default="22:00", pattern=r"^\d{2}:\d{2}$")
    push_quiet_end: str = Field(default="07:00", pattern=r"^\d{2}:\d{2}$")

    # SMS
    sms_notifications_enabled: bool = False
    sms_urgent_only: bool = True

    # WhatsApp
    whatsapp_notifications_enabled: bool = False
    whatsapp_phone: str | None = None


class DashboardConfigSchema(BaseModel):
    """Configuração do dashboard."""

    layout: str = Field(default="default", max_length=20)
    widgets: list[str] = Field(
        default_factory=lambda: [
            "payslip_summary",
            "vacation_balance",
            "time_entry_today",
            "pending_documents",
            "recent_notifications",
        ]
    )
    default_page: str = Field(default="dashboard", max_length=50)


class PrivacyConfigSchema(BaseModel):
    """Configuração de privacidade."""

    show_birthday: bool = True
    show_photo: bool = True
    show_department: bool = True
    show_position: bool = True
    allow_colleague_contact: bool = True


class SecurityConfigSchema(BaseModel):
    """Configuração de segurança."""

    two_factor_enabled: bool = False
    two_factor_method: str | None = Field(None, pattern="^(app|sms|email)$")
    session_timeout_minutes: bool = True
    remember_device: bool = True


class AccessibilityConfigSchema(BaseModel):
    """Configuração de acessibilidade."""

    screen_reader_mode: bool = False
    keyboard_navigation: bool = True
    reduce_motion: bool = False
    color_blind_mode: str | None = Field(None, pattern="^(protanopia|deuteranopia|tritanopia)$")


class TrustedDeviceSchema(BaseModel):
    """Dispositivo confiável."""

    device_id: str
    name: str
    device_type: str  # mobile, desktop, tablet
    browser: str | None = None
    os: str | None = None
    last_used: datetime
    ip_address: str | None = None
    location: str | None = None


class PreferencesCreate(BaseModel):
    """Schema para criação de preferências."""

    employee_id: UUID

    # Aparência
    theme: ThemePreference = ThemePreference.SYSTEM
    language: LanguagePreference = LanguagePreference.PT_BR
    font_size: str = Field(default="medium", pattern="^(small|medium|large)$")
    compact_mode: bool = False
    animations_enabled: bool = True

    # Notificações
    notifications_enabled: bool = True
    notification_sound: bool = True
    notification_badge: bool = True

    # Dashboard
    dashboard_layout: str = Field(default="default", max_length=20)
    dashboard_widgets: list[str] = Field(default_factory=list)
    default_page: str = Field(default="dashboard", max_length=50)


class PreferencesUpdate(BaseModel):
    """Schema para atualização de preferências."""

    # Aparência
    theme: ThemePreference | None = None
    language: LanguagePreference | None = None
    font_size: str | None = Field(None, pattern="^(small|medium|large)$")
    compact_mode: bool | None = None
    animations_enabled: bool | None = None

    # Notificações - Portal
    notifications_enabled: bool | None = None
    notification_sound: bool | None = None
    notification_badge: bool | None = None

    # Notificações - Email
    email_notifications_enabled: bool | None = None
    email_payslip: bool | None = None
    email_documents: bool | None = None
    email_vacation: bool | None = None
    email_announcements: bool | None = None
    email_birthday: bool | None = None
    email_digest: bool | None = None
    email_digest_time: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")

    # Notificações - Push
    push_notifications_enabled: bool | None = None
    push_payslip: bool | None = None
    push_documents: bool | None = None
    push_vacation: bool | None = None
    push_announcements: bool | None = None
    push_time_entry: bool | None = None
    push_quiet_hours: bool | None = None
    push_quiet_start: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")
    push_quiet_end: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")

    # Notificações - SMS
    sms_notifications_enabled: bool | None = None
    sms_urgent_only: bool | None = None

    # Notificações - WhatsApp
    whatsapp_notifications_enabled: bool | None = None
    whatsapp_phone: str | None = Field(None, max_length=20)

    # Dashboard
    dashboard_layout: str | None = Field(None, max_length=20)
    dashboard_widgets: list[str] | None = None
    default_page: str | None = Field(None, max_length=50)

    # Férias
    vacation_reminder_days: list[int] | None = None
    vacation_balance_notification: bool | None = None

    # Ponto
    time_entry_reminder: bool | None = None
    time_entry_reminder_times: list[str] | None = None
    time_entry_geofence_reminder: bool | None = None

    # Privacidade
    show_birthday: bool | None = None
    show_photo: bool | None = None
    show_department: bool | None = None
    show_position: bool | None = None
    allow_colleague_contact: bool | None = None

    # Segurança
    two_factor_enabled: bool | None = None
    two_factor_method: str | None = Field(None, pattern="^(app|sms|email)$")
    session_timeout_minutes: bool | None = None
    remember_device: bool | None = None

    # Acessibilidade
    screen_reader_mode: bool | None = None
    keyboard_navigation: bool | None = None
    reduce_motion: bool | None = None
    color_blind_mode: str | None = Field(None, pattern="^(protanopia|deuteranopia|tritanopia)$")


class PreferencesResponse(BaseModel):
    """Schema de resposta para preferências."""

    id: UUID
    condominio_id: UUID
    employee_id: UUID

    # Aparência
    theme: str
    language: str
    font_size: str
    compact_mode: bool
    animations_enabled: bool

    # Notificações
    notification_channels: list[str]
    notifications_enabled: bool
    notification_sound: bool
    notification_badge: bool

    # Email
    email_notifications_enabled: bool
    email_payslip: bool
    email_documents: bool
    email_vacation: bool
    email_announcements: bool
    email_birthday: bool
    email_digest: bool
    email_digest_time: str

    # Push
    push_notifications_enabled: bool
    push_payslip: bool
    push_documents: bool
    push_vacation: bool
    push_announcements: bool
    push_time_entry: bool
    push_quiet_hours: bool
    push_quiet_start: str
    push_quiet_end: str

    # SMS
    sms_notifications_enabled: bool
    sms_urgent_only: bool

    # WhatsApp
    whatsapp_notifications_enabled: bool
    whatsapp_phone: str | None

    # Dashboard
    dashboard_layout: str
    dashboard_widgets: list[str]
    default_page: str

    # Férias
    vacation_reminder_days: list[int]
    vacation_balance_notification: bool

    # Ponto
    time_entry_reminder: bool
    time_entry_reminder_times: list[str]
    time_entry_geofence_reminder: bool

    # Privacidade
    show_birthday: bool
    show_photo: bool
    show_department: bool
    show_position: bool
    allow_colleague_contact: bool

    # Segurança
    two_factor_enabled: bool
    two_factor_method: str | None
    session_timeout_minutes: bool
    remember_device: bool
    trusted_devices: list[TrustedDeviceSchema]

    # Acessibilidade
    screen_reader_mode: bool
    keyboard_navigation: bool
    reduce_motion: bool
    color_blind_mode: str | None

    # Metadados
    last_login_at: datetime | None
    last_login_ip: str | None
    last_login_device: str | None
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class PrivacySettingsUpdate(BaseModel):
    """Schema para atualização de configurações de privacidade."""

    show_birthday: bool | None = None
    show_photo: bool | None = None
    show_department: bool | None = None
    show_position: bool | None = None
    allow_colleague_contact: bool | None = None


class DashboardSettingsUpdate(BaseModel):
    """Schema para atualização de configurações do dashboard."""

    layout: str | None = Field(None, max_length=20)
    widgets: list[str] | None = None
    default_page: str | None = Field(None, max_length=50)


class DeviceInfo(BaseModel):
    """Informação de dispositivo para registro."""

    name: str = Field(..., min_length=1, max_length=100)
    user_agent: str | None = None
    ip_address: str | None = None


class TwoFactorSetupResponse(BaseModel):
    """Resposta de configuração 2FA."""

    secret: str
    qr_code_uri: str
    backup_codes: list[str]


class ClientConfigResponse(BaseModel):
    """Configurações para o frontend."""

    theme: str
    language: str
    font_size: str
    compact_mode: bool
    animations_enabled: bool
    notifications_enabled: bool
    notification_sound: bool
    dashboard_layout: str
    dashboard_widgets: list[str]
    default_page: str
    accessibility: AccessibilityConfigSchema
