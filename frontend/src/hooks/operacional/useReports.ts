/**
 * Reports Hooks - Gestão de Relatórios Operacionais
 *
 * Re-exports dos hooks Orval do módulo operacional-relatorios
 */

import {
  useGetOperationalReportApiV1OperacionalReportsGet,
  useGetAttendanceReportApiV1OperacionalReportsAttendanceGet,
  useGetOccurrencesReportApiV1OperacionalReportsOccurrencesGet,
  useGetPerformanceReportApiV1OperacionalReportsPerformanceGet,
  useGetTimeBankReportApiV1OperacionalReportsTimeBankGet,
} from '@/types/generated/operacional/operacional-relatorios/operacional-relatorios';

// Reports (read-only)
export const useOperationalReport = useGetOperationalReportApiV1OperacionalReportsGet;
export const useAttendanceReport = useGetAttendanceReportApiV1OperacionalReportsAttendanceGet;
export const useOccurrencesReport = useGetOccurrencesReportApiV1OperacionalReportsOccurrencesGet;
export const usePerformanceReport = useGetPerformanceReportApiV1OperacionalReportsPerformanceGet;
export const useTimeBankReport = useGetTimeBankReportApiV1OperacionalReportsTimeBankGet;

// Re-export types
export type {
  OperationalReportResponse,
  AttendanceReportResponse,
  OccurrencesReportResponse,
  PerformanceReportResponse,
  TimeBankReportResponse,
} from '@/types/generated/operacional/conectaPROMóduloOPERACIONAL.schemas';
