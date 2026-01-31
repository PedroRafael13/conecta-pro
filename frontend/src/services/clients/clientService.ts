/**
 * Service Layer - Client Management
 * Gestão de Clientes com cobertura completa
 */

import { axiosInstance } from '@/lib/axios-instance';
import type {
  ClientCreate,
  ClientUpdate,
  ClientResponse,
  ClientListResponse,
  ClientStats,
//   ClientFilter,  // TODO: Tipo não existe na API
} from '@/types/generated/clients/conectaPROMóduloCLIENTS.schemas';

const BASE_URL = '/api/v1/clients';

/**
 * Service de Clientes
 */
export const clientService = {
  /**
   * Cria novo cliente
   */
  create: async (data: ClientCreate): Promise<ClientResponse> => {
    const response = await axiosInstance.post<ClientResponse>(BASE_URL, data);
    return response.data;
  },

  /**
   * Lista clientes com filtros
   */
  list: async (params?: {
    skip?: number;
    limit?: number;
    type?: string;
    status?: string;
    segment?: string;
    is_defaulter?: boolean;
    is_vip?: boolean;
    guardian_enabled?: boolean;
    plus_enabled?: boolean;
    city?: string;
    state?: string;
    search?: string;
    order_by?: string;
    order_desc?: boolean;
  }): Promise<ClientListResponse[]> => {
    const response = await axiosInstance.get<ClientListResponse[]>(BASE_URL, {
      params,
    });
    return response.data;
  },

  /**
   * Obtém estatísticas de clientes
   */
  getStats: async (): Promise<ClientStats> => {
    const response = await axiosInstance.get<ClientStats>(`${BASE_URL}/stats`);
    return response.data;
  },

  /**
   * Obtém cliente por ID
   */
  getById: async (clientId: string): Promise<ClientResponse> => {
    const response = await axiosInstance.get<ClientResponse>(
      `${BASE_URL}/${clientId}`
    );
    return response.data;
  },

  /**
   * Obtém cliente com todas as relações
   */
  getFullById: async (clientId: string): Promise<ClientResponse> => {
    const response = await axiosInstance.get<ClientResponse>(
      `${BASE_URL}/${clientId}/full`
    );
    return response.data;
  },

  /**
   * Atualiza cliente
   */
  update: async (
    clientId: string,
    data: ClientUpdate
  ): Promise<ClientResponse> => {
    const response = await axiosInstance.put<ClientResponse>(
      `${BASE_URL}/${clientId}`,
      data
    );
    return response.data;
  },

  /**
   * Remove cliente
   */
  delete: async (clientId: string): Promise<void> => {
    await axiosInstance.delete(`${BASE_URL}/${clientId}`);
  },

  /**
   * Ativa cliente
   */
  activate: async (clientId: string): Promise<ClientResponse> => {
    const response = await axiosInstance.post<ClientResponse>(
      `${BASE_URL}/${clientId}/activate`
    );
    return response.data;
  },

  /**
   * Suspende cliente
   */
  suspend: async (
    clientId: string,
    reason?: string
  ): Promise<ClientResponse> => {
    const response = await axiosInstance.post<ClientResponse>(
      `${BASE_URL}/${clientId}/suspend`,
      null,
      { params: { reason } }
    );
    return response.data;
  },

  /**
   * Bloqueia cliente
   */
  block: async (clientId: string, reason?: string): Promise<ClientResponse> => {
    const response = await axiosInstance.post<ClientResponse>(
      `${BASE_URL}/${clientId}/block`,
      null,
      { params: { reason } }
    );
    return response.data;
  },

  /**
   * Marca cliente como inadimplente
   */
  setDefaulter: async (
    clientId: string,
    debtAmount: number
  ): Promise<ClientResponse> => {
    const response = await axiosInstance.post<ClientResponse>(
      `${BASE_URL}/${clientId}/set-defaulter`,
      null,
      { params: { debt_amount: debtAmount } }
    );
    return response.data;
  },

  /**
   * Remove status de inadimplente
   */
  clearDefaulter: async (clientId: string): Promise<ClientResponse> => {
    const response = await axiosInstance.post<ClientResponse>(
      `${BASE_URL}/${clientId}/clear-defaulter`
    );
    return response.data;
  },

  /**
   * Habilita integração com Guardian
   */
  enableGuardian: async (
    clientId: string,
    guardianClientId: string
  ): Promise<ClientResponse> => {
    const response = await axiosInstance.post<ClientResponse>(
      `${BASE_URL}/${clientId}/enable-guardian`,
      null,
      { params: { guardian_client_id: guardianClientId } }
    );
    return response.data;
  },

  /**
   * Habilita integração com Conecta Plus
   */
  enablePlus: async (
    clientId: string,
    plusClientId: string
  ): Promise<ClientResponse> => {
    const response = await axiosInstance.post<ClientResponse>(
      `${BASE_URL}/${clientId}/enable-plus`,
      null,
      { params: { plus_client_id: plusClientId } }
    );
    return response.data;
  },
};
