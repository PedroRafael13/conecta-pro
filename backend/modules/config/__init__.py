"""
Módulo de Configurações e Multi-tenant
Sprint 35: Configurações e Multi-tenant

Este módulo fornece:
- Tenant: Gestão de inquilinos/clientes do sistema
- TenantSettings: Configurações específicas por tenant
- SystemConfig: Configurações globais do sistema
- FeatureFlag: Feature flags com A/B testing e rollout gradual
- NotificationTemplate: Templates de notificação multicanal
"""

from modules.config.controllers import router
from modules.config.models import (
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
from modules.config.repositories import ConfigRepository
from modules.config.services import ConfigService

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
    "NotificationChannel",
    "NotificationType",
    "TemplateStatus",
    # Repository & Service
    "ConfigRepository",
    "ConfigService",
    # Router
    "router",
]
