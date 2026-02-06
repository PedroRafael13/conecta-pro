/**
 * Document Kits AI Service
 * Análise inteligente de kits documentais: compliance, previsões, prioridades
 */

import { getDocumentKits } from '@/types/generated/ai/document-kits/document-kits';
import { EntityType } from '@/types/generated/ai/conectaPROAIBartoloAPI.schemas';

const kitsApi = getDocumentKits();

/**
 * Service para análise de kits documentais com IA
 */
export class DocumentKitsAIService {
  /**
   * Verifica compliance de documentos de entidade
   */
  static async checkCompliance(
    entityType: EntityType,
    entityId: string,
    condominioId: string
  ): Promise<any> {
    return kitsApi.analyzeComplianceApiV1DocumentKitsAiComplianceEntityTypeEntityIdGet(
      entityType,
      entityId,
      { condominio_id: condominioId }
    );
  }

  /**
   * Lista documentos expirando em breve
   */
  static async getExpiringDocuments(
    condominioId: string,
    daysAhead?: number
  ): Promise<any> {
    return kitsApi.getExpiringDocumentsApiV1DocumentKitsAiExpiringGet({
      condominio_id: condominioId,
      days_ahead: daysAhead,
    });
  }

  /**
   * Prevê status futuro de documentação
   */
  static async predictStatus(
    assignmentId: string,
    condominioId: string
  ): Promise<any> {
    return kitsApi.predictCompletionApiV1DocumentKitsAiPredictAssignmentIdGet(
      assignmentId,
      { condominio_id: condominioId }
    );
  }

  /**
   * Obtém prioridades de documentação
   */
  static async getPriorities(
    condominioId: string,
    limit?: number
  ): Promise<any> {
    return kitsApi.getPrioritiesApiV1DocumentKitsAiPrioritiesGet({
      condominio_id: condominioId,
      limit,
    });
  }

  /**
   * Sugere documentos necessários
   */
  static async suggestDocuments(
    condominioId: string,
    entityType: EntityType,
    cargo?: string,
    departamento?: string
  ): Promise<any> {
    return kitsApi.suggestKitsApiV1DocumentKitsAiSuggestGet({
      condominio_id: condominioId,
      entity_type: entityType,
      cargo,
      departamento,
    });
  }

  /**
   * Analisa uso e padrões de documentação
   */
  static async analyzeUsage(condominioId: string): Promise<any> {
    return kitsApi.analyzeUsageApiV1DocumentKitsAiUsageGet({
      condominio_id: condominioId,
    });
  }
}

export default DocumentKitsAIService;
