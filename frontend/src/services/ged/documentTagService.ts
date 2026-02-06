import api from '@/lib/api';

export const documentTagService = {
  async getTags() {
    const response = await api.get('/api/v1/ged/tags');
    return response.data;
  },

  async createTag(data: any) {
    const response = await api.post('/api/v1/ged/tags', data);
    return response.data;
  },

  async updateTag(id: string, data: any) {
    const response = await api.put(`/api/v1/ged/tags/${id}`, data);
    return response.data;
  },

  async deleteTag(id: string) {
    const response = await api.delete(`/api/v1/ged/tags/${id}`);
    return response.data;
  },

  async addTagToDocument(documentId: string, tagId: string) {
    const response = await api.post(`/api/v1/ged/documents/${documentId}/tags/${tagId}`);
    return response.data;
  },

  async removeTagFromDocument(documentId: string, tagId: string) {
    const response = await api.delete(`/api/v1/ged/documents/${documentId}/tags/${tagId}`);
    return response.data;
  },
};
