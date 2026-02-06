/**
 * Hooks React Query - Distributed Locks
 *
 * Gerenciamento de locks distribuídos
 * - Adquirir/Liberar locks
 * - Renovar TTL
 * - Listar locks ativos
 *
 * Sprint 35 - Task Scheduler
 */

import { useQuery, useMutation, useQueryClient, UseQueryResult, UseMutationResult } from '@tanstack/react-query';
import {
  acquireLock,
  releaseLock,
  renewLock,
  listLocks,
} from '@/services/scheduler/locks.service';
import type {
  LockCreate,
  LockResponse,
} from '@/types/generated/scheduler/models';

// Query Keys
export const lockKeys = {
  all: ['scheduler', 'locks'] as const,
  lists: () => [...lockKeys.all, 'list'] as const,
};

// ==================== Queries ====================

/**
 * Lista locks ativos do tenant
 */
export function useLocks(): UseQueryResult<LockResponse[], Error> {
  return useQuery({
    queryKey: lockKeys.lists(),
    queryFn: listLocks,
    staleTime: 30000, // 30s
    refetchInterval: 60000, // Auto-refresh 1min
  });
}

// ==================== Mutations ====================

/**
 * Adquire lock distribuído
 */
export function useAcquireLock(): UseMutationResult<LockResponse, Error, LockCreate> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: acquireLock,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: lockKeys.lists() });
    },
  });
}

/**
 * Libera lock
 */
export function useReleaseLock(): UseMutationResult<void, Error, string> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: releaseLock,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: lockKeys.lists() });
    },
  });
}

/**
 * Renova TTL de lock
 */
export function useRenewLock(): UseMutationResult<
  LockResponse,
  Error,
  { lockKey: string; ttlSeconds?: number }
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ lockKey, ttlSeconds }) => renewLock(lockKey, ttlSeconds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: lockKeys.lists() });
    },
  });
}
