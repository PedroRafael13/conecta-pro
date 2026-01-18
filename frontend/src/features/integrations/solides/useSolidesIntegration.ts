/**
 * Hook para gerenciamento da integração Sólides
 * Sprint 33: Integration Framework
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { api } from '@/core/api';
import type {
  SolidesConfig,
  SolidesConfigRequest,
  SyncStatusResponse,
  HealthCheckResponse,
  SyncLog,
  SyncConflict,
  SyncTriggerResponse,
  ConflictResolutionRequest,
  DashboardMetrics,
  IntegrationStatus,
  EntityType,
  EntitySyncStatus,
} from './types';

// ==================== API ENDPOINTS ====================

const SOLIDES_API = {
  CONFIG: '/integrations/solides/config',
  STATUS: '/integrations/solides/status',
  HEALTH: '/integrations/solides/health',
  LOGS: '/integrations/solides/logs',
  CONFLICTS: '/integrations/solides/conflicts',
  SYNC_FULL: '/integrations/solides/sync/full',
  SYNC_INCREMENTAL: '/integrations/solides/sync/incremental',
  SYNC_ENTITY: (type: string, id: string) =>
    `/integrations/solides/sync/entity/${type}/${id}`,
  RESOLVE_CONFLICT: (id: string) => `/integrations/solides/conflicts/${id}/resolve`,
  IGNORE_CONFLICT: (id: string) => `/integrations/solides/conflicts/${id}/ignore`,
} as const;

// ==================== LOADING STATE ====================

interface LoadingState {
  config: boolean;
  status: boolean;
  health: boolean;
  logs: boolean;
  conflicts: boolean;
  sync: boolean;
  configSave: boolean;
}

// ==================== HOOK ====================

export function useSolidesIntegration() {
  // State
  const [config, setConfig] = useState<SolidesConfig | null>(null);
  const [syncStatus, setSyncStatus] = useState<SyncStatusResponse | null>(null);
  const [health, setHealth] = useState<HealthCheckResponse | null>(null);
  const [logs, setLogs] = useState<SyncLog[]>([]);
  const [conflicts, setConflicts] = useState<SyncConflict[]>([]);
  const [loading, setLoading] = useState<LoadingState>({
    config: false,
    status: false,
    health: false,
    logs: false,
    conflicts: false,
    sync: false,
    configSave: false,
  });
  const [error, setError] = useState<string | null>(null);

  // Refs para controle de polling
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const mountedRef = useRef(true);

  // ==================== FETCH FUNCTIONS ====================

  const fetchConfig = useCallback(async () => {
    if (!mountedRef.current) return;
    setLoading((prev) => ({ ...prev, config: true }));
    setError(null);

    try {
      const data = await api.get<SolidesConfig>(SOLIDES_API.CONFIG);
      if (mountedRef.current) {
        setConfig(data);
      }
    } catch (err) {
      console.error('Erro ao buscar configuração:', err);
      if (mountedRef.current) {
        setError('Erro ao carregar configuração da integração');
      }
    } finally {
      if (mountedRef.current) {
        setLoading((prev) => ({ ...prev, config: false }));
      }
    }
  }, []);

  const fetchStatus = useCallback(async () => {
    if (!mountedRef.current) return;
    setLoading((prev) => ({ ...prev, status: true }));

    try {
      const data = await api.get<SyncStatusResponse>(SOLIDES_API.STATUS);
      if (mountedRef.current) {
        setSyncStatus(data);
      }
    } catch (err) {
      console.error('Erro ao buscar status:', err);
    } finally {
      if (mountedRef.current) {
        setLoading((prev) => ({ ...prev, status: false }));
      }
    }
  }, []);

  const fetchHealth = useCallback(async () => {
    if (!mountedRef.current) return;
    setLoading((prev) => ({ ...prev, health: true }));

    try {
      const data = await api.get<HealthCheckResponse>(SOLIDES_API.HEALTH);
      if (mountedRef.current) {
        setHealth(data);
      }
    } catch (err) {
      console.error('Erro ao verificar saúde:', err);
      if (mountedRef.current) {
        setHealth({ healthy: false, latency_ms: null, message: 'Falha na verificação' });
      }
    } finally {
      if (mountedRef.current) {
        setLoading((prev) => ({ ...prev, health: false }));
      }
    }
  }, []);

  const fetchLogs = useCallback(async (limit = 50) => {
    if (!mountedRef.current) return;
    setLoading((prev) => ({ ...prev, logs: true }));

    try {
      const data = await api.get<SyncLog[]>(`${SOLIDES_API.LOGS}?limit=${limit}`);
      if (mountedRef.current) {
        setLogs(data);
      }
    } catch (err) {
      console.error('Erro ao buscar logs:', err);
    } finally {
      if (mountedRef.current) {
        setLoading((prev) => ({ ...prev, logs: false }));
      }
    }
  }, []);

  const fetchConflicts = useCallback(async () => {
    if (!mountedRef.current) return;
    setLoading((prev) => ({ ...prev, conflicts: true }));

    try {
      const data = await api.get<SyncConflict[]>(SOLIDES_API.CONFLICTS);
      if (mountedRef.current) {
        setConflicts(data);
      }
    } catch (err) {
      console.error('Erro ao buscar conflitos:', err);
    } finally {
      if (mountedRef.current) {
        setLoading((prev) => ({ ...prev, conflicts: false }));
      }
    }
  }, []);

  // ==================== ACTION FUNCTIONS ====================

  const saveConfig = useCallback(async (configData: SolidesConfigRequest) => {
    setLoading((prev) => ({ ...prev, configSave: true }));
    setError(null);

    try {
      await api.post(SOLIDES_API.CONFIG, configData);
      await fetchConfig();
      return { success: true };
    } catch (err) {
      console.error('Erro ao salvar configuração:', err);
      setError('Erro ao salvar configuração');
      return { success: false, error: 'Erro ao salvar configuração' };
    } finally {
      setLoading((prev) => ({ ...prev, configSave: false }));
    }
  }, [fetchConfig]);

  const disableIntegration = useCallback(async () => {
    setLoading((prev) => ({ ...prev, configSave: true }));

    try {
      await api.delete(SOLIDES_API.CONFIG);
      await fetchConfig();
      return { success: true };
    } catch (err) {
      console.error('Erro ao desabilitar integração:', err);
      return { success: false, error: 'Erro ao desabilitar' };
    } finally {
      setLoading((prev) => ({ ...prev, configSave: false }));
    }
  }, [fetchConfig]);

  const triggerFullSync = useCallback(async () => {
    setLoading((prev) => ({ ...prev, sync: true }));

    try {
      const response = await api.post<SyncTriggerResponse>(SOLIDES_API.SYNC_FULL);
      // Atualizar status após disparar
      setTimeout(() => {
        fetchStatus();
        fetchLogs();
      }, 2000);
      return response;
    } catch (err) {
      console.error('Erro ao disparar sync:', err);
      throw err;
    } finally {
      setLoading((prev) => ({ ...prev, sync: false }));
    }
  }, [fetchStatus, fetchLogs]);

  const triggerIncrementalSync = useCallback(async () => {
    setLoading((prev) => ({ ...prev, sync: true }));

    try {
      const response = await api.post<SyncTriggerResponse>(SOLIDES_API.SYNC_INCREMENTAL);
      setTimeout(() => {
        fetchStatus();
        fetchLogs();
      }, 2000);
      return response;
    } catch (err) {
      console.error('Erro ao disparar sync incremental:', err);
      throw err;
    } finally {
      setLoading((prev) => ({ ...prev, sync: false }));
    }
  }, [fetchStatus, fetchLogs]);

  const syncEntity = useCallback(
    async (entityType: EntityType, solidesId: string) => {
      try {
        const response = await api.post<SyncTriggerResponse>(
          SOLIDES_API.SYNC_ENTITY(entityType, solidesId)
        );
        return response;
      } catch (err) {
        console.error('Erro ao sincronizar entidade:', err);
        throw err;
      }
    },
    []
  );

  const resolveConflict = useCallback(
    async (conflictId: string, resolution: ConflictResolutionRequest) => {
      try {
        await api.post(SOLIDES_API.RESOLVE_CONFLICT(conflictId), resolution);
        await fetchConflicts();
        return { success: true };
      } catch (err) {
        console.error('Erro ao resolver conflito:', err);
        return { success: false };
      }
    },
    [fetchConflicts]
  );

  const ignoreConflict = useCallback(
    async (conflictId: string, notes?: string) => {
      try {
        await api.post(SOLIDES_API.IGNORE_CONFLICT(conflictId), { notes });
        await fetchConflicts();
        return { success: true };
      } catch (err) {
        console.error('Erro ao ignorar conflito:', err);
        return { success: false };
      }
    },
    [fetchConflicts]
  );

  // ==================== REFRESH ALL ====================

  const refreshAll = useCallback(async () => {
    await Promise.all([
      fetchConfig(),
      fetchStatus(),
      fetchHealth(),
      fetchLogs(20),
      fetchConflicts(),
    ]);
  }, [fetchConfig, fetchStatus, fetchHealth, fetchLogs, fetchConflicts]);

  // ==================== COMPUTED METRICS ====================

  const getMetrics = useCallback((): DashboardMetrics => {
    const entities = syncStatus?.entities || {} as Record<EntityType, EntitySyncStatus>;
    const colaboradores = entities.colaboradores as EntitySyncStatus | undefined;

    const totalEmployees = colaboradores?.total_count || 0;
    const syncedEmployees = colaboradores?.synced_count || 0;
    const pendingSync = colaboradores?.pending_count || 0;
    const errorCount = colaboradores?.error_count || 0;
    const syncPercentage =
      totalEmployees > 0 ? Math.round((syncedEmployees / totalEmployees) * 100) : 0;

    // Determinar status geral
    let overallStatus: IntegrationStatus = 'disconnected';

    if (config?.is_connected && syncStatus?.connected) {
      if (health?.healthy) {
        if (errorCount > 0 || conflicts.length > 0) {
          overallStatus = 'warning';
        } else {
          overallStatus = 'healthy';
        }
      } else {
        overallStatus = 'error';
      }
    }

    // Formatar última sincronização
    let lastSyncFormatted = 'Nunca';
    const lastSync =
      syncStatus?.last_incremental_sync_at || syncStatus?.last_full_sync_at;
    if (lastSync) {
      const date = new Date(lastSync);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffMinutes = Math.floor(diffMs / 60000);

      if (diffMinutes < 1) {
        lastSyncFormatted = 'Agora mesmo';
      } else if (diffMinutes < 60) {
        lastSyncFormatted = `${diffMinutes} min atrás`;
      } else if (diffMinutes < 1440) {
        const hours = Math.floor(diffMinutes / 60);
        lastSyncFormatted = `${hours}h atrás`;
      } else {
        lastSyncFormatted = date.toLocaleDateString('pt-BR', {
          day: '2-digit',
          month: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
        });
      }
    }

    return {
      totalEmployees,
      syncedEmployees,
      pendingSync,
      errorCount,
      syncPercentage,
      overallStatus,
      lastSyncFormatted,
      pendingConflicts: syncStatus?.pending_conflicts || 0,
    };
  }, [config, syncStatus, health, conflicts]);

  // ==================== EFFECTS ====================

  // Initial load
  useEffect(() => {
    mountedRef.current = true;
    refreshAll();

    return () => {
      mountedRef.current = false;
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
    };
  }, [refreshAll]);

  // Polling para atualização automática (a cada 30 segundos)
  useEffect(() => {
    if (config?.is_enabled && config?.is_connected) {
      pollingRef.current = setInterval(() => {
        fetchStatus();
        fetchHealth();
      }, 30000);

      return () => {
        if (pollingRef.current) {
          clearInterval(pollingRef.current);
        }
      };
    }
  }, [config?.is_enabled, config?.is_connected, fetchStatus, fetchHealth]);

  // ==================== RETURN ====================

  return {
    // State
    config,
    syncStatus,
    health,
    logs,
    conflicts,
    loading,
    error,

    // Computed
    metrics: getMetrics(),
    isConnected: config?.is_connected && syncStatus?.connected,
    isEnabled: config?.is_enabled,

    // Actions
    fetchConfig,
    fetchStatus,
    fetchHealth,
    fetchLogs,
    fetchConflicts,
    saveConfig,
    disableIntegration,
    triggerFullSync,
    triggerIncrementalSync,
    syncEntity,
    resolveConflict,
    ignoreConflict,
    refreshAll,
  };
}

export default useSolidesIntegration;
