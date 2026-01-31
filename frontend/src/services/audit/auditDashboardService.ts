/**
 * Service Layer - AuditDashboard
 *
 * Dashboards e visões gerenciais de auditoria
 * - Dashboard principal de auditoria
 * - Overview de compliance
 * - Overview de segurança
 *
 * Compliance: Gestão visual de conformidade
 */

import { api } from '@/lib/api';
import type {
  AuditDashboard,
  ComplianceOverview,
  SecurityOverview,
} from '@/types/generated/audit/models';

const BASE_URL = '/api/v1/audit';

export const auditDashboardService = {
  /**
   * Obtém dashboard principal de auditoria
   * Métricas consolidadas de logs, checks, acessos
   */
  async getDashboard(): Promise<AuditDashboard> {
    const response = await api.get<AuditDashboard>(`${BASE_URL}/dashboard`);
    return response.data;
  },

  /**
   * Obtém overview de compliance
   * Status de regras, verificações, frameworks
   */
  async getComplianceOverview(): Promise<ComplianceOverview> {
    const response = await api.get<ComplianceOverview>(`${BASE_URL}/compliance/overview`);
    return response.data;
  },

  /**
   * Obtém overview de segurança
   * Acessos, anomalias, riscos
   */
  async getSecurityOverview(): Promise<SecurityOverview> {
    const response = await api.get<SecurityOverview>(`${BASE_URL}/security/overview`);
    return response.data;
  },
};
