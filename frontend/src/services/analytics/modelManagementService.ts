/**
 * Model Management Service
 *
 * Serviço para gerenciamento de modelos de ML.
 */

import {
  listModelsApiV1AnalyticsModelsGet,
  listModelVersionsApiV1AnalyticsModelsModelNameVersionsGet,
  compareModelVersionsApiV1AnalyticsModelsModelNameCompareGet,
  promoteModelApiV1AnalyticsModelsModelNamePromotePost,
} from '@/api/generated/analytics/analytics-predictive/analytics-predictive';

export const modelManagementService = {
  /**
   * Listar modelos registrados
   */
  async listModels() {
    return listModelsApiV1AnalyticsModelsGet() as Promise<unknown>;
  },

  /**
   * Listar versões de um modelo
   */
  async listModelVersions(modelName: string, stage?: string) {
    return listModelVersionsApiV1AnalyticsModelsModelNameVersionsGet(modelName, {
      stage,
    }) as Promise<unknown>;
  },

  /**
   * Comparar versões de modelo
   */
  async compareVersions(modelName: string, version1: string, version2: string) {
    return compareModelVersionsApiV1AnalyticsModelsModelNameCompareGet(modelName, {
      version1,
      version2,
    }) as Promise<unknown>;
  },

  /**
   * Promover modelo para produção
   */
  async promoteModel(modelName: string, version: string, targetStage = 'production') {
    return promoteModelApiV1AnalyticsModelsModelNamePromotePost(modelName, {
      version,
      target_stage: targetStage,
    }) as Promise<unknown>;
  },
};
