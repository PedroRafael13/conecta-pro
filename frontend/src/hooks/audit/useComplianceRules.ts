/**
 * Hooks React Query - ComplianceRule
 *
 * Gerencia estado de regras de compliance
 * - Queries: listagem por framework, detalhes
 * - Mutations: CRUD completo, ativação
 */

import { useQuery, useMutation, useQueryClient, UseQueryResult, UseMutationResult } from '@tanstack/react-query';
import { complianceRuleService, type ComplianceRuleFilters } from '@/services/audit/complianceRuleService';
import type {
  ComplianceRuleCreate,
  ComplianceRuleUpdate,
  ComplianceRuleResponse,
  ComplianceRuleList,
} from '@/types/generated/audit/models';

// Query Keys
export const complianceRuleKeys = {
  all: ['audit', 'compliance-rules'] as const,
  lists: () => [...complianceRuleKeys.all, 'list'] as const,
  list: (filters?: ComplianceRuleFilters) => [...complianceRuleKeys.lists(), filters] as const,
  details: () => [...complianceRuleKeys.all, 'detail'] as const,
  detail: (id: string) => [...complianceRuleKeys.details(), id] as const,
};

/**
 * Lista regras de compliance com filtros
 */
export function useComplianceRules(
  filters?: ComplianceRuleFilters
): UseQueryResult<ComplianceRuleList, Error> {
  return useQuery({
    queryKey: complianceRuleKeys.list(filters),
    queryFn: () => complianceRuleService.list(filters),
    staleTime: 60000, // 1min
  });
}

/**
 * Busca regra específica por ID
 */
export function useComplianceRule(ruleId: string): UseQueryResult<ComplianceRuleResponse, Error> {
  return useQuery({
    queryKey: complianceRuleKeys.detail(ruleId),
    queryFn: () => complianceRuleService.getById(ruleId),
    enabled: !!ruleId,
  });
}

/**
 * Cria nova regra de compliance
 */
export function useCreateComplianceRule(): UseMutationResult<
  ComplianceRuleResponse,
  Error,
  ComplianceRuleCreate
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ComplianceRuleCreate) => complianceRuleService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: complianceRuleKeys.lists() });
    },
  });
}

/**
 * Atualiza regra de compliance
 */
export function useUpdateComplianceRule(): UseMutationResult<
  ComplianceRuleResponse,
  Error,
  { ruleId: string; data: ComplianceRuleUpdate }
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ ruleId, data }) => complianceRuleService.update(ruleId, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: complianceRuleKeys.detail(data.id) });
      queryClient.invalidateQueries({ queryKey: complianceRuleKeys.lists() });
    },
  });
}

/**
 * Ativa regra de compliance
 */
export function useActivateRule(): UseMutationResult<ComplianceRuleResponse, Error, string> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (ruleId: string) => complianceRuleService.activate(ruleId),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: complianceRuleKeys.detail(data.id) });
      queryClient.invalidateQueries({ queryKey: complianceRuleKeys.lists() });
    },
  });
}

/**
 * Remove regra de compliance
 */
export function useDeleteRule(): UseMutationResult<void, Error, string> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (ruleId: string) => complianceRuleService.delete(ruleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: complianceRuleKeys.lists() });
    },
  });
}
