/**
 * Hook: useConnectors
 * Gerenciamento de conectores externos
 */

import { useQuery } from '@tanstack/react-query';
import { connectorService } from '@/lib/api/services/integrations';

const QUERY_KEY = 'integrations-connectors';

/**
 * Hook para listar conectores disponíveis
 */
export function useConnectors() {
  return useQuery({
    queryKey: [QUERY_KEY, 'list'],
    queryFn: () => connectorService.listConnectors(),
  });
}

/**
 * Hook para obter detalhes de um conector
 */
export function useConnector(connectorName: string) {
  return useQuery({
    queryKey: [QUERY_KEY, 'detail', connectorName],
    queryFn: () => connectorService.getConnector(connectorName),
    enabled: !!connectorName,
  });
}

/**
 * Hook para health check de uma conta de integração
 */
export function useConnectorHealthCheck(accountId: string) {
  return useQuery({
    queryKey: [QUERY_KEY, 'health', accountId],
    queryFn: () => connectorService.healthCheckAccount(accountId),
    enabled: !!accountId,
    refetchInterval: 60000, // Refetch a cada 1 minuto
  });
}
