/**
 * Time Bank Hooks - Gestão de Banco de Horas
 *
 * Re-exports dos hooks Orval do módulo operacional-banco-de-horas
 */

import {
  useListTimeBankEntriesApiV1OperacionalTimeBankGet,
  useCreateTimeBankEntryApiV1OperacionalTimeBankPost,
  useGetTimeBankEntryApiV1OperacionalTimeBankEntryIdGet,
  useUpdateTimeBankEntryApiV1OperacionalTimeBankEntryIdPatch,
  useDeleteTimeBankEntryApiV1OperacionalTimeBankEntryIdDelete,
  useGetTimeBankByEmployeeApiV1OperacionalTimeBankEmployeeEmployeeIdGet,
  useGetTimeBankBalanceApiV1OperacionalTimeBankEmployeeEmployeeIdBalanceGet,
} from '@/types/generated/operacional/operacional-banco-de-horas/operacional-banco-de-horas';

// List & Read
export const useTimeBankEntries = useListTimeBankEntriesApiV1OperacionalTimeBankGet;
export const useTimeBankEntry = useGetTimeBankEntryApiV1OperacionalTimeBankEntryIdGet;
export const useTimeBankByEmployee = useGetTimeBankByEmployeeApiV1OperacionalTimeBankEmployeeEmployeeIdGet;
export const useTimeBankBalance = useGetTimeBankBalanceApiV1OperacionalTimeBankEmployeeEmployeeIdBalanceGet;

// Mutations
export const useCreateTimeBankEntry = useCreateTimeBankEntryApiV1OperacionalTimeBankPost;
export const useUpdateTimeBankEntry = useUpdateTimeBankEntryApiV1OperacionalTimeBankEntryIdPatch;
export const useDeleteTimeBankEntry = useDeleteTimeBankEntryApiV1OperacionalTimeBankEntryIdDelete;

// Re-export types
export type {
  TimeBankEntryCreate,
  TimeBankEntryUpdate,
  TimeBankEntryResponse,
  TimeBankBalance,
} from '@/types/generated/operacional/conectaPROMóduloOPERACIONAL.schemas';
