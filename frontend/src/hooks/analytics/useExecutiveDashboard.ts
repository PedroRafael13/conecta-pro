/**
 * Executive Dashboard Hooks
 *
 * Hooks React Query para dashboard executivo.
 */

import { useQuery, UseQueryOptions } from '@tanstack/react-query';
import { executiveDashboardService } from '@/services/analytics';
import type {
  GetExecutiveDashboardApiV1AnalyticsExecutiveDashboardGet200,
  GetKpisByCategoryApiV1AnalyticsExecutiveKpisCategoryGet200,
  GetActiveAlertsApiV1AnalyticsExecutiveAlertsActiveGet200,
  GetPredictiveInsightsApiV1AnalyticsExecutiveInsightsPredictiveGet200,
  GetExecutiveSummaryApiV1AnalyticsExecutiveSummaryGet200,
} from '@/api/generated/analytics/conectaPROAnalyticsModule.schemas';

/**
 * Hook para obter dashboard executivo completo
 */
export function useExecutiveDashboard(
  refresh?: boolean,
  options?: Omit<UseQueryOptions<GetExecutiveDashboardApiV1AnalyticsExecutiveDashboardGet200>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['executive-dashboard', refresh],
    queryFn: () => executiveDashboardService.getDashboard(refresh),
    staleTime: 60000, // 1 minuto
    ...options,
  });
}

/**
 * Hook para obter KPIs por categoria
 */
export function useKpisByCategory(
  category: string,
  options?: Omit<UseQueryOptions<GetKpisByCategoryApiV1AnalyticsExecutiveKpisCategoryGet200>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['executive-kpis', category],
    queryFn: () => executiveDashboardService.getKpisByCategory(category),
    enabled: !!category,
    staleTime: 60000,
    ...options,
  });
}

/**
 * Hook para obter alertas ativos
 */
export function useActiveAlerts(
  options?: Omit<UseQueryOptions<GetActiveAlertsApiV1AnalyticsExecutiveAlertsActiveGet200>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['executive-alerts-active'],
    queryFn: () => executiveDashboardService.getActiveAlerts(),
    staleTime: 30000, // 30 segundos
    refetchInterval: 60000, // Atualiza a cada 1 minuto
    ...options,
  });
}

/**
 * Hook para obter insights preditivos
 */
export function usePredictiveInsights(
  options?: Omit<UseQueryOptions<GetPredictiveInsightsApiV1AnalyticsExecutiveInsightsPredictiveGet200>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['executive-insights-predictive'],
    queryFn: () => executiveDashboardService.getPredictiveInsights(),
    staleTime: 300000, // 5 minutos
    ...options,
  });
}

/**
 * Hook para obter resumo executivo
 */
export function useExecutiveSummary(
  options?: Omit<UseQueryOptions<GetExecutiveSummaryApiV1AnalyticsExecutiveSummaryGet200>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['executive-summary'],
    queryFn: () => executiveDashboardService.getSummary(),
    staleTime: 60000,
    ...options,
  });
}

/**
 * Hook para exportar dashboard
 */
export function useExportDashboard() {
  return {
    exportJson: () => executiveDashboardService.exportDashboard('json'),
    exportCsv: () => executiveDashboardService.exportDashboard('csv'),
  };
}

/**
 * Hook para health check do dashboard
 */
export function useDashboardHealth(
  options?: Omit<UseQueryOptions<any>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['executive-dashboard-health'],
    queryFn: () => executiveDashboardService.healthCheck(),
    staleTime: 60000,
    ...options,
  });
}
