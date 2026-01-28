/**
 * Fraud Detection Hooks
 *
 * Hooks React Query para detecção de fraudes.
 */

import { useQuery, useMutation, UseQueryOptions, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { fraudDetectionService } from '@/services/analytics';
import type {
  TransactionAnalysisRequest,
  FraudAlertResponse,
} from '@/api/generated/analytics/conectaPROAnalyticsModule.schemas';

/**
 * Hook para analisar transação
 */
export function useAnalyzeTransaction(
  options?: UseMutationOptions<FraudAlertResponse, Error, TransactionAnalysisRequest>
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (transaction: TransactionAnalysisRequest) =>
      fraudDetectionService.analyzeTransaction(transaction),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fraud-alerts'] });
      queryClient.invalidateQueries({ queryKey: ['fraud-analytics'] });
    },
    ...options,
  });
}

/**
 * Hook para listar alertas de fraude
 */
export function useFraudAlerts(
  minRisk?: string,
  acknowledged?: boolean,
  limit = 50,
  options?: Omit<UseQueryOptions<any>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['fraud-alerts', minRisk, acknowledged, limit],
    queryFn: () => fraudDetectionService.getFraudAlerts(minRisk, acknowledged, limit),
    staleTime: 30000, // 30 segundos
    refetchInterval: 60000, // Atualiza a cada 1 minuto
    ...options,
  });
}

/**
 * Hook para atualizar status de alerta
 */
export function useUpdateAlertStatus(
  options?: UseMutationOptions<any, Error, { alertId: string; newStatus: string; notes?: string }>
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ alertId, newStatus, notes }) =>
      fraudDetectionService.updateAlertStatus(alertId, newStatus, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fraud-alerts'] });
    },
    ...options,
  });
}

/**
 * Hook para analytics de fraude
 */
export function useFraudAnalytics(
  options?: Omit<UseQueryOptions<any>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['fraud-analytics'],
    queryFn: () => fraudDetectionService.getFraudAnalytics(),
    staleTime: 300000, // 5 minutos
    ...options,
  });
}

/**
 * Hook para perfil de risco de usuário
 */
export function useUserRiskProfile(
  userId: number,
  options?: Omit<UseQueryOptions<any>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['fraud-user-risk-profile', userId],
    queryFn: () => fraudDetectionService.getUserRiskProfile(userId),
    enabled: !!userId,
    staleTime: 300000,
    ...options,
  });
}
