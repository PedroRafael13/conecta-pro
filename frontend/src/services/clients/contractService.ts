/**
 * Service Layer - Contract Management
 * Gestão de Contratos de Clientes
 */

import { axiosInstance } from '@/lib/axios-instance';
import type {
  ClientContractCreate,
  ClientContractUpdate,
  ClientContractResponse,
} from '@/types/generated/clients/conectaPROMóduloCLIENTS.schemas';

const BASE_URL = '/api/v1/clients';

/**
 * Service de Contratos
 */
export const contractService = {
  /**
   * Cria novo contrato
   */
  create: async (
    clientId: string,
    data: ClientContractCreate
  ): Promise<ClientContractResponse> => {
    const response = await axiosInstance.post<ClientContractResponse>(
      `${BASE_URL}/${clientId}/contracts`,
      data
    );
    return response.data;
  },

  /**
   * Lista contratos do cliente
   */
  list: async (
    clientId: string,
    params?: {
      skip?: number;
      limit?: number;
    }
  ): Promise<ClientContractResponse[]> => {
    const response = await axiosInstance.get<ClientContractResponse[]>(
      `${BASE_URL}/${clientId}/contracts`,
      { params }
    );
    return response.data;
  },

  /**
   * Obtém contrato por ID
   */
  getById: async (contractId: string): Promise<ClientContractResponse> => {
    const response = await axiosInstance.get<ClientContractResponse>(
      `${BASE_URL}/contracts/${contractId}`
    );
    return response.data;
  },

  /**
   * Atualiza contrato
   */
  update: async (
    contractId: string,
    data: ClientContractUpdate
  ): Promise<ClientContractResponse> => {
    const response = await axiosInstance.put<ClientContractResponse>(
      `${BASE_URL}/contracts/${contractId}`,
      data
    );
    return response.data;
  },

  /**
   * Ativa contrato
   */
  activate: async (contractId: string): Promise<ClientContractResponse> => {
    const response = await axiosInstance.post<ClientContractResponse>(
      `${BASE_URL}/contracts/${contractId}/activate`
    );
    return response.data;
  },

  /**
   * Suspende contrato
   */
  suspend: async (
    contractId: string,
    reason?: string
  ): Promise<ClientContractResponse> => {
    const response = await axiosInstance.post<ClientContractResponse>(
      `${BASE_URL}/contracts/${contractId}/suspend`,
      null,
      { params: { reason } }
    );
    return response.data;
  },

  /**
   * Cancela contrato
   */
  cancel: async (
    contractId: string,
    reason?: string
  ): Promise<ClientContractResponse> => {
    const response = await axiosInstance.post<ClientContractResponse>(
      `${BASE_URL}/contracts/${contractId}/cancel`,
      null,
      { params: { reason } }
    );
    return response.data;
  },
};
