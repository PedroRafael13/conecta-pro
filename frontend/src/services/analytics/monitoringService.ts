/**
 * Monitoring Service
 *
 * Serviço para monitoramento de modelos de ML.
 */

import {
  getMonitoringDashboardApiV1AnalyticsMonitoringDashboardGet,
  getModelHealthApiV1AnalyticsMonitoringModelsModelNameHealthGet,
  getMonitoringAlertsApiV1AnalyticsMonitoringAlertsGet,
  acknowledgeMonitoringAlertApiV1AnalyticsMonitoringAlertsAlertIdAcknowledgePut,
} from '@/api/generated/analytics/analytics-predictive/analytics-predictive';

import type {
  ModelHealthResponse,
} from '@/api/generated/analytics/conectaPROAnalyticsModule.schemas';

export const monitoringService = {
  /**
   * Dashboard de monitoramento
   */
  async getDashboard() {
    const response = await getMonitoringDashboardApiV1AnalyticsMonitoringDashboardGet();
    return response.data;
  },

  /**
   * Saúde de um modelo específico
   */
  async getModelHealth(modelName: string): Promise<ModelHealthResponse> {
    const response = await getModelHealthApiV1AnalyticsMonitoringModelsModelNameHealthGet(modelName);
    return response.data;
  },

  /**
   * Listar alertas de monitoramento
   */
  async getAlerts(modelName?: string, acknowledged?: boolean) {
    const response = await getMonitoringAlertsApiV1AnalyticsMonitoringAlertsGet({
      model_name: modelName,
      acknowledged,
    });
    return response.data;
  },

  /**
   * Reconhecer alerta
   */
  async acknowledgeAlert(alertId: string) {
    const response = await acknowledgeMonitoringAlertApiV1AnalyticsMonitoringAlertsAlertIdAcknowledgePut(alertId);
    return response.data;
  },
};
