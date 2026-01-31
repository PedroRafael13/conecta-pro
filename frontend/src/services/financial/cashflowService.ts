/**
 * Service: Cashflow Management
 * Cobertura: 29 endpoints
 */

import { getFinancialCashflow } from '@/types/generated/financial/financial-cashflow/financial-cashflow';
import type {
  CashFlowEntryCreate,
  CashFlowEntryUpdate,
  CashFlowEntryRealize,
  CashFlowForecastCreate,
  CashFlowForecastUpdate,
  ForecastActualsUpdate,
  AIForecastRequest,
  AnomalyDetectionRequest,
  ListEntriesApiV1FinancialCashflowCashflowEntriesGetParams,
  GetPendingEntriesApiV1FinancialCashflowCashflowEntriesPendingGetParams,
  GetEntryTotalsApiV1FinancialCashflowCashflowEntriesTotalsGetParams,
  ListForecastsApiV1FinancialCashflowCashflowForecastsGetParams,
  GetActiveForecastsApiV1FinancialCashflowCashflowForecastsActiveGetParams,
  GetProjectionApiV1FinancialCashflowCashflowProjectionGetParams,
  GetSummaryApiV1FinancialCashflowCashflowSummaryGetParams,
  GetTrendsApiV1FinancialCashflowCashflowTrendsGetParams,
  GetCategoryBreakdownApiV1FinancialCashflowCashflowCategoryBreakdownGetParams,
  GetSupplierBreakdownApiV1FinancialCashflowCashflowSupplierBreakdownGetParams,
  GetDashboardApiV1FinancialCashflowCashflowDashboardGetParams,
  GetOptimizationSuggestionsApiV1FinancialCashflowCashflowAiSuggestionsGetParams,
  GetRisksApiV1FinancialCashflowCashflowAiRisksGetParams,
  GetOpportunitiesApiV1FinancialCashflowCashflowAiOpportunitiesGetParams,
} from '@/types/generated/financial/models';

const cashflow = getFinancialCashflow();

export const cashflowService = {
  // Entries
  async createEntry(data: CashFlowEntryCreate) {
    return await cashflow.createEntryApiV1FinancialCashflowCashflowEntriesPost(
      data
    );
  },

  async listEntries(
    params: ListEntriesApiV1FinancialCashflowCashflowEntriesGetParams
  ) {
    return await cashflow.listEntriesApiV1FinancialCashflowCashflowEntriesGet(
      params
    );
  },

  async getEntry(entryId: string) {
    return await cashflow.getEntryApiV1FinancialCashflowCashflowEntriesEntryIdGet(
      entryId
    );
  },

  async updateEntry(entryId: string, data: CashFlowEntryUpdate) {
    return await cashflow.updateEntryApiV1FinancialCashflowCashflowEntriesEntryIdPut(
      entryId,
      data
    );
  },

  async deleteEntry(entryId: string) {
    return await cashflow.deleteEntryApiV1FinancialCashflowCashflowEntriesEntryIdDelete(
      entryId
    );
  },

  async realizeEntry(entryId: string, data: CashFlowEntryRealize) {
    return await cashflow.realizeEntryApiV1FinancialCashflowCashflowEntriesEntryIdRealizePost(
      entryId,
      data
    );
  },

  async getPendingEntries(
    params: GetPendingEntriesApiV1FinancialCashflowCashflowEntriesPendingGetParams
  ) {
    return await cashflow.getPendingEntriesApiV1FinancialCashflowCashflowEntriesPendingGet(
      params
    );
  },

  async getEntryTotals(
    params: GetEntryTotalsApiV1FinancialCashflowCashflowEntriesTotalsGetParams
  ) {
    return await cashflow.getEntryTotalsApiV1FinancialCashflowCashflowEntriesTotalsGet(
      params
    );
  },

  // Forecasts
  async createForecast(data: CashFlowForecastCreate) {
    return await cashflow.createForecastApiV1FinancialCashflowCashflowForecastsPost(
      data
    );
  },

  async listForecasts(
    params: ListForecastsApiV1FinancialCashflowCashflowForecastsGetParams
  ) {
    return await cashflow.listForecastsApiV1FinancialCashflowCashflowForecastsGet(
      params
    );
  },

  async getForecast(forecastId: string) {
    return await cashflow.getForecastApiV1FinancialCashflowCashflowForecastsForecastIdGet(
      forecastId
    );
  },

  async updateForecast(forecastId: string, data: CashFlowForecastUpdate) {
    return await cashflow.updateForecastApiV1FinancialCashflowCashflowForecastsForecastIdPut(
      forecastId,
      data
    );
  },

  async deleteForecast(forecastId: string) {
    return await cashflow.deleteForecastApiV1FinancialCashflowCashflowForecastsForecastIdDelete(
      forecastId
    );
  },

  async getActiveForecasts(
    params: GetActiveForecastsApiV1FinancialCashflowCashflowForecastsActiveGetParams
  ) {
    return await cashflow.getActiveForecastsApiV1FinancialCashflowCashflowForecastsActiveGet(
      params
    );
  },

  async updateForecastActuals(forecastId: string, data: ForecastActualsUpdate) {
    return await cashflow.updateForecastActualsApiV1FinancialCashflowCashflowForecastsForecastIdUpdateActualsPost(
      forecastId,
      data
    );
  },

  // Analysis
  async getProjection(
    params: GetProjectionApiV1FinancialCashflowCashflowProjectionGetParams
  ) {
    return await cashflow.getProjectionApiV1FinancialCashflowCashflowProjectionGet(
      params
    );
  },

  async getSummary(
    params: GetSummaryApiV1FinancialCashflowCashflowSummaryGetParams
  ) {
    return await cashflow.getSummaryApiV1FinancialCashflowCashflowSummaryGet(
      params
    );
  },

  async getTrends(
    params: GetTrendsApiV1FinancialCashflowCashflowTrendsGetParams
  ) {
    return await cashflow.getTrendsApiV1FinancialCashflowCashflowTrendsGet(
      params
    );
  },

  async getCategoryBreakdown(
    params: GetCategoryBreakdownApiV1FinancialCashflowCashflowCategoryBreakdownGetParams
  ) {
    return await cashflow.getCategoryBreakdownApiV1FinancialCashflowCashflowCategoryBreakdownGet(
      params
    );
  },

  async getSupplierBreakdown(
    params: GetSupplierBreakdownApiV1FinancialCashflowCashflowSupplierBreakdownGetParams
  ) {
    return await cashflow.getSupplierBreakdownApiV1FinancialCashflowCashflowSupplierBreakdownGet(
      params
    );
  },

  async getDashboard(
    params: GetDashboardApiV1FinancialCashflowCashflowDashboardGetParams
  ) {
    return await cashflow.getDashboardApiV1FinancialCashflowCashflowDashboardGet(
      params
    );
  },

  // AI Features
  async generateAiForecast(data: AIForecastRequest) {
    return await cashflow.generateAiForecastApiV1FinancialCashflowCashflowAiForecastPost(
      data
    );
  },

  async detectAnomalies(data: AnomalyDetectionRequest) {
    return await cashflow.detectAnomaliesApiV1FinancialCashflowCashflowAiAnomaliesPost(
      data
    );
  },

  async getOptimizationSuggestions(
    params: GetOptimizationSuggestionsApiV1FinancialCashflowCashflowAiSuggestionsGetParams
  ) {
    return await cashflow.getOptimizationSuggestionsApiV1FinancialCashflowCashflowAiSuggestionsGet(
      params
    );
  },

  async getRisks(
    params: GetRisksApiV1FinancialCashflowCashflowAiRisksGetParams
  ) {
    return await cashflow.getRisksApiV1FinancialCashflowCashflowAiRisksGet(
      params
    );
  },

  async getOpportunities(
    params: GetOpportunitiesApiV1FinancialCashflowCashflowAiOpportunitiesGetParams
  ) {
    return await cashflow.getOpportunitiesApiV1FinancialCashflowCashflowAiOpportunitiesGet(
      params
    );
  },
};

export default cashflowService;
