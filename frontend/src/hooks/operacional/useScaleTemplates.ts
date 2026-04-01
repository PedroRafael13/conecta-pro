/**
 * Scale Templates Hooks - Gestão de Templates de Escalas
 *
 * Re-exports dos hooks Orval do módulo operacional-templates-de-escalas
 */

import {
  useListTemplatesApiV1OperacionalScalesTemplatesGet,
  useCreateTemplateApiV1OperacionalScalesTemplatesPost,
  useGetTemplateApiV1OperacionalScalesTemplatesTemplateIdGet,
  useUpdateTemplateApiV1OperacionalScalesTemplatesTemplateIdPatch,
  useDeleteTemplateApiV1OperacionalScalesTemplatesTemplateIdDelete,
  useApplyTemplateApiV1OperacionalScalesTemplatesTemplateIdApplyPost,
} from '@/types/generated/operacional/operacional-templates-de-escalas/operacional-templates-de-escalas';

// List & Read
export const useScaleTemplates = useListTemplatesApiV1OperacionalScalesTemplatesGet;
export const useScaleTemplate = useGetTemplateApiV1OperacionalScalesTemplatesTemplateIdGet;
export const useActiveScaleTemplates = useListTemplatesApiV1OperacionalScalesTemplatesGet;

// Mutations
export const useCreateScaleTemplate = useCreateTemplateApiV1OperacionalScalesTemplatesPost;
export const useUpdateScaleTemplate = useUpdateTemplateApiV1OperacionalScalesTemplatesTemplateIdPatch;
export const useDeleteScaleTemplate = useDeleteTemplateApiV1OperacionalScalesTemplatesTemplateIdDelete;
export const useApplyScaleTemplate = useApplyTemplateApiV1OperacionalScalesTemplatesTemplateIdApplyPost;

// Re-export types
export type {
  ScaleTemplateCreate,
  ScaleTemplateUpdate,
  ScaleTemplateResponse,
  ScaleTemplateApplyRequest,
} from '@/types/generated/operacional/conectaPROMóduloOPERACIONAL.schemas';
