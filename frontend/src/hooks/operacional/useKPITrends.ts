/**
 * KPI Trends Hooks - Gestão de Tendências de KPIs Operacionais
 *
 * Re-exports dos hooks Orval do módulo operacional-kpi-trends
 */

import {
  useGetKpiTrendsApiV1OperacionalKpiTrendsGet,
  useGetKpiTrendsByMetricApiV1OperacionalKpiTrendsMetricMetricNameGet,
  useGetDashboardKpisApiV1OperacionalKpiTrendsDashboardGet,
} from '@/types/generated/operacional/operacional-kpi-trends/operacional-kpi-trends';

// Read only
export const useKPITrends = useGetKpiTrendsApiV1OperacionalKpiTrendsGet;
export const useKPITrendsByMetric = useGetKpiTrendsByMetricApiV1OperacionalKpiTrendsMetricMetricNameGet;
export const useDashboardKPIs = useGetDashboardKpisApiV1OperacionalKpiTrendsDashboardGet;

// Re-export types
export type {
  KPITrendResponse,
  KPIDashboardResponse,
} from '@/types/generated/operacional/conectaPROMóduloOPERACIONAL.schemas';
