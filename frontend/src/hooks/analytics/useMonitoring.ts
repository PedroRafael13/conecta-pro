/**
 * Monitoring Hooks
 *
 * Hooks React Query para monitoramento de modelos ML.
 */

import { useQuery, useMutation, UseQueryOptions, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { monitoringService } from '@/services/analytics';
import type { ModelHealthResponse } from '@/api/generated/analytics/conectaPROAnalyticsModule.schemas';

/**
 * Hook para dashboard de monitoramento
 */
export function useMonitoringDashboard(
  options?: Omit<UseQueryOptions<any>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['ml-monitoring-dashboard'],
    queryFn: () => monitoringService.getDashboard(),
    staleTime: 60000, // 1 minuto
    refetchInterval: 120000, // Atualiza a cada 2 minutos
    ...options,
  });
}

/**
 * Hook para saúde de modelo
 */
export function useModelHealth(
  modelName: string,
  options?: Omit<UseQueryOptions<ModelHealthResponse>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['ml-model-health', modelName],
    queryFn: () => monitoringService.getModelHealth(modelName),
    enabled: !!modelName,
    staleTime: 60000,
    refetchInterval: 120000,
    ...options,
  });
}

/**
 * Hook para alertas de monitoramento
 */
export function useMonitoringAlerts(
  modelName?: string,
  acknowledged?: boolean,
  options?: Omit<UseQueryOptions<any>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['ml-monitoring-alerts', modelName, acknowledged],
    queryFn: () => monitoringService.getAlerts(modelName, acknowledged),
    staleTime: 30000, // 30 segundos
    refetchInterval: 60000, // Atualiza a cada 1 minuto
    ...options,
  });
}

/**
 * Hook para reconhecer alerta
 */
export function useAcknowledgeAlert(
  options?: UseMutationOptions<any, Error, string>
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (alertId: string) => monitoringService.acknowledgeAlert(alertId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ml-monitoring-alerts'] });
      queryClient.invalidateQueries({ queryKey: ['ml-monitoring-dashboard'] });
    },
    ...options,
  });
}
