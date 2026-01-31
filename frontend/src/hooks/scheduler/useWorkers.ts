/**
 * Hooks React Query - Task Workers
 *
 * Monitoramento de workers de processamento
 * - Listar workers ativos
 * - Status e utilização
 * - Estatísticas
 *
 * Sprint 35 - Task Scheduler
 */

import { useQuery, UseQueryResult } from '@tanstack/react-query';
import {
  listWorkers,
  getWorker,
  getWorkerStats,
  type ListWorkersParams,
} from '@/services/scheduler/workers.service';
import type {
  WorkerResponse,
  WorkerStatsResponse,
} from '@/types/generated/scheduler/models';

// Query Keys
export const workerKeys = {
  all: ['scheduler', 'workers'] as const,
  lists: () => [...workerKeys.all, 'list'] as const,
  list: (params?: ListWorkersParams) => [...workerKeys.lists(), params] as const,
  details: () => [...workerKeys.all, 'detail'] as const,
  detail: (id: string) => [...workerKeys.details(), id] as const,
  stats: () => [...workerKeys.all, 'stats'] as const,
};

// ==================== Queries ====================

/**
 * Lista workers registrados
 */
export function useWorkers(
  params?: ListWorkersParams
): UseQueryResult<WorkerResponse[], Error> {
  return useQuery({
    queryKey: workerKeys.list(params),
    queryFn: () => listWorkers(params),
    staleTime: 30000, // 30s
    refetchInterval: 60000, // Auto-refresh 1min
  });
}

/**
 * Busca worker por ID
 */
export function useWorker(workerId: string): UseQueryResult<WorkerResponse, Error> {
  return useQuery({
    queryKey: workerKeys.detail(workerId),
    queryFn: () => getWorker(workerId),
    enabled: !!workerId,
    staleTime: 30000, // 30s
    refetchInterval: 60000, // Auto-refresh 1min
  });
}

/**
 * Estatísticas consolidadas de workers
 */
export function useWorkerStats(): UseQueryResult<WorkerStatsResponse, Error> {
  return useQuery({
    queryKey: workerKeys.stats(),
    queryFn: () => getWorkerStats(),
    staleTime: 60000, // 1min
    refetchInterval: 120000, // Auto-refresh 2min
  });
}
