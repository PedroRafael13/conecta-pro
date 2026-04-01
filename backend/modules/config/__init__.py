"""
Módulo de Configurações e Multi-tenant

DEPRECATED: Use 'modules.gestao' instead for router imports.
Deprecation date: 2026-03-11. Removal target: 2026-05-11.
"""

import warnings

warnings.warn(
    "Importing from 'modules.config' is deprecated. "
    "Use 'modules.gestao' for router access. "
    "This module will be removed after 2026-05-11.",
    DeprecationWarning,
    stacklevel=2,
)

from modules.config.controllers import router  # noqa: E402
from modules.config.models import (  # noqa: E402
    ConfigNotificationChannel,
    ConfigPriority,
    ConfigScope,
    FeatureFlag,
    FlagStatus,
    FlagType,
    NotificationChannel,
    NotificationTemplate,
    NotificationType,
    RolloutStrategy,
    SettingCategory,
    SettingType,
    SystemConfig,
    TemplateStatus,
    Tenant,
    TenantPlan,
    TenantSettings,
    TenantStatus,
    TenantType,
)
from modules.config.repositories import ConfigRepository  # noqa: E402
from modules.config.services import ConfigService  # noqa: E402

__all__ = [
    # Models
    "Tenant",
    "TenantSettings",
    "SystemConfig",
    "FeatureFlag",
    "NotificationTemplate",
    # Enums
    "TenantStatus",
    "TenantPlan",
    "TenantType",
    "SettingCategory",
    "SettingType",
    "ConfigScope",
    "ConfigPriority",
    "FlagStatus",
    "FlagType",
    "RolloutStrategy",
    "ConfigNotificationChannel",  # nome canônico (StrEnum)
    "NotificationChannel",  # alias retroativo de ConfigNotificationChannel
    "NotificationType",
    "TemplateStatus",
    # Repository & Service
    "ConfigRepository",
    "ConfigService",
    # Router
    "router",
]
