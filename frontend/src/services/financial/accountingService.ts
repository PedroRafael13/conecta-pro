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
  ListAccountsApiV1FinancialAccountingAccountsGetParams,
} from '@/types/generated/financial/models';

const accounting = getFinancialAccounting();

export const accountingService = {
  // Chart of Accounts
  async createChart(data: ChartOfAccountsCreate) {
    const response = await accounting.createChartApiV1FinancialAccountingChartsPost(
      data
    );
    return response.data;
  },

  async listCharts(params: any = {}) {
    const response = await accounting.listChartsApiV1FinancialAccountingChartsGet(
      params
    );
    return response.data;
  },

  // Accounts
  async createAccount(data: AccountingAccountCreate) {
    const response = await accounting.createAccountApiV1FinancialAccountingAccountsPost(
      data
    );
    return response.data;
  },

  async listAccounts(
    params: ListAccountsApiV1FinancialAccountingAccountsGetParams = {}
  ) {
    const response = await accounting.listAccountsApiV1FinancialAccountingAccountsGet(
      params
    );
    return response.data;
  },

  async getAccount(accountId: string) {
    const response = await accounting.getAccountApiV1FinancialAccountingAccountsAccountIdGet(
      accountId
    );
    return response.data;
  },

  // Cost Centers
  async createCostCenter(data: CostCenterCreate) {
    const response = await accounting.createCostCenterApiV1FinancialAccountingCostCentersPost(
      data
    );
    return response.data;
  },

  async listCostCenters(params: any = {}) {
    const response = await accounting.listCostCentersApiV1FinancialAccountingCostCentersGet(
      params
    );
    return response.data;
  },

  // Journal Entries
  async createJournalEntry(data: JournalEntryCreate) {
    const response = await accounting.createJournalEntryApiV1FinancialAccountingJournalEntriesPost(
      data
    );
    return response.data;
  },

  async listJournalEntries(params: any = {}) {
    const response = await accounting.listJournalEntriesApiV1FinancialAccountingJournalEntriesGet(
      params
    );
    return response.data;
  },

  async getJournalEntry(entryId: string) {
    const response = await accounting.getJournalEntryApiV1FinancialAccountingJournalEntriesEntryIdGet(
      entryId
    );
    return response.data;
  },

  // Periods
  async createPeriod(data: AccountingPeriodCreate) {
    const response = await accounting.createPeriodApiV1FinancialAccountingPeriodsPost(
      data
    );
    return response.data;
  },

  async listPeriods(params: any = {}) {
    const response = await accounting.listPeriodsApiV1FinancialAccountingPeriodsGet(
      params
    );
    return response.data;
  },

  async closePeriod(periodId: string) {
    const response = await accounting.closePeriodApiV1FinancialAccountingPeriodsPeriodIdClosePost(
      periodId
    );
    return response.data;
  },

  async reopenPeriod(periodId: string) {
    const response = await accounting.reopenPeriodApiV1FinancialAccountingPeriodsPeriodIdReopenPost(
      periodId
    );
    return response.data;
  },

  // Reports
  async getTrialBalance(condominioId: string, periodId: string) {
    const response = await accounting.getTrialBalanceApiV1FinancialAccountingReportsTrialBalanceGet(
      { condominio_id: condominioId, period_id: periodId }
    );
    return response.data;
  },

  async getBalanceSheet(condominioId: string, date: string) {
    const response = await accounting.getBalanceSheetApiV1FinancialAccountingReportsBalanceSheetGet(
      { condominio_id: condominioId, date }
    );
    return response.data;
  },

  async getIncomeStatement(
    condominioId: string,
    startDate: string,
    endDate: string
  ) {
    const response = await accounting.getIncomeStatementApiV1FinancialAccountingReportsIncomeStatementGet(
      { condominio_id: condominioId, start_date: startDate, end_date: endDate }
    );
    return response.data;
  },

  async getCashFlowStatement(
    condominioId: string,
    startDate: string,
    endDate: string
  ) {
    const response = await accounting.getCashFlowStatementApiV1FinancialAccountingReportsCashFlowStatementGet(
      { condominio_id: condominioId, start_date: startDate, end_date: endDate }
    );
    return response.data;
  },

  async exportToExcel(params: any) {
    const response = await accounting.exportAccountingToExcelApiV1FinancialAccountingExportExcelGet(
      params
    );
    return response.data;
  },
};

export default accountingService;
