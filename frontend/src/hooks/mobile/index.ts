/**
 * Mobile Hooks - Index
 *
 * Exporta todos os hooks React Query do módulo MOBILE.
 *
 * Cobertura:
 * - Sync Operations (3 hooks + auto-sync)
 * - Device Management (3 hooks)
 * - Push Notifications (8 hooks)
 * - Mobile Core (9 hooks)
 *
 * Total: 23+ hooks customizados
 *
 * @module hooks/mobile
 */

// Sync Operations
export {
  useSyncData,
  useSyncStatus,
  useResolveSyncConflict,
  useAutoSync,
} from './useSync';

// Device Management
export {
  useRegisterDevice,
  useUnregisterDevice,
  useDeviceInfo,
  useAutoRegisterDevice,
} from './useDevice';

// Push Notifications
export {
  useNotifications,
  useMarkAsRead,
  useMarkAsDelivered,
  useNotificationPreferences,
  useUpdateNotificationPreferences,
  useSendBroadcast,
  useNotificationStats,
  useMarkMultipleAsRead,
  useUnreadCount,
} from './usePushNotifications';

// Mobile Core
export {
  useMobileHealth,
  useMobileConfig,
  useMobileDashboard,
  useOfflineData,
  useBatchOperations,
  useRequiresUpdate,
  useMaintenanceMode,
  useFeatureFlag,
  useMobileAppInit,
} from './useMobile';
