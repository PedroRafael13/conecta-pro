/**
 * Service Layer - Integration Settings
 * Gestão de Configurações de Integrações
 */

import { axiosInstance } from '@/lib/axios-instance';
import type {
  IntegrationSettingsCreate,
  IntegrationSettingsUpdate,
  IntegrationSettingsResponse,
} from '@/types/generated/clients/conectaPROMóduloCLIENTS.schemas';

const BASE_URL = '/api/v1/clients';

/**
 * Service de Integrações
 */
export const integrationService = {
  /**
   * Cria configuração de integração
   */
  create: async (
    clientId: string,
    data: IntegrationSettingsCreate
  ): Promise<IntegrationSettingsResponse> => {
    const response = await axiosInstance.post<IntegrationSettingsResponse>(
      `${BASE_URL}/${clientId}/integrations`,
      data
    );
    return response.data;
  },

  /**
   * Lista integrações do cliente
   */
  list: async (clientId: string): Promise<IntegrationSettingsResponse[]> => {
    const response = await axiosInstance.get<IntegrationSettingsResponse[]>(
      `${BASE_URL}/${clientId}/integrations`
    );
    return response.data;
  },

  /**
   * Obtém integração por ID
   */
  getById: async (settingsId: string): Promise<IntegrationSettingsResponse> => {
    const response = await axiosInstance.get<IntegrationSettingsResponse>(
      `${BASE_URL}/integrations/${settingsId}`
    );
    return response.data;
  },

  /**
   * Atualiza integração
   */
  update: async (
    settingsId: string,
    data: IntegrationSettingsUpdate
  ): Promise<IntegrationSettingsResponse> => {
    const response = await axiosInstance.put<IntegrationSettingsResponse>(
      `${BASE_URL}/integrations/${settingsId}`,
      data
    );
    return response.data;
  },

  /**
   * Habilita integração
   */
  enable: async (settingsId: string): Promise<IntegrationSettingsResponse> => {
    const response = await axiosInstance.post<IntegrationSettingsResponse>(
      `${BASE_URL}/integrations/${settingsId}/enable`
    );
    return response.data;
  },

  /**
   * Desabilita integração
   */
  disable: async (settingsId: string): Promise<IntegrationSettingsResponse> => {
    const response = await axiosInstance.post<IntegrationSettingsResponse>(
      `${BASE_URL}/integrations/${settingsId}/disable`
    );
    return response.data;
  },
};
