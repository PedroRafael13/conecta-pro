/**
 * Service: Bank Transaction Management
 * Cobertura: 13 endpoints
 */

import { getFinancialBankTransactions } from '@/types/generated/financial/financial-bank-transactions/financial-bank-transactions';
import type {
  BankTransactionCreate,
  BankTransactionUpdate,
  BankTransactionResponse,
  ListTransactionsApiV1FinancialBankTransactionsTransactionsGetParams,
} from '@/types/generated/financial/models';

const transactions = getFinancialBankTransactions();

export const bankTransactionService = {
  async create(data: BankTransactionCreate): Promise<BankTransactionResponse> {
    const response = await transactions.createTransactionApiV1FinancialBankTransactionsTransactionsPost(
      data
    );
    return response.data;
  },

  async list(
    params: ListTransactionsApiV1FinancialBankTransactionsTransactionsGetParams = {}
  ) {
    const response = await transactions.listTransactionsApiV1FinancialBankTransactionsTransactionsGet(
      params
    );
    return response.data;
  },

  async getById(transactionId: string): Promise<BankTransactionResponse> {
    const response = await transactions.getTransactionApiV1FinancialBankTransactionsTransactionsTransactionIdGet(
      transactionId
    );
    return response.data;
  },

  async update(
    transactionId: string,
    data: BankTransactionUpdate
  ): Promise<BankTransactionResponse> {
    const response = await transactions.updateTransactionApiV1FinancialBankTransactionsTransactionsTransactionIdPut(
      transactionId,
      data
    );
    return response.data;
  },

  async delete(transactionId: string): Promise<void> {
    await transactions.deleteTransactionApiV1FinancialBankTransactionsTransactionsTransactionIdDelete(
      transactionId
    );
  },

  async importOFX(accountId: string, file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await transactions.importOfxApiV1FinancialBankTransactionsImportOfxPost(
      accountId,
      formData as any
    );
    return response.data;
  },

  async categorize(transactionId: string, categoryId: string) {
    const response = await transactions.categorizeTransactionApiV1FinancialBankTransactionsTransactionsTransactionIdCategorizePost(
      transactionId,
      { category_id: categoryId }
    );
    return response.data;
  },

  async reconcile(transactionId: string) {
    const response = await transactions.reconcileTransactionApiV1FinancialBankTransactionsTransactionsTransactionIdReconcilePost(
      transactionId
    );
    return response.data;
  },
};

export default bankTransactionService;
