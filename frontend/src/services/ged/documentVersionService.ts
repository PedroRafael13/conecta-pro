import api from '@/lib/api';

export const documentVersionService = {
  async getVersions(documentId: string) {
    const response = await api.get(`/api/v1/ged/documents/${documentId}/versions`);
    return response.data;
  },

  async getVersion(documentId: string, versionId: string) {
    const response = await api.get(`/api/v1/ged/documents/${documentId}/versions/${versionId}`);
    return response.data;
  },

  async createVersion(documentId: string, formData: FormData) {
    const response = await api.post(`/api/v1/ged/documents/${documentId}/versions`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async restoreVersion(documentId: string, versionId: string) {
    const response = await api.post(`/api/v1/ged/documents/${documentId}/versions/${versionId}/restore`);
    return response.data;
  },

  async downloadVersion(documentId: string, versionId: string) {
    const response = await api.get(`/api/v1/ged/documents/${documentId}/versions/${versionId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  async compareVersions(documentId: string, version1Id: string, version2Id: string) {
    const response = await api.get(`/api/v1/ged/documents/${documentId}/versions/compare`, {
      params: {
        version1: version1Id,
        version2: version2Id,
      },
    });
    return response.data;
  },

  async setCurrent(versionId: string) {
    const response = await api.post(`/api/v1/ged/document-versions/${versionId}/set-current`);
    return response.data;
  },

  async archive(versionId: string) {
    const response = await api.post(`/api/v1/ged/document-versions/${versionId}/archive`);
    return response.data;
  },

  async delete(versionId: string) {
    const response = await api.delete(`/api/v1/ged/document-versions/${versionId}`);
    return response.data;
  },

  async listByDocument(documentId: string) {
    const response = await api.get(`/api/v1/ged/documents/${documentId}/versions`);
    return response.data;
  },

  async compare(documentId: string, versionA: number, versionB: number) {
    const response = await api.get(`/api/v1/ged/document-versions/document/${documentId}/compare`, {
      params: { version_a: versionA, version_b: versionB },
    });
    return response.data;
  },
};
