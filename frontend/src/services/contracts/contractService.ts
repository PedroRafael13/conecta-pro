/**
 * Service Layer - Contract Management
 * Gestão de Contratos CRM com cobertura completa
 */

import { customInstance } from '@/lib/axios-instance';
import type {
  ContractCreate,
  ContractUpdate,
  ContractResponse,
  ContractDetailResponse,
  ContractListResponse,
  ContractStats,
  ContractAlert,
  ContractRenewal,
  RenewalResult,
  AdjustmentResult,
} from '@/types/generated/contracts/cRMContractsAPI.schemas';

const BASE_URL = '/api/v1/contracts';

/**
 * Service principal de Contratos
 */
export const contractService = {
  /**
   * Cria novo contrato
   */
  create: async (data: ContractCreate): Promise<ContractDetailResponse> => {
    return await customInstance.post<ContractDetailResponse>(
      BASE_URL,
      data
    );
  },

  /**
   * Lista contratos com filtros e paginação
   */
  list: async (params?: {
    page?: number;
    page_size?: number;
    status?: string;
    contract_type?: string;
    client_id?: string;
    commercial_manager_id?: string;
    account_manager_id?: string;
    has_sla?: boolean;
    min_value?: number;
    max_value?: number;
    search?: string;
  }): Promise<ContractListResponse> => {
    return await customInstance.get<ContractListResponse>(BASE_URL, {
      params,
    });
  },

  /**
   * Obtém estatísticas de contratos
   */
  getStats: async (params?: {
    client_id?: string;
    commercial_manager_id?: string;
  }): Promise<ContractStats> => {
    return await customInstance.get<ContractStats>(
      `${BASE_URL}/stats`,
      { params }
    );
  },

  /**
   * Obtém alertas de contratos (vencimento, reajuste)
   */
  getAlerts: async (params?: {
    days_ahead?: number;
  }): Promise<ContractAlert[]> => {
    return await customInstance.get<ContractAlert[]>(
      `${BASE_URL}/alerts`,
      { params }
    );
  },

  /**
   * Obtém contrato por ID
   */
  getById: async (contractId: string): Promise<ContractDetailResponse> => {
    return await customInstance.get<ContractDetailResponse>(
      `${BASE_URL}/${contractId}`
    );
  },

  /**
   * Atualiza contrato
   */
  update: async (
    contractId: string,
    data: ContractUpdate
  ): Promise<ContractDetailResponse> => {
    return await customInstance.put<ContractDetailResponse>(
      `${BASE_URL}/${contractId}`,
      data
    );
  },

  /**
   * Envia contrato para assinatura (DRAFT -> PENDING_SIGNATURE)
   */
  submit: async (contractId: string): Promise<ContractResponse> => {
    return await customInstance.post<ContractResponse>(
      `${BASE_URL}/${contractId}/submit`
    );
  },

  /**
   * Ativa contrato após assinatura (PENDING_SIGNATURE -> ACTIVE)
   */
  activate: async (contractId: string): Promise<ContractResponse> => {
    return await customInstance.post<ContractResponse>(
      `${BASE_URL}/${contractId}/activate`
    );
  },

  /**
   * Suspende contrato ativo
   */
  suspend: async (
    contractId: string,
    reason?: string
  ): Promise<ContractResponse> => {
    return await customInstance.post<ContractResponse>(
      `${BASE_URL}/${contractId}/suspend`,
      null,
      { params: { reason } }
    );
  },

  /**
   * Encerra contrato
   */
  terminate: async (
    contractId: string,
    reason?: string
  ): Promise<ContractResponse> => {
    return await customInstance.post<ContractResponse>(
      `${BASE_URL}/${contractId}/terminate`,
      null,
      { params: { reason } }
    );
  },

  /**
   * Calcula renovação do contrato (simulação)
   */
  calculateRenewal: async (
    contractId: string,
    data: ContractRenewal
  ): Promise<RenewalResult> => {
    return await customInstance.post<RenewalResult>(
      `${BASE_URL}/${contractId}/renew`,
      data
    );
  },

  /**
   * Calcula reajuste do contrato (simulação)
   */
  calculateAdjustment: async (
    contractId: string,
    params?: {
      custom_percent?: number;
      effective_date?: string;
    }
  ): Promise<AdjustmentResult> => {
    return await customInstance.post<AdjustmentResult>(
      `${BASE_URL}/${contractId}/calculate-adjustment`,
      null,
      { params }
    );
  },

  /**
   * Remove contrato (soft delete - apenas DRAFT)
   */
  delete: async (contractId: string): Promise<void> => {
    await customInstance.delete(`${BASE_URL}/${contractId}`);
  },
};
