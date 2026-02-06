/**
 * Hook: useSyncQueue
 * Fila de sincronização
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { syncQueueService } from '@/lib/api/services/integrations';
import type {
  SyncQueueCreate,
  SyncQueueBatchCreate,
  ListSyncItemsApiV1IntegrationsSyncGetParams,
  CancelSyncItemApiV1IntegrationsSyncItemIdCancelPostParams,
} from '@/types/generated/integrations/conectaPROIntegrationsAPI.schemas';

const QUERY_KEY = 'integrations-sync-queue';

/**
 * Hook para listar itens da fila
 */
export function useSyncQueue(params?: ListSyncItemsApiV1IntegrationsSyncGetParams) {
  return useQuery({
    queryKey: [QUERY_KEY, 'list', params],
    queryFn: () => syncQueueService.listSyncItems(params),
  });
}

/**
 * Hook para obter item da fila por ID
 */
export function useSyncQueueItem(itemId: string) {
  return useQuery({
    queryKey: [QUERY_KEY, 'detail', itemId],
    queryFn: () => syncQueueService.getSyncItem(itemId),
    enabled: !!itemId,
  });
}

/**
 * Hook para obter estatísticas da fila
 */
export function useSyncQueueStats() {
  return useQuery({
    queryKey: [QUERY_KEY, 'stats'],
    queryFn: () => syncQueueService.getSyncStats(),
  });
}

/**
 * Hook para criar item na fila
 */
export function useCreateSyncItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SyncQueueCreate) => syncQueueService.createSyncItem(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}

/**
 * Hook para criar múltiplos itens na fila
 */
export function useCreateSyncBatch() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SyncQueueBatchCreate) => syncQueueService.createSyncBatch(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}

/**
 * Hook para cancelar item da fila
 */
export function useCancelSyncItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      itemId,
      params,
    }: {
      itemId: string;
      params: CancelSyncItemApiV1IntegrationsSyncItemIdCancelPostParams;
    }) => syncQueueService.cancelSyncItem(itemId, params),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}
