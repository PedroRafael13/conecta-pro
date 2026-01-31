/**
 * Hook: useIntegrationLogs
 * Logs de integrações
 */

import { useQuery } from '@tanstack/react-query';
import { integrationLogService } from '@/lib/api/services/integrations';
import type { ListLogsApiV1IntegrationsLogsGetParams } from '@/types/generated/integrations/conectaPROIntegrationsAPI.schemas';

const QUERY_KEY = 'integrations-logs';

/**
 * Hook para listar logs
 */
export function useIntegrationLogs(params?: ListLogsApiV1IntegrationsLogsGetParams) {
  return useQuery({
    queryKey: [QUERY_KEY, 'list', params],
    queryFn: () => integrationLogService.listLogs(params),
  });
}

/**
 * Hook para obter log por ID
 */
export function useIntegrationLog(logId: string) {
  return useQuery({
    queryKey: [QUERY_KEY, 'detail', logId],
    queryFn: () => integrationLogService.getLog(logId),
    enabled: !!logId,
  });
}
