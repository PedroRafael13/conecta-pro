/**
 * React Query Hooks - Sync Operations
 *
 * Hooks para sincronização offline-online, status de sync
 * e resolução de conflitos.
 *
 * @module hooks/mobile/useSync
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  syncData,
  getSyncStatus,
  resolveSyncConflict,
} from '@/services/mobile/syncService';
import type { MobileSyncRequest } from '@/types/generated/mobile/conectaPROMobileAPI.schemas';

/**
 * Hook para sincronizar dados offline com servidor.
 *
 * @example
 * ```tsx
 * const { mutate: sync, isPending } = useSyncData();
 *
 * const handleSync = () => {
 *   sync({
 *     operations: pendingOps,
 *     last_sync_token: lastToken,
 *   });
 * };
 * ```
 */
export function useSyncData() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: syncData,
    onSuccess: (data) => {
      // Invalidar queries relacionadas
      queryClient.invalidateQueries({ queryKey: ['sync', 'status'] });

      // Se houver mudanças do servidor, invalidar dados afetados
      if (data.server_changes && data.server_changes.length > 0) {
        queryClient.invalidateQueries({ queryKey: ['offline-data'] });
      }
    },
  });
}

/**
 * Hook para obter status de sincronização.
 *
 * @param options - Opções do useQuery
 *
 * @example
 * ```tsx
 * const { data: status, isLoading } = useSyncStatus({
 *   refetchInterval: 30000, // Refetch a cada 30s
 * });
 *
 * console.log('Pending ops:', status?.pending_operations);
 * ```
 */
export function useSyncStatus(options?: {
  refetchInterval?: number;
  enabled?: boolean;
}) {
  return useQuery({
    queryKey: ['sync', 'status'],
    queryFn: getSyncStatus,
    refetchInterval: options?.refetchInterval,
    enabled: options?.enabled,
  });
}

/**
 * Hook para resolver conflito de sincronização.
 *
 * @example
 * ```tsx
 * const { mutate: resolve } = useResolveSyncConflict();
 *
 * const handleResolve = (conflictId: string) => {
 *   resolve({
 *     conflictId,
 *     resolution: 'use_client',
 *   });
 * };
 * ```
 */
export function useResolveSyncConflict() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      conflictId,
      resolution,
      mergedData,
    }: {
      conflictId: string;
      resolution: 'use_client' | 'use_server' | 'merge';
      mergedData?: Record<string, unknown>;
    }) => resolveSyncConflict(conflictId, resolution, mergedData),
    onSuccess: () => {
      // Invalidar status após resolver conflito
      queryClient.invalidateQueries({ queryKey: ['sync', 'status'] });
    },
  });
}

/**
 * Hook combinado para auto-sync.
 *
 * Sincroniza automaticamente em intervalo definido se houver
 * operações pendentes.
 *
 * @param interval - Intervalo em ms (padrão: 5 minutos)
 *
 * @example
 * ```tsx
 * const {
 *   sync,
 *   status,
 *   isAutoSyncEnabled,
 *   setAutoSyncEnabled
 * } = useAutoSync(300000);
 * ```
 */
export function useAutoSync(interval: number = 300000) {
  const { data: status } = useSyncStatus({
    refetchInterval: interval,
  });

  const { mutate: sync, isPending } = useSyncData();

  // Auto-sync se houver operações pendentes
  const shouldAutoSync =
    status?.pending_operations && status.pending_operations > 0;

  return {
    sync,
    status,
    isPending,
    shouldAutoSync,
    pendingCount: status?.pending_operations || 0,
    conflictsCount: status?.conflicts_count || 0,
  };
}
