import api from '@/lib/api';

export const documentSignatureService = {
  async getSignatures(documentId: string) {
    const response = await api.get(`/api/v1/ged/documents/${documentId}/signatures`);
    return response.data;
  },

  async requestSignature(documentId: string, data: any) {
    const response = await api.post(`/api/v1/ged/documents/${documentId}/signatures/request`, data);
    return response.data;
  },

  async sign(documentId: string, signatureId: string, data: any) {
    const response = await api.post(`/api/v1/ged/documents/${documentId}/signatures/${signatureId}/sign`, data);
    return response.data;
  },

  async verifySignature(documentId: string, signatureId: string) {
    const response = await api.get(`/api/v1/ged/documents/${documentId}/signatures/${signatureId}/verify`);
    return response.data;
  },
};
