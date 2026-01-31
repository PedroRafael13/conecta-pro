/**
 * Email Intelligence Hooks - Análise e Classificação de Emails com IA
 *
 * Re-exports dos hooks Orval do módulo fase5 - Email Intelligence
 */

import {
  useAnalisarEmailApiV1Fase5EmailAnalisarPost,
  useObterContextoEmailApiV1Fase5EmailContextoEmailAddressGet,
} from '@/types/generated/fase5/fase-5-grand-finale/fase-5-grand-finale';

// Read
export const useEmailContext = useObterContextoEmailApiV1Fase5EmailContextoEmailAddressGet;

// Mutations
export const useAnalisarEmail = useAnalisarEmailApiV1Fase5EmailAnalisarPost;

// Re-export types
export type {
  AnalisarEmailRequest,
} from '@/types/generated/fase5/conectaPROFase5ModuleAPI.schemas';
