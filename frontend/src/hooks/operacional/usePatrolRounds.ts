/**
 * Patrol Rounds Hooks - Gestão de Rondas de Inspeção
 *
 * Re-exports dos hooks Orval do módulo operacional-rondas-de-inspecao
 */

import {
  useListPatrolRoundsApiV1OperacionalPatrolRoundsGet,
  useCreatePatrolRoundApiV1OperacionalPatrolRoundsPost,
  useGetPatrolRoundApiV1OperacionalPatrolRoundsPatrolRoundIdGet,
  useUpdatePatrolRoundApiV1OperacionalPatrolRoundsPatrolRoundIdPatch,
  useDeletePatrolRoundApiV1OperacionalPatrolRoundsPatrolRoundIdDelete,
  useGetPatrolRoundsByPostApiV1OperacionalPatrolRoundsPostPostIdGet,
  useGetPatrolRoundsByEmployeeApiV1OperacionalPatrolRoundsEmployeeEmployeeIdGet,
  useCompletePatrolRoundApiV1OperacionalPatrolRoundsPatrolRoundIdCompletePost,
} from '@/types/generated/operacional/operacional-rondas-de-inspecao/operacional-rondas-de-inspecao';

// List & Read
export const usePatrolRounds = useListPatrolRoundsApiV1OperacionalPatrolRoundsGet;
export const usePatrolRound = useGetPatrolRoundApiV1OperacionalPatrolRoundsPatrolRoundIdGet;
export const usePatrolRoundsByPost = useGetPatrolRoundsByPostApiV1OperacionalPatrolRoundsPostPostIdGet;
export const usePatrolRoundsByEmployee = useGetPatrolRoundsByEmployeeApiV1OperacionalPatrolRoundsEmployeeEmployeeIdGet;

// Mutations
export const useCreatePatrolRound = useCreatePatrolRoundApiV1OperacionalPatrolRoundsPost;
export const useUpdatePatrolRound = useUpdatePatrolRoundApiV1OperacionalPatrolRoundsPatrolRoundIdPatch;
export const useDeletePatrolRound = useDeletePatrolRoundApiV1OperacionalPatrolRoundsPatrolRoundIdDelete;
export const useCompletePatrolRound = useCompletePatrolRoundApiV1OperacionalPatrolRoundsPatrolRoundIdCompletePost;

// Re-export types
export type {
  PatrolRoundCreate,
  PatrolRoundUpdate,
  PatrolRoundResponse,
  PatrolRoundComplete,
} from '@/types/generated/operacional/conectaPROMóduloOPERACIONAL.schemas';
