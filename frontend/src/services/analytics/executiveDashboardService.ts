/**
 * Executive Dashboard Service
 *
 * Serviço para gerenciar dashboard executivo com KPIs,
 * alertas e insights preditivos.
 */

import {
  getExecutiveDashboardApiV1AnalyticsExecutiveDashboardGet,
  getKpisByCategoryApiV1AnalyticsExecutiveKpisCategoryGet,
  getActiveAlertsApiV1AnalyticsExecutiveAlertsActiveGet,
  getPredictiveInsightsApiV1AnalyticsExecutiveInsightsPredictiveGet,
  getExecutiveSummaryApiV1AnalyticsExecutiveSummaryGet,
  exportDashboardApiV1AnalyticsExecutiveExportGet,
  dashboardHealthCheckApiV1AnalyticsExecutiveHealthGet,
} from '@/api/generated/analytics/analytics-executive-dashboard/analytics-executive-dashboard';

import type {
  GetExecutiveDashboardApiV1AnalyticsExecutiveDashboardGet200,
  GetKpisByCategoryApiV1AnalyticsExecutiveKpisCategoryGet200,
  GetActiveAlertsApiV1AnalyticsExecutiveAlertsActiveGet200,
  GetPredictiveInsightsApiV1AnalyticsExecutiveInsightsPredictiveGet200,
  GetExecutiveSummaryApiV1AnalyticsExecutiveSummaryGet200,
  ExportDashboardApiV1AnalyticsExecutiveExportGet200,
  DashboardHealthCheckApiV1AnalyticsExecutiveHealthGet200,
} from '@/api/generated/analytics/conectaPROAnalyticsModule.schemas';

export const executiveDashboardService = {
  /**
   * Obter dashboard executivo completo
   */
  async getDashboard(refresh?: boolean): Promise<GetExecutiveDashboardApiV1AnalyticsExecutiveDashboardGet200> {
    const response = await getExecutiveDashboardApiV1AnalyticsExecutiveDashboardGet({
      refresh: refresh || false,
    });
    return response.data;
  },

  /**
   * Obter KPIs por categoria
   */
  async getKpisByCategory(category: string): Promise<GetKpisByCategoryApiV1AnalyticsExecutiveKpisCategoryGet200> {
    const response = await getKpisByCategoryApiV1AnalyticsExecutiveKpisCategoryGet(category);
    return response.data;
  },

  /**
   * Obter alertas ativos
   */
  async getActiveAlerts(): Promise<GetActiveAlertsApiV1AnalyticsExecutiveAlertsActiveGet200> {
    const response = await getActiveAlertsApiV1AnalyticsExecutiveAlertsActiveGet();
    return response.data;
  },

  /**
   * Obter insights preditivos
   */
  async getPredictiveInsights(): Promise<GetPredictiveInsightsApiV1AnalyticsExecutiveInsightsPredictiveGet200> {
    const response = await getPredictiveInsightsApiV1AnalyticsExecutiveInsightsPredictiveGet();
    return response.data;
  },

  /**
   * Obter resumo executivo
   */
  async getSummary(): Promise<GetExecutiveSummaryApiV1AnalyticsExecutiveSummaryGet200> {
    const response = await getExecutiveSummaryApiV1AnalyticsExecutiveSummaryGet();
    return response.data;
  },

  /**
   * Exportar dashboard
   */
  async exportDashboard(formatType: 'json' | 'csv' = 'json'): Promise<ExportDashboardApiV1AnalyticsExecutiveExportGet200> {
    const response = await exportDashboardApiV1AnalyticsExecutiveExportGet({
      format_type: formatType,
    });
    return response.data;
  },

  /**
   * Health check do dashboard
   */
  async healthCheck(): Promise<DashboardHealthCheckApiV1AnalyticsExecutiveHealthGet200> {
    const response = await dashboardHealthCheckApiV1AnalyticsExecutiveHealthGet();
    return response.data;
  },
};
