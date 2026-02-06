/**
 * Reports Hooks - Gestão de Relatórios Operacionais
 *
 * Re-exports dos hooks Orval do módulo operacional-relatorios
 */

import {
  useCoverageReportApiV1OperacionalReportsCoverageGet,
  useHoursReportApiV1OperacionalReportsHoursGet,
  useCostsReportApiV1OperacionalReportsCostsGet,
} from '@/types/generated/operacional/operacional-relatorios/operacional-relatorios';

// Reports (read-only)
export const useCoverageReport = useCoverageReportApiV1OperacionalReportsCoverageGet;
export const useHoursReport = useHoursReportApiV1OperacionalReportsHoursGet;
export const useCostsReport = useCostsReportApiV1OperacionalReportsCostsGet;

// Re-export types
export type {
  CoverageReportResponse,
  HoursReportResponse,
  CostsReportResponse,
  CoverageReportApiV1OperacionalReportsCoverageGetParams,
  HoursReportApiV1OperacionalReportsHoursGetParams,
  CostsReportApiV1OperacionalReportsCostsGetParams,
} from '@/types/generated/operacional/conectaPROMóduloOPERACIONAL.schemas';
