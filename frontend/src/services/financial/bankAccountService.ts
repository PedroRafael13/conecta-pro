/**
 * Service: Bank Account Management
 * Cobertura: 12 endpoints
 */

import { getFinancialBankAccounts } from '@/types/generated/financial/financial-bank-accounts/financial-bank-accounts';
import type {
  BankAccountCreate,
  BankAccountUpdate,
  ListBankAccountsApiV1FinancialBankAccountsBankAccountsGetParams,
  GetStatsApiV1FinancialBankAccountsBankAccountsStatsGetParams,
  GetMainAccountApiV1FinancialBankAccountsBankAccountsMainGetParams,
  AdjustBalanceApiV1FinancialBankAccountsBankAccountsAccountIdAdjustBalancePostParams,
  TransferRequest,
} from '@/types/generated/financial/models';

const bankAccounts = getFinancialBankAccounts();

export const bankAccountService = {
  async create(data: BankAccountCreate) {
    return await bankAccounts.createBankAccountApiV1FinancialBankAccountsBankAccountsPost(
      data
    );
  },

  async list(
    params: ListBankAccountsApiV1FinancialBankAccountsBankAccountsGetParams
  ) {
    return await bankAccounts.listBankAccountsApiV1FinancialBankAccountsBankAccountsGet(
      params
    );
  },

  async getById(accountId: string) {
    return await bankAccounts.getBankAccountApiV1FinancialBankAccountsBankAccountsAccountIdGet(
      accountId
    );
  },

  async update(accountId: string, data: BankAccountUpdate) {
    return await bankAccounts.updateBankAccountApiV1FinancialBankAccountsBankAccountsAccountIdPut(
      accountId,
      data
    );
  },

  async delete(accountId: string) {
    return await bankAccounts.deleteBankAccountApiV1FinancialBankAccountsBankAccountsAccountIdDelete(
      accountId
    );
  },

  async getMainAccount(params: GetMainAccountApiV1FinancialBankAccountsBankAccountsMainGetParams) {
    return await bankAccounts.getMainAccountApiV1FinancialBankAccountsBankAccountsMainGet(
      params
    );
  },

  async getStats(params: GetStatsApiV1FinancialBankAccountsBankAccountsStatsGetParams) {
    return await bankAccounts.getStatsApiV1FinancialBankAccountsBankAccountsStatsGet(
      params
    );
  },

  async activate(accountId: string) {
    return await bankAccounts.activateAccountApiV1FinancialBankAccountsBankAccountsAccountIdActivatePost(
      accountId
    );
  },

  async suspend(accountId: string) {
    return await bankAccounts.suspendAccountApiV1FinancialBankAccountsBankAccountsAccountIdSuspendPost(
      accountId
    );
  },

  async setAsMain(accountId: string) {
    return await bankAccounts.setAsMainAccountApiV1FinancialBankAccountsBankAccountsAccountIdSetMainPost(
      accountId
    );
  },

  async transfer(data: TransferRequest) {
    return await bankAccounts.transferBetweenAccountsApiV1FinancialBankAccountsBankAccountsTransferPost(
      data
    );
  },

  async adjustBalance(
    accountId: string,
    params: AdjustBalanceApiV1FinancialBankAccountsBankAccountsAccountIdAdjustBalancePostParams
  ) {
    return await bankAccounts.adjustBalanceApiV1FinancialBankAccountsBankAccountsAccountIdAdjustBalancePost(
      accountId,
      params
    );
  },
};

export default bankAccountService;
