/**
 * Time Bank Hooks - Gestão de Banco de Horas
 *
 * Re-exports dos hooks Orval do módulo operacional-banco-de-horas
 */

import {
  useListEntriesApiV1OperacionalTimeBankGet,
  useGetEntryApiV1OperacionalTimeBankEntryIdGet,
  useGetPendingEntriesApiV1OperacionalTimeBankPendingGet,
  useGetStatsApiV1OperacionalTimeBankStatsGet,
  useGetEmployeeSummaryApiV1OperacionalTimeBankSummaryEmployeeIdGet,
  useGetExpirationAlertsApiV1OperacionalTimeBankAlertsGet,
  useCreateEntryApiV1OperacionalTimeBankPost,
  useUpdateEntryApiV1OperacionalTimeBankEntryIdPatch,
  useDeleteEntryApiV1OperacionalTimeBankEntryIdDelete,
  useApproveEntryApiV1OperacionalTimeBankEntryIdApprovePost,
  useRejectEntryApiV1OperacionalTimeBankEntryIdRejectPost,
  useCompensateHoursApiV1OperacionalTimeBankCompensateEmployeeIdPost,
} from '@/types/generated/operacional/operacional-banco-de-horas/operacional-banco-de-horas';

// List & Read
export const useTimeBankEntries = useListEntriesApiV1OperacionalTimeBankGet;
export const useTimeBankEntry = useGetEntryApiV1OperacionalTimeBankEntryIdGet;
export const usePendingEntries = useGetPendingEntriesApiV1OperacionalTimeBankPendingGet;
export const useTimeBankStats = useGetStatsApiV1OperacionalTimeBankStatsGet;
export const useEmployeeSummary = useGetEmployeeSummaryApiV1OperacionalTimeBankSummaryEmployeeIdGet;
export const useExpirationAlerts = useGetExpirationAlertsApiV1OperacionalTimeBankAlertsGet;

// Mutations
export const useCreateTimeBankEntry = useCreateEntryApiV1OperacionalTimeBankPost;
export const useUpdateTimeBankEntry = useUpdateEntryApiV1OperacionalTimeBankEntryIdPatch;
export const useDeleteTimeBankEntry = useDeleteEntryApiV1OperacionalTimeBankEntryIdDelete;
export const useApproveTimeBankEntry = useApproveEntryApiV1OperacionalTimeBankEntryIdApprovePost;
export const useRejectTimeBankEntry = useRejectEntryApiV1OperacionalTimeBankEntryIdRejectPost;
export const useCompensateHours = useCompensateHoursApiV1OperacionalTimeBankCompensateEmployeeIdPost;

// Re-export types
export type {
  TimeBankCreate,
  TimeBankUpdate,
  TimeBankResponse,
  TimeBankStats,
  TimeBankSummary,
  TimeBankStatus,
  TimeBankEntryType,
} from '@/types/generated/operacional/conectaPROMóduloOPERACIONAL.schemas';
