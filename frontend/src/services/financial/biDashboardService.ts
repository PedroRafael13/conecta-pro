/**
 * Service: BI Dashboard Management
 * Cobertura: 60 endpoints
 */

import { getFinancialBiDashboard } from '@/types/generated/financial/financial-bi-dashboard/financial-bi-dashboard';
import type {
  DashboardCreate,
  DashboardUpdate,
  WidgetCreate,
  WidgetUpdate,
  KPICreate,
  KPIUpdate,
  ReportCreate,
  ReportUpdate,
  CacheInvalidate,
  ListDashboardsApiV1FinancialBiDashboardBiDashboardsGetParams,
  CreateDashboardApiV1FinancialBiDashboardBiDashboardsPostParams,
  GetDashboardApiV1FinancialBiDashboardBiDashboardsDashboardIdGetParams,
  UpdateDashboardApiV1FinancialBiDashboardBiDashboardsDashboardIdPutParams,
  DeleteDashboardApiV1FinancialBiDashboardBiDashboardsDashboardIdDeleteParams,
  GetDashboardStatsApiV1FinancialBiDashboardBiDashboardsStatsGetParams,
  GetDefaultDashboardApiV1FinancialBiDashboardBiDashboardsDefaultGetParams,
  SetDefaultDashboardApiV1FinancialBiDashboardBiDashboardsDashboardIdSetDefaultPostParams,
  DuplicateDashboardApiV1FinancialBiDashboardBiDashboardsDashboardIdDuplicatePostParams,
  PublishDashboardApiV1FinancialBiDashboardBiDashboardsDashboardIdPublishPostParams,
  ArchiveDashboardApiV1FinancialBiDashboardBiDashboardsDashboardIdArchivePostParams,
  ToggleDashboardFavoriteApiV1FinancialBiDashboardBiDashboardsDashboardIdFavoritePostParams,
  ListWidgetsApiV1FinancialBiDashboardBiWidgetsGetParams,
  CreateWidgetApiV1FinancialBiDashboardBiWidgetsPostParams,
  GetWidgetApiV1FinancialBiDashboardBiWidgetsWidgetIdGetParams,
  UpdateWidgetApiV1FinancialBiDashboardBiWidgetsWidgetIdPutParams,
  DeleteWidgetApiV1FinancialBiDashboardBiWidgetsWidgetIdDeleteParams,
  RefreshWidgetDataApiV1FinancialBiDashboardBiWidgetsWidgetIdRefreshPostParams,
  GetWidgetDataApiV1FinancialBiDashboardBiWidgetsWidgetIdDataGetParams,
  GetDashboardWidgetsApiV1FinancialBiDashboardBiDashboardsDashboardIdWidgetsGetParams,
  ListKpisApiV1FinancialBiDashboardBiKpisGetParams,
  CreateKpiApiV1FinancialBiDashboardBiKpisPostParams,
  GetKpiApiV1FinancialBiDashboardBiKpisKpiIdGetParams,
  UpdateKpiApiV1FinancialBiDashboardBiKpisKpiIdPutParams,
  DeleteKpiApiV1FinancialBiDashboardBiKpisKpiIdDeleteParams,
  CalculateKpiApiV1FinancialBiDashboardBiKpisKpiIdCalculatePostParams,
  GetKpiHistoryApiV1FinancialBiDashboardBiKpisKpiIdHistoryGetParams,
  GetKpisSummaryApiV1FinancialBiDashboardBiKpisSummaryGetParams,
  GetKpisAlertsApiV1FinancialBiDashboardBiKpisAlertsGetParams,
  GetKpisStatsApiV1FinancialBiDashboardBiKpisStatsGetParams,
  CalculateAllKpisApiV1FinancialBiDashboardBiKpisCalculateAllPostParams,
  ListReportsApiV1FinancialBiDashboardBiReportsGetParams,
  CreateReportApiV1FinancialBiDashboardBiReportsPostParams,
  GetReportApiV1FinancialBiDashboardBiReportsReportIdGetParams,
  UpdateReportApiV1FinancialBiDashboardBiReportsReportIdPutParams,
  DeleteReportApiV1FinancialBiDashboardBiReportsReportIdDeleteParams,
  ExecuteReportNowApiV1FinancialBiDashboardBiReportsReportIdExecutePostParams,
  PauseReportApiV1FinancialBiDashboardBiReportsReportIdPausePostParams,
  ResumeReportApiV1FinancialBiDashboardBiReportsReportIdResumePostParams,
  GetDueReportsApiV1FinancialBiDashboardBiReportsDueGetParams,
  GetCacheStatsApiV1FinancialBiDashboardBiCacheStatsGetParams,
  InvalidateCacheApiV1FinancialBiDashboardBiCacheInvalidatePostParams,
  CleanupCacheApiV1FinancialBiDashboardBiCacheCleanupPostParams,
  GetFinancialSummaryApiV1FinancialBiDashboardBiSummaryFinancialGetParams,
  ComparePeriodsApiV1FinancialBiDashboardBiSummaryCompareGetParams,
} from '@/types/generated/financial/models';

const biDashboard = getFinancialBiDashboard();

export const biDashboardService = {
  // Dashboards
  async createDashboard(
    data: DashboardCreate,
    params: CreateDashboardApiV1FinancialBiDashboardBiDashboardsPostParams
  ) {
    return await biDashboard.createDashboardApiV1FinancialBiDashboardBiDashboardsPost(
      data,
      params
    );
  },

  async listDashboards(
    params: ListDashboardsApiV1FinancialBiDashboardBiDashboardsGetParams
  ) {
    return await biDashboard.listDashboardsApiV1FinancialBiDashboardBiDashboardsGet(
      params
    );
  },

  async getDashboard(
    dashboardId: string,
    params: GetDashboardApiV1FinancialBiDashboardBiDashboardsDashboardIdGetParams
  ) {
    return await biDashboard.getDashboardApiV1FinancialBiDashboardBiDashboardsDashboardIdGet(
      dashboardId,
      params
    );
  },

  async updateDashboard(
    dashboardId: string,
    data: DashboardUpdate,
    params: UpdateDashboardApiV1FinancialBiDashboardBiDashboardsDashboardIdPutParams
  ) {
    return await biDashboard.updateDashboardApiV1FinancialBiDashboardBiDashboardsDashboardIdPut(
      dashboardId,
      data,
      params
    );
  },

  async deleteDashboard(
    dashboardId: string,
    params: DeleteDashboardApiV1FinancialBiDashboardBiDashboardsDashboardIdDeleteParams
  ) {
    return await biDashboard.deleteDashboardApiV1FinancialBiDashboardBiDashboardsDashboardIdDelete(
      dashboardId,
      params
    );
  },

  async getDefaultDashboard(
    params: GetDefaultDashboardApiV1FinancialBiDashboardBiDashboardsDefaultGetParams
  ) {
    return await biDashboard.getDefaultDashboardApiV1FinancialBiDashboardBiDashboardsDefaultGet(
      params
    );
  },

  async setDefaultDashboard(
    dashboardId: string,
    params: SetDefaultDashboardApiV1FinancialBiDashboardBiDashboardsDashboardIdSetDefaultPostParams
  ) {
    return await biDashboard.setDefaultDashboardApiV1FinancialBiDashboardBiDashboardsDashboardIdSetDefaultPost(
      dashboardId,
      params
    );
  },

  async duplicateDashboard(
    dashboardId: string,
    params: DuplicateDashboardApiV1FinancialBiDashboardBiDashboardsDashboardIdDuplicatePostParams
  ) {
    return await biDashboard.duplicateDashboardApiV1FinancialBiDashboardBiDashboardsDashboardIdDuplicatePost(
      dashboardId,
      params
    );
  },

  async publishDashboard(
    dashboardId: string,
    params: PublishDashboardApiV1FinancialBiDashboardBiDashboardsDashboardIdPublishPostParams
  ) {
    return await biDashboard.publishDashboardApiV1FinancialBiDashboardBiDashboardsDashboardIdPublishPost(
      dashboardId,
      params
    );
  },

  async archiveDashboard(
    dashboardId: string,
    params: ArchiveDashboardApiV1FinancialBiDashboardBiDashboardsDashboardIdArchivePostParams
  ) {
    return await biDashboard.archiveDashboardApiV1FinancialBiDashboardBiDashboardsDashboardIdArchivePost(
      dashboardId,
      params
    );
  },

  async toggleFavorite(
    dashboardId: string,
    params: ToggleDashboardFavoriteApiV1FinancialBiDashboardBiDashboardsDashboardIdFavoritePostParams
  ) {
    return await biDashboard.toggleDashboardFavoriteApiV1FinancialBiDashboardBiDashboardsDashboardIdFavoritePost(
      dashboardId,
      params
    );
  },

  async getDashboardStats(
    params: GetDashboardStatsApiV1FinancialBiDashboardBiDashboardsStatsGetParams
  ) {
    return await biDashboard.getDashboardStatsApiV1FinancialBiDashboardBiDashboardsStatsGet(
      params
    );
  },

  // Widgets
  async createWidget(
    data: WidgetCreate,
    params: CreateWidgetApiV1FinancialBiDashboardBiWidgetsPostParams
  ) {
    return await biDashboard.createWidgetApiV1FinancialBiDashboardBiWidgetsPost(
      data,
      params
    );
  },

  async listWidgets(
    params: ListWidgetsApiV1FinancialBiDashboardBiWidgetsGetParams
  ) {
    return await biDashboard.listWidgetsApiV1FinancialBiDashboardBiWidgetsGet(
      params
    );
  },

  async getWidget(
    widgetId: string,
    params: GetWidgetApiV1FinancialBiDashboardBiWidgetsWidgetIdGetParams
  ) {
    return await biDashboard.getWidgetApiV1FinancialBiDashboardBiWidgetsWidgetIdGet(
      widgetId,
      params
    );
  },

  async updateWidget(
    widgetId: string,
    data: WidgetUpdate,
    params: UpdateWidgetApiV1FinancialBiDashboardBiWidgetsWidgetIdPutParams
  ) {
    return await biDashboard.updateWidgetApiV1FinancialBiDashboardBiWidgetsWidgetIdPut(
      widgetId,
      data,
      params
    );
  },

  async deleteWidget(
    widgetId: string,
    params: DeleteWidgetApiV1FinancialBiDashboardBiWidgetsWidgetIdDeleteParams
  ) {
    return await biDashboard.deleteWidgetApiV1FinancialBiDashboardBiWidgetsWidgetIdDelete(
      widgetId,
      params
    );
  },

  async refreshWidget(
    widgetId: string,
    params: RefreshWidgetDataApiV1FinancialBiDashboardBiWidgetsWidgetIdRefreshPostParams
  ) {
    return await biDashboard.refreshWidgetDataApiV1FinancialBiDashboardBiWidgetsWidgetIdRefreshPost(
      widgetId,
      params
    );
  },

  async getWidgetData(
    widgetId: string,
    params: GetWidgetDataApiV1FinancialBiDashboardBiWidgetsWidgetIdDataGetParams
  ) {
    return await biDashboard.getWidgetDataApiV1FinancialBiDashboardBiWidgetsWidgetIdDataGet(
      widgetId,
      params
    );
  },

  async getDashboardWidgets(
    dashboardId: string,
    params: GetDashboardWidgetsApiV1FinancialBiDashboardBiDashboardsDashboardIdWidgetsGetParams
  ) {
    return await biDashboard.getDashboardWidgetsApiV1FinancialBiDashboardBiDashboardsDashboardIdWidgetsGet(
      dashboardId,
      params
    );
  },

  // KPIs
  async createKPI(
    data: KPICreate,
    params: CreateKpiApiV1FinancialBiDashboardBiKpisPostParams
  ) {
    return await biDashboard.createKpiApiV1FinancialBiDashboardBiKpisPost(
      data,
      params
    );
  },

  async listKPIs(
    params: ListKpisApiV1FinancialBiDashboardBiKpisGetParams
  ) {
    return await biDashboard.listKpisApiV1FinancialBiDashboardBiKpisGet(
      params
    );
  },

  async getKPI(
    kpiId: string,
    params: GetKpiApiV1FinancialBiDashboardBiKpisKpiIdGetParams
  ) {
    return await biDashboard.getKpiApiV1FinancialBiDashboardBiKpisKpiIdGet(
      kpiId,
      params
    );
  },

  async updateKPI(
    kpiId: string,
    data: KPIUpdate,
    params: UpdateKpiApiV1FinancialBiDashboardBiKpisKpiIdPutParams
  ) {
    return await biDashboard.updateKpiApiV1FinancialBiDashboardBiKpisKpiIdPut(
      kpiId,
      data,
      params
    );
  },

  async deleteKPI(
    kpiId: string,
    params: DeleteKpiApiV1FinancialBiDashboardBiKpisKpiIdDeleteParams
  ) {
    return await biDashboard.deleteKpiApiV1FinancialBiDashboardBiKpisKpiIdDelete(
      kpiId,
      params
    );
  },

  async calculateKPI(
    kpiId: string,
    params: CalculateKpiApiV1FinancialBiDashboardBiKpisKpiIdCalculatePostParams
  ) {
    return await biDashboard.calculateKpiApiV1FinancialBiDashboardBiKpisKpiIdCalculatePost(
      kpiId,
      params
    );
  },

  async getKPIHistory(
    kpiId: string,
    params: GetKpiHistoryApiV1FinancialBiDashboardBiKpisKpiIdHistoryGetParams
  ) {
    return await biDashboard.getKpiHistoryApiV1FinancialBiDashboardBiKpisKpiIdHistoryGet(
      kpiId,
      params
    );
  },

  async getKPIsSummary(
    params: GetKpisSummaryApiV1FinancialBiDashboardBiKpisSummaryGetParams
  ) {
    return await biDashboard.getKpisSummaryApiV1FinancialBiDashboardBiKpisSummaryGet(
      params
    );
  },

  async getKPIsAlerts(
    params: GetKpisAlertsApiV1FinancialBiDashboardBiKpisAlertsGetParams
  ) {
    return await biDashboard.getKpisAlertsApiV1FinancialBiDashboardBiKpisAlertsGet(
      params
    );
  },

  async getKPIsStats(
    params: GetKpisStatsApiV1FinancialBiDashboardBiKpisStatsGetParams
  ) {
    return await biDashboard.getKpisStatsApiV1FinancialBiDashboardBiKpisStatsGet(
      params
    );
  },

  async calculateAllKPIs(
    params: CalculateAllKpisApiV1FinancialBiDashboardBiKpisCalculateAllPostParams
  ) {
    return await biDashboard.calculateAllKpisApiV1FinancialBiDashboardBiKpisCalculateAllPost(
      params
    );
  },

  // Reports
  async createReport(
    data: ReportCreate,
    params: CreateReportApiV1FinancialBiDashboardBiReportsPostParams
  ) {
    return await biDashboard.createReportApiV1FinancialBiDashboardBiReportsPost(
      data,
      params
    );
  },

  async listReports(
    params: ListReportsApiV1FinancialBiDashboardBiReportsGetParams
  ) {
    return await biDashboard.listReportsApiV1FinancialBiDashboardBiReportsGet(
      params
    );
  },

  async getReport(
    reportId: string,
    params: GetReportApiV1FinancialBiDashboardBiReportsReportIdGetParams
  ) {
    return await biDashboard.getReportApiV1FinancialBiDashboardBiReportsReportIdGet(
      reportId,
      params
    );
  },

  async updateReport(
    reportId: string,
    data: ReportUpdate,
    params: UpdateReportApiV1FinancialBiDashboardBiReportsReportIdPutParams
  ) {
    return await biDashboard.updateReportApiV1FinancialBiDashboardBiReportsReportIdPut(
      reportId,
      data,
      params
    );
  },

  async deleteReport(
    reportId: string,
    params: DeleteReportApiV1FinancialBiDashboardBiReportsReportIdDeleteParams
  ) {
    return await biDashboard.deleteReportApiV1FinancialBiDashboardBiReportsReportIdDelete(
      reportId,
      params
    );
  },

  async executeReport(
    reportId: string,
    params: ExecuteReportNowApiV1FinancialBiDashboardBiReportsReportIdExecutePostParams
  ) {
    return await biDashboard.executeReportNowApiV1FinancialBiDashboardBiReportsReportIdExecutePost(
      reportId,
      params
    );
  },

  async pauseReport(
    reportId: string,
    params: PauseReportApiV1FinancialBiDashboardBiReportsReportIdPausePostParams
  ) {
    return await biDashboard.pauseReportApiV1FinancialBiDashboardBiReportsReportIdPausePost(
      reportId,
      params
    );
  },

  async resumeReport(
    reportId: string,
    params: ResumeReportApiV1FinancialBiDashboardBiReportsReportIdResumePostParams
  ) {
    return await biDashboard.resumeReportApiV1FinancialBiDashboardBiReportsReportIdResumePost(
      reportId,
      params
    );
  },

  async getDueReports(
    params: GetDueReportsApiV1FinancialBiDashboardBiReportsDueGetParams
  ) {
    return await biDashboard.getDueReportsApiV1FinancialBiDashboardBiReportsDueGet(
      params
    );
  },

  // Cache
  async getCacheStats(
    params: GetCacheStatsApiV1FinancialBiDashboardBiCacheStatsGetParams
  ) {
    return await biDashboard.getCacheStatsApiV1FinancialBiDashboardBiCacheStatsGet(
      params
    );
  },

  async invalidateCache(
    data: CacheInvalidate,
    params: InvalidateCacheApiV1FinancialBiDashboardBiCacheInvalidatePostParams
  ) {
    return await biDashboard.invalidateCacheApiV1FinancialBiDashboardBiCacheInvalidatePost(
      data,
      params
    );
  },

  async cleanupCache(
    params: CleanupCacheApiV1FinancialBiDashboardBiCacheCleanupPostParams
  ) {
    return await biDashboard.cleanupCacheApiV1FinancialBiDashboardBiCacheCleanupPost(
      params
    );
  },

  // Summary
  async getFinancialSummary(
    params: GetFinancialSummaryApiV1FinancialBiDashboardBiSummaryFinancialGetParams
  ) {
    return await biDashboard.getFinancialSummaryApiV1FinancialBiDashboardBiSummaryFinancialGet(
      params
    );
  },

  async comparePeriods(
    params: ComparePeriodsApiV1FinancialBiDashboardBiSummaryCompareGetParams
  ) {
    return await biDashboard.comparePeriodsApiV1FinancialBiDashboardBiSummaryCompareGet(
      params
    );
  },
};

export default biDashboardService;
