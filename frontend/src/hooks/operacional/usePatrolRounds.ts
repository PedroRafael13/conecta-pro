/**
 * Patrol Rounds Hooks - Gestão de Rondas de Inspeção
 *
 * Re-exports dos hooks Orval do módulo operacional-rondas-de-inspecao
 */

import {
  useListRoundsApiV1OperacionalRondasGet,
  useCreateRoundApiV1OperacionalRondasPost,
  useGetRoundApiV1OperacionalRondasRoundIdGet,
  useUpdateRoundApiV1OperacionalRondasRoundIdPatch,
  useDeleteRoundApiV1OperacionalRondasRoundIdDelete,
  useCompleteRoundApiV1OperacionalRondasRoundIdConcluirPost,
  useStartRoundApiV1OperacionalRondasRoundIdIniciarPost,
  usePauseRoundApiV1OperacionalRondasRoundIdPausarPost,
  useResumeRoundApiV1OperacionalRondasRoundIdRetomarPost,
  useCancelRoundApiV1OperacionalRondasRoundIdCancelarPost,
  useCreateCheckpointApiV1OperacionalRondasRoundIdCheckpointsPost,
} from '@/types/generated/operacional/operacional-rondas-de-inspecao/operacional-rondas-de-inspecao';

// List & Read
export const usePatrolRounds = useListRoundsApiV1OperacionalRondasGet;
export const usePatrolRound = useGetRoundApiV1OperacionalRondasRoundIdGet;

// Mutations
export const useCreatePatrolRound = useCreateRoundApiV1OperacionalRondasPost;
export const useUpdatePatrolRound = useUpdateRoundApiV1OperacionalRondasRoundIdPatch;
export const useDeletePatrolRound = useDeleteRoundApiV1OperacionalRondasRoundIdDelete;
export const useCompletePatrolRound = useCompleteRoundApiV1OperacionalRondasRoundIdConcluirPost;
export const useStartPatrolRound = useStartRoundApiV1OperacionalRondasRoundIdIniciarPost;
export const usePausePatrolRound = usePauseRoundApiV1OperacionalRondasRoundIdPausarPost;
export const useResumePatrolRound = useResumeRoundApiV1OperacionalRondasRoundIdRetomarPost;
export const useCancelPatrolRound = useCancelRoundApiV1OperacionalRondasRoundIdCancelarPost;
export const useCreatePatrolCheckpoint = useCreateCheckpointApiV1OperacionalRondasRoundIdCheckpointsPost;

// Re-export types
export type {
  InspectionRoundCreate,
  InspectionRoundUpdate,
  InspectionRoundResponse,
  InspectionRoundSummary,
  CheckpointCreate,
  CheckpointResponse,
  StartRoundApiV1OperacionalRondasRoundIdIniciarPostBody,
  CompleteRoundApiV1OperacionalRondasRoundIdConcluirPostBody,
  CancelRoundApiV1OperacionalRondasRoundIdCancelarPostParams,
} from '@/types/generated/operacional/conectaPROMóduloOPERACIONAL.schemas';
