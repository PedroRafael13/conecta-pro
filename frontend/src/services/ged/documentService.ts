import api from '@/lib/api';

export const documentService = {
  async getDocument(id: string) {
    const response = await api.get(`/api/v1/ged/documents/${id}`);
    return response.data;
  },

  async updateDocument(id: string, data: any) {
    const response = await api.put(`/api/v1/ged/documents/${id}`, data);
    return response.data;
  },

  async deleteDocument(id: string) {
    const response = await api.delete(`/api/v1/ged/documents/${id}`);
    return response.data;
  },

  async uploadDocument(formData: FormData) {
    const response = await api.post('/api/v1/ged/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async downloadDocument(id: string) {
    const response = await api.get(`/api/v1/ged/documents/${id}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },
};
