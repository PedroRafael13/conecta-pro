/**
 * Hook: useEvaluations
 *
 * Gerenciamento de avaliações de diaristas.
 */

import { useQuery } from '@tanstack/react-query';
import { diaristCoreService } from '@/services/diarists';

/**
 * Hook para listar avaliações
 */
export function useListEvaluations(params?: {
  diaristId?: string;
  notaMinima?: number;
  skip?: number;
  limit?: number;
}) {
  return useQuery({
    queryKey: ['diarists', 'evaluations', 'list', params],
    queryFn: () => diaristCoreService.listEvaluations(params),
  });
}

/**
 * Hook para buscar avaliação por ID
 */
export function useEvaluation(evaluationId: string) {
  return useQuery({
    queryKey: ['diarists', 'evaluations', 'detail', evaluationId],
    queryFn: () => diaristCoreService.getEvaluation(evaluationId),
    enabled: !!evaluationId,
  });
}
