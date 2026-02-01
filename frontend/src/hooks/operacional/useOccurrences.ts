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
  useResolveOccurrenceApiV1OperacionalOccurrencesOccurrenceIdResolvePost,
  useGetOccurrenceStatsApiV1OperacionalOccurrencesStatsGet,
  useGetOccurrencesByPostApiV1OperacionalOccurrencesByPostPostIdGet,
  useAddAttachmentApiV1OperacionalOccurrencesOccurrenceIdAttachmentsPost,
} from '@/types/generated/operacional/operacional-ocorrencias/operacional-ocorrencias';

// List & Read
export const useOccurrences = useListOccurrencesApiV1OperacionalOccurrencesGet;
export const useOccurrence = useGetOccurrenceApiV1OperacionalOccurrencesOccurrenceIdGet;
export const useOccurrenceStats = useGetOccurrenceStatsApiV1OperacionalOccurrencesStatsGet;
export const useOccurrencesByPost = useGetOccurrencesByPostApiV1OperacionalOccurrencesByPostPostIdGet;

// Mutations
export const useCreateOccurrence = useCreateOccurrenceApiV1OperacionalOccurrencesPost;
export const useUpdateOccurrence = useUpdateOccurrenceApiV1OperacionalOccurrencesOccurrenceIdPatch;
export const useDeleteOccurrence = useDeleteOccurrenceApiV1OperacionalOccurrencesOccurrenceIdDelete;
export const useResolveOccurrence = useResolveOccurrenceApiV1OperacionalOccurrencesOccurrenceIdResolvePost;
export const useAddAttachment = useAddAttachmentApiV1OperacionalOccurrencesOccurrenceIdAttachmentsPost;

// Re-export types
export type {
  OccurrenceCreate,
  OccurrenceUpdate,
  OccurrenceResponse,
  OccurrenceResolve,
} from '@/types/generated/operacional/conectaPROMóduloOPERACIONAL.schemas';
