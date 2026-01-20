"""Schemas para preferências do funcionário."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field

from modules.hr.employee_portal.models import ThemePreference, LanguagePreference


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
    whatsapp_phone: Optional[str] = None


class DashboardConfigSchema(BaseModel):
    """Configuração do dashboard."""

    layout: str = Field(default="default", max_length=20)
    widgets: List[str] = Field(
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
    two_factor_method: Optional[str] = Field(None, pattern="^(app|sms|email)$")
    session_timeout_minutes: bool = True
    remember_device: bool = True


class AccessibilityConfigSchema(BaseModel):
    """Configuração de acessibilidade."""

    screen_reader_mode: bool = False
    keyboard_navigation: bool = True
    reduce_motion: bool = False
    color_blind_mode: Optional[str] = Field(
        None, pattern="^(protanopia|deuteranopia|tritanopia)$"
    )


class TrustedDeviceSchema(BaseModel):
    """Dispositivo confiável."""

    device_id: str
    name: str
    device_type: str  # mobile, desktop, tablet
    browser: Optional[str] = None
    os: Optional[str] = None
    last_used: datetime
    ip_address: Optional[str] = None
    location: Optional[str] = None


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
    dashboard_widgets: List[str] = Field(default_factory=list)
    default_page: str = Field(default="dashboard", max_length=50)


class PreferencesUpdate(BaseModel):
    """Schema para atualização de preferências."""

    # Aparência
    theme: Optional[ThemePreference] = None
    language: Optional[LanguagePreference] = None
    font_size: Optional[str] = Field(None, pattern="^(small|medium|large)$")
    compact_mode: Optional[bool] = None
    animations_enabled: Optional[bool] = None

    # Notificações - Portal
    notifications_enabled: Optional[bool] = None
    notification_sound: Optional[bool] = None
    notification_badge: Optional[bool] = None

    # Notificações - Email
    email_notifications_enabled: Optional[bool] = None
    email_payslip: Optional[bool] = None
    email_documents: Optional[bool] = None
    email_vacation: Optional[bool] = None
    email_announcements: Optional[bool] = None
    email_birthday: Optional[bool] = None
    email_digest: Optional[bool] = None
    email_digest_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")

    # Notificações - Push
    push_notifications_enabled: Optional[bool] = None
    push_payslip: Optional[bool] = None
    push_documents: Optional[bool] = None
    push_vacation: Optional[bool] = None
    push_announcements: Optional[bool] = None
    push_time_entry: Optional[bool] = None
    push_quiet_hours: Optional[bool] = None
    push_quiet_start: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    push_quiet_end: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")

    # Notificações - SMS
    sms_notifications_enabled: Optional[bool] = None
    sms_urgent_only: Optional[bool] = None

    # Notificações - WhatsApp
    whatsapp_notifications_enabled: Optional[bool] = None
    whatsapp_phone: Optional[str] = Field(None, max_length=20)

    # Dashboard
    dashboard_layout: Optional[str] = Field(None, max_length=20)
    dashboard_widgets: Optional[List[str]] = None
    default_page: Optional[str] = Field(None, max_length=50)

    # Férias
    vacation_reminder_days: Optional[List[int]] = None
    vacation_balance_notification: Optional[bool] = None

    # Ponto
    time_entry_reminder: Optional[bool] = None
    time_entry_reminder_times: Optional[List[str]] = None
    time_entry_geofence_reminder: Optional[bool] = None

    # Privacidade
    show_birthday: Optional[bool] = None
    show_photo: Optional[bool] = None
    show_department: Optional[bool] = None
    show_position: Optional[bool] = None
    allow_colleague_contact: Optional[bool] = None

    # Segurança
    two_factor_enabled: Optional[bool] = None
    two_factor_method: Optional[str] = Field(None, pattern="^(app|sms|email)$")
    session_timeout_minutes: Optional[bool] = None
    remember_device: Optional[bool] = None

    # Acessibilidade
    screen_reader_mode: Optional[bool] = None
    keyboard_navigation: Optional[bool] = None
    reduce_motion: Optional[bool] = None
    color_blind_mode: Optional[str] = Field(
        None, pattern="^(protanopia|deuteranopia|tritanopia)$"
    )


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
    notification_channels: List[str]
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
    whatsapp_phone: Optional[str]

    # Dashboard
    dashboard_layout: str
    dashboard_widgets: List[str]
    default_page: str

    # Férias
    vacation_reminder_days: List[int]
    vacation_balance_notification: bool

    # Ponto
    time_entry_reminder: bool
    time_entry_reminder_times: List[str]
    time_entry_geofence_reminder: bool

    # Privacidade
    show_birthday: bool
    show_photo: bool
    show_department: bool
    show_position: bool
    allow_colleague_contact: bool

    # Segurança
    two_factor_enabled: bool
    two_factor_method: Optional[str]
    session_timeout_minutes: bool
    remember_device: bool
    trusted_devices: List[TrustedDeviceSchema]

    # Acessibilidade
    screen_reader_mode: bool
    keyboard_navigation: bool
    reduce_motion: bool
    color_blind_mode: Optional[str]

    # Metadados
    last_login_at: Optional[datetime]
    last_login_ip: Optional[str]
    last_login_device: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class PrivacySettingsUpdate(BaseModel):
    """Schema para atualização de configurações de privacidade."""

    show_birthday: Optional[bool] = None
    show_photo: Optional[bool] = None
    show_department: Optional[bool] = None
    show_position: Optional[bool] = None
    allow_colleague_contact: Optional[bool] = None


class DashboardSettingsUpdate(BaseModel):
    """Schema para atualização de configurações do dashboard."""

    layout: Optional[str] = Field(None, max_length=20)
    widgets: Optional[List[str]] = None
    default_page: Optional[str] = Field(None, max_length=50)


class DeviceInfo(BaseModel):
    """Informação de dispositivo para registro."""

    name: str = Field(..., min_length=1, max_length=100)
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None


class TwoFactorSetupResponse(BaseModel):
    """Resposta de configuração 2FA."""

    secret: str
    qr_code_uri: str
    backup_codes: List[str]


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
    dashboard_widgets: List[str]
    default_page: str
    accessibility: AccessibilityConfigSchema
