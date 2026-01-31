/**
 * Shifts Hooks - Gestão de Turnos de Trabalho
 *
 * Re-exports dos hooks Orval do módulo operacional-turnos
 */

import {
  useListShiftsApiV1OperacionalShiftsGet,
  useCreateShiftApiV1OperacionalShiftsPost,
  useGetShiftApiV1OperacionalShiftsShiftIdGet,
  useUpdateShiftApiV1OperacionalShiftsShiftIdPatch,
  useDeleteShiftApiV1OperacionalShiftsShiftIdDelete,
  useGetActiveShiftsApiV1OperacionalShiftsActiveGet,
  useCheckInApiV1OperacionalShiftsShiftIdCheckInPost,
  useCheckOutApiV1OperacionalShiftsShiftIdCheckOutPost,
  useMarkAsMissedApiV1OperacionalShiftsShiftIdMarkMissedPost,
} from '@/types/generated/operacional/operacional-turnos/operacional-turnos';

// List & Read
export const useShifts = useListShiftsApiV1OperacionalShiftsGet;
export const useShift = useGetShiftApiV1OperacionalShiftsShiftIdGet;
export const useActiveShifts = useGetActiveShiftsApiV1OperacionalShiftsActiveGet;

// Mutations
export const useCreateShift = useCreateShiftApiV1OperacionalShiftsPost;
export const useUpdateShift = useUpdateShiftApiV1OperacionalShiftsShiftIdPatch;
export const useDeleteShift = useDeleteShiftApiV1OperacionalShiftsShiftIdDelete;
export const useCheckInShift = useCheckInApiV1OperacionalShiftsShiftIdCheckInPost;
export const useCheckOutShift = useCheckOutApiV1OperacionalShiftsShiftIdCheckOutPost;
export const useMarkShiftMissed = useMarkAsMissedApiV1OperacionalShiftsShiftIdMarkMissedPost;

// Re-export types
export type {
  ShiftCreate,
  ShiftUpdate,
  ShiftResponse,
} from '@/types/generated/operacional/conectaPROMóduloOPERACIONAL.schemas';
