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
    return analyzeTransactionApiV1AnalyticsFraudAnalyzePost(transaction) as Promise<FraudAlertResponse>;
  },

  /**
   * Listar alertas de fraude
   */
  async getFraudAlerts(minRisk?: string, acknowledged?: boolean, limit = 50) {
    return getFraudAlertsApiV1AnalyticsFraudAlertsGet({
      min_risk: minRisk,
      acknowledged,
      limit,
    }) as Promise<unknown>;
  },

  /**
   * Atualizar status de alerta de fraude
   */
  async updateAlertStatus(alertId: string, newStatus: string, notes?: string) {
    return updateAlertStatusApiV1AnalyticsFraudAlertsAlertIdStatusPut(alertId, {
      new_status: newStatus,
      notes,
    }) as Promise<unknown>;
  },

  /**
   * Analytics de fraude
   */
  async getFraudAnalytics() {
    return getFraudAnalyticsApiV1AnalyticsFraudAnalyticsGet() as Promise<unknown>;
  },

  /**
   * Perfil de risco de usuário
   */
  async getUserRiskProfile(userId: string) {
    return getUserRiskProfileApiV1AnalyticsFraudUserUserIdRiskGet(Number(userId)) as Promise<unknown>;
  },
};
