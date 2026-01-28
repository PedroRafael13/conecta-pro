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
    const response = await listModelsApiV1AnalyticsModelsGet();
    return response.data;
  },

  /**
   * Listar versões de um modelo
   */
  async listModelVersions(modelName: string, stage?: string) {
    const response = await listModelVersionsApiV1AnalyticsModelsModelNameVersionsGet(modelName, {
      stage,
    });
    return response.data;
  },

  /**
   * Comparar versões de modelo
   */
  async compareVersions(modelName: string, version1: string, version2: string) {
    const response = await compareModelVersionsApiV1AnalyticsModelsModelNameCompareGet(modelName, {
      version1,
      version2,
    });
    return response.data;
  },

  /**
   * Promover modelo para produção
   */
  async promoteModel(modelName: string, version: string, targetStage = 'production') {
    const response = await promoteModelApiV1AnalyticsModelsModelNamePromotePost(modelName, {
      version,
      target_stage: targetStage,
    });
    return response.data;
  },
};
