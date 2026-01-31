/**
 * Service Layer - Condominium Management
 * Gestão de Condomínios
 */

import { axiosInstance } from '@/lib/axios-instance';
import type {
  CondominiumCreate,
  CondominiumUpdate,
  CondominiumResponse,
  CondominiumListResponse,
  CondominiumStats,
} from '@/types/generated/clients/conectaPROMóduloCLIENTS.schemas';

const BASE_URL = '/api/v1/clients';

/**
 * Service de Condomínios
 */
export const condominiumService = {
  /**
   * Cria novo condomínio
   */
  create: async (
    clientId: string,
    data: CondominiumCreate
  ): Promise<CondominiumResponse> => {
    const response = await axiosInstance.post<CondominiumResponse>(
      `${BASE_URL}/${clientId}/condominiums`,
      data
    );
    return response.data;
  },

  /**
   * Lista condomínios do cliente
   */
  list: async (
    clientId: string,
    params?: {
      skip?: number;
      limit?: number;
    }
  ): Promise<CondominiumListResponse[]> => {
    const response = await axiosInstance.get<CondominiumListResponse[]>(
      `${BASE_URL}/${clientId}/condominiums`,
      { params }
    );
    return response.data;
  },

  /**
   * Obtém condomínio por ID
   */
  getById: async (condominiumId: string): Promise<CondominiumResponse> => {
    const response = await axiosInstance.get<CondominiumResponse>(
      `${BASE_URL}/condominiums/${condominiumId}`
    );
    return response.data;
  },

  /**
   * Atualiza condomínio
   */
  update: async (
    condominiumId: string,
    data: CondominiumUpdate
  ): Promise<CondominiumResponse> => {
    const response = await axiosInstance.put<CondominiumResponse>(
      `${BASE_URL}/condominiums/${condominiumId}`,
      data
    );
    return response.data;
  },

  /**
   * Remove condomínio
   */
  delete: async (condominiumId: string): Promise<void> => {
    await axiosInstance.delete(`${BASE_URL}/condominiums/${condominiumId}`);
  },

  /**
   * Ativa condomínio
   */
  activate: async (condominiumId: string): Promise<CondominiumResponse> => {
    const response = await axiosInstance.post<CondominiumResponse>(
      `${BASE_URL}/condominiums/${condominiumId}/activate`
    );
    return response.data;
  },

  /**
   * Inicia implantação
   */
  startImplantation: async (
    condominiumId: string
  ): Promise<CondominiumResponse> => {
    const response = await axiosInstance.post<CondominiumResponse>(
      `${BASE_URL}/condominiums/${condominiumId}/start-implantation`
    );
    return response.data;
  },

  /**
   * Finaliza implantação
   */
  finishImplantation: async (
    condominiumId: string
  ): Promise<CondominiumResponse> => {
    const response = await axiosInstance.post<CondominiumResponse>(
      `${BASE_URL}/condominiums/${condominiumId}/finish-implantation`
    );
    return response.data;
  },

  /**
   * Obtém estatísticas de condomínios
   */
  getStats: async (clientId?: string): Promise<CondominiumStats> => {
    const response = await axiosInstance.get<CondominiumStats>(
      `${BASE_URL}/condominiums/stats`,
      { params: { client_id: clientId } }
    );
    return response.data;
  },
};
