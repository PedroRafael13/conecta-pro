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
    return getExecutiveDashboardApiV1AnalyticsExecutiveDashboardGet({
      refresh: refresh || false,
    }) as Promise<GetExecutiveDashboardApiV1AnalyticsExecutiveDashboardGet200>;
  },

  /**
   * Obter KPIs por categoria
   */
  async getKpisByCategory(category: string): Promise<GetKpisByCategoryApiV1AnalyticsExecutiveKpisCategoryGet200> {
    return getKpisByCategoryApiV1AnalyticsExecutiveKpisCategoryGet(category) as Promise<GetKpisByCategoryApiV1AnalyticsExecutiveKpisCategoryGet200>;
  },

  /**
   * Obter alertas ativos
   */
  async getActiveAlerts(): Promise<GetActiveAlertsApiV1AnalyticsExecutiveAlertsActiveGet200> {
    return getActiveAlertsApiV1AnalyticsExecutiveAlertsActiveGet() as Promise<GetActiveAlertsApiV1AnalyticsExecutiveAlertsActiveGet200>;
  },

  /**
   * Obter insights preditivos
   */
  async getPredictiveInsights(): Promise<GetPredictiveInsightsApiV1AnalyticsExecutiveInsightsPredictiveGet200> {
    return getPredictiveInsightsApiV1AnalyticsExecutiveInsightsPredictiveGet() as Promise<GetPredictiveInsightsApiV1AnalyticsExecutiveInsightsPredictiveGet200>;
  },

  /**
   * Obter resumo executivo
   */
  async getSummary(): Promise<GetExecutiveSummaryApiV1AnalyticsExecutiveSummaryGet200> {
    return getExecutiveSummaryApiV1AnalyticsExecutiveSummaryGet() as Promise<GetExecutiveSummaryApiV1AnalyticsExecutiveSummaryGet200>;
  },

  /**
   * Exportar dashboard
   */
  async exportDashboard(formatType: 'json' | 'csv' = 'json'): Promise<ExportDashboardApiV1AnalyticsExecutiveExportGet200> {
    return exportDashboardApiV1AnalyticsExecutiveExportGet({
      format_type: formatType,
    }) as Promise<ExportDashboardApiV1AnalyticsExecutiveExportGet200>;
  },

  /**
   * Health check do dashboard
   */
  async healthCheck(): Promise<DashboardHealthCheckApiV1AnalyticsExecutiveHealthGet200> {
    return dashboardHealthCheckApiV1AnalyticsExecutiveHealthGet() as Promise<DashboardHealthCheckApiV1AnalyticsExecutiveHealthGet200>;
  },
};
