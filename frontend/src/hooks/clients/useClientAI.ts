/**
 * Hooks React Query - Client AI Services
 * Serviços de IA para Clientes
 */

import { useQuery } from '@tanstack/react-query';
import { clientAIService } from '@/services/clients';

/**
 * Query keys para cache
 */
export const clientAIKeys = {
  all: ['clientAI'] as const,
  profile: (clientId: string) => [...clientAIKeys.all, 'profile', clientId] as const,
  segmentation: (clientId: string) =>
    [...clientAIKeys.all, 'segmentation', clientId] as const,
  churnRisk: (clientId: string) =>
    [...clientAIKeys.all, 'churnRisk', clientId] as const,
  recommendations: (clientId: string) =>
    [...clientAIKeys.all, 'recommendations', clientId] as const,
  condominiumHealth: (condominiumId: string) =>
    [...clientAIKeys.all, 'condominiumHealth', condominiumId] as const,
  dashboard: () => [...clientAIKeys.all, 'dashboard'] as const,
};

/**
 * Hook para análise de perfil do cliente
 */
export function useClientProfileAnalysis(clientId: string, enabled = true) {
  return useQuery({
    queryKey: clientAIKeys.profile(clientId),
    queryFn: () => clientAIService.analyzeProfile(clientId),
    enabled: enabled && !!clientId,
    // Cache por 5 minutos (análise de IA é custosa)
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook para sugestão de segmentação
 */
export function useClientSegmentation(clientId: string, enabled = true) {
  return useQuery({
    queryKey: clientAIKeys.segmentation(clientId),
    queryFn: () => clientAIService.suggestSegmentation(clientId),
    enabled: enabled && !!clientId,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook para predição de churn
 */
export function useClientChurnRisk(clientId: string, enabled = true) {
  return useQuery({
    queryKey: clientAIKeys.churnRisk(clientId),
    queryFn: () => clientAIService.predictChurnRisk(clientId),
    enabled: enabled && !!clientId,
    // Cache por 10 minutos (predição de churn não muda rapidamente)
    staleTime: 10 * 60 * 1000,
  });
}

/**
 * Hook para recomendações de serviços
 */
export function useServiceRecommendations(clientId: string, enabled = true) {
  return useQuery({
    queryKey: clientAIKeys.recommendations(clientId),
    queryFn: () => clientAIService.recommendServices(clientId),
    enabled: enabled && !!clientId,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook para análise de saúde do condomínio
 */
export function useCondominiumHealth(condominiumId: string, enabled = true) {
  return useQuery({
    queryKey: clientAIKeys.condominiumHealth(condominiumId),
    queryFn: () => clientAIService.analyzeCondominiumHealth(condominiumId),
    enabled: enabled && !!condominiumId,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook para insights do dashboard
 */
export function useClientDashboardInsights() {
  return useQuery({
    queryKey: clientAIKeys.dashboard(),
    queryFn: () => clientAIService.getDashboardInsights(),
    // Atualizar a cada 2 minutos
    staleTime: 2 * 60 * 1000,
    refetchInterval: 2 * 60 * 1000,
  });
}
