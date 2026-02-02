import api from '@/lib/api';

export const folderService = {
  async getFolders() {
    const response = await api.get('/api/v1/ged/folders');
    return response.data;
  },

  async getFolder(id: string) {
    const response = await api.get(`/api/v1/ged/folders/${id}`);
    return response.data;
  },

  async createFolder(data: any) {
    const response = await api.post('/api/v1/ged/folders', data);
    return response.data;
  },

  async updateFolder(id: string, data: any) {
    const response = await api.put(`/api/v1/ged/folders/${id}`, data);
    return response.data;
  },

  async deleteFolder(id: string) {
    const response = await api.delete(`/api/v1/ged/folders/${id}`);
    return response.data;
  },

  async moveFolder(id: string, targetFolderId: string) {
    const response = await api.post(`/api/v1/ged/folders/${id}/move`, {
      target_folder_id: targetFolderId,
    });
    return response.data;
  },
};
