/**
 * Scales Hooks - Gestão de Escalas de Trabalho
 *
 * Re-exports dos hooks Orval do módulo operacional-escalas
 */

import {
  useListScalesApiV1OperacionalScalesGet,
  useCreateScaleApiV1OperacionalScalesPost,
  useGetScaleApiV1OperacionalScalesScaleIdGet,
  useUpdateScaleApiV1OperacionalScalesScaleIdPatch,
  useDeleteScaleApiV1OperacionalScalesScaleIdDelete,
  usePublishScaleApiV1OperacionalScalesScaleIdPublishPost,
  useGenerateScaleApiV1OperacionalScalesGeneratePost,
  useGetScaleStatsApiV1OperacionalScalesStatsGet,
  useSubmitScaleForApprovalApiV1OperacionalScalesScaleIdSubmitPost,
  useApproveScaleApiV1OperacionalScalesScaleIdApprovePost,
  useAutoGenerateScalesApiV1OperacionalScalesAutoGeneratePost,
} from '@/types/generated/operacional/operacional-escalas/operacional-escalas';

// List & Read
export const useScales = useListScalesApiV1OperacionalScalesGet;
export const useScale = useGetScaleApiV1OperacionalScalesScaleIdGet;
export const useScaleStats = useGetScaleStatsApiV1OperacionalScalesStatsGet;

// Mutations
export const useCreateScale = useCreateScaleApiV1OperacionalScalesPost;
export const useUpdateScale = useUpdateScaleApiV1OperacionalScalesScaleIdPatch;
export const useDeleteScale = useDeleteScaleApiV1OperacionalScalesScaleIdDelete;
export const usePublishScale = usePublishScaleApiV1OperacionalScalesScaleIdPublishPost;
export const useGenerateScale = useGenerateScaleApiV1OperacionalScalesGeneratePost;
export const useSubmitScaleForApproval = useSubmitScaleForApprovalApiV1OperacionalScalesScaleIdSubmitPost;
export const useApproveScale = useApproveScaleApiV1OperacionalScalesScaleIdApprovePost;
export const useAutoGenerateScales = useAutoGenerateScalesApiV1OperacionalScalesAutoGeneratePost;

// Re-export types
export type {
  ScaleCreate,
  ScaleUpdate,
  ScaleResponse,
} from '@/types/generated/operacional/conectaPROMóduloOPERACIONAL.schemas';
