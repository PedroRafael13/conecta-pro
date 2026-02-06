/**
 * Hooks React Query - DataRetention
 *
 * Gerencia políticas de retenção de dados (LGPD)
 * - Queries: listagem, detalhes
 * - Mutations: CRUD, execução manual
 */

import { useQuery, useMutation, useQueryClient, UseQueryResult, UseMutationResult } from '@tanstack/react-query';
import { dataRetentionService, type DataRetentionFilters } from '@/services/audit/dataRetentionService';
import type {
  DataRetentionCreate,
  DataRetentionUpdate,
  DataRetentionResponse,
  DataRetentionList,
  DataRetentionExecution,
} from '@/types/generated/audit/models';

// Query Keys
export const dataRetentionKeys = {
  all: ['audit', 'data-retention'] as const,
  lists: () => [...dataRetentionKeys.all, 'list'] as const,
  list: (filters?: DataRetentionFilters) => [...dataRetentionKeys.lists(), filters] as const,
  details: () => [...dataRetentionKeys.all, 'detail'] as const,
  detail: (id: string) => [...dataRetentionKeys.details(), id] as const,
};

/**
 * Lista políticas de retenção
 */
export function useDataRetentionPolicies(
  filters?: DataRetentionFilters
): UseQueryResult<DataRetentionList, Error> {
  return useQuery({
    queryKey: dataRetentionKeys.list(filters),
    queryFn: () => dataRetentionService.list(filters),
    staleTime: 60000, // 1min
  });
}

/**
 * Busca política específica por ID
 */
export function useDataRetention(policyId: string): UseQueryResult<DataRetentionResponse, Error> {
  return useQuery({
    queryKey: dataRetentionKeys.detail(policyId),
    queryFn: () => dataRetentionService.getById(policyId),
    enabled: !!policyId,
  });
}

/**
 * Cria nova política de retenção
 */
export function useCreateRetention(): UseMutationResult<
  DataRetentionResponse,
  Error,
  DataRetentionCreate
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: DataRetentionCreate) => dataRetentionService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: dataRetentionKeys.lists() });
    },
  });
}

/**
 * Atualiza política de retenção
 */
export function useUpdateRetention(): UseMutationResult<
  DataRetentionResponse,
  Error,
  { policyId: string; data: DataRetentionUpdate }
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ policyId, data }) => dataRetentionService.update(policyId, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: dataRetentionKeys.detail(data.id) });
      queryClient.invalidateQueries({ queryKey: dataRetentionKeys.lists() });
    },
  });
}

/**
 * Executa política manualmente
 */
export function useExecuteRetention(): UseMutationResult<DataRetentionExecution, Error, string> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (policyId: string) => dataRetentionService.execute(policyId),
    onSuccess: (data, policyId) => {
      queryClient.invalidateQueries({ queryKey: dataRetentionKeys.detail(policyId) });
    },
  });
}

/**
 * Remove política de retenção
 */
export function useDeleteRetention(): UseMutationResult<void, Error, string> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (policyId: string) => dataRetentionService.delete(policyId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: dataRetentionKeys.lists() });
    },
  });
}
