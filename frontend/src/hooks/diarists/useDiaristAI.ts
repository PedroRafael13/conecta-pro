/**
 * Hook: useDiaristAI
 *
 * Funcionalidades de IA para diaristas:
 * - Sugestões inteligentes
 * - Análise de disponibilidade
 * - Análise de performance
 * - Otimização de agendamentos
 */

import { useQuery } from '@tanstack/react-query';
import { diaristCoreService } from '@/services/diarists';
import type { DiaristType } from '@/api/diarists/generated/models';

/**
 * Hook para sugerir diaristas usando IA
 */
export function useSuggestDiarists(params: {
  data: string;
  tipo?: DiaristType;
  duracaoHoras?: number;
  priorizarConhecidas?: boolean;
}) {
  return useQuery({
    queryKey: ['diarists', 'ai', 'suggest', params],
    queryFn: () => diaristCoreService.suggestDiarists(params),
    enabled: !!params.data,
  });
}

/**
 * Hook para analisar disponibilidade
 */
export function useAnalyzeAvailability(params: {
  dataInicio: string;
  dataFim: string;
  tipo?: DiaristType;
}) {
  return useQuery({
    queryKey: ['diarists', 'ai', 'availability', params],
    queryFn: () => diaristCoreService.analyzeAvailability(params),
    enabled: !!params.dataInicio && !!params.dataFim,
  });
}

/**
 * Hook para analisar performance de diarista
 */
export function useAnalyzePerformance(
  diaristId: string,
  params?: {
    dataInicio?: string;
    dataFim?: string;
  }
) {
  return useQuery({
    queryKey: ['diarists', 'ai', 'performance', diaristId, params],
    queryFn: () => diaristCoreService.analyzePerformance(diaristId, params),
    enabled: !!diaristId,
  });
}

/**
 * Hook para otimizar agendamentos
 */
export function useOptimizeSchedule(params: {
  dataInicio: string;
  dataFim: string;
  budget?: number;
}) {
  return useQuery({
    queryKey: ['diarists', 'ai', 'optimize', params],
    queryFn: () => diaristCoreService.optimizeSchedule(params),
    enabled: !!params.dataInicio && !!params.dataFim,
  });
}
