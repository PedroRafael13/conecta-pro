/**
 * React Query hooks for Clients AI
 */

import { useQuery } from '@tanstack/react-query';
import { ClientsAIService } from '../clients.service';

/**
 * Hook para analisar risco de churn
 */
export function useChurnRisk(clientId: string) {
  return useQuery({
    queryKey: ['clients-ai', 'churn-risk', clientId],
    queryFn: () => ClientsAIService.analyzeChurnRisk(clientId),
    enabled: !!clientId,
    staleTime: 10 * 60 * 1000,
  });
}

/**
 * Hook para obter perfil do cliente
 */
export function useClientProfile(clientId: string) {
  return useQuery({
    queryKey: ['clients-ai', 'profile', clientId],
    queryFn: () => ClientsAIService.getClientProfile(clientId),
    enabled: !!clientId,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook para recomendações personalizadas
 */
export function useClientRecommendations(clientId: string) {
  return useQuery({
    queryKey: ['clients-ai', 'recommendations', clientId],
    queryFn: () => ClientsAIService.getRecommendations(clientId),
    enabled: !!clientId,
    staleTime: 15 * 60 * 1000,
  });
}

/**
 * Hook para segmentação de cliente
 */
export function useClientSegmentation(clientId: string) {
  return useQuery({
    queryKey: ['clients-ai', 'segmentation', clientId],
    queryFn: () => ClientsAIService.getSegmentation(clientId),
    enabled: !!clientId,
    staleTime: 30 * 60 * 1000,
  });
}

/**
 * Hook para dashboard de clientes
 */
export function useClientsDashboard() {
  return useQuery({
    queryKey: ['clients-ai', 'dashboard'],
    queryFn: () => ClientsAIService.getDashboard(),
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook para análise de saúde do condomínio
 */
export function useCondominiumHealth(condominiumId: string) {
  return useQuery({
    queryKey: ['clients-ai', 'condominium-health', condominiumId],
    queryFn: () => ClientsAIService.analyzeCondominiumHealth(condominiumId),
    enabled: !!condominiumId,
    staleTime: 10 * 60 * 1000,
  });
}
