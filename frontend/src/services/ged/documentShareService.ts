import api from '@/lib/api';

export const documentShareService = {
  async getShares(documentId: string) {
    const response = await api.get(`/api/v1/ged/documents/${documentId}/shares`);
    return response.data;
  },

  async shareDocument(documentId: string, data: any) {
    const response = await api.post(`/api/v1/ged/documents/${documentId}/shares`, data);
    return response.data;
  },

  async updateShare(documentId: string, shareId: string, data: any) {
    const response = await api.put(`/api/v1/ged/documents/${documentId}/shares/${shareId}`, data);
    return response.data;
  },

  async revokeShare(documentId: string, shareId: string) {
    const response = await api.delete(`/api/v1/ged/documents/${documentId}/shares/${shareId}`);
    return response.data;
  },

  async getPublicLink(documentId: string) {
    const response = await api.post(`/api/v1/ged/documents/${documentId}/shares/public-link`);
    return response.data;
  },
};
