/**
 * Hooks React Query - Task Queue
 *
 * Gerenciamento de filas de execução
 * - Adicionar itens
 * - Listar pendentes
 * - Estatísticas
 *
 * Sprint 35 - Task Scheduler
 */

import { useQuery, useMutation, useQueryClient, UseQueryResult, UseMutationResult } from '@tanstack/react-query';
import {
  enqueueItem,
  listQueueItems,
  deleteQueueItem,
  getQueueStats,
  type ListQueueItemsParams,
} from '@/services/scheduler/queue.service';
import type {
  QueueItemCreate,
  QueueItemResponse,
  QueueStatsResponse,
} from '@/types/generated/scheduler/models';

// Query Keys
export const queueKeys = {
  all: ['scheduler', 'queue'] as const,
  lists: () => [...queueKeys.all, 'list'] as const,
  list: (params?: ListQueueItemsParams) => [...queueKeys.lists(), params] as const,
  stats: (queueName?: string) => [...queueKeys.all, 'stats', queueName] as const,
};

// ==================== Queries ====================

/**
 * Lista itens da fila
 */
export function useQueueItems(
  params?: ListQueueItemsParams
): UseQueryResult<QueueItemResponse[], Error> {
  return useQuery({
    queryKey: queueKeys.list(params),
    queryFn: () => listQueueItems(params),
    staleTime: 10000, // 10s
    refetchInterval: 30000, // Auto-refresh 30s
  });
}

/**
 * Estatísticas da fila
 */
export function useQueueStats(
  queueName: string = 'default'
): UseQueryResult<QueueStatsResponse, Error> {
  return useQuery({
    queryKey: queueKeys.stats(queueName),
    queryFn: () => getQueueStats(queueName),
    staleTime: 30000, // 30s
    refetchInterval: 60000, // Auto-refresh 1min
  });
}

// ==================== Mutations ====================

/**
 * Adiciona item à fila
 */
export function useEnqueueItem(): UseMutationResult<
  QueueItemResponse,
  Error,
  QueueItemCreate
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: enqueueItem,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queueKeys.lists() });
      queryClient.invalidateQueries({ queryKey: queueKeys.all });
    },
  });
}

/**
 * Remove item da fila
 */
export function useDeleteQueueItem(): UseMutationResult<void, Error, string> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteQueueItem,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queueKeys.lists() });
      queryClient.invalidateQueries({ queryKey: queueKeys.all });
    },
  });
}
