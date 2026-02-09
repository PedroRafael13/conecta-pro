import api from '@/lib/api';

const BASE = '/api/v1/reimbursements';

export const reimbursementService = {
  async create(data: unknown) {
    const response = await api.post(BASE, data);
    return response.data;
  },

  async update(requestId: string, data: unknown) {
    const response = await api.put(`${BASE}/${requestId}`, data);
    return response.data;
  },

  async submit(requestId: string) {
    const response = await api.post(`${BASE}/${requestId}/submit`);
    return response.data;
  },

  async cancel(requestId: string) {
    const response = await api.post(`${BASE}/${requestId}/cancel`);
    return response.data;
  },

  async addItem(requestId: string, item: unknown) {
    const response = await api.post(`${BASE}/${requestId}/items`, item);
    return response.data;
  },

  async deleteItem(requestId: string, itemId: string) {
    const response = await api.delete(`${BASE}/${requestId}/items/${itemId}`);
    return response.data;
  },

  async uploadAttachment(requestId: string, file: File, options?: { description?: string }) {
    const formData = new FormData();
    formData.append('file', file);
    if (options?.description) {
      formData.append('description', options.description);
    }
    const response = await api.post(`${BASE}/${requestId}/attachments`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  getAttachmentDownloadUrl(attachmentId: string) {
    return `${BASE}/attachments/${attachmentId}/download`;
  },

  async approve(requestId: string, data: unknown) {
    const response = await api.post(`${BASE}/${requestId}/approve`, data);
    return response.data;
  },

  async reject(requestId: string, data: unknown) {
    const response = await api.post(`${BASE}/${requestId}/reject`, data);
    return response.data;
  },

  async returnToDraft(requestId: string, data: unknown) {
    const response = await api.post(`${BASE}/${requestId}/return`, data);
    return response.data;
  },
};
