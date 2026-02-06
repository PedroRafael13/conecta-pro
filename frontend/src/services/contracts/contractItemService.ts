/**
 * Service Layer - Contract Items
 * Gestão de Itens/Serviços do Contrato
 */

import { customInstance } from '@/lib/axios-instance';
import type {
  ContractItemCreate,
  ContractItemUpdate,
  ContractItemResponse,
} from '@/types/generated/contracts/cRMContractsAPI.schemas';

const BASE_URL = '/api/v1/contracts';

/**
 * Service de Itens do Contrato
 */
export const contractItemService = {
  /**
   * Adiciona item ao contrato
   */
  add: async (
    contractId: string,
    data: ContractItemCreate
  ): Promise<ContractItemResponse> => {
    return await customInstance.post<ContractItemResponse>(
      `${BASE_URL}/${contractId}/items`,
      data
    );
  },

  /**
   * Atualiza item do contrato
   */
  update: async (
    contractId: string,
    itemId: string,
    data: ContractItemUpdate
  ): Promise<ContractItemResponse> => {
    return await customInstance.put<ContractItemResponse>(
      `${BASE_URL}/${contractId}/items/${itemId}`,
      data
    );
  },

  /**
   * Remove item do contrato
   */
  remove: async (contractId: string, itemId: string): Promise<void> => {
    await customInstance.delete(`${BASE_URL}/${contractId}/items/${itemId}`);
  },
};
