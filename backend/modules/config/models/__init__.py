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
    ConfigNotificationTemplate as NotificationTemplate,
)
from modules.config.models.notification_template import (
    NotificationChannel,
    NotificationType,
    TemplateStatus,
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
    "NotificationChannel",
    "NotificationType",
    "TemplateStatus",
]
