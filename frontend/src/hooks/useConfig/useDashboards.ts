/**
 * Custom Hooks - Dashboards
 */

import { useQuery } from '@tanstack/react-query';
import * as dashboardsService from '@/services/config/dashboards';

export const dashboardsKeys = {
  all: ['dashboards'] as const,
  config: () => [...dashboardsKeys.all, 'config'] as const,
  tenant: (tenantId: string) => [...dashboardsKeys.all, 'tenant', tenantId] as const,
};

/**
 * Hook para obter dashboard geral de configurações
 */
export const useConfigDashboard = () => {
  return useQuery({
    queryKey: dashboardsKeys.config(),
    queryFn: () => dashboardsService.getConfigDashboard(),
  });
};

/**
 * Hook para obter dashboard de tenant específico
 */
export const useTenantDashboard = (tenantId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: dashboardsKeys.tenant(tenantId),
    queryFn: () => dashboardsService.getTenantDashboard(tenantId),
    enabled: enabled && !!tenantId,
  });
};
