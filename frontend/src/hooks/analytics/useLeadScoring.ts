/**
 * Lead Scoring Hooks
 *
 * Hooks React Query para pontuação de leads.
 */

import { useQuery, useMutation, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';
import { leadScoringService } from '@/services/analytics';
import type {
  LeadScoreRequest,
  LeadScoreResponse,
} from '@/api/generated/analytics/conectaPROAnalyticsModule.schemas';

/**
 * Hook para calcular score de lead
 */
export function useScoreLead(
  options?: UseMutationOptions<LeadScoreResponse, Error, LeadScoreRequest>
) {
  return useMutation({
    mutationFn: (lead: LeadScoreRequest) => leadScoringService.scoreLead(lead),
    ...options,
  });
}

/**
 * Hook para top leads
 */
export function useTopLeads(
  limit = 50,
  minQuality = 'warm',
  options?: Omit<UseQueryOptions<any>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['lead-scoring-top', limit, minQuality],
    queryFn: () => leadScoringService.getTopLeads(limit, minQuality),
    staleTime: 300000, // 5 minutos
    ...options,
  });
}

/**
 * Hook para analytics de lead scoring
 */
export function useScoringAnalytics(
  options?: Omit<UseQueryOptions<any>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['lead-scoring-analytics'],
    queryFn: () => leadScoringService.getScoringAnalytics(),
    staleTime: 300000,
    ...options,
  });
}
