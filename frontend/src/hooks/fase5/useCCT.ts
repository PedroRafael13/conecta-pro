/**
 * CCT Compliance Hooks - Validação de Cargos e Salários (SINDCOND 2026)
 *
 * Re-exports dos hooks Orval do módulo fase5 - CCT Compliance
 */

import {
  useListarCargosApiV1Fase5CctCargosGet,
  useObterCargoApiV1Fase5CctCargoCargoGet,
  useValidarSalarioApiV1Fase5CctValidarSalarioPost,
  useValidarCompletoApiV1Fase5CctValidarCompletoPost,
  useCalcularCustoApiV1Fase5CctCalcularCustoPost,
  useGerarPropostaApiV1Fase5CctGerarPropostaPost,
} from '@/types/generated/fase5/fase-5-grand-finale/fase-5-grand-finale';

// Read
export const useCCTCargos = useListarCargosApiV1Fase5CctCargosGet;
export const useCCTCargo = useObterCargoApiV1Fase5CctCargoCargoGet;

// Mutations
export const useValidarSalarioCCT = useValidarSalarioApiV1Fase5CctValidarSalarioPost;
export const useValidarCompletoCCT = useValidarCompletoApiV1Fase5CctValidarCompletoPost;
export const useCalcularCustoCCT = useCalcularCustoApiV1Fase5CctCalcularCustoPost;
export const useGerarPropostaCCT = useGerarPropostaApiV1Fase5CctGerarPropostaPost;

// Re-export types
export type {
  ValidarSalarioRequest,
  ValidarCompletoRequest,
  CalcularCustoRequest,
  GerarPropostaRequest,
} from '@/types/generated/fase5/conectaPROFase5ModuleAPI.schemas';
