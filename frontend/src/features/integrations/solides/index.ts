/**
 * Exports para módulo de integração Sólides
 * Sprint 33: Integration Framework
 */

// Page
export { SolidesIntegrationPage } from './SolidesIntegrationPage';

// Hook
export { useSolidesIntegration } from './useSolidesIntegration';

// Types
export type {
  SyncDirection,
  ConflictStrategy,
  IntegrationStatus,
  SyncStatus,
  ConflictStatus,
  EntityType,
  SolidesConfig,
  SolidesConfigRequest,
  EntitySyncStatus,
  SyncStatusResponse,
  HealthCheckResponse,
  SyncLog,
  SyncLogDetail,
  SyncConflict,
  ConflictResolutionRequest,
  SyncTriggerRequest,
  SyncTriggerResponse,
  SolidesDashboardState,
  DashboardMetrics,
} from './types';
