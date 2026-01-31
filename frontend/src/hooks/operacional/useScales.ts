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
  useGetScalesByPostApiV1OperacionalScalesPostPostIdGet,
  useGetScalesByEmployeeApiV1OperacionalScalesEmployeeEmployeeIdGet,
  useGetScalesByDateRangeApiV1OperacionalScalesDateRangeGet,
  useGetActiveScalesApiV1OperacionalScalesActiveGet,
  usePublishScaleApiV1OperacionalScalesScaleIdPublishPost,
} from '@/types/generated/operacional/operacional-escalas/operacional-escalas';

// List & Read
export const useScales = useListScalesApiV1OperacionalScalesGet;
export const useScale = useGetScaleApiV1OperacionalScalesScaleIdGet;
export const useScalesByPost = useGetScalesByPostApiV1OperacionalScalesPostPostIdGet;
export const useScalesByEmployee = useGetScalesByEmployeeApiV1OperacionalScalesEmployeeEmployeeIdGet;
export const useScalesByDateRange = useGetScalesByDateRangeApiV1OperacionalScalesDateRangeGet;
export const useActiveScales = useGetActiveScalesApiV1OperacionalScalesActiveGet;

// Mutations
export const useCreateScale = useCreateScaleApiV1OperacionalScalesPost;
export const useUpdateScale = useUpdateScaleApiV1OperacionalScalesScaleIdPatch;
export const useDeleteScale = useDeleteScaleApiV1OperacionalScalesScaleIdDelete;
export const usePublishScale = usePublishScaleApiV1OperacionalScalesScaleIdPublishPost;

// Re-export types
export type {
  ScaleCreate,
  ScaleUpdate,
  ScaleResponse,
} from '@/types/generated/operacional/conectaPROMóduloOPERACIONAL.schemas';
