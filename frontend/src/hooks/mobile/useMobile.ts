/**
 * React Query Hooks - Mobile Core
 *
 * Hooks para funcionalidades core do módulo mobile:
 * health, config, dashboard, offline data e batch operations.
 *
 * @module hooks/mobile/useMobile
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  healthCheck,
  getMobileConfig,
  getMobileDashboard,
  getOfflineData,
  executeBatch,
  requiresUpdate,
  isMaintenanceMode,
  isFeatureEnabled,
  createBatchRequest,
} from '@/services/mobile/mobileService';
import type { BatchRequest } from '@/types/generated/mobile/conectaPROMobileAPI.schemas';

/**
 * Hook para health check do serviço mobile.
 *
 * @example
 * ```tsx
 * const { data: health } = useMobileHealth();
 *
 * if (health?.status === 'healthy') {
 *   // Serviço OK
 * }
 * ```
 */
export function useMobileHealth(options?: { refetchInterval?: number }) {
  return useQuery({
    queryKey: ['mobile', 'health'],
    queryFn: healthCheck,
    refetchInterval: options?.refetchInterval || 60000, // 1 minuto
  });
}

/**
 * Hook para configuração do app mobile.
 *
 * @example
 * ```tsx
 * const { data: config } = useMobileConfig();
 *
 * if (config?.force_update) {
 *   // Mostrar modal de atualização obrigatória
 * }
 * ```
 */
export function useMobileConfig() {
  return useQuery({
    queryKey: ['mobile', 'config'],
    queryFn: getMobileConfig,
    staleTime: 300000, // 5 minutos
  });
}

/**
 * Hook para dashboard mobile.
 *
 * @example
 * ```tsx
 * const { data: dashboard, isLoading } = useMobileDashboard();
 *
 * return (
 *   <div>
 *     <Summary data={dashboard?.summary} />
 *     <QuickActions actions={dashboard?.quick_actions} />
 *   </div>
 * );
 * ```
 */
export function useMobileDashboard() {
  return useQuery({
    queryKey: ['mobile', 'dashboard'],
    queryFn: getMobileDashboard,
    refetchInterval: 30000, // 30 segundos
  });
}

/**
 * Hook para dados offline.
 *
 * @param modules - Módulos a sincronizar (ex: 'leads,tasks')
 *
 * @example
 * ```tsx
 * const { data: offlineData } = useOfflineData('leads,tasks,contacts');
 *
 * // Armazenar em IndexedDB/SQLite
 * saveOfflineData(offlineData);
 * ```
 */
export function useOfflineData(modules?: string) {
  return useQuery({
    queryKey: ['mobile', 'offline-data', modules],
    queryFn: () => getOfflineData(modules),
    staleTime: 600000, // 10 minutos
  });
}

/**
 * Hook para executar batch operations.
 *
 * @example
 * ```tsx
 * const { mutate: executeBatchOps } = useBatchOperations();
 *
 * const batchRequest = createBatchRequest([
 *   { id: '1', method: 'GET', endpoint: '/api/v1/leads' },
 *   { id: '2', method: 'GET', endpoint: '/api/v1/tasks' },
 * ]);
 *
 * executeBatchOps(batchRequest);
 * ```
 */
export function useBatchOperations() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: executeBatch,
    onSuccess: () => {
      // Invalidar queries relacionadas baseado nos endpoints do batch
      queryClient.invalidateQueries({ queryKey: ['mobile'] });
    },
  });
}

/**
 * Hook para verificar se app requer atualização.
 *
 * @param currentVersion - Versão atual do app
 *
 * @example
 * ```tsx
 * const needsUpdate = useRequiresUpdate('1.0.0');
 *
 * if (needsUpdate) {
 *   showUpdateModal();
 * }
 * ```
 */
export function useRequiresUpdate(currentVersion: string) {
  const { data } = useQuery({
    queryKey: ['mobile', 'requires-update', currentVersion],
    queryFn: () => requiresUpdate(currentVersion),
  });

  return data || false;
}

/**
 * Hook para verificar modo manutenção.
 *
 * @example
 * ```tsx
 * const inMaintenance = useMaintenanceMode();
 *
 * if (inMaintenance) {
 *   return <MaintenancePage />;
 * }
 * ```
 */
export function useMaintenanceMode() {
  const { data } = useQuery({
    queryKey: ['mobile', 'maintenance'],
    queryFn: isMaintenanceMode,
    refetchInterval: 60000, // 1 minuto
  });

  return data || false;
}

/**
 * Hook para verificar feature flag.
 *
 * @param featureId - ID da feature
 *
 * @example
 * ```tsx
 * const canUseBiometric = useFeatureFlag('biometric_auth');
 *
 * if (canUseBiometric) {
 *   return <BiometricLogin />;
 * }
 * ```
 */
export function useFeatureFlag(featureId: string) {
  const { data } = useQuery({
    queryKey: ['mobile', 'feature', featureId],
    queryFn: () => isFeatureEnabled(featureId),
    staleTime: 300000, // 5 minutos
  });

  return data || false;
}

/**
 * Hook combinado para app initialization.
 *
 * Retorna todas as informações necessárias para inicializar o app.
 *
 * @example
 * ```tsx
 * const {
 *   config,
 *   health,
 *   needsUpdate,
 *   inMaintenance,
 *   isReady
 * } = useMobileAppInit('1.0.0');
 *
 * if (!isReady) return <LoadingScreen />;
 * if (inMaintenance) return <MaintenancePage />;
 * if (needsUpdate) return <UpdatePrompt />;
 * ```
 */
export function useMobileAppInit(currentVersion: string) {
  const { data: config, isLoading: loadingConfig } = useMobileConfig();
  const { data: health, isLoading: loadingHealth } = useMobileHealth();
  const needsUpdate = useRequiresUpdate(currentVersion);
  const inMaintenance = useMaintenanceMode();

  return {
    config,
    health,
    needsUpdate,
    inMaintenance,
    isReady: !loadingConfig && !loadingHealth,
    isHealthy: health?.status === 'healthy',
  };
}
