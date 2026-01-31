/**
 * Service Layer - Reimbursement Approvals
 *
 * Gerencia fluxo de aprovação de reembolsos
 * Cobertura: 4 endpoints de aprovação
 */

import { apiClient } from '@/lib/api/client';
import type {
  ReimbursementRequestResponse,
  PaginatedReimbursementResponse,
  ReimbursementApproveRequest,
  ReimbursementRejectRequest,
  ReimbursementReturnRequest,
} from '@/types/generated/reimbursement/models';

const BASE_URL = '/api/v1/reimbursements';

export const reimbursementApprovalService = {
  /**
   * Lista solicitações pendentes de aprovação
   */
  async listPending(params?: {
    page?: number;
    page_size?: number;
    approval_level?: string;
  }): Promise<PaginatedReimbursementResponse> {
    const response = await apiClient.get<PaginatedReimbursementResponse>(
      `${BASE_URL}/approvals/pending`,
      { params }
    );
    return response.data;
  },

  /**
   * Inicia análise de uma solicitação
   * Muda status para EM_ANALISE
   */
  async startAnalysis(requestId: string): Promise<ReimbursementRequestResponse> {
    const response = await apiClient.post<ReimbursementRequestResponse>(
      `${BASE_URL}/${requestId}/analyze`
    );
    return response.data;
  },

  /**
   * Aprova uma solicitação de reembolso
   * Pode aprovar parcialmente (alguns itens)
   */
  async approve(
    requestId: string,
    data?: ReimbursementApproveRequest
  ): Promise<ReimbursementRequestResponse> {
    const response = await apiClient.post<ReimbursementRequestResponse>(
      `${BASE_URL}/${requestId}/approve`,
      data || {}
    );
    return response.data;
  },

  /**
   * Rejeita uma solicitação de reembolso
   * Requer motivo (mínimo 10 caracteres)
   */
  async reject(
    requestId: string,
    data: ReimbursementRejectRequest
  ): Promise<ReimbursementRequestResponse> {
    const response = await apiClient.post<ReimbursementRequestResponse>(
      `${BASE_URL}/${requestId}/reject`,
      data
    );
    return response.data;
  },

  /**
   * Devolve solicitação para rascunho
   * Requer motivo (mínimo 10 caracteres)
   */
  async returnToDraft(
    requestId: string,
    data: ReimbursementReturnRequest
  ): Promise<ReimbursementRequestResponse> {
    const response = await apiClient.post<ReimbursementRequestResponse>(
      `${BASE_URL}/${requestId}/return`,
      data
    );
    return response.data;
  },
};
