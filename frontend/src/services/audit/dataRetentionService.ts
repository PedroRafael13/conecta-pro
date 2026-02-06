/**
 * Service Layer - DataRetention
 *
 * Gerencia políticas de retenção de dados (LGPD Art. 16)
 * - CRUD de políticas de retenção
 * - Execução manual e agendada
 * - Categorização por tipo de dado
 * - Logs de execução
 *
 * Compliance: LGPD - Retenção e eliminação de dados
 */

import { api } from '@/lib/api';
import type {
  DataRetentionCreate,
  DataRetentionUpdate,
  DataRetentionResponse,
  DataRetentionList,
  DataRetentionExecution,
} from '@/types/generated/audit/models';

const BASE_URL = '/api/v1/audit/retention';

export interface DataRetentionFilters {
  data_category?: string;
  status?: string;
  schedule_enabled?: boolean;
  page?: number;
  page_size?: number;
}

export const dataRetentionService = {
  /**
   * Cria nova política de retenção
   */
  async create(data: DataRetentionCreate): Promise<DataRetentionResponse> {
    const response = await api.post<DataRetentionResponse>(BASE_URL, data);
    return response.data;
  },

  /**
   * Lista políticas com filtros
   */
  async list(filters?: DataRetentionFilters): Promise<DataRetentionList> {
    const response = await api.get<DataRetentionList>(BASE_URL, {
      params: filters,
    });
    return response.data;
  },

  /**
   * Busca política específica por ID
   */
  async getById(policyId: string): Promise<DataRetentionResponse> {
    const response = await api.get<DataRetentionResponse>(`${BASE_URL}/${policyId}`);
    return response.data;
  },

  /**
   * Atualiza política de retenção
   */
  async update(policyId: string, data: DataRetentionUpdate): Promise<DataRetentionResponse> {
    const response = await api.put<DataRetentionResponse>(`${BASE_URL}/${policyId}`, data);
    return response.data;
  },

  /**
   * Executa política manualmente
   */
  async execute(policyId: string): Promise<DataRetentionExecution> {
    const response = await api.post<DataRetentionExecution>(`${BASE_URL}/${policyId}/execute`);
    return response.data;
  },

  /**
   * Remove política de retenção
   */
  async delete(policyId: string): Promise<void> {
    await api.delete(`${BASE_URL}/${policyId}`);
  },
};
