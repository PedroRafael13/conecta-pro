/**
 * React Query Hooks - LGPD Status
 * Hooks para monitoramento de status e health check
 */

import { useQuery } from '@tanstack/react-query';
import { StatusService } from '@/services/security-lgpd';

/**
 * Hook para obter status do módulo LGPD
 */
export function useLGPDStatus() {
  return useQuery({
    queryKey: ['lgpd', 'status'],
    queryFn: () => StatusService.getLGPDStatus(),
    staleTime: 1 * 60 * 1000, // 1 minuto
    refetchInterval: 2 * 60 * 1000, // Refetch a cada 2 minutos
  });
}

/**
 * Hook para health check
 */
export function useHealthCheck() {
  return useQuery({
    queryKey: ['lgpd', 'health'],
    queryFn: () => StatusService.healthCheck(),
    staleTime: 30 * 1000, // 30 segundos
    refetchInterval: 60 * 1000, // Refetch a cada minuto
  });
}

/**
 * Hook para verificar se módulo está saudável
 */
export function useIsHealthy() {
  return useQuery({
    queryKey: ['lgpd', 'is-healthy'],
    queryFn: () => StatusService.isHealthy(),
    staleTime: 30 * 1000,
    refetchInterval: 60 * 1000,
  });
}

/**
 * Hook para status de componentes
 */
export function useComponentsStatus() {
  return useQuery({
    queryKey: ['lgpd', 'components', 'status'],
    queryFn: () => StatusService.getComponentsStatus(),
    staleTime: 1 * 60 * 1000,
    refetchInterval: 2 * 60 * 1000,
  });
}
