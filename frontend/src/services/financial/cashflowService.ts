/**
 * Service: Cashflow Management
 * Cobertura: 29 endpoints
 */

import { getFinancialCashflow } from '@/types/generated/financial/financial-cashflow/financial-cashflow';
import type {
  CashFlowEntryCreate,
  CashFlowForecastCreate,
  GetEntriesApiV1FinancialCashflowEntriesGetParams,
  GetForecastApiV1FinancialCashflowForecastGetParams,
} from '@/types/generated/financial/models';

const cashflow = getFinancialCashflow();

export const cashflowService = {
  // Entries
  async createEntry(data: CashFlowEntryCreate) {
    const response = await cashflow.createEntryApiV1FinancialCashflowEntriesPost(
      data
    );
    return response.data;
  },

  async listEntries(
    params: GetEntriesApiV1FinancialCashflowEntriesGetParams = {}
  ) {
    const response = await cashflow.getEntriesApiV1FinancialCashflowEntriesGet(
      params
    );
    return response.data;
  },

  async getEntry(entryId: string) {
    const response = await cashflow.getEntryApiV1FinancialCashflowEntriesEntryIdGet(
      entryId
    );
    return response.data;
  },

  async deleteEntry(entryId: string) {
    await cashflow.deleteEntryApiV1FinancialCashflowEntriesEntryIdDelete(
      entryId
    );
  },

  // Forecast
  async createForecast(data: CashFlowForecastCreate) {
    const response = await cashflow.createForecastApiV1FinancialCashflowForecastPost(
      data
    );
    return response.data;
  },

  async getForecast(
    params: GetForecastApiV1FinancialCashflowForecastGetParams
  ) {
    const response = await cashflow.getForecastApiV1FinancialCashflowForecastGet(
      params
    );
    return response.data;
  },

  // Analysis
  async getDailyFlow(condominioId: string, startDate: string, endDate: string) {
    const response = await cashflow.getDailyFlowApiV1FinancialCashflowDailyFlowGet(
      { condominio_id: condominioId, start_date: startDate, end_date: endDate }
    );
    return response.data;
  },

  async getProjection(condominioId: string, months: number = 12) {
    const response = await cashflow.getProjectionApiV1FinancialCashflowProjectionGet(
      { condominio_id: condominioId, months }
    );
    return response.data;
  },

  async getDRE(condominioId: string, referenceMonth: string) {
    const response = await cashflow.getDreApiV1FinancialCashflowDreGet(
      { condominio_id: condominioId, reference_month: referenceMonth }
    );
    return response.data;
  },

  async getDashboard(condominioId: string) {
    const response = await cashflow.getCashflowDashboardApiV1FinancialCashflowDashboardGet(
      { condominio_id: condominioId }
    );
    return response.data;
  },

  // Reconciliation
  async reconcileBanks(condominioId: string, date: string) {
    const response = await cashflow.reconcileBanksApiV1FinancialCashflowReconcileBanksPost(
      { condominio_id: condominioId, date }
    );
    return response.data;
  },

  // Reports
  async exportToExcel(params: any) {
    const response = await cashflow.exportCashflowToExcelApiV1FinancialCashflowExportExcelGet(
      params
    );
    return response.data;
  },
};

export default cashflowService;
