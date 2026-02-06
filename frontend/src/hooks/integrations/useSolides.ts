/**
 * Hook: useSolides
 * Integração com Sólides DP
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { solidesService } from '@/lib/api/services/integrations';
import type {
  SolidesConfigRequest,
  SyncTriggerRequest,
  ConflictResolutionRequest,
  ListSolidesEmployeesApiV1IntegrationsSolidesEmployeesGetParams,
  GetSyncLogsApiV1IntegrationsSolidesLogsGetParams,
  ListConflictsApiV1IntegrationsSolidesConflictsGetParams,
  BodyIgnoreConflictApiV1IntegrationsSolidesConflictsConflictIdIgnorePost,
} from '@/types/generated/integrations/conectaPROIntegrationsAPI.schemas';

const QUERY_KEY = 'integrations-solides';

/**
 * Hook para listar colaboradores sincronizados
 */
export function useSolidesEmployees(
  params?: ListSolidesEmployeesApiV1IntegrationsSolidesEmployeesGetParams
) {
  return useQuery({
    queryKey: [QUERY_KEY, 'employees', params],
    queryFn: () => solidesService.listEmployees(params),
  });
}

/**
 * Hook para obter status da integração
 */
export function useSolidesStatus() {
  return useQuery({
    queryKey: [QUERY_KEY, 'status'],
    queryFn: () => solidesService.getIntegrationStatus(),
  });
}

/**
 * Hook para obter configuração
 */
export function useSolidesConfig() {
  return useQuery({
    queryKey: [QUERY_KEY, 'config'],
    queryFn: () => solidesService.getIntegrationConfig(),
  });
}

/**
 * Hook para obter status da sincronização (usa getIntegrationStatus)
 */
export function useSolidesSyncStatus() {
  return useQuery({
    queryKey: [QUERY_KEY, 'sync-status'],
    queryFn: () => solidesService.getIntegrationStatus(),
  });
}

/**
 * Hook para listar logs de sincronização
 */
export function useSolidesSyncLogs(params?: GetSyncLogsApiV1IntegrationsSolidesLogsGetParams) {
  return useQuery({
    queryKey: [QUERY_KEY, 'sync-logs', params],
    queryFn: () => solidesService.getSyncLogs(params),
  });
}

/**
 * Hook para obter detalhes de um log
 */
export function useSolidesSyncLogDetail(logId: string) {
  return useQuery({
    queryKey: [QUERY_KEY, 'sync-log-detail', logId],
    queryFn: () => solidesService.getSyncLogDetail(logId),
    enabled: !!logId,
  });
}

/**
 * Hook para listar conflitos
 */
export function useSolidesConflicts(params?: ListConflictsApiV1IntegrationsSolidesConflictsGetParams) {
  return useQuery({
    queryKey: [QUERY_KEY, 'conflicts', params],
    queryFn: () => solidesService.listConflicts(params),
  });
}

/**
 * Hook para obter detalhes de um conflito
 * NOTA: Função getConflictDetail foi removida do service
 * Use listConflicts com filtro para obter conflito específico
 */
export function useSolidesConflictDetail(conflictId: string) {
  return useQuery({
    queryKey: [QUERY_KEY, 'conflict-detail', conflictId],
    queryFn: async () => {
      // Buscar conflito específico via lista
      const conflicts = await solidesService.listConflicts();
      return conflicts.find((c: any) => c.id === conflictId);
    },
    enabled: !!conflictId,
  });
}

/**
 * Hook para configurar integração
 */
export function useConfigureSolides() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SolidesConfigRequest) => solidesService.configureIntegration(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}

/**
 * Hook para desabilitar integração
 */
export function useDisableSolides() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => solidesService.disableIntegration(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}

/**
 * Hook para testar conexão
 * NOTA: Função testConnection foi removida do service
 * Use configureIntegration para testar credenciais
 */
export function useTestSolidesConnection() {
  return useMutation({
    mutationFn: async (config: any) => {
      // Usar configureIntegration para validar credenciais
      return solidesService.configureIntegration(config);
    },
  });
}

/**
 * Hook para disparar sincronização
 */
export function useTriggerSolidesSync() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SyncTriggerRequest) => solidesService.triggerSync(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}

/**
 * Hook para resolver conflito
 */
export function useResolveSolidesConflict() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ conflictId, data }: { conflictId: string; data: ConflictResolutionRequest }) =>
      solidesService.resolveConflict(conflictId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}

/**
 * Hook para ignorar conflito
 */
export function useIgnoreSolidesConflict() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      conflictId,
      data,
    }: {
      conflictId: string;
      data: BodyIgnoreConflictApiV1IntegrationsSolidesConflictsConflictIdIgnorePost;
    }) => solidesService.ignoreConflict(conflictId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}
