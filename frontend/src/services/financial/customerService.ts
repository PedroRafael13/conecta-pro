/**
 * Service: Customer Management
 *
 * Gestao de Clientes (Contas a Receber).
 * Cobertura: 12 endpoints
 */

import { getFinancialCustomers } from '@/types/generated/financial/financial-customers/financial-customers';
import type {
  CustomerCreate,
  CustomerUpdate,
  ListCustomersApiV1FinancialCustomersCustomersGetParams,
  ListDebtorsApiV1FinancialCustomersCustomersDebtorsGetParams,
  BlockCustomerApiV1FinancialCustomersCustomersCustomerIdBlockPostParams,
} from '@/types/generated/financial/models';

const customers = getFinancialCustomers();

export const customerService = {
  async create(data: CustomerCreate) {
    return await customers.createCustomerApiV1FinancialCustomersCustomersPost(
      data
    );
  },

  async list(params: ListCustomersApiV1FinancialCustomersCustomersGetParams) {
    return await customers.listCustomersApiV1FinancialCustomersCustomersGet(
      params
    );
  },

  async getById(customerId: string) {
    return await customers.getCustomerApiV1FinancialCustomersCustomersCustomerIdGet(
      customerId
    );
  },

  async update(customerId: string, data: CustomerUpdate) {
    return await customers.updateCustomerApiV1FinancialCustomersCustomersCustomerIdPut(
      customerId,
      data
    );
  },

  async delete(customerId: string) {
    return await customers.deleteCustomerApiV1FinancialCustomersCustomersCustomerIdDelete(
      customerId
    );
  },

  async listDebtors(
    params: ListDebtorsApiV1FinancialCustomersCustomersDebtorsGetParams
  ) {
    return await customers.listDebtorsApiV1FinancialCustomersCustomersDebtorsGet(
      params
    );
  },

  async getByDocument(document: string) {
    return await customers.getCustomerByDocumentApiV1FinancialCustomersCustomersDocumentDocumentGet(
      document
    );
  },

  async getByMorador(moradorId: string) {
    return await customers.getCustomerByMoradorApiV1FinancialCustomersCustomersMoradorMoradorIdGet(
      moradorId
    );
  },

  async getByUnidade(unidadeId: string) {
    return await customers.getCustomersByUnidadeApiV1FinancialCustomersCustomersUnidadeUnidadeIdGet(
      unidadeId
    );
  },

  async block(
    customerId: string,
    params: BlockCustomerApiV1FinancialCustomersCustomersCustomerIdBlockPostParams
  ) {
    return await customers.blockCustomerApiV1FinancialCustomersCustomersCustomerIdBlockPost(
      customerId,
      params
    );
  },

  async unblock(customerId: string) {
    return await customers.unblockCustomerApiV1FinancialCustomersCustomersCustomerIdUnblockPost(
      customerId
    );
  },

  async getDebtSummary(customerId: string) {
    return await customers.getCustomerDebtSummaryApiV1FinancialCustomersCustomersCustomerIdDebtSummaryGet(
      customerId
    );
  },
};

export default customerService;
