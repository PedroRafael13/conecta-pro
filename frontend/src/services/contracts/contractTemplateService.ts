/**
 * Service Layer - Contract Templates
 * Gestão de Templates de Contrato
 */

import { customInstance } from '@/lib/axios-instance';
import type {
  ContractTemplateCreate,
  ContractTemplateUpdate,
  ContractTemplateResponse,
  ContractTemplateListResponse,
} from '@/types/generated/contracts/cRMContractsAPI.schemas';

const BASE_URL = '/api/v1/contracts/templates';

/**
 * Service de Templates de Contrato
 */
export const contractTemplateService = {
  /**
   * Cria template de contrato
   */
  create: async (
    data: ContractTemplateCreate
  ): Promise<ContractTemplateResponse> => {
    return await customInstance.post<ContractTemplateResponse>(
      BASE_URL,
      data
    );
  },

  /**
   * Lista templates de contrato
   */
  list: async (params?: {
    service_type?: string;
    approved_only?: boolean;
  }): Promise<ContractTemplateListResponse> => {
    return await customInstance.get<ContractTemplateListResponse>(
      BASE_URL,
      { params }
    );
  },

  /**
   * Obtém template por ID
   */
  getById: async (templateId: string): Promise<ContractTemplateResponse> => {
    return await customInstance.get<ContractTemplateResponse>(
      `${BASE_URL}/${templateId}`
    );
  },

  /**
   * Atualiza template
   */
  update: async (
    templateId: string,
    data: ContractTemplateUpdate
  ): Promise<ContractTemplateResponse> => {
    return await customInstance.put<ContractTemplateResponse>(
      `${BASE_URL}/${templateId}`,
      data
    );
  },

  /**
   * Aprova template juridicamente
   */
  approve: async (templateId: string): Promise<ContractTemplateResponse> => {
    return await customInstance.post<ContractTemplateResponse>(
      `${BASE_URL}/${templateId}/approve`
    );
  },

  /**
   * Remove template (soft delete)
   */
  delete: async (templateId: string): Promise<void> => {
    await customInstance.delete(`${BASE_URL}/${templateId}`);
  },
};
