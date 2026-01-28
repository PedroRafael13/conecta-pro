/**
 * Service: BI Dashboard Management
 * Cobertura: 60 endpoints
 */

import { getFinancialBiDashboard } from '@/types/generated/financial/financial-bi-dashboard/financial-bi-dashboard';
import type {
  FinancialDashboardCreate,
  FinancialWidgetCreate,
  FinancialKPICreate,
  ScheduledReportCreate,
  GetDashboardApiV1FinancialBiDashboardDashboardsGetParams,
} from '@/types/generated/financial/models';

const biDashboard = getFinancialBiDashboard();

export const biDashboardService = {
  // Dashboards
  async createDashboard(data: FinancialDashboardCreate) {
    const response = await biDashboard.createDashboardApiV1FinancialBiDashboardDashboardsPost(
      data
    );
    return response.data;
  },

  async listDashboards(
    params: GetDashboardApiV1FinancialBiDashboardDashboardsGetParams = {}
  ) {
    const response = await biDashboard.getDashboardApiV1FinancialBiDashboardDashboardsGet(
      params
    );
    return response.data;
  },

  async getDashboard(dashboardId: string) {
    const response = await biDashboard.getDashboardByIdApiV1FinancialBiDashboardDashboardsDashboardIdGet(
      dashboardId
    );
    return response.data;
  },

  async updateDashboard(dashboardId: string, data: any) {
    const response = await biDashboard.updateDashboardApiV1FinancialBiDashboardDashboardsDashboardIdPut(
      dashboardId,
      data
    );
    return response.data;
  },

  async deleteDashboard(dashboardId: string) {
    await biDashboard.deleteDashboardApiV1FinancialBiDashboardDashboardsDashboardIdDelete(
      dashboardId
    );
  },

  // Widgets
  async createWidget(data: FinancialWidgetCreate) {
    const response = await biDashboard.createWidgetApiV1FinancialBiDashboardWidgetsPost(
      data
    );
    return response.data;
  },

  async listWidgets(params: any = {}) {
    const response = await biDashboard.listWidgetsApiV1FinancialBiDashboardWidgetsGet(
      params
    );
    return response.data;
  },

  async getWidget(widgetId: string) {
    const response = await biDashboard.getWidgetApiV1FinancialBiDashboardWidgetsWidgetIdGet(
      widgetId
    );
    return response.data;
  },

  async updateWidget(widgetId: string, data: any) {
    const response = await biDashboard.updateWidgetApiV1FinancialBiDashboardWidgetsWidgetIdPut(
      widgetId,
      data
    );
    return response.data;
  },

  async deleteWidget(widgetId: string) {
    await biDashboard.deleteWidgetApiV1FinancialBiDashboardWidgetsWidgetIdDelete(
      widgetId
    );
  },

  async refreshWidget(widgetId: string) {
    const response = await biDashboard.refreshWidgetApiV1FinancialBiDashboardWidgetsWidgetIdRefreshPost(
      widgetId
    );
    return response.data;
  },

  // KPIs
  async createKPI(data: FinancialKPICreate) {
    const response = await biDashboard.createKpiApiV1FinancialBiDashboardKpisPost(
      data
    );
    return response.data;
  },

  async listKPIs(params: any = {}) {
    const response = await biDashboard.listKpisApiV1FinancialBiDashboardKpisGet(
      params
    );
    return response.data;
  },

  async getKPI(kpiId: string) {
    const response = await biDashboard.getKpiApiV1FinancialBiDashboardKpisKpiIdGet(
      kpiId
    );
    return response.data;
  },

  async calculateKPI(kpiId: string, params: any) {
    const response = await biDashboard.calculateKpiApiV1FinancialBiDashboardKpisKpiIdCalculatePost(
      kpiId,
      params
    );
    return response.data;
  },

  // Analytics
  async getFinancialOverview(condominioId: string) {
    const response = await biDashboard.getFinancialOverviewApiV1FinancialBiDashboardAnalyticsOverviewGet(
      { condominio_id: condominioId }
    );
    return response.data;
  },

  async getRevenueAnalysis(
    condominioId: string,
    startDate: string,
    endDate: string
  ) {
    const response = await biDashboard.getRevenueAnalysisApiV1FinancialBiDashboardAnalyticsRevenueGet(
      { condominio_id: condominioId, start_date: startDate, end_date: endDate }
    );
    return response.data;
  },

  async getExpenseAnalysis(
    condominioId: string,
    startDate: string,
    endDate: string
  ) {
    const response = await biDashboard.getExpenseAnalysisApiV1FinancialBiDashboardAnalyticsExpensesGet(
      { condominio_id: condominioId, start_date: startDate, end_date: endDate }
    );
    return response.data;
  },

  async getProfitabilityAnalysis(condominioId: string, period: string) {
    const response = await biDashboard.getProfitabilityAnalysisApiV1FinancialBiDashboardAnalyticsProfitabilityGet(
      { condominio_id: condominioId, period }
    );
    return response.data;
  },

  async getTrendAnalysis(condominioId: string, metric: string, months: number) {
    const response = await biDashboard.getTrendAnalysisApiV1FinancialBiDashboardAnalyticsTrendsGet(
      { condominio_id: condominioId, metric, months }
    );
    return response.data;
  },

  // Scheduled Reports
  async createScheduledReport(data: ScheduledReportCreate) {
    const response = await biDashboard.createScheduledReportApiV1FinancialBiDashboardScheduledReportsPost(
      data
    );
    return response.data;
  },

  async listScheduledReports(params: any = {}) {
    const response = await biDashboard.listScheduledReportsApiV1FinancialBiDashboardScheduledReportsGet(
      params
    );
    return response.data;
  },

  async getScheduledReport(reportId: string) {
    const response = await biDashboard.getScheduledReportApiV1FinancialBiDashboardScheduledReportsReportIdGet(
      reportId
    );
    return response.data;
  },

  async executeScheduledReport(reportId: string) {
    const response = await biDashboard.executeReportApiV1FinancialBiDashboardScheduledReportsReportIdExecutePost(
      reportId
    );
    return response.data;
  },

  // Cache Management
  async clearCache(condominioId: string) {
    const response = await biDashboard.clearCacheApiV1FinancialBiDashboardCacheClearPost(
      { condominio_id: condominioId }
    );
    return response.data;
  },

  async warmupCache(condominioId: string) {
    const response = await biDashboard.warmupCacheApiV1FinancialBiDashboardCacheWarmupPost(
      { condominio_id: condominioId }
    );
    return response.data;
  },
};

export default biDashboardService;
