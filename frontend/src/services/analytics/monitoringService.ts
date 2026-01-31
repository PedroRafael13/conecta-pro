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
    return getMonitoringDashboardApiV1AnalyticsMonitoringDashboardGet() as Promise<unknown>;
  },

  /**
   * Saúde de um modelo específico
   */
  async getModelHealth(modelName: string): Promise<ModelHealthResponse> {
    return getModelHealthApiV1AnalyticsMonitoringModelsModelNameHealthGet(modelName) as Promise<ModelHealthResponse>;
  },

  /**
   * Listar alertas de monitoramento
   */
  async getAlerts(modelName?: string, acknowledged?: boolean) {
    return getMonitoringAlertsApiV1AnalyticsMonitoringAlertsGet({
      model_name: modelName,
      acknowledged,
    }) as Promise<unknown>;
  },

  /**
   * Reconhecer alerta
   */
  async acknowledgeAlert(alertId: string) {
    return acknowledgeMonitoringAlertApiV1AnalyticsMonitoringAlertsAlertIdAcknowledgePut(alertId) as Promise<unknown>;
  },
};
