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

from modules.config.models import (
    Tenant,
    TenantStatus,
    TenantPlan,
    TenantType,
    TenantSettings,
    SettingCategory,
    SettingType,
    SystemConfig,
    ConfigScope,
    ConfigPriority,
    FeatureFlag,
    FlagStatus,
    FlagType,
    RolloutStrategy,
    NotificationTemplate,
    NotificationChannel,
    NotificationType,
    TemplateStatus,
)
from modules.config.repositories import ConfigRepository
from modules.config.services import ConfigService
from modules.config.controllers import router

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
