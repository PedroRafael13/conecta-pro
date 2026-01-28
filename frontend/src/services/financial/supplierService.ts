/**
 * Service: Supplier Management
 *
 * Camada de abstração para operações de fornecedores.
 * Encapsula lógica de negócio e validações.
 *
 * Cobertura: 11 endpoints
 * - CRUD completo de fornecedores
 * - Busca e filtros avançados
 * - Qualificação e bloqueio
 * - Estatísticas e reports
 */

import { getFinancialSuppliers } from '@/types/generated/financial/financial-suppliers/financial-suppliers';
import type {
  SupplierCreate,
  SupplierUpdate,
  SupplierResponse,
  SupplierListResponse,
  SupplierStats,
  ListSuppliersApiV1FinancialSuppliersSuppliersGetParams,
  GetStatsApiV1FinancialSuppliersSuppliersStatsGetParams,
  SearchSuppliersApiV1FinancialSuppliersSuppliersSearchGetParams,
  QualifySupplierApiV1FinancialSuppliersSuppliersSupplierIdQualifyPostBody,
  SupplierBlockRequest,
} from '@/types/generated/financial/models';

const suppliers = getFinancialSuppliers();

/**
 * Interface para parâmetros de listagem
 */
export interface ListSuppliersParams {
  skip?: number;
  limit?: number;
  status?: string;
  supplier_type?: string;
  search?: string;
  sort?: string;
  order?: 'asc' | 'desc';
}

/**
 * Service de Fornecedores
 */
export const supplierService = {
  /**
   * Criar novo fornecedor
   */
  async create(data: SupplierCreate): Promise<SupplierResponse> {
    const response = await suppliers.createSupplierApiV1FinancialSuppliersSuppliersPost(
      data
    );
    return response.data;
  },

  /**
   * Listar fornecedores com filtros
   */
  async list(
    params: ListSuppliersParams = {}
  ): Promise<SupplierListResponse[]> {
    const response = await suppliers.listSuppliersApiV1FinancialSuppliersSuppliersGet(
      params as ListSuppliersApiV1FinancialSuppliersSuppliersGetParams
    );
    return response.data;
  },

  /**
   * Buscar fornecedor por ID
   */
  async getById(supplierId: string): Promise<SupplierResponse> {
    const response = await suppliers.getSupplierApiV1FinancialSuppliersSuppliersSupplierIdGet(
      supplierId
    );
    return response.data;
  },

  /**
   * Atualizar fornecedor
   */
  async update(
    supplierId: string,
    data: SupplierUpdate
  ): Promise<SupplierResponse> {
    const response = await suppliers.updateSupplierApiV1FinancialSuppliersSuppliersSupplierIdPut(
      supplierId,
      data
    );
    return response.data;
  },

  /**
   * Deletar fornecedor
   */
  async delete(supplierId: string): Promise<void> {
    await suppliers.deleteSupplierApiV1FinancialSuppliersSuppliersSupplierIdDelete(
      supplierId
    );
  },

  /**
   * Busca rápida de fornecedores
   */
  async search(params: {
    q: string;
    limit?: number;
  }): Promise<SupplierListResponse[]> {
    const response = await suppliers.searchSuppliersApiV1FinancialSuppliersSuppliersSearchGet(
      params as SearchSuppliersApiV1FinancialSuppliersSuppliersSearchGetParams
    );
    return response.data;
  },

  /**
   * Obter estatísticas de fornecedores
   */
  async getStats(params: {
    condominio_id: string;
  }): Promise<SupplierStats> {
    const response = await suppliers.getStatsApiV1FinancialSuppliersSuppliersStatsGet(
      params as GetStatsApiV1FinancialSuppliersSuppliersStatsGetParams
    );
    return response.data;
  },

  /**
   * Qualificar fornecedor
   */
  async qualify(
    supplierId: string,
    data: QualifySupplierApiV1FinancialSuppliersSuppliersSupplierIdQualifyPostBody
  ): Promise<SupplierResponse> {
    const response = await suppliers.qualifySupplierApiV1FinancialSuppliersSuppliersSupplierIdQualifyPost(
      supplierId,
      data
    );
    return response.data;
  },

  /**
   * Bloquear fornecedor
   */
  async block(
    supplierId: string,
    data: SupplierBlockRequest
  ): Promise<SupplierResponse> {
    const response = await suppliers.blockSupplierApiV1FinancialSuppliersSuppliersSupplierIdBlockPost(
      supplierId,
      data
    );
    return response.data;
  },

  /**
   * Desbloquear fornecedor
   */
  async unblock(supplierId: string): Promise<SupplierResponse> {
    const response = await suppliers.unblockSupplierApiV1FinancialSuppliersSuppliersSupplierIdUnblockPost(
      supplierId
    );
    return response.data;
  },

  /**
   * Obter histórico do fornecedor
   */
  async getHistory(supplierId: string): Promise<any> {
    const response = await suppliers.getSupplierHistoryApiV1FinancialSuppliersSuppliersSupplierIdHistoryGet(
      supplierId
    );
    return response.data;
  },
};

export default supplierService;
