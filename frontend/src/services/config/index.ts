/**
 * Services - Modulo CONFIG
 * Export central de todos os services de configuracao
 */

// Tenants - exports completos
export {
  listTenants,
  createTenant,
  getTenant,
  updateTenant,
  deleteTenant,
  updateTenantPlan,
  updateTenantAddress,
  activateTenant,
  suspendTenant,
  cancelTenant,
  convertTrialTenant,
  enableTenantFeature,
  disableTenantFeature,
  calculateTenantStats,
  isTenantActive,
  isTenantTrial,
  isTenantSuspended,
  hasTenantFeature,
  type ListTenantsParams,
  type TenantStats,
} from './tenants';

// Tenant Settings - exports com alias para getCategoryLabel
export {
  listTenantSettings,
  createTenantSetting,
  getTenantSetting,
  updateTenantSetting,
  deleteTenantSetting,
  updateTenantSettingValue,
  resetTenantSetting,
  groupSettingsByCategory,
  findSettingByKey,
  getSettingValue,
  isSettingEnabled,
  validateSettingValue,
  SETTING_CATEGORIES,
  getCategoryLabel as getSettingCategoryLabel,
  type ListTenantSettingsParams,
  type SettingCategory,
} from './tenant-settings';

// System Config - exports com alias para getCategoryLabel
export {
  listSystemConfigs,
  createSystemConfig,
  getSystemConfig,
  updateSystemConfig,
  deleteSystemConfig,
  groupConfigsByCategory,
  groupConfigsByScope,
  findConfigByKey,
  getConfigValue,
  isConfigEnabled,
  validateConfigValue,
  CONFIG_CATEGORIES,
  CONFIG_SCOPES,
  getCategoryLabel as getSystemConfigCategoryLabel,
  getScopeLabel,
  isConfigSensitive,
  maskSensitiveValue,
  type ListSystemConfigParams,
  type ConfigCategory,
  type ConfigScope,
} from './system-config';

// Feature Flags - exports com alias para getCategoryLabel
export {
  listFeatureFlags,
  createFeatureFlag,
  getFeatureFlag,
  updateFeatureFlag,
  deleteFeatureFlag,
  enableFeatureFlag,
  disableFeatureFlag,
  setFeatureFlagPercentage,
  setGradualRollout,
  toggleFeatureFlagForTenant,
  evaluateFeatureFlag,
  isFeatureFlagEnabled,
  isFeatureFlagInRollout,
  isTenantInRollout,
  groupFlagsByCategory,
  findFlagByKey,
  filterFlagsByStatus,
  FLAG_CATEGORIES,
  getCategoryLabel as getFlagCategoryLabel,
  getStatusLabel as getFlagStatusLabel,
  getStatusColor as getFlagStatusColor,
  type ListFeatureFlagsParams,
  type SetPercentageParams,
  type FlagCategory,
} from './feature-flags';

// Notification Templates - exports com alias para getCategoryLabel
export {
  listNotificationTemplates,
  createNotificationTemplate,
  getNotificationTemplate,
  updateNotificationTemplate,
  deleteNotificationTemplate,
  activateNotificationTemplate,
  deactivateNotificationTemplate,
  renderNotificationTemplate,
  cloneNotificationTemplate,
  isTemplateActive,
  groupTemplatesByChannel,
  groupTemplatesByCategory,
  findTemplateByCode,
  filterTemplatesByChannel,
  filterActiveTemplates,
  extractTemplateVariables,
  validateTemplateVariables,
  NOTIFICATION_CHANNELS,
  NOTIFICATION_CATEGORIES,
  getChannelLabel,
  getChannelIcon,
  getCategoryLabel as getTemplateCategoryLabel,
  type ListNotificationTemplatesParams,
  type NotificationChannel,
  type NotificationCategory,
} from './notification-templates';

// Dashboards
export * from './dashboards';
