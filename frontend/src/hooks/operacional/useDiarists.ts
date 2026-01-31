/**
 * Diarists Hooks - Gestão de Diaristas
 *
 * Re-exports dos hooks Orval do módulo operacional-diaristas
 */

import {
  useListDiaristsApiV1OperacionalDiaristsGet,
  useCreateDiaristApiV1OperacionalDiaristsPost,
  useGetDiaristApiV1OperacionalDiaristsDiaristIdGet,
  useUpdateDiaristApiV1OperacionalDiaristsDiaristIdPatch,
  useDeleteDiaristApiV1OperacionalDiaristsDiaristIdDelete,
  useGetActiveDiaristsApiV1OperacionalDiaristsActiveGet,
  useGetDiaristsByCondominiumApiV1OperacionalDiaristsCondominiumCondominiumIdGet,
} from '@/types/generated/operacional/operacional-diaristas/operacional-diaristas';

// List & Read
export const useDiarists = useListDiaristsApiV1OperacionalDiaristsGet;
export const useDiarist = useGetDiaristApiV1OperacionalDiaristsDiaristIdGet;
export const useActiveDiarists = useGetActiveDiaristsApiV1OperacionalDiaristsActiveGet;
export const useDiaristsByCondominium = useGetDiaristsByCondominiumApiV1OperacionalDiaristsCondominiumCondominiumIdGet;

// Mutations
export const useCreateDiarist = useCreateDiaristApiV1OperacionalDiaristsPost;
export const useUpdateDiarist = useUpdateDiaristApiV1OperacionalDiaristsDiaristIdPatch;
export const useDeleteDiarist = useDeleteDiaristApiV1OperacionalDiaristsDiaristIdDelete;

// Re-export types
export type {
  DiaristCreate,
  DiaristUpdate,
  DiaristResponse,
} from '@/types/generated/operacional/conectaPROMóduloOPERACIONAL.schemas';
