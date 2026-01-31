/**
 * Hooks React Query - Task Executions
 *
 * Histórico e controle de execuções
 * - Listar execuções
 * - Logs detalhados
 * - Cancelamento
 *
 * Sprint 35 - Task Scheduler
 */

import { useQuery, useMutation, useQueryClient, UseQueryResult, UseMutationResult } from '@tanstack/react-query';
import {
  listExecutions,
  getExecution,
  getExecutionLogs,
  cancelExecution,
  type ListExecutionsParams,
  type GetExecutionLogsParams,
} from '@/services/scheduler/executions.service';
import type {
  ExecutionResponse,
  ExecutionLogResponse,
} from '@/types/generated/scheduler/models';

// Query Keys
export const executionKeys = {
  all: ['scheduler', 'executions'] as const,
  lists: () => [...executionKeys.all, 'list'] as const,
  list: (params?: ListExecutionsParams) => [...executionKeys.lists(), params] as const,
  details: () => [...executionKeys.all, 'detail'] as const,
  detail: (id: string) => [...executionKeys.details(), id] as const,
  logs: (id: string, params?: GetExecutionLogsParams) =>
    [...executionKeys.detail(id), 'logs', params] as const,
};

// ==================== Queries ====================

/**
 * Lista execuções com filtros
 */
export function useExecutions(
  params?: ListExecutionsParams
): UseQueryResult<ExecutionResponse[], Error> {
  return useQuery({
    queryKey: executionKeys.list(params),
    queryFn: () => listExecutions(params),
    staleTime: 30000, // 30s
    refetchInterval: 60000, // Auto-refresh 1min
  });
}

/**
 * Busca execução por ID
 */
export function useExecution(
  executionId: string
): UseQueryResult<ExecutionResponse, Error> {
  return useQuery({
    queryKey: executionKeys.detail(executionId),
    queryFn: () => getExecution(executionId),
    enabled: !!executionId,
    staleTime: 10000, // 10s
    refetchInterval: 30000, // Auto-refresh 30s
  });
}

/**
 * Lista logs de execução
 */
export function useExecutionLogs(
  executionId: string,
  params?: GetExecutionLogsParams
): UseQueryResult<ExecutionLogResponse[], Error> {
  return useQuery({
    queryKey: executionKeys.logs(executionId, params),
    queryFn: () => getExecutionLogs(executionId, params),
    enabled: !!executionId,
    staleTime: 5000, // 5s
  });
}

// ==================== Mutations ====================

/**
 * Cancela execução pendente
 */
export function useCancelExecution(): UseMutationResult<
  ExecutionResponse,
  Error,
  { executionId: string; reason?: string }
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ executionId, reason }) => cancelExecution(executionId, reason),
    onSuccess: (_, { executionId }) => {
      queryClient.invalidateQueries({ queryKey: executionKeys.lists() });
      queryClient.invalidateQueries({ queryKey: executionKeys.detail(executionId) });
    },
  });
}
