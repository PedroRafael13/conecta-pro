/**
 * Hooks React Query - ComplianceCheck
 *
 * Gerencia verificações de compliance
 * - Queries: listagem, detalhes
 * - Mutations: criação, execução, finalização
 * - Workflow: pending → in_progress → completed
 */

import { useQuery, useMutation, useQueryClient, UseQueryResult, UseMutationResult } from '@tanstack/react-query';
import { complianceCheckService, type ComplianceCheckFilters } from '@/services/audit/complianceCheckService';
import type {
  ComplianceCheckCreate,
  ComplianceCheckResponse,
  ComplianceCheckList,
} from '@/types/generated/audit/models';

// Query Keys
export const complianceCheckKeys = {
  all: ['audit', 'compliance-checks'] as const,
  lists: () => [...complianceCheckKeys.all, 'list'] as const,
  list: (filters?: ComplianceCheckFilters) => [...complianceCheckKeys.lists(), filters] as const,
  details: () => [...complianceCheckKeys.all, 'detail'] as const,
  detail: (id: string) => [...complianceCheckKeys.details(), id] as const,
};

/**
 * Lista verificações de compliance
 */
export function useComplianceChecks(
  filters?: ComplianceCheckFilters
): UseQueryResult<ComplianceCheckList, Error> {
  return useQuery({
    queryKey: complianceCheckKeys.list(filters),
    queryFn: () => complianceCheckService.list(filters),
    staleTime: 30000, // 30s
  });
}

/**
 * Busca verificação específica por ID
 */
export function useComplianceCheck(checkId: string): UseQueryResult<ComplianceCheckResponse, Error> {
  return useQuery({
    queryKey: complianceCheckKeys.detail(checkId),
    queryFn: () => complianceCheckService.getById(checkId),
    enabled: !!checkId,
  });
}

/**
 * Cria nova verificação
 */
export function useCreateCheck(): UseMutationResult<
  ComplianceCheckResponse,
  Error,
  ComplianceCheckCreate
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ComplianceCheckCreate) => complianceCheckService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: complianceCheckKeys.lists() });
    },
  });
}

/**
 * Inicia execução de verificação
 */
export function useStartCheck(): UseMutationResult<ComplianceCheckResponse, Error, string> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (checkId: string) => complianceCheckService.start(checkId),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: complianceCheckKeys.detail(data.id) });
      queryClient.invalidateQueries({ queryKey: complianceCheckKeys.lists() });
    },
  });
}

/**
 * Completa verificação como conforme
 */
export function useCompleteCheckCompliant(): UseMutationResult<
  ComplianceCheckResponse,
  Error,
  { checkId: string; evidence?: Record<string, unknown>; notes?: string }
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ checkId, evidence, notes }) =>
      complianceCheckService.completeCompliant(checkId, evidence, notes),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: complianceCheckKeys.detail(data.id) });
      queryClient.invalidateQueries({ queryKey: complianceCheckKeys.lists() });
    },
  });
}

/**
 * Completa verificação como não conforme
 */
export function useCompleteCheckNonCompliant(): UseMutationResult<
  ComplianceCheckResponse,
  Error,
  { checkId: string; violations: Array<Record<string, unknown>>; remediationDeadlineDays?: number }
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ checkId, violations, remediationDeadlineDays }) =>
      complianceCheckService.completeNonCompliant(checkId, violations, remediationDeadlineDays),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: complianceCheckKeys.detail(data.id) });
      queryClient.invalidateQueries({ queryKey: complianceCheckKeys.lists() });
    },
  });
}
