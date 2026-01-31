/**
 * Service Layer - AuditLog
 *
 * Gerencia logs de auditoria do sistema
 * - Criação e consulta de logs
 * - Estatísticas e análises
 * - Revisão de logs críticos
 *
 * Compliance: LGPD, rastreabilidade de ações
 */

import { api } from '@/lib/api';
import type {
  AuditLogCreate,
  AuditLogResponse,
  AuditLogList,
  AuditLogStats,
} from '@/types/generated/audit/models';

const BASE_URL = '/api/v1/audit/logs';

export interface AuditLogFilters {
  action?: string;
  category?: string;
  severity?: string;
  result?: string;
  user_id?: string;
  entity_type?: string;
  entity_id?: string;
  start_date?: string;
  end_date?: string;
  requires_review?: boolean;
  search?: string;
  page?: number;
  page_size?: number;
}

export const auditLogService = {
  /**
   * Cria um novo log de auditoria
   */
  async createLog(data: AuditLogCreate): Promise<AuditLogResponse> {
    const response = await api.post<AuditLogResponse>(BASE_URL, data);
    return response.data;
  },

  /**
   * Lista logs de auditoria com filtros complexos
   */
  async listLogs(filters?: AuditLogFilters): Promise<AuditLogList> {
    const response = await api.get<AuditLogList>(BASE_URL, {
      params: filters,
    });
    return response.data;
  },

  /**
   * Busca log específico por ID
   */
  async getLog(logId: string): Promise<AuditLogResponse> {
    const response = await api.get<AuditLogResponse>(`${BASE_URL}/${logId}`);
    return response.data;
  },

  /**
   * Obtém estatísticas de auditoria
   */
  async getStats(startDate?: string, endDate?: string): Promise<AuditLogStats> {
    const response = await api.get<AuditLogStats>(`${BASE_URL}/stats`, {
      params: {
        start_date: startDate,
        end_date: endDate,
      },
    });
    return response.data;
  },

  /**
   * Completa revisão de log crítico
   */
  async completeReview(logId: string, notes?: string): Promise<AuditLogResponse> {
    const response = await api.post<AuditLogResponse>(`${BASE_URL}/${logId}/review`, {
      notes,
    });
    return response.data;
  },
};
