"""
Models do módulo de Configurações e Multi-tenant
Sprint 35: Configurações e Multi-tenant
"""

from modules.config.models.tenant import (
    Tenant,
    TenantStatus,
    TenantPlan,
    TenantType,
)
from modules.config.models.tenant_settings import (
    TenantSettings,
    SettingCategory,
    SettingType,
)
from modules.config.models.system_config import (
    SystemConfig,
    ConfigScope,
    ConfigPriority,
)
from modules.config.models.feature_flag import (
    FeatureFlag,
    FlagStatus,
    FlagType,
    RolloutStrategy,
)
from modules.config.models.notification_template import (
    NotificationTemplate,
    NotificationChannel,
    NotificationType,
    TemplateStatus,
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
