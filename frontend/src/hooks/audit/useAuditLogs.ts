/**
 * Hooks React Query - AuditLog
 *
 * Gerencia estado e cache de logs de auditoria
 * - Queries: listagem, detalhes, estatísticas
 * - Mutations: criação, revisão
 * - Invalidação inteligente de cache
 */

import { useQuery, useMutation, useQueryClient, UseQueryResult, UseMutationResult } from '@tanstack/react-query';
import { auditLogService, type AuditLogFilters } from '@/services/audit/auditLogService';
import type {
  AuditLogCreate,
  AuditLogResponse,
  AuditLogList,
  AuditLogStats,
} from '@/types/generated/audit/models';

// Query Keys
export const auditLogKeys = {
  all: ['audit', 'logs'] as const,
  lists: () => [...auditLogKeys.all, 'list'] as const,
  list: (filters?: AuditLogFilters) => [...auditLogKeys.lists(), filters] as const,
  details: () => [...auditLogKeys.all, 'detail'] as const,
  detail: (id: string) => [...auditLogKeys.details(), id] as const,
  stats: (startDate?: string, endDate?: string) => [...auditLogKeys.all, 'stats', startDate, endDate] as const,
};

/**
 * Lista logs de auditoria com filtros
 */
export function useAuditLogs(filters?: AuditLogFilters): UseQueryResult<AuditLogList, Error> {
  return useQuery({
    queryKey: auditLogKeys.list(filters),
    queryFn: () => auditLogService.listLogs(filters),
    staleTime: 30000, // 30s
  });
}

/**
 * Busca log específico por ID
 */
export function useAuditLog(logId: string): UseQueryResult<AuditLogResponse, Error> {
  return useQuery({
    queryKey: auditLogKeys.detail(logId),
    queryFn: () => auditLogService.getLog(logId),
    enabled: !!logId,
  });
}

/**
 * Obtém estatísticas de auditoria
 */
export function useAuditStats(
  startDate?: string,
  endDate?: string
): UseQueryResult<AuditLogStats, Error> {
  return useQuery({
    queryKey: auditLogKeys.stats(startDate, endDate),
    queryFn: () => auditLogService.getStats(startDate, endDate),
    staleTime: 60000, // 1min
  });
}

/**
 * Cria novo log de auditoria
 */
export function useCreateAuditLog(): UseMutationResult<AuditLogResponse, Error, AuditLogCreate> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: AuditLogCreate) => auditLogService.createLog(data),
    onSuccess: () => {
      // Invalida listas e estatísticas
      queryClient.invalidateQueries({ queryKey: auditLogKeys.lists() });
      queryClient.invalidateQueries({ queryKey: [...auditLogKeys.all, 'stats'] });
    },
  });
}

/**
 * Completa revisão de log
 */
export function useCompleteReview(): UseMutationResult<
  AuditLogResponse,
  Error,
  { logId: string; notes?: string }
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ logId, notes }) => auditLogService.completeReview(logId, notes),
    onSuccess: (data) => {
      // Invalida cache do log específico
      queryClient.invalidateQueries({ queryKey: auditLogKeys.detail(data.id) });
      // Invalida listas (log pode mudar posição/filtros)
      queryClient.invalidateQueries({ queryKey: auditLogKeys.lists() });
    },
  });
}
