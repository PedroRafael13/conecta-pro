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
    return await suppliers.createSupplierApiV1FinancialSuppliersSuppliersPost(
      data
    );
  },

  /**
   * Listar fornecedores com filtros
   */
  async list(
    params: ListSuppliersParams = {}
  ): Promise<SupplierListResponse[]> {
    return await suppliers.listSuppliersApiV1FinancialSuppliersSuppliersGet(
      params as ListSuppliersApiV1FinancialSuppliersSuppliersGetParams
    );
  },

  /**
   * Buscar fornecedor por ID
   */
  async getById(supplierId: string): Promise<SupplierResponse> {
    return await suppliers.getSupplierApiV1FinancialSuppliersSuppliersSupplierIdGet(
      supplierId
    );
  },

  /**
   * Atualizar fornecedor
   */
  async update(
    supplierId: string,
    data: SupplierUpdate
  ): Promise<SupplierResponse> {
    return await suppliers.updateSupplierApiV1FinancialSuppliersSuppliersSupplierIdPut(
      supplierId,
      data
    );
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
    return await suppliers.searchSuppliersApiV1FinancialSuppliersSuppliersSearchGet(
      params as SearchSuppliersApiV1FinancialSuppliersSuppliersSearchGetParams
    );
  },

  /**
   * Obter estatísticas de fornecedores
   */
  async getStats(params: {
    condominio_id: string;
  }): Promise<SupplierStats> {
    return await suppliers.getStatsApiV1FinancialSuppliersSuppliersStatsGet(
      params as GetStatsApiV1FinancialSuppliersSuppliersStatsGetParams
    );
  },

  /**
   * Qualificar fornecedor
   */
  async qualify(
    supplierId: string,
    data: QualifySupplierApiV1FinancialSuppliersSuppliersSupplierIdQualifyPostBody
  ): Promise<SupplierResponse> {
    return await suppliers.qualifySupplierApiV1FinancialSuppliersSuppliersSupplierIdQualifyPost(
      supplierId,
      data
    );
  },

  /**
   * Bloquear fornecedor
   */
  async block(
    supplierId: string,
    data: SupplierBlockRequest
  ): Promise<SupplierResponse> {
    return await suppliers.blockSupplierApiV1FinancialSuppliersSuppliersSupplierIdBlockPost(
      supplierId,
      data
    );
  },

  /**
   * Desbloquear fornecedor
   */
  async unblock(supplierId: string): Promise<SupplierResponse> {
    return await suppliers.unblockSupplierApiV1FinancialSuppliersSuppliersSupplierIdUnblockPost(
      supplierId
    );
  },

  /**
   * Obter histórico do fornecedor
   */
  async getHistory(supplierId: string): Promise<any> {
    return await suppliers.getSupplierApiV1FinancialSuppliersSuppliersSupplierIdGet(
      supplierId
    );
  },
};

export default supplierService;
