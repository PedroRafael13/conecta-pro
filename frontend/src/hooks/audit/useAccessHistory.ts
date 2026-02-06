/**
 * Hooks React Query - AccessHistory
 *
 * Gerencia histórico de acessos e segurança
 * - Queries: listagem, detalhes, estatísticas, histórico por usuário
 * - Mutations: registro de acesso
 */

import { useQuery, useMutation, useQueryClient, UseQueryResult, UseMutationResult } from '@tanstack/react-query';
import { accessHistoryService, type AccessHistoryFilters } from '@/services/audit/accessHistoryService';
import type {
  AccessHistoryCreate,
  AccessHistoryResponse,
  AccessHistoryList,
  AccessHistoryStats,
} from '@/types/generated/audit/models';

// Query Keys
export const accessHistoryKeys = {
  all: ['audit', 'access-history'] as const,
  lists: () => [...accessHistoryKeys.all, 'list'] as const,
  list: (filters?: AccessHistoryFilters) => [...accessHistoryKeys.lists(), filters] as const,
  details: () => [...accessHistoryKeys.all, 'detail'] as const,
  detail: (id: string) => [...accessHistoryKeys.details(), id] as const,
  stats: (startDate?: string, endDate?: string) => [...accessHistoryKeys.all, 'stats', startDate, endDate] as const,
  userHistory: (userId: string, limit: number) => [...accessHistoryKeys.all, 'user', userId, limit] as const,
};

/**
 * Lista histórico de acessos
 */
export function useAccessHistory(
  filters?: AccessHistoryFilters
): UseQueryResult<AccessHistoryList, Error> {
  return useQuery({
    queryKey: accessHistoryKeys.list(filters),
    queryFn: () => accessHistoryService.list(filters),
    staleTime: 30000, // 30s
  });
}

/**
 * Busca acesso específico por ID
 */
export function useAccessHistoryItem(accessId: string): UseQueryResult<AccessHistoryResponse, Error> {
  return useQuery({
    queryKey: accessHistoryKeys.detail(accessId),
    queryFn: () => accessHistoryService.getById(accessId),
    enabled: !!accessId,
  });
}

/**
 * Obtém estatísticas de acessos
 */
export function useAccessStats(
  startDate?: string,
  endDate?: string
): UseQueryResult<AccessHistoryStats, Error> {
  return useQuery({
    queryKey: accessHistoryKeys.stats(startDate, endDate),
    queryFn: () => accessHistoryService.getStats(startDate, endDate),
    staleTime: 60000, // 1min
  });
}

/**
 * Busca histórico de um usuário específico
 */
export function useUserAccessHistory(
  userId: string,
  limit: number = 50
): UseQueryResult<AccessHistoryResponse[], Error> {
  return useQuery({
    queryKey: accessHistoryKeys.userHistory(userId, limit),
    queryFn: () => accessHistoryService.getUserHistory(userId, limit),
    enabled: !!userId,
    staleTime: 60000, // 1min
  });
}

/**
 * Registra novo acesso ao sistema
 */
export function useRecordAccess(): UseMutationResult<
  AccessHistoryResponse,
  Error,
  AccessHistoryCreate
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: AccessHistoryCreate) => accessHistoryService.record(data),
    onSuccess: () => {
      // Invalida listas e estatísticas
      queryClient.invalidateQueries({ queryKey: accessHistoryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: [...accessHistoryKeys.all, 'stats'] });
    },
  });
}
