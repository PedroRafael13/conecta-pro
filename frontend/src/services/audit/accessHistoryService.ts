/**
 * Service Layer - AccessHistory
 *
 * Gerencia histórico de acessos ao sistema
 * - Registro de logins e ações
 * - Detecção de anomalias
 * - Análise de risco
 * - Rastreabilidade por IP, device, geolocalização
 *
 * Compliance: Segurança da informação, rastreabilidade
 */

import { api } from '@/lib/api';
import type {
  AccessHistoryCreate,
  AccessHistoryResponse,
  AccessHistoryList,
  AccessHistoryStats,
} from '@/types/generated/audit/models';

const BASE_URL = '/api/v1/audit/access';

export interface AccessHistoryFilters {
  access_type?: string;
  result?: string;
  user_id?: string;
  ip_address?: string;
  risk_level?: string;
  anomaly_detected?: boolean;
  requires_review?: boolean;
  start_date?: string;
  end_date?: string;
  page?: number;
  page_size?: number;
}

export const accessHistoryService = {
  /**
   * Registra novo acesso ao sistema
   */
  async record(data: AccessHistoryCreate): Promise<AccessHistoryResponse> {
    const response = await api.post<AccessHistoryResponse>(BASE_URL, data);
    return response.data;
  },

  /**
   * Lista histórico de acessos com filtros
   */
  async list(filters?: AccessHistoryFilters): Promise<AccessHistoryList> {
    const response = await api.get<AccessHistoryList>(BASE_URL, {
      params: filters,
    });
    return response.data;
  },

  /**
   * Busca acesso específico por ID
   */
  async getById(accessId: string): Promise<AccessHistoryResponse> {
    const response = await api.get<AccessHistoryResponse>(`${BASE_URL}/${accessId}`);
    return response.data;
  },

  /**
   * Obtém estatísticas de acessos
   */
  async getStats(startDate?: string, endDate?: string): Promise<AccessHistoryStats> {
    const response = await api.get<AccessHistoryStats>(`${BASE_URL}/stats`, {
      params: {
        start_date: startDate,
        end_date: endDate,
      },
    });
    return response.data;
  },

  /**
   * Busca histórico de acessos de um usuário específico
   */
  async getUserHistory(userId: string, limit: number = 50): Promise<AccessHistoryResponse[]> {
    const response = await api.get<AccessHistoryResponse[]>(`${BASE_URL}/user/${userId}`, {
      params: { limit },
    });
    return response.data;
  },
};
