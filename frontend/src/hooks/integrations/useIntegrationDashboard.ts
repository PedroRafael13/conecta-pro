/**
 * Hook: useIntegrationDashboard
 * Dashboard e Health Check de integrações
 */

import { useQuery } from '@tanstack/react-query';
import { apiEndpointService } from '@/lib/api/services/integrations';

const QUERY_KEY = 'integrations-dashboard';

/**
 * Hook para obter dashboard de integrações
 */
export function useIntegrationDashboard() {
  return useQuery({
    queryKey: [QUERY_KEY, 'dashboard'],
    queryFn: () => apiEndpointService.getDashboard(),
  });
}

/**
 * Hook para health check
 */
export function useIntegrationHealthCheck() {
  return useQuery({
    queryKey: [QUERY_KEY, 'health'],
    queryFn: () => apiEndpointService.healthCheck(),
    refetchInterval: 60000, // Refetch a cada 1 minuto
  });
}
