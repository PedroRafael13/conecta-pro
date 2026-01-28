/**
 * Forecast Hooks
 *
 * Hooks React Query para previsões e forecast.
 */

import { useQuery, useMutation, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';
import { forecastService } from '@/services/analytics';
import type { ForecastResponse } from '@/api/generated/analytics/conectaPROAnalyticsModule.schemas';

interface ForecastParams {
  periods?: number;
  granularity?: 'daily' | 'weekly' | 'monthly';
  entityType?: string;
}

/**
 * Hook para previsão de vendas
 */
export function useSalesForecast(
  options?: UseMutationOptions<ForecastResponse, Error, ForecastParams>
) {
  return useMutation({
    mutationFn: ({ periods, granularity, entityType }: ForecastParams) =>
      forecastService.forecastSales(periods, granularity, entityType),
    ...options,
  });
}

/**
 * Hook para cenários de previsão
 */
export function useForecastScenarios(
  periods = 30,
  options?: Omit<UseQueryOptions<any>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['forecast-scenarios', periods],
    queryFn: () => forecastService.getForecastScenarios(periods),
    staleTime: 600000, // 10 minutos
    ...options,
  });
}

/**
 * Hook para acurácia do forecast
 */
export function useForecastAccuracy(
  lookbackDays = 90,
  options?: Omit<UseQueryOptions<any>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['forecast-accuracy', lookbackDays],
    queryFn: () => forecastService.getForecastAccuracy(lookbackDays),
    staleTime: 600000,
    ...options,
  });
}
