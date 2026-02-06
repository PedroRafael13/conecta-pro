import api from '@/lib/api';

export const occurrencesService = {
  async getOccurrences(params?: any) {
    const response = await api.get('/api/v1/operacional/occurrences', { params });
    return response.data;
  },

  async getOccurrence(id: string) {
    const response = await api.get(`/api/v1/operacional/occurrences/${id}`);
    return response.data;
  },

  async createOccurrence(data: any) {
    const response = await api.post('/api/v1/operacional/occurrences', data);
    return response.data;
  },

  async updateOccurrence(id: string, data: any) {
    const response = await api.put(`/api/v1/operacional/occurrences/${id}`, data);
    return response.data;
  },

  async resolveOccurrence(id: string, data: any) {
    const response = await api.post(`/api/v1/operacional/occurrences/${id}/resolve`, data);
    return response.data;
  },

  async deleteOccurrence(id: string) {
    const response = await api.delete(`/api/v1/operacional/occurrences/${id}`);
    return response.data;
  },

  async addComment(id: string, comment: string) {
    const response = await api.post(`/api/v1/operacional/occurrences/${id}/comments`, {
      comment,
    });
    return response.data;
  },

  async uploadAttachment(id: string, file: File) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post(`/api/v1/operacional/occurrences/${id}/attachments`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Aliases for component compatibility
  async create(data: unknown) {
    const response = await api.post('/api/v1/operacional/occurrences', data);
    return response.data;
  },

  async update(id: string, data: unknown) {
    const response = await api.put(`/api/v1/operacional/occurrences/${id}`, data);
    return response.data;
  },

  async resolve(id: string, data: unknown) {
    const response = await api.post(`/api/v1/operacional/occurrences/${id}/resolve`, data);
    return response.data;
  },
};
