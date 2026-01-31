/**
 * Quality Framework Hooks - Validação de Qualidade do Sistema
 *
 * Re-exports dos hooks Orval do módulo fase5 - Quality Framework
 */

import {
  useValidarQualidadeApiV1Fase5QualityValidatePost,
} from '@/types/generated/fase5/fase-5-grand-finale/fase-5-grand-finale';

// Mutations
export const useValidarQualidade = useValidarQualidadeApiV1Fase5QualityValidatePost;

// Re-export types
export type {
  QualidadeRequest,
} from '@/types/generated/fase5/conectaPROFase5ModuleAPI.schemas';
