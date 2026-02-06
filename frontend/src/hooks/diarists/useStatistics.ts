/**
 * Hook: useStatistics
 *
 * Estatísticas e rankings de diaristas.
 */

import { useQuery } from '@tanstack/react-query';
import { diaristCoreService } from '@/services/diarists';

/**
 * Hook para estatísticas gerais
 */
export function useGeneralStatistics(params?: {
  dataInicio?: string;
  dataFim?: string;
}) {
  return useQuery({
    queryKey: ['diarists', 'statistics', 'general', params],
    queryFn: () => diaristCoreService.getGeneralStatistics(params),
  });
}

/**
 * Hook para ranking de diaristas
 */
export function useTopDiarists(limit?: number) {
  return useQuery({
    queryKey: ['diarists', 'statistics', 'ranking', limit],
    queryFn: () => diaristCoreService.getTopDiarists(limit),
  });
}
