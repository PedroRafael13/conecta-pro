"""
Schemas do módulo de Configurações e Multi-tenant
Sprint 35: Configurações e Multi-tenant
"""

from modules.config.schemas.config_schemas import (
    # Tenant
    TenantBase,
    TenantCreate,
    TenantUpdate,
    TenantPlanUpdate,
    TenantAddressUpdate,
    TenantResponse,
    TenantList,
    TenantFilter,
    # TenantSettings
    TenantSettingsBase,
    TenantSettingsCreate,
    TenantSettingsUpdate,
    TenantSettingsValueUpdate,
    TenantSettingsResponse,
    TenantSettingsList,
    TenantSettingsFilter,
    # SystemConfig
    SystemConfigBase,
    SystemConfigCreate,
    SystemConfigUpdate,
    SystemConfigValueUpdate,
    SystemConfigResponse,
    SystemConfigList,
    SystemConfigFilter,
    # FeatureFlag
    FeatureFlagBase,
    FeatureFlagCreate,
    FeatureFlagUpdate,
    FeatureFlagRolloutUpdate,
    FeatureFlagGradualRollout,
    FeatureFlagTenantToggle,
    FeatureFlagUserToggle,
    FeatureFlagEvaluate,
    FeatureFlagEvaluateResponse,
    FeatureFlagResponse,
    FeatureFlagList,
    FeatureFlagFilter,
    # NotificationTemplate
    NotificationTemplateBase,
    NotificationTemplateCreate,
    NotificationTemplateUpdate,
    NotificationTemplateRender,
    NotificationTemplateRenderResponse,
    NotificationTemplateResponse,
    NotificationTemplateList,
    NotificationTemplateFilter,
    # Dashboard
    ConfigDashboard,
    TenantDashboard,
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
