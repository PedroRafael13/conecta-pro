/**
 * Hooks React Query - AuditDashboard
 *
 * Dashboards e visões gerenciais
 * - Dashboard principal
 * - Overview de compliance
 * - Overview de segurança
 */

import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { auditDashboardService } from '@/services/audit/auditDashboardService';
import type {
  AuditDashboard,
  ComplianceOverview,
  SecurityOverview,
} from '@/types/generated/audit/models';

// Query Keys
export const auditDashboardKeys = {
  all: ['audit', 'dashboard'] as const,
  main: () => [...auditDashboardKeys.all, 'main'] as const,
  compliance: () => [...auditDashboardKeys.all, 'compliance'] as const,
  security: () => [...auditDashboardKeys.all, 'security'] as const,
};

/**
 * Dashboard principal de auditoria
 */
export function useAuditDashboard(): UseQueryResult<AuditDashboard, Error> {
  return useQuery({
    queryKey: auditDashboardKeys.main(),
    queryFn: () => auditDashboardService.getDashboard(),
    staleTime: 60000, // 1min
    refetchInterval: 120000, // 2min auto-refresh
  });
}

/**
 * Overview de compliance
 */
export function useComplianceOverview(): UseQueryResult<ComplianceOverview, Error> {
  return useQuery({
    queryKey: auditDashboardKeys.compliance(),
    queryFn: () => auditDashboardService.getComplianceOverview(),
    staleTime: 60000, // 1min
  });
}

/**
 * Overview de segurança
 */
export function useSecurityOverview(): UseQueryResult<SecurityOverview, Error> {
  return useQuery({
    queryKey: auditDashboardKeys.security(),
    queryFn: () => auditDashboardService.getSecurityOverview(),
    staleTime: 60000, // 1min
  });
}
