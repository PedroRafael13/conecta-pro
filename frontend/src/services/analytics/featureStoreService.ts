/**
 * Feature Store Service
 *
 * Serviço para gerenciamento de features de ML.
 */

import {
  getUserFeaturesApiV1AnalyticsFeaturesUserUserIdGet,
  listAvailableFeaturesApiV1AnalyticsFeaturesAvailableGet,
  getFeatureMetadataApiV1AnalyticsFeaturesFeatureNameMetadataGet,
} from '@/api/generated/analytics/analytics-predictive/analytics-predictive';

export const featureStoreService = {
  /**
   * Features de um usuário
   */
  async getUserFeatures(userId: string, features?: string[]) {
    return getUserFeaturesApiV1AnalyticsFeaturesUserUserIdGet(Number(userId), {
      features: features?.join(','),
    }) as Promise<unknown>;
  },

  /**
   * Listar features disponíveis
   */
  async listAvailableFeatures() {
    return listAvailableFeaturesApiV1AnalyticsFeaturesAvailableGet() as Promise<unknown>;
  },

  /**
   * Metadados de uma feature
   */
  async getFeatureMetadata(featureName: string) {
    return getFeatureMetadataApiV1AnalyticsFeaturesFeatureNameMetadataGet(featureName) as Promise<unknown>;
  },
};
