/**
 * Service Layer - ComplianceRule
 *
 * Gerencia regras de compliance (LGPD, GDPR, SOX, etc)
 * - CRUD de regras de compliance
 * - Ativação/desativação de regras
 * - Categorização por framework
 *
 * Compliance: Gestão de políticas regulatórias
 */

import { api } from '@/lib/api';
import type {
  ComplianceRuleCreate,
  ComplianceRuleUpdate,
  ComplianceRuleResponse,
  ComplianceRuleList,
} from '@/types/generated/audit/models';

const BASE_URL = '/api/v1/audit/rules';

export interface ComplianceRuleFilters {
  framework?: string;
  category?: string;
  status?: string;
  severity?: string;
  page?: number;
  page_size?: number;
}

export const complianceRuleService = {
  /**
   * Cria uma nova regra de compliance
   */
  async create(data: ComplianceRuleCreate): Promise<ComplianceRuleResponse> {
    const response = await api.post<ComplianceRuleResponse>(BASE_URL, data);
    return response.data;
  },

  /**
   * Lista regras de compliance com filtros
   */
  async list(filters?: ComplianceRuleFilters): Promise<ComplianceRuleList> {
    const response = await api.get<ComplianceRuleList>(BASE_URL, {
      params: filters,
    });
    return response.data;
  },

  /**
   * Busca regra específica por ID
   */
  async getById(ruleId: string): Promise<ComplianceRuleResponse> {
    const response = await api.get<ComplianceRuleResponse>(`${BASE_URL}/${ruleId}`);
    return response.data;
  },

  /**
   * Atualiza regra de compliance
   */
  async update(ruleId: string, data: ComplianceRuleUpdate): Promise<ComplianceRuleResponse> {
    const response = await api.put<ComplianceRuleResponse>(`${BASE_URL}/${ruleId}`, data);
    return response.data;
  },

  /**
   * Ativa regra de compliance
   */
  async activate(ruleId: string): Promise<ComplianceRuleResponse> {
    const response = await api.post<ComplianceRuleResponse>(`${BASE_URL}/${ruleId}/activate`);
    return response.data;
  },

  /**
   * Remove regra de compliance
   */
  async delete(ruleId: string): Promise<void> {
    await api.delete(`${BASE_URL}/${ruleId}`);
  },
};
