/**
 * Service: Accounting Management
 * Cobertura: 46 endpoints
 */

import { getFinancialAccounting } from '@/types/generated/financial/financial-accounting/financial-accounting';
import type {
  ChartOfAccountsCreate,
  AccountingAccountCreate,
  JournalEntryCreate,
  CostCenterCreate,
  AccountingPeriodCreate,
  ListAccountsApiV1FinancialAccountingAccountingAccountsGetParams,
  ListChartsApiV1FinancialAccountingAccountingChartsGetParams,
  ListCostCentersApiV1FinancialAccountingAccountingCostCentersGetParams,
  ListJournalEntriesApiV1FinancialAccountingAccountingJournalEntriesGetParams,
  ListPeriodsApiV1FinancialAccountingAccountingPeriodsGetParams,
  ListTrialBalancesApiV1FinancialAccountingAccountingTrialBalancesGetParams,
  PeriodCloseRequest,
  PeriodReopenRequest,
} from '@/types/generated/financial/models';

const accounting = getFinancialAccounting();

export const accountingService = {
  // Chart of Accounts
  async createChart(data: ChartOfAccountsCreate) {
    return await accounting.createChartApiV1FinancialAccountingAccountingChartsPost(
      data
    );
  },

  async listCharts(params: ListChartsApiV1FinancialAccountingAccountingChartsGetParams = {}) {
    return await accounting.listChartsApiV1FinancialAccountingAccountingChartsGet(
      params
    );
  },

  // Accounts
  async createAccount(data: AccountingAccountCreate) {
    return await accounting.createAccountApiV1FinancialAccountingAccountingAccountsPost(
      data
    );
  },

  async listAccounts(
    params: ListAccountsApiV1FinancialAccountingAccountingAccountsGetParams
  ) {
    return await accounting.listAccountsApiV1FinancialAccountingAccountingAccountsGet(
      params
    );
  },

  async getAccount(accountId: string) {
    return await accounting.getAccountApiV1FinancialAccountingAccountingAccountsAccountIdGet(
      accountId
    );
  },

  // Cost Centers
  async createCostCenter(data: CostCenterCreate) {
    return await accounting.createCostCenterApiV1FinancialAccountingAccountingCostCentersPost(
      data
    );
  },

  async listCostCenters(params: ListCostCentersApiV1FinancialAccountingAccountingCostCentersGetParams = {}) {
    return await accounting.listCostCentersApiV1FinancialAccountingAccountingCostCentersGet(
      params
    );
  },

  // Journal Entries
  async createJournalEntry(data: JournalEntryCreate) {
    return await accounting.createJournalEntryApiV1FinancialAccountingAccountingJournalEntriesPost(
      data
    );
  },

  async listJournalEntries(params: ListJournalEntriesApiV1FinancialAccountingAccountingJournalEntriesGetParams = {}) {
    return await accounting.listJournalEntriesApiV1FinancialAccountingAccountingJournalEntriesGet(
      params
    );
  },

  async getJournalEntry(entryId: string) {
    return await accounting.getJournalEntryApiV1FinancialAccountingAccountingJournalEntriesEntryIdGet(
      entryId
    );
  },

  // Periods
  async createPeriod(data: AccountingPeriodCreate) {
    return await accounting.createPeriodApiV1FinancialAccountingAccountingPeriodsPost(
      data
    );
  },

  async listPeriods(params: ListPeriodsApiV1FinancialAccountingAccountingPeriodsGetParams = {}) {
    return await accounting.listPeriodsApiV1FinancialAccountingAccountingPeriodsGet(
      params
    );
  },

  async closePeriod(periodId: string, data: PeriodCloseRequest) {
    return await accounting.closePeriodApiV1FinancialAccountingAccountingPeriodsPeriodIdClosePost(
      periodId,
      data
    );
  },

  async reopenPeriod(periodId: string, data: PeriodReopenRequest) {
    return await accounting.reopenPeriodApiV1FinancialAccountingAccountingPeriodsPeriodIdReopenPost(
      periodId,
      data
    );
  },

  // Reports
  async getTrialBalance(params: ListTrialBalancesApiV1FinancialAccountingAccountingTrialBalancesGetParams = {}) {
    return await accounting.listTrialBalancesApiV1FinancialAccountingAccountingTrialBalancesGet(
      params
    );
  },

  async getLatestBalance() {
    return await accounting.getLatestBalanceApiV1FinancialAccountingAccountingTrialBalancesLatestGet();
  },

  async getActiveChart() {
    return await accounting.getActiveChartApiV1FinancialAccountingAccountingChartsActiveGet();
  },

  async getCurrentPeriod() {
    return await accounting.getCurrentPeriodApiV1FinancialAccountingAccountingPeriodsCurrentGet();
  },
};

export default accountingService;
