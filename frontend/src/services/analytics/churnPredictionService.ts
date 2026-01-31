/**
 * Churn Prediction Service
 *
 * Serviço para predição de churn de usuários com IA.
 */

import {
  predictChurnApiV1AnalyticsChurnPredictPost,
  getHighRiskUsersApiV1AnalyticsChurnHighRiskGet,
  getChurnAnalyticsApiV1AnalyticsChurnAnalyticsGet,
} from '@/api/generated/analytics/analytics-predictive/analytics-predictive';

import type {
  ChurnPredictionRequest,
  ChurnPredictionResponse,
} from '@/api/generated/analytics/conectaPROAnalyticsModule.schemas';

export const churnPredictionService = {
  /**
   * Predizer churn de usuário
   */
  async predictChurn(userId: number): Promise<ChurnPredictionResponse> {
    return predictChurnApiV1AnalyticsChurnPredictPost({
      user_id: userId,
    }) as Promise<ChurnPredictionResponse>;
  },

  /**
   * Listar usuários com alto risco de churn
   */
  async getHighRiskUsers(limit = 50, minRisk = 'high') {
    return getHighRiskUsersApiV1AnalyticsChurnHighRiskGet({
      limit,
      min_risk: minRisk,
    }) as Promise<unknown>;
  },

  /**
   * Analytics de churn
   */
  async getChurnAnalytics() {
    return getChurnAnalyticsApiV1AnalyticsChurnAnalyticsGet() as Promise<unknown>;
  },
};
