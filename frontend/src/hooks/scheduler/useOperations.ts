/**
 * Hooks React Query - Scheduler Operations
 *
 * Operações administrativas
 * - Executar ciclo manual
 *
 * Sprint 35 - Task Scheduler
 * Uso restrito: ADMIN/SYSTEM apenas
 */

import { useMutation, useQueryClient, UseMutationResult } from '@tanstack/react-query';
import { runSchedulerCycle, type RunCycleResponse } from '@/services/scheduler/operations.service';
import { taskKeys } from './useTasks';
import { executionKeys } from './useExecutions';

// ==================== Mutations ====================

/**
 * Executa ciclo do scheduler manualmente
 * Requer permissões admin/system
 */
export function useRunSchedulerCycle(): UseMutationResult<RunCycleResponse, Error, void> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: runSchedulerCycle,
    onSuccess: () => {
      // Invalida todas as queries relacionadas
      queryClient.invalidateQueries({ queryKey: taskKeys.all });
      queryClient.invalidateQueries({ queryKey: executionKeys.all });
    },
  });
}
