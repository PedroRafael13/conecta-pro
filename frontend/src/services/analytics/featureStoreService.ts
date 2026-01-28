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
  async getUserFeatures(userId: number, features?: string[]) {
    const response = await getUserFeaturesApiV1AnalyticsFeaturesUserUserIdGet(userId.toString(), {
      features: features?.join(','),
    });
    return response.data;
  },

  /**
   * Listar features disponíveis
   */
  async listAvailableFeatures() {
    const response = await listAvailableFeaturesApiV1AnalyticsFeaturesAvailableGet();
    return response.data;
  },

  /**
   * Metadados de uma feature
   */
  async getFeatureMetadata(featureName: string) {
    const response = await getFeatureMetadataApiV1AnalyticsFeaturesFeatureNameMetadataGet(featureName);
    return response.data;
  },
};
