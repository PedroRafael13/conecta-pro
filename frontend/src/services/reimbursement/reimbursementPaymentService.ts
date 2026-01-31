/**
 * Service Layer - Reimbursement Payment Processing
 *
 * Gerencia processamento financeiro de reembolsos aprovados
 * Cobertura: 2 endpoints de processamento
 */

import { apiClient } from '@/lib/api/client';
import type {
  ReimbursementRequestResponse,
  PaginatedReimbursementResponse,
  ReimbursementProcessRequest,
} from '@/types/generated/reimbursement/models';

const BASE_URL = '/api/v1/reimbursements';

export const reimbursementPaymentService = {
  /**
   * Lista solicitações aprovadas prontas para pagamento
   * Status: APROVADO
   */
  async listReadyForPayment(params?: {
    page?: number;
    page_size?: number;
  }): Promise<PaginatedReimbursementResponse> {
    const response = await apiClient.get<PaginatedReimbursementResponse>(
      `${BASE_URL}/ready-for-payment`,
      { params }
    );
    return response.data;
  },

  /**
   * Processa reembolso aprovado gerando conta a pagar
   * Requer permissão de processamento financeiro
   * Após processamento, status muda para PROCESSADO
   */
  async process(
    requestId: string,
    data?: ReimbursementProcessRequest
  ): Promise<ReimbursementRequestResponse> {
    const response = await apiClient.post<ReimbursementRequestResponse>(
      `${BASE_URL}/${requestId}/process`,
      data || {}
    );
    return response.data;
  },
};
