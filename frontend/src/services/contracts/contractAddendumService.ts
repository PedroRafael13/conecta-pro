/**
 * Service Layer - Contract Addendums
 * Gestão de Aditivos Contratuais
 */

import { customInstance } from '@/lib/axios-instance';
import type {
  ContractAddendumCreate,
  ContractAddendumResponse,
  ContractAddendumSign,
} from '@/types/generated/contracts/cRMContractsAPI.schemas';

const BASE_URL = '/api/v1/contracts';

/**
 * Service de Aditivos Contratuais
 */
export const contractAddendumService = {
  /**
   * Cria aditivo do contrato
   */
  create: async (
    contractId: string,
    data: ContractAddendumCreate
  ): Promise<ContractAddendumResponse> => {
    return await customInstance.post<ContractAddendumResponse>(
      `${BASE_URL}/${contractId}/addendums`,
      data
    );
  },

  /**
   * Lista aditivos do contrato
   */
  list: async (contractId: string): Promise<ContractAddendumResponse[]> => {
    return await customInstance.get<ContractAddendumResponse[]>(
      `${BASE_URL}/${contractId}/addendums`
    );
  },

  /**
   * Assina aditivo e aplica alterações
   */
  sign: async (
    addendumId: string,
    data: ContractAddendumSign
  ): Promise<ContractAddendumResponse> => {
    return await customInstance.post<ContractAddendumResponse>(
      `${BASE_URL}/addendums/${addendumId}/sign`,
      data
    );
  },
};
