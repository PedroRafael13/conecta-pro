/**
 * Service Layer - Reimbursement Requests
 *
 * Gerencia solicitações de reembolso (CRUD, submissão, cancelamento)
 * Cobertura: 8 endpoints principais de requests
 */

import { apiClient } from '@/lib/api/client';
import type {
  ReimbursementRequestCreate,
  ReimbursementRequestUpdate,
  ReimbursementRequestResponse,
  PaginatedReimbursementResponse,
  ReimbursementRequestStats,
} from '@/types/generated/reimbursement/models';

const BASE_URL = '/api/v1/reimbursements';

export const reimbursementRequestService = {
  /**
   * Cria nova solicitação de reembolso (status RASCUNHO)
   */
  async create(data: ReimbursementRequestCreate): Promise<ReimbursementRequestResponse> {
    const response = await apiClient.post<ReimbursementRequestResponse>(BASE_URL, data);
    return response.data;
  },

  /**
   * Lista solicitações de reembolso com filtros e paginação
   * Gestores veem todas, admins veem de todos os condomínios
   */
  async list(params?: {
    page?: number;
    page_size?: number;
    status?: string;
    approval_level?: string;
    expense_date_start?: string;
    expense_date_end?: string;
    search?: string;
    cost_center?: string;
    project?: string;
  }): Promise<PaginatedReimbursementResponse> {
    const response = await apiClient.get<PaginatedReimbursementResponse>(BASE_URL, { params });
    return response.data;
  },

  /**
   * Lista solicitações do usuário autenticado
   */
  async listMy(params?: {
    page?: number;
    page_size?: number;
    status?: string;
  }): Promise<PaginatedReimbursementResponse> {
    const response = await apiClient.get<PaginatedReimbursementResponse>(`${BASE_URL}/my`, { params });
    return response.data;
  },

  /**
   * Busca solicitação por ID
   */
  async getById(requestId: string): Promise<ReimbursementRequestResponse> {
    const response = await apiClient.get<ReimbursementRequestResponse>(`${BASE_URL}/${requestId}`);
    return response.data;
  },

  /**
   * Atualiza solicitação (apenas em rascunho)
   */
  async update(requestId: string, data: ReimbursementRequestUpdate): Promise<ReimbursementRequestResponse> {
    const response = await apiClient.put<ReimbursementRequestResponse>(`${BASE_URL}/${requestId}`, data);
    return response.data;
  },

  /**
   * Exclui solicitação (apenas em rascunho)
   */
  async delete(requestId: string): Promise<void> {
    await apiClient.delete(`${BASE_URL}/${requestId}`);
  },

  /**
   * Submete solicitação para aprovação
   */
  async submit(requestId: string, notes?: string): Promise<ReimbursementRequestResponse> {
    const response = await apiClient.post<ReimbursementRequestResponse>(
      `${BASE_URL}/${requestId}/submit`,
      { notes }
    );
    return response.data;
  },

  /**
   * Cancela uma solicitação
   */
  async cancel(requestId: string, reason?: string): Promise<ReimbursementRequestResponse> {
    const response = await apiClient.post<ReimbursementRequestResponse>(
      `${BASE_URL}/${requestId}/cancel`,
      null,
      { params: { reason } }
    );
    return response.data;
  },

  /**
   * Retorna estatísticas de reembolsos
   */
  async getStats(myOnly: boolean = false): Promise<ReimbursementRequestStats> {
    const response = await apiClient.get<ReimbursementRequestStats>(`${BASE_URL}/stats`, {
      params: { my_only: myOnly },
    });
    return response.data;
  },

  /**
   * Lista categorias de despesa disponíveis
   */
  async getCategories(): Promise<Array<{ code: string; name: string }>> {
    const response = await apiClient.get<Array<{ code: string; name: string }>>(`${BASE_URL}/categories`);
    return response.data;
  },

  /**
   * Lista tipos de despesa (enum)
   */
  async getExpenseTypes(): Promise<Array<{ value: string; label: string }>> {
    const response = await apiClient.get<Array<{ value: string; label: string }>>(`${BASE_URL}/expense-types`);
    return response.data;
  },

  /**
   * Lista tipos de anexo (enum)
   */
  async getAttachmentTypes(): Promise<Array<{ value: string; label: string }>> {
    const response = await apiClient.get<Array<{ value: string; label: string }>>(`${BASE_URL}/attachment-types`);
    return response.data;
  },
};
