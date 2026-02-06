/**
 * Service Layer - Reimbursement Attachments
 *
 * Gerencia anexos/comprovantes de reembolso
 * Cobertura: 4 endpoints de anexos
 */

import { apiClient } from '@/lib/api/client';
import type { ReimbursementAttachmentResponse } from '@/types/generated/reimbursement/models';

const BASE_URL = '/api/v1/reimbursements';

export const reimbursementAttachmentService = {
  /**
   * Upload de comprovante/anexo
   * Suporta: JPEG, PNG, GIF, WebP, PDF (máx 10MB)
   */
  async upload(
    requestId: string,
    file: File,
    options?: {
      itemId?: string;
      attachmentType?: string;
      description?: string;
    }
  ): Promise<ReimbursementAttachmentResponse> {
    const formData = new FormData();
    formData.append('file', file);

    if (options?.itemId) {
      formData.append('item_id', options.itemId);
    }
    if (options?.attachmentType) {
      formData.append('attachment_type', options.attachmentType);
    }
    if (options?.description) {
      formData.append('description', options.description);
    }

    const response = await apiClient.post<ReimbursementAttachmentResponse>(
      `${BASE_URL}/${requestId}/attachments`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  /**
   * Lista anexos de uma solicitação
   */
  async list(requestId: string, itemId?: string): Promise<ReimbursementAttachmentResponse[]> {
    const response = await apiClient.get<ReimbursementAttachmentResponse[]>(
      `${BASE_URL}/${requestId}/attachments`,
      {
        params: { item_id: itemId },
      }
    );
    return response.data;
  },

  /**
   * Remove um anexo
   */
  async delete(attachmentId: string): Promise<void> {
    await apiClient.delete(`${BASE_URL}/attachments/${attachmentId}`);
  },

  /**
   * Download de anexo
   * Retorna URL para download
   */
  getDownloadUrl(attachmentId: string): string {
    return `${BASE_URL}/attachments/${attachmentId}/download`;
  },

  /**
   * Download de anexo via blob
   */
  async download(attachmentId: string): Promise<Blob> {
    const response = await apiClient.get<Blob>(`${BASE_URL}/attachments/${attachmentId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },
};
