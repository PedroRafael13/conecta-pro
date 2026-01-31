/**
 * Occurrences Hooks - Gestão de Ocorrências Operacionais
 *
 * Re-exports dos hooks Orval do módulo operacional-ocorrencias
 */

import {
  useListOccurrencesApiV1OperacionalOccurrencesGet,
  useCreateOccurrenceApiV1OperacionalOccurrencesPost,
  useGetOccurrenceApiV1OperacionalOccurrencesOccurrenceIdGet,
  useUpdateOccurrenceApiV1OperacionalOccurrencesOccurrenceIdPatch,
  useDeleteOccurrenceApiV1OperacionalOccurrencesOccurrenceIdDelete,
  useGetOccurrencesByEmployeeApiV1OperacionalOccurrencesEmployeeEmployeeIdGet,
  useGetOccurrencesByPostApiV1OperacionalOccurrencesPostPostIdGet,
  useGetOccurrencesByTypeApiV1OperacionalOccurrencesTypeTypeGet,
  useResolveOccurrenceApiV1OperacionalOccurrencesOccurrenceIdResolvePost,
} from '@/types/generated/operacional/operacional-ocorrencias/operacional-ocorrencias';

// List & Read
export const useOccurrences = useListOccurrencesApiV1OperacionalOccurrencesGet;
export const useOccurrence = useGetOccurrenceApiV1OperacionalOccurrencesOccurrenceIdGet;
export const useOccurrencesByEmployee = useGetOccurrencesByEmployeeApiV1OperacionalOccurrencesEmployeeEmployeeIdGet;
export const useOccurrencesByPost = useGetOccurrencesByPostApiV1OperacionalOccurrencesPostPostIdGet;
export const useOccurrencesByType = useGetOccurrencesByTypeApiV1OperacionalOccurrencesTypeTypeGet;

// Mutations
export const useCreateOccurrence = useCreateOccurrenceApiV1OperacionalOccurrencesPost;
export const useUpdateOccurrence = useUpdateOccurrenceApiV1OperacionalOccurrencesOccurrenceIdPatch;
export const useDeleteOccurrence = useDeleteOccurrenceApiV1OperacionalOccurrencesOccurrenceIdDelete;
export const useResolveOccurrence = useResolveOccurrenceApiV1OperacionalOccurrencesOccurrenceIdResolvePost;

// Re-export types
export type {
  OccurrenceCreate,
  OccurrenceUpdate,
  OccurrenceResponse,
  OccurrenceResolve,
} from '@/types/generated/operacional/conectaPROMóduloOPERACIONAL.schemas';
