/**
 * Tipos TypeScript para integração Sólides
 * Sprint 33: Integration Framework
 */

// ==================== ENUMS ====================

export type SyncDirection = 'solides_to_conecta' | 'conecta_to_solides' | 'bidirectional';

export type ConflictStrategy = 'solides_wins' | 'conecta_wins' | 'most_recent' | 'manual';

export type IntegrationStatus = 'healthy' | 'warning' | 'error' | 'disconnected';

export type SyncStatus = 'pending' | 'running' | 'completed' | 'failed';

export type ConflictStatus = 'pending' | 'resolved' | 'ignored';

export type EntityType =
  | 'colaboradores'
  | 'departamentos'
  | 'cargos'
  | 'ocorrencias'
  | 'absenteismos';

// ==================== CONFIG ====================

export interface SolidesConfig {
  is_enabled: boolean;
  is_connected: boolean;
  sync_direction: SyncDirection | null;
  conflict_strategy: ConflictStrategy | null;
  enabled_entities: EntityType[];
  last_health_check_at: string | null;
  last_health_check_status: boolean | null;
}

export interface SolidesConfigRequest {
  api_token: string;
  sync_direction?: SyncDirection;
  conflict_strategy?: ConflictStrategy;
  enabled_entities?: EntityType[];
  incremental_sync_interval_minutes?: number;
  auto_create_departments?: boolean;
  auto_create_positions?: boolean;
  webhook_enabled?: boolean;
}

// ==================== STATUS ====================

export interface EntitySyncStatus {
  entity_type: EntityType;
  total_count: number;
  synced_count: number;
  pending_count: number;
  error_count: number;
  last_sync_at: string | null;
}

export interface SyncStatusResponse {
  connected: boolean;
  api_latency_ms: number | null;
  entities: Record<EntityType, EntitySyncStatus>;
  pending_conflicts: number;
  last_full_sync_at: string | null;
  last_incremental_sync_at: string | null;
}

export interface HealthCheckResponse {
  healthy: boolean;
  latency_ms: number | null;
  message: string | null;
}

// ==================== SYNC LOGS ====================

export interface SyncLog {
  id: string;
  sync_type: 'full' | 'incremental' | 'entity';
  entity_type: EntityType;
  status: SyncStatus;
  started_at: string;
  completed_at: string | null;
  duration_seconds: number | null;
  total_processed: number;
  created_count: number;
  updated_count: number;
  error_count: number;
}

export interface SyncLogDetail extends SyncLog {
  direction: SyncDirection | null;
  deleted_count: number;
  skipped_count: number;
  conflict_count: number;
  errors: Record<string, string>[] | null;
  triggered_by: string | null;
  trigger_info: Record<string, unknown> | null;
}

// ==================== CONFLICTS ====================

export interface SyncConflict {
  id: string;
  entity_type: EntityType;
  entity_id: string;
  solides_id: string;
  status: ConflictStatus;
  changed_fields: string[];
  detected_at: string;
  solides_data: Record<string, unknown>;
  conecta_data: Record<string, unknown>;
}

export interface ConflictResolutionRequest {
  strategy: ConflictStrategy;
  resolution_notes?: string;
}

// ==================== SYNC TRIGGERS ====================

export interface SyncTriggerRequest {
  entity_types?: EntityType[];
  full_sync?: boolean;
}

export interface SyncTriggerResponse {
  success: boolean;
  message: string;
  task_id: string;
}

// ==================== DASHBOARD STATE ====================

export interface SolidesDashboardState {
  config: SolidesConfig | null;
  syncStatus: SyncStatusResponse | null;
  health: HealthCheckResponse | null;
  logs: SyncLog[];
  conflicts: SyncConflict[];
  loading: {
    config: boolean;
    status: boolean;
    health: boolean;
    logs: boolean;
    conflicts: boolean;
    sync: boolean;
  };
  error: string | null;
}

// ==================== COMPUTED TYPES ====================

export interface DashboardMetrics {
  totalEmployees: number;
  syncedEmployees: number;
  pendingSync: number;
  errorCount: number;
  syncPercentage: number;
  overallStatus: IntegrationStatus;
  lastSyncFormatted: string;
  pendingConflicts: number;
}
