/**
 * KPI Trends Hooks - Gestão de Tendências de KPIs Operacionais
 *
 * Re-exports dos hooks Orval do módulo operacional-kpi-trends
 */

import {
  useGetKpiTrendsApiV1OperacionalKpiTrendsGet,
} from '@/types/generated/operacional/operacional-kpi-trends/operacional-kpi-trends';

// Read only
export const useKPITrends = useGetKpiTrendsApiV1OperacionalKpiTrendsGet;

// Re-export types
export type {
  KPITrendsResponse,
} from '@/types/generated/operacional/conectaPROMóduloOPERACIONAL.schemas';
