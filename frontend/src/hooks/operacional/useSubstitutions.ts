/**
 * Substitutions Hooks - Gestão de Substituições de Funcionários
 *
 * Re-exports dos hooks Orval do módulo operacional-substituicoes
 */

import {
  useListSubstitutionsApiV1OperacionalSubstitutionsGet,
  useCreateSubstitutionApiV1OperacionalSubstitutionsPost,
  useGetSubstitutionApiV1OperacionalSubstitutionsSubstitutionIdGet,
  useUpdateSubstitutionApiV1OperacionalSubstitutionsSubstitutionIdPatch,
  useDeleteSubstitutionApiV1OperacionalSubstitutionsSubstitutionIdDelete,
  useGetSubstitutionsByEmployeeApiV1OperacionalSubstitutionsEmployeeEmployeeIdGet,
  useGetActiveSubstitutionsApiV1OperacionalSubstitutionsActiveGet,
} from '@/types/generated/operacional/operacional-substituicoes/operacional-substituicoes';

// List & Read
export const useSubstitutions = useListSubstitutionsApiV1OperacionalSubstitutionsGet;
export const useSubstitution = useGetSubstitutionApiV1OperacionalSubstitutionsSubstitutionIdGet;
export const useSubstitutionsByEmployee = useGetSubstitutionsByEmployeeApiV1OperacionalSubstitutionsEmployeeEmployeeIdGet;
export const useActiveSubstitutions = useGetActiveSubstitutionsApiV1OperacionalSubstitutionsActiveGet;

// Mutations
export const useCreateSubstitution = useCreateSubstitutionApiV1OperacionalSubstitutionsPost;
export const useUpdateSubstitution = useUpdateSubstitutionApiV1OperacionalSubstitutionsSubstitutionIdPatch;
export const useDeleteSubstitution = useDeleteSubstitutionApiV1OperacionalSubstitutionsSubstitutionIdDelete;

// Re-export types
export type {
  SubstitutionCreate,
  SubstitutionUpdate,
  SubstitutionResponse,
} from '@/types/generated/operacional/conectaPROMóduloOPERACIONAL.schemas';
