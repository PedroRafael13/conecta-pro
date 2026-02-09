"""
Schemas do módulo de Configurações e Multi-tenant
Sprint 35: Configurações e Multi-tenant
"""

from modules.config.schemas.config_schemas import (
    # Dashboard
    ConfigDashboard,
    # FeatureFlag
    FeatureFlagBase,
    FeatureFlagCreate,
    FeatureFlagEvaluate,
    FeatureFlagEvaluateResponse,
    FeatureFlagFilter,
    FeatureFlagGradualRollout,
    FeatureFlagList,
    FeatureFlagResponse,
    FeatureFlagRolloutUpdate,
    FeatureFlagTenantToggle,
    FeatureFlagUpdate,
    FeatureFlagUserToggle,
    # NotificationTemplate
    NotificationTemplateBase,
    NotificationTemplateCreate,
    NotificationTemplateFilter,
    NotificationTemplateList,
    NotificationTemplateRender,
    NotificationTemplateRenderResponse,
    NotificationTemplateResponse,
    NotificationTemplateUpdate,
    # SystemConfig
    SystemConfigBase,
    SystemConfigCreate,
    SystemConfigFilter,
    SystemConfigList,
    SystemConfigResponse,
    SystemConfigUpdate,
    SystemConfigValueUpdate,
    TenantAddressUpdate,
    # Tenant
    TenantBase,
    TenantCreate,
    TenantDashboard,
    TenantFilter,
    TenantList,
    TenantPlanUpdate,
    TenantResponse,
    # TenantSettings
    TenantSettingsBase,
    TenantSettingsCreate,
    TenantSettingsFilter,
    TenantSettingsList,
    TenantSettingsResponse,
    TenantSettingsUpdate,
    TenantSettingsValueUpdate,
    TenantUpdate,
)

__all__ = [
    # Tenant
    "TenantBase",
    "TenantCreate",
    "TenantUpdate",
    "TenantPlanUpdate",
    "TenantAddressUpdate",
    "TenantResponse",
    "TenantList",
    "TenantFilter",
    # TenantSettings
    "TenantSettingsBase",
    "TenantSettingsCreate",
    "TenantSettingsUpdate",
    "TenantSettingsValueUpdate",
    "TenantSettingsResponse",
    "TenantSettingsList",
    "TenantSettingsFilter",
    # SystemConfig
    "SystemConfigBase",
    "SystemConfigCreate",
    "SystemConfigUpdate",
    "SystemConfigValueUpdate",
    "SystemConfigResponse",
    "SystemConfigList",
    "SystemConfigFilter",
    # FeatureFlag
    "FeatureFlagBase",
    "FeatureFlagCreate",
    "FeatureFlagUpdate",
    "FeatureFlagRolloutUpdate",
    "FeatureFlagGradualRollout",
    "FeatureFlagTenantToggle",
    "FeatureFlagUserToggle",
    "FeatureFlagEvaluate",
    "FeatureFlagEvaluateResponse",
    "FeatureFlagResponse",
    "FeatureFlagList",
    "FeatureFlagFilter",
    # NotificationTemplate
    "NotificationTemplateBase",
    "NotificationTemplateCreate",
    "NotificationTemplateUpdate",
    "NotificationTemplateRender",
    "NotificationTemplateRenderResponse",
    "NotificationTemplateResponse",
    "NotificationTemplateList",
    "NotificationTemplateFilter",
    # Dashboard
    "ConfigDashboard",
    "TenantDashboard",
]
