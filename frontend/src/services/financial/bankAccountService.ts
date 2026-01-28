/**
 * Service: Bank Account Management
 * Cobertura: 12 endpoints
 */

import { getFinancialBankAccounts } from '@/types/generated/financial/financial-bank-accounts/financial-bank-accounts';
import type {
  BankAccountCreate,
  BankAccountUpdate,
  BankAccountResponse,
  ListBankAccountsApiV1FinancialBankAccountsBankAccountsGetParams,
} from '@/types/generated/financial/models';

const bankAccounts = getFinancialBankAccounts();

export const bankAccountService = {
  async create(data: BankAccountCreate): Promise<BankAccountResponse> {
    const response = await bankAccounts.createBankAccountApiV1FinancialBankAccountsBankAccountsPost(
      data
    );
    return response.data;
  },

  async list(
    params: ListBankAccountsApiV1FinancialBankAccountsBankAccountsGetParams = {}
  ) {
    const response = await bankAccounts.listBankAccountsApiV1FinancialBankAccountsBankAccountsGet(
      params
    );
    return response.data;
  },

  async getById(accountId: string): Promise<BankAccountResponse> {
    const response = await bankAccounts.getBankAccountApiV1FinancialBankAccountsBankAccountsAccountIdGet(
      accountId
    );
    return response.data;
  },

  async update(
    accountId: string,
    data: BankAccountUpdate
  ): Promise<BankAccountResponse> {
    const response = await bankAccounts.updateBankAccountApiV1FinancialBankAccountsBankAccountsAccountIdPut(
      accountId,
      data
    );
    return response.data;
  },

  async delete(accountId: string): Promise<void> {
    await bankAccounts.deleteBankAccountApiV1FinancialBankAccountsBankAccountsAccountIdDelete(
      accountId
    );
  },

  async getBalance(accountId: string) {
    const response = await bankAccounts.getBalanceApiV1FinancialBankAccountsBankAccountsAccountIdBalanceGet(
      accountId
    );
    return response.data;
  },

  async getStatement(accountId: string, params: any) {
    const response = await bankAccounts.getStatementApiV1FinancialBankAccountsBankAccountsAccountIdStatementGet(
      accountId,
      params
    );
    return response.data;
  },

  async activate(accountId: string) {
    const response = await bankAccounts.activateBankAccountApiV1FinancialBankAccountsBankAccountsAccountIdActivatePost(
      accountId
    );
    return response.data;
  },

  async deactivate(accountId: string) {
    const response = await bankAccounts.deactivateBankAccountApiV1FinancialBankAccountsBankAccountsAccountIdDeactivatePost(
      accountId
    );
    return response.data;
  },

  async reconcile(accountId: string, params: any) {
    const response = await bankAccounts.reconcileApiV1FinancialBankAccountsBankAccountsAccountIdReconcilePost(
      accountId,
      params
    );
    return response.data;
  },
};

export default bankAccountService;
