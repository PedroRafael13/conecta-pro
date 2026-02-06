/**
 * Service Layer - Exports centralizados
 *
 * Módulos disponíveis:
 * - recruitment: Recrutamento e Seleção
 * - audit: Auditoria e Compliance
 * - config: Configurações do Sistema
 * - document-kits: Kits Documentais
 * - government: Integração Governamental
 * - notifications: Notificações Multi-canal
 * - bidding: Licitações e Contratos
 * - documents: Document Intelligence (OCR, Classificação, Extração)
 * - security-lgpd: Compliance LGPD (Lei 13.709/2018)
 *
 * NOTA: Alguns tipos tem conflitos de nome entre modulos.
 * Para usar tipos especificos, importe diretamente do modulo:
 * - NotificationChannel: './notifications' (preferido) ou './config' como ConfigNotificationChannel
 * - ValidationResult: './documents' (preferido) ou './document-kits' como DocumentKitValidationResult
 */

export { recruitmentService } from './recruitment.service';
export type * from '@/types/generated/recruitment/conectaPROMóduloRECRUITMENT.schemas';

// Audit
export * from './audit';

// Config - re-exporta tudo exceto NotificationChannel (conflito com notifications)
export {
  // Tenants
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
  // Tenant Settings
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
  getSettingCategoryLabel,
  type ListTenantSettingsParams,
  type SettingCategory,
  // System Config
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
  validateConfigValue as validateSystemConfigValue,
  CONFIG_CATEGORIES,
  CONFIG_SCOPES,
  getSystemConfigCategoryLabel,
  getScopeLabel,
  isConfigSensitive,
  maskSensitiveValue,
  type ListSystemConfigParams,
  type ConfigCategory,
  type ConfigScope,
  // Feature Flags
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
  getFlagCategoryLabel,
  getFlagStatusLabel,
  getFlagStatusColor,
  type ListFeatureFlagsParams,
  type SetPercentageParams,
  type FlagCategory,
  // Notification Templates
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
  getTemplateCategoryLabel,
  type ListNotificationTemplatesParams,
  type NotificationChannel as ConfigNotificationChannel,
  type NotificationCategory,
} from './config';

// Dashboards do config
export * from './config/dashboards';

// Document Kits - re-exporta tudo exceto ValidationResult (conflito com documents)
export {
  documentKitService,
  documentKitItemService,
  documentKitAssignmentService,
  documentKitItemStatusService,
  documentKitAIService,
  documentKitOperationalService,
} from './document-kits';
// Tipos do document-kits com alias para ValidationResult
export type { ValidationResult as DocumentKitValidationResult } from './document-kits/documentKitOperationalService';

// Government
export * from './government';

// Notifications - NotificationChannel definido aqui como preferido
export * from './notifications';

// Bidding
export * from './bidding';

// Documents - ValidationResult definido aqui como preferido
export * from './documents';

// Security LGPD
export * from './security-lgpd';
