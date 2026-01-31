/**
 * Service Layer - ComplianceCheck
 *
 * Gerencia verificações de compliance
 * - Criação e execução de checks
 * - Workflow: pending → in_progress → completed
 * - Resultados: compliant / non_compliant
 * - Gestão de remediação
 *
 * Compliance: Auditoria e verificações regulatórias
 */

import { api } from '@/lib/api';
import type {
  ComplianceCheckCreate,
  ComplianceCheckResponse,
  ComplianceCheckList,
} from '@/types/generated/audit/models';

const BASE_URL = '/api/v1/audit/checks';

export interface ComplianceCheckFilters {
  rule_id?: string;
  status?: string;
  result?: string;
  requires_review?: boolean;
  remediation_required?: boolean;
  start_date?: string;
  end_date?: string;
  page?: number;
  page_size?: number;
}

export const complianceCheckService = {
  /**
   * Cria uma nova verificação de compliance
   */
  async create(data: ComplianceCheckCreate): Promise<ComplianceCheckResponse> {
    const response = await api.post<ComplianceCheckResponse>(BASE_URL, data);
    return response.data;
  },

  /**
   * Lista verificações com filtros
   */
  async list(filters?: ComplianceCheckFilters): Promise<ComplianceCheckList> {
    const response = await api.get<ComplianceCheckList>(BASE_URL, {
      params: filters,
    });
    return response.data;
  },

  /**
   * Busca verificação específica por ID
   */
  async getById(checkId: string): Promise<ComplianceCheckResponse> {
    const response = await api.get<ComplianceCheckResponse>(`${BASE_URL}/${checkId}`);
    return response.data;
  },

  /**
   * Inicia execução de verificação
   */
  async start(checkId: string): Promise<ComplianceCheckResponse> {
    const response = await api.post<ComplianceCheckResponse>(`${BASE_URL}/${checkId}/start`);
    return response.data;
  },

  /**
   * Marca verificação como conforme
   */
  async completeCompliant(
    checkId: string,
    evidence?: Record<string, unknown>,
    notes?: string
  ): Promise<ComplianceCheckResponse> {
    const response = await api.post<ComplianceCheckResponse>(
      `${BASE_URL}/${checkId}/complete/compliant`,
      {
        evidence,
        notes,
      }
    );
    return response.data;
  },

  /**
   * Marca verificação como não conforme
   */
  async completeNonCompliant(
    checkId: string,
    violations: Array<Record<string, unknown>>,
    remediationDeadlineDays?: number
  ): Promise<ComplianceCheckResponse> {
    const response = await api.post<ComplianceCheckResponse>(
      `${BASE_URL}/${checkId}/complete/non-compliant`,
      {
        violations,
        remediation_deadline_days: remediationDeadlineDays,
      }
    );
    return response.data;
  },
};
