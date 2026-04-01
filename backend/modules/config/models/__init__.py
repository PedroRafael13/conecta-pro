"""
Models do módulo de Configurações e Multi-tenant
Sprint 35: Configurações e Multi-tenant
"""

from modules.config.models.feature_flag import (
    FeatureFlag,
    FlagStatus,
    FlagType,
    RolloutStrategy,
)
from modules.config.models.notification_template import (
    ConfigNotificationChannel,
    NotificationType,
    TemplateStatus,
)
from modules.config.models.notification_template import (
    ConfigNotificationTemplate as NotificationTemplate,
)
from modules.config.models.system_config import (
    ConfigPriority,
    ConfigScope,
    SystemConfig,
)
from modules.config.models.tenant import (
    Tenant,
    TenantPlan,
    TenantStatus,
    TenantType,
)
from modules.config.models.tenant_settings import (
    SettingCategory,
    SettingType,
    TenantSettings,
)

# Alias retroativo: ConfigNotificationChannel exportado como NotificationChannel
# para não quebrar código existente que importa de modules.config.models.
# NOTA: Este é um StrEnum, NÃO o modelo SQLAlchemy NotificationChannel que mapeia
# a tabela 'notification_channels' (modules.notifications.models.notification_channel).
NotificationChannel = ConfigNotificationChannel

__all__ = [
    # Tenant
    "Tenant",
    "TenantStatus",
    "TenantPlan",
    "TenantType",
    # TenantSettings
    "TenantSettings",
    "SettingCategory",
    "SettingType",
    # SystemConfig
    "SystemConfig",
    "ConfigScope",
    "ConfigPriority",
    # FeatureFlag
    "FeatureFlag",
    "FlagStatus",
    "FlagType",
    "RolloutStrategy",
    # NotificationTemplate
    "NotificationTemplate",
    "ConfigNotificationChannel",  # nome canônico (StrEnum)
    "NotificationChannel",  # alias retroativo de ConfigNotificationChannel
    "NotificationType",
    "TemplateStatus",
]
