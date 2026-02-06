import api from '@/lib/api';
import type { AllocationCreate } from '@/types/operacional';

const BASE_URL = '/api/v1/operacional/allocations';

export const allocationsService = {
  async list(params?: Record<string, unknown>) {
    const response = await api.get(BASE_URL, { params });
    return response.data;
  },

  async get(id: string) {
    const response = await api.get(`${BASE_URL}/${id}`);
    return response.data;
  },

  async create(data: AllocationCreate) {
    const response = await api.post(BASE_URL, data);
    return response.data;
  },

  async update(id: string, data: Partial<AllocationCreate>) {
    const response = await api.put(`${BASE_URL}/${id}`, data);
    return response.data;
  },

  async delete(id: string) {
    const response = await api.delete(`${BASE_URL}/${id}`);
    return response.data;
  },
};
