/**
 * Churn Prediction Hooks
 *
 * Hooks React Query para predição de churn.
 */

import { useQuery, useMutation, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';
import { churnPredictionService } from '@/services/analytics';
import type { ChurnPredictionResponse } from '@/api/generated/analytics/conectaPROAnalyticsModule.schemas';

/**
 * Hook para predizer churn de usuário
 */
export function usePredictChurn(
  options?: UseMutationOptions<ChurnPredictionResponse, Error, number>
) {
  return useMutation({
    mutationFn: (userId: number) => churnPredictionService.predictChurn(userId),
    ...options,
  });
}

/**
 * Hook para listar usuários com alto risco de churn
 */
export function useHighRiskUsers(
  limit = 50,
  minRisk = 'high',
  options?: Omit<UseQueryOptions<any>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['churn-high-risk-users', limit, minRisk],
    queryFn: () => churnPredictionService.getHighRiskUsers(limit, minRisk),
    staleTime: 300000, // 5 minutos
    ...options,
  });
}

/**
 * Hook para analytics de churn
 */
export function useChurnAnalytics(
  options?: Omit<UseQueryOptions<any>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['churn-analytics'],
    queryFn: () => churnPredictionService.getChurnAnalytics(),
    staleTime: 300000,
    ...options,
  });
}
