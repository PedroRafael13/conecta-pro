/**
 * Fraud Detection Service
 *
 * Serviço para detecção de fraudes em tempo real com IA.
 */

import {
  analyzeTransactionApiV1AnalyticsFraudAnalyzePost,
  getFraudAlertsApiV1AnalyticsFraudAlertsGet,
  updateAlertStatusApiV1AnalyticsFraudAlertsAlertIdStatusPut,
  getFraudAnalyticsApiV1AnalyticsFraudAnalyticsGet,
  getUserRiskProfileApiV1AnalyticsFraudUserUserIdRiskGet,
} from '@/api/generated/analytics/analytics-predictive/analytics-predictive';

import type {
  TransactionAnalysisRequest,
  FraudAlertResponse,
} from '@/api/generated/analytics/conectaPROAnalyticsModule.schemas';

export const fraudDetectionService = {
  /**
   * Analisar transação para detecção de fraude
   */
  async analyzeTransaction(transaction: TransactionAnalysisRequest): Promise<FraudAlertResponse> {
    const response = await analyzeTransactionApiV1AnalyticsFraudAnalyzePost(transaction);
    return response.data;
  },

  /**
   * Listar alertas de fraude
   */
  async getFraudAlerts(minRisk?: string, acknowledged?: boolean, limit = 50) {
    const response = await getFraudAlertsApiV1AnalyticsFraudAlertsGet({
      min_risk: minRisk,
      acknowledged,
      limit,
    });
    return response.data;
  },

  /**
   * Atualizar status de alerta de fraude
   */
  async updateAlertStatus(alertId: string, newStatus: string, notes?: string) {
    const response = await updateAlertStatusApiV1AnalyticsFraudAlertsAlertIdStatusPut(alertId, {
      new_status: newStatus,
      notes,
    });
    return response.data;
  },

  /**
   * Analytics de fraude
   */
  async getFraudAnalytics() {
    const response = await getFraudAnalyticsApiV1AnalyticsFraudAnalyticsGet();
    return response.data;
  },

  /**
   * Perfil de risco de usuário
   */
  async getUserRiskProfile(userId: number) {
    const response = await getUserRiskProfileApiV1AnalyticsFraudUserUserIdRiskGet(userId.toString());
    return response.data;
  },
};
