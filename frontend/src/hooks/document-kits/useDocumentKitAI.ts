/**
 * React Query Hooks - Document Kit AI
 *
 * Hooks customizados para funcionalidades de IA dos kits documentais.
 */

import { useQuery } from '@tanstack/react-query';
import {
  documentKitAIService,
  type SuggestKitsParams,
  type AnalyzeComplianceParams,
  type PredictCompletionParams,
  type GetPrioritiesParams,
  type GetExpiringParams,
} from '@/services/document-kits/documentKitAIService';

// Query Keys
export const documentKitAIKeys = {
  all: ['document-kit-ai'] as const,
  suggestions: (params: SuggestKitsParams) =>
    [...documentKitAIKeys.all, 'suggestions', params] as const,
  compliance: (params: AnalyzeComplianceParams) =>
    [...documentKitAIKeys.all, 'compliance', params] as const,
  prediction: (params: PredictCompletionParams) =>
    [...documentKitAIKeys.all, 'prediction', params] as const,
  priorities: (params: GetPrioritiesParams) =>
    [...documentKitAIKeys.all, 'priorities', params] as const,
  usage: (condominio_id: string) =>
    [...documentKitAIKeys.all, 'usage', condominio_id] as const,
  expiring: (params: GetExpiringParams) =>
    [...documentKitAIKeys.all, 'expiring', params] as const,
};

/**
 * Hook para sugerir kits para uma entidade
 */
export function useSuggestKits(params: SuggestKitsParams) {
  return useQuery({
    queryKey: documentKitAIKeys.suggestions(params),
    queryFn: () => documentKitAIService.suggestKits(params),
    enabled: !!params.entity_type && !!params.condominio_id,
    staleTime: 10 * 60 * 1000, // 10 minutos
  });
}

/**
 * Hook para analisar compliance de uma entidade
 */
export function useAnalyzeCompliance(params: AnalyzeComplianceParams) {
  return useQuery({
    queryKey: documentKitAIKeys.compliance(params),
    queryFn: () => documentKitAIService.analyzeCompliance(params),
    enabled:
      !!params.entity_type && !!params.entity_id && !!params.condominio_id,
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
}

/**
 * Hook para predizer data de conclusão de uma atribuição
 */
export function usePredictCompletion(params: PredictCompletionParams) {
  return useQuery({
    queryKey: documentKitAIKeys.prediction(params),
    queryFn: () => documentKitAIService.predictCompletion(params),
    enabled: !!params.assignment_id && !!params.condominio_id,
    staleTime: 15 * 60 * 1000, // 15 minutos
  });
}

/**
 * Hook para obter atribuições prioritárias
 */
export function useGetPriorities(params: GetPrioritiesParams) {
  return useQuery({
    queryKey: documentKitAIKeys.priorities(params),
    queryFn: () => documentKitAIService.getPriorities(params),
    enabled: !!params.condominio_id,
    staleTime: 2 * 60 * 1000, // 2 minutos
    refetchInterval: 5 * 60 * 1000, // Refetch a cada 5 minutos
  });
}

/**
 * Hook para analisar uso dos kits
 */
export function useAnalyzeUsage(condominio_id: string) {
  return useQuery({
    queryKey: documentKitAIKeys.usage(condominio_id),
    queryFn: () => documentKitAIService.analyzeUsage(condominio_id),
    enabled: !!condominio_id,
    staleTime: 30 * 60 * 1000, // 30 minutos
  });
}

/**
 * Hook para obter documentos próximos ao vencimento
 */
export function useGetExpiringDocuments(params: GetExpiringParams) {
  return useQuery({
    queryKey: documentKitAIKeys.expiring(params),
    queryFn: () => documentKitAIService.getExpiringDocuments(params),
    enabled: !!params.condominio_id,
    staleTime: 1 * 60 * 60 * 1000, // 1 hora
    refetchInterval: 6 * 60 * 60 * 1000, // Refetch a cada 6 horas
  });
}
