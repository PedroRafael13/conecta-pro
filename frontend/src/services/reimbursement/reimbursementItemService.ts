/**
 * Service Layer - Reimbursement Items
 *
 * Gerencia itens de reembolso (despesas individuais)
 * Cobertura: 3 endpoints de itens
 */

import { apiClient } from '@/lib/api/client';
import type {
  ReimbursementItemCreate,
  ReimbursementItemUpdate,
  ReimbursementItemResponse,
} from '@/types/generated/reimbursement/models';

const BASE_URL = '/api/v1/reimbursements';

export const reimbursementItemService = {
  /**
   * Adiciona item a uma solicitação
   */
  async create(requestId: string, data: ReimbursementItemCreate): Promise<ReimbursementItemResponse> {
    const response = await apiClient.post<ReimbursementItemResponse>(
      `${BASE_URL}/${requestId}/items`,
      data
    );
    return response.data;
  },

  /**
   * Atualiza um item (apenas em rascunho)
   */
  async update(
    requestId: string,
    itemId: string,
    data: ReimbursementItemUpdate
  ): Promise<ReimbursementItemResponse> {
    const response = await apiClient.put<ReimbursementItemResponse>(
      `${BASE_URL}/${requestId}/items/${itemId}`,
      data
    );
    return response.data;
  },

  /**
   * Remove um item (apenas em rascunho)
   */
  async delete(requestId: string, itemId: string): Promise<void> {
    await apiClient.delete(`${BASE_URL}/${requestId}/items/${itemId}`);
  },
};
