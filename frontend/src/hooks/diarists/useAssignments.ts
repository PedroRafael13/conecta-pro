/**
 * Hook: useAssignments
 *
 * Gerenciamento de alocações de diaristas.
 */

import { useQuery } from '@tanstack/react-query';
import { diaristCoreService } from '@/services/diarists';
import type { AssignmentStatus } from '@/api/diarists/generated/models';

/**
 * Hook para listar alocações
 */
export function useListAssignments(params?: {
  diaristId?: string;
  status?: AssignmentStatus;
  skip?: number;
  limit?: number;
}) {
  return useQuery({
    queryKey: ['diarists', 'assignments', 'list', params],
    queryFn: () => diaristCoreService.listAssignments(params),
  });
}

/**
 * Hook para buscar alocação por ID
 */
export function useAssignment(assignmentId: string) {
  return useQuery({
    queryKey: ['diarists', 'assignments', 'detail', assignmentId],
    queryFn: () => diaristCoreService.getAssignment(assignmentId),
    enabled: !!assignmentId,
  });
}
