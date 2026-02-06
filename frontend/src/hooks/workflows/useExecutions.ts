/**
 * Execution Hooks
 * React Query hooks para gestão de execuções de workflows
 */

import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseQueryOptions,
  type UseMutationOptions,
} from '@tanstack/react-query';
import { ExecutionService } from '@/services/workflows/executionService';
import type {
  ExecutionResponse,
  ExecutionStatus,
  ListExecutionsApiV1WorkflowsWorkflowIdExecutionsGetParams,
} from '@/types/generated/workflows/conectaPROWorkflowsAPI.schemas';
import { AxiosResponse } from 'axios';

const EXECUTION_KEYS = {
  all: ['executions'] as const,
  lists: () => [...EXECUTION_KEYS.all, 'list'] as const,
  list: (
    workflowId: string,
    params?: ListExecutionsApiV1WorkflowsWorkflowIdExecutionsGetParams
  ) => [...EXECUTION_KEYS.lists(), workflowId, params] as const,
  byWorkflow: (workflowId: string) =>
    [...EXECUTION_KEYS.all, 'by-workflow', workflowId] as const,
  byStatus: (workflowId: string, status: ExecutionStatus) =>
    [...EXECUTION_KEYS.all, 'by-status', workflowId, status] as const,
  running: (workflowId: string) =>
    [...EXECUTION_KEYS.all, 'running', workflowId] as const,
  recent: (workflowId: string) =>
    [...EXECUTION_KEYS.all, 'recent', workflowId] as const,
};

/**
 * Hook para listar execuções de um workflow
 */
export const useExecutionList = (
  workflowId: string,
  params?: ListExecutionsApiV1WorkflowsWorkflowIdExecutionsGetParams,
  options?: Omit<
    UseQueryOptions<AxiosResponse<ExecutionResponse[]>>,
    'queryKey' | 'queryFn'
  >
) => {
  return useQuery({
    queryKey: EXECUTION_KEYS.list(workflowId, params),
    queryFn: () => ExecutionService.listExecutions(workflowId, params),
    enabled: !!workflowId,
    ...options,
  });
};

/**
 * Hook para listar execuções por status
 */
export const useExecutionsByStatus = (
  workflowId: string,
  status: ExecutionStatus,
  options?: Omit<
    UseQueryOptions<AxiosResponse<ExecutionResponse[]>>,
    'queryKey' | 'queryFn'
  >
) => {
  return useQuery({
    queryKey: EXECUTION_KEYS.byStatus(workflowId, status),
    queryFn: () => ExecutionService.listExecutions(workflowId, { status }),
    enabled: !!workflowId,
    ...options,
  });
};

/**
 * Hook para listar execuções em andamento
 */
export const useRunningExecutions = (
  workflowId: string,
  options?: Omit<
    UseQueryOptions<AxiosResponse<ExecutionResponse[]>>,
    'queryKey' | 'queryFn'
  >
) => {
  return useQuery({
    queryKey: EXECUTION_KEYS.running(workflowId),
    queryFn: async () => {
      const response = await ExecutionService.listExecutions(workflowId);
      // Filtra apenas execuções em andamento
      const runningExecutions = response.data.filter((execution) =>
        ExecutionService.isExecutionRunning(execution)
      );
      return {
        ...response,
        data: runningExecutions,
      };
    },
    enabled: !!workflowId,
    refetchInterval: 5000, // Atualiza a cada 5 segundos
    ...options,
  });
};

/**
 * Hook para listar execuções recentes
 */
export const useRecentExecutions = (
  workflowId: string,
  limit = 10,
  options?: Omit<
    UseQueryOptions<AxiosResponse<ExecutionResponse[]>>,
    'queryKey' | 'queryFn'
  >
) => {
  return useQuery({
    queryKey: EXECUTION_KEYS.recent(workflowId),
    queryFn: () =>
      ExecutionService.listExecutions(workflowId, {
        skip: 0,
        limit,
      }),
    enabled: !!workflowId,
    ...options,
  });
};

/**
 * Hook para cancelar execução
 */
export const useCancelExecution = (
  options?: UseMutationOptions<AxiosResponse<unknown>, Error, string>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (executionId: string) =>
      ExecutionService.cancelExecution(executionId),
    onSuccess: () => {
      // Invalida todas as listas de execuções
      queryClient.invalidateQueries({ queryKey: EXECUTION_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: EXECUTION_KEYS.all });
    },
    ...options,
  });
};

/**
 * Hook para obter estatísticas de execuções
 */
export const useExecutionStats = (
  workflowId: string,
  options?: Omit<
    UseQueryOptions<
      {
        total: number;
        successful: number;
        failed: number;
        running: number;
        cancelled: number;
        successRate: number;
        failureRate: number;
        avgExecutionTime: number;
      },
      Error
    >,
    'queryKey' | 'queryFn'
  >
) => {
  return useQuery({
    queryKey: [...EXECUTION_KEYS.byWorkflow(workflowId), 'stats'],
    queryFn: async () => {
      const response = await ExecutionService.listExecutions(workflowId, {
        skip: 0,
        limit: 500, // Pegamos um limite grande para calcular stats
      });
      return ExecutionService.getExecutionStats(response.data);
    },
    enabled: !!workflowId,
    staleTime: 30000, // Cache por 30 segundos
    ...options,
  });
};

/**
 * Hook para monitorar execuções em tempo real
 * Útil para dashboards e monitoring
 */
export const useExecutionMonitoring = (
  workflowId: string,
  refreshInterval = 5000,
  options?: Omit<
    UseQueryOptions<AxiosResponse<ExecutionResponse[]>>,
    'queryKey' | 'queryFn'
  >
) => {
  return useQuery({
    queryKey: [...EXECUTION_KEYS.byWorkflow(workflowId), 'monitoring'],
    queryFn: () => ExecutionService.listExecutions(workflowId),
    enabled: !!workflowId,
    refetchInterval: refreshInterval,
    refetchIntervalInBackground: true,
    ...options,
  });
};
