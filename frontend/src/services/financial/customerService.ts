/**
 * Service: Customer Management
 *
 * Gestão de Clientes (Contas a Receber).
 * Cobertura: 12 endpoints
 */

import { getFinancialCustomers } from '@/types/generated/financial/financial-customers/financial-customers';
import type {
  CustomerCreate,
  CustomerUpdate,
  CustomerResponse,
  ListCustomersApiV1FinancialCustomersCustomersGetParams,
} from '@/types/generated/financial/models';

const customers = getFinancialCustomers();

export const customerService = {
  async create(data: CustomerCreate): Promise<CustomerResponse> {
    const response = await customers.createCustomerApiV1FinancialCustomersCustomersPost(
      data
    );
    return response.data;
  },

  async list(
    params: ListCustomersApiV1FinancialCustomersCustomersGetParams = {}
  ) {
    const response = await customers.listCustomersApiV1FinancialCustomersCustomersGet(
      params
    );
    return response.data;
  },

  async getById(customerId: string): Promise<CustomerResponse> {
    const response = await customers.getCustomerApiV1FinancialCustomersCustomersCustomerIdGet(
      customerId
    );
    return response.data;
  },

  async update(
    customerId: string,
    data: CustomerUpdate
  ): Promise<CustomerResponse> {
    const response = await customers.updateCustomerApiV1FinancialCustomersCustomersCustomerIdPut(
      customerId,
      data
    );
    return response.data;
  },

  async delete(customerId: string): Promise<void> {
    await customers.deleteCustomerApiV1FinancialCustomersCustomersCustomerIdDelete(
      customerId
    );
  },

  async search(params: { q: string; limit?: number }) {
    const response = await customers.searchCustomersApiV1FinancialCustomersCustomersSearchGet(
      params
    );
    return response.data;
  },

  async getStats(condominioId: string) {
    const response = await customers.getStatsApiV1FinancialCustomersCustomersStatsGet(
      { condominio_id: condominioId }
    );
    return response.data;
  },

  async getHistory(customerId: string) {
    const response = await customers.getCustomerHistoryApiV1FinancialCustomersCustomersCustomerIdHistoryGet(
      customerId
    );
    return response.data;
  },

  async block(customerId: string, reason: string) {
    const response = await customers.blockCustomerApiV1FinancialCustomersCustomersCustomerIdBlockPost(
      customerId,
      { reason }
    );
    return response.data;
  },

  async unblock(customerId: string) {
    const response = await customers.unblockCustomerApiV1FinancialCustomersCustomersCustomerIdUnblockPost(
      customerId
    );
    return response.data;
  },

  async getCreditAnalysis(customerId: string) {
    const response = await customers.getCreditAnalysisApiV1FinancialCustomersCustomersCustomerIdCreditAnalysisGet(
      customerId
    );
    return response.data;
  },

  async updateCreditLimit(customerId: string, creditLimit: number) {
    const response = await customers.updateCreditLimitApiV1FinancialCustomersCustomersCustomerIdCreditLimitPut(
      customerId,
      { credit_limit: creditLimit }
    );
    return response.data;
  },
};

export default customerService;
