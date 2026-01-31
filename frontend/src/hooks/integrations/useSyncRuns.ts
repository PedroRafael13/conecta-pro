/**
 * Hook: useSyncRuns
 * Gerenciamento de execuções de sincronização
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { syncRunService } from '@/lib/api/services/integrations';
import type {
  SyncRunCreate,
  ListSyncRunsApiV1IntegrationsIntegrationsConnectorsSyncRunsGetParams,
} from '@/types/generated/integrations/conectaPROIntegrationsAPI.schemas';

const QUERY_KEY = 'integrations-sync-runs';

/**
 * Hook para listar execuções de sincronização
 */
export function useSyncRuns(
  params?: ListSyncRunsApiV1IntegrationsIntegrationsConnectorsSyncRunsGetParams
) {
  return useQuery({
    queryKey: [QUERY_KEY, 'list', params],
    queryFn: () => syncRunService.listSyncRuns(params),
  });
}

/**
 * Hook para obter execução por ID
 */
export function useSyncRun(syncRunId: string) {
  return useQuery({
    queryKey: [QUERY_KEY, 'detail', syncRunId],
    queryFn: () => syncRunService.getSyncRun(syncRunId),
    enabled: !!syncRunId,
  });
}

/**
 * Hook para iniciar sincronização
 */
export function useStartSync() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SyncRunCreate) => syncRunService.startSync(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}
