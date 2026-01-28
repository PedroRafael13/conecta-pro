/**
 * Forecast Service
 *
 * Serviço para previsões de vendas e forecast com IA.
 */

import {
  forecastSalesApiV1AnalyticsForecastSalesPost,
  getForecastScenariosApiV1AnalyticsForecastScenariosGet,
  getForecastAccuracyApiV1AnalyticsForecastAccuracyGet,
} from '@/api/generated/analytics/analytics-predictive/analytics-predictive';

import type {
  ForecastRequest,
  ForecastResponse,
} from '@/api/generated/analytics/conectaPROAnalyticsModule.schemas';

export const forecastService = {
  /**
   * Previsão de vendas
   */
  async forecastSales(
    periods = 30,
    granularity: 'daily' | 'weekly' | 'monthly' = 'daily',
    entityType = 'revenue'
  ): Promise<ForecastResponse> {
    const response = await forecastSalesApiV1AnalyticsForecastSalesPost({
      periods,
      granularity,
      entity_type: entityType,
    });
    return response.data;
  },

  /**
   * Cenários de previsão (pessimista, base, otimista)
   */
  async getForecastScenarios(periods = 30) {
    const response = await getForecastScenariosApiV1AnalyticsForecastScenariosGet({
      periods,
    });
    return response.data;
  },

  /**
   * Relatório de acurácia do forecast
   */
  async getForecastAccuracy(lookbackDays = 90) {
    const response = await getForecastAccuracyApiV1AnalyticsForecastAccuracyGet({
      lookback_days: lookbackDays,
    });
    return response.data;
  },
};
