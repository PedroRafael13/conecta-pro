/**
 * Scale Templates Hooks - Gestão de Templates de Escalas
 *
 * Re-exports dos hooks Orval do módulo operacional-templates-de-escalas
 */

import {
  useListScaleTemplatesApiV1OperacionalScaleTemplatesGet,
  useCreateScaleTemplateApiV1OperacionalScaleTemplatesPost,
  useGetScaleTemplateApiV1OperacionalScaleTemplatesTemplateIdGet,
  useUpdateScaleTemplateApiV1OperacionalScaleTemplatesTemplateIdPatch,
  useDeleteScaleTemplateApiV1OperacionalScaleTemplatesTemplateIdDelete,
  useGetActiveScaleTemplatesApiV1OperacionalScaleTemplatesActiveGet,
  useApplyScaleTemplateApiV1OperacionalScaleTemplatesTemplateIdApplyPost,
} from '@/types/generated/operacional/operacional-templates-de-escalas/operacional-templates-de-escalas';

// List & Read
export const useScaleTemplates = useListScaleTemplatesApiV1OperacionalScaleTemplatesGet;
export const useScaleTemplate = useGetScaleTemplateApiV1OperacionalScaleTemplatesTemplateIdGet;
export const useActiveScaleTemplates = useGetActiveScaleTemplatesApiV1OperacionalScaleTemplatesActiveGet;

// Mutations
export const useCreateScaleTemplate = useCreateScaleTemplateApiV1OperacionalScaleTemplatesPost;
export const useUpdateScaleTemplate = useUpdateScaleTemplateApiV1OperacionalScaleTemplatesTemplateIdPatch;
export const useDeleteScaleTemplate = useDeleteScaleTemplateApiV1OperacionalScaleTemplatesTemplateIdDelete;
export const useApplyScaleTemplate = useApplyScaleTemplateApiV1OperacionalScaleTemplatesTemplateIdApplyPost;

// Re-export types
export type {
  ScaleTemplateCreate,
  ScaleTemplateUpdate,
  ScaleTemplateResponse,
  ScaleTemplateApply,
} from '@/types/generated/operacional/conectaPROMóduloOPERACIONAL.schemas';
