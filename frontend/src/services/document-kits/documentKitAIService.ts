/**
 * Service Layer - Document Kit AI
 *
 * Funcionalidades de IA para kits documentais.
 * Endpoints cobertos:
 * - GET /document-kits/ai/suggest - Sugerir kits para entidade
 * - GET /document-kits/ai/compliance/{type}/{id} - Análise de compliance
 * - GET /document-kits/ai/predict/{id} - Predição de conclusão
 * - GET /document-kits/ai/priorities - Atribuições prioritárias
 * - GET /document-kits/ai/usage - Análise de uso
 * - GET /document-kits/ai/expiring - Documentos próximos ao vencimento
 */

import { axiosInstance } from '@/lib/api';
import type {
  KitSuggestionResponse,
  EntityType,
} from '@/types/generated/document-kits';

export interface SuggestKitsParams {
  entity_type: EntityType;
  condominio_id: string;
  cargo?: string;
  departamento?: string;
}

export interface AnalyzeComplianceParams {
  entity_type: EntityType;
  entity_id: string;
  condominio_id: string;
}

export interface PredictCompletionParams {
  assignment_id: string;
  condominio_id: string;
}

export interface GetPrioritiesParams {
  condominio_id: string;
  limit?: number;
}

export interface GetExpiringParams {
  condominio_id: string;
  days_ahead?: number;
}

class DocumentKitAIService {
  private readonly basePath = '/api/v1/document-kits/ai';

  /**
   * Sugere kits documentais para uma entidade
   */
  async suggestKits(
    params: SuggestKitsParams
  ): Promise<KitSuggestionResponse[]> {
    const { entity_type, condominio_id, cargo, departamento } = params;
    const response = await axiosInstance.get<KitSuggestionResponse[]>(
      `${this.basePath}/suggest`,
      {
        params: {
          entity_type,
          condominio_id,
          cargo,
          departamento,
        },
      }
    );
    return response.data;
  }

  /**
   * Analisa compliance de uma entidade
   */
  async analyzeCompliance(params: AnalyzeComplianceParams): Promise<{
    entity_id: string;
    entity_type: EntityType;
    compliance_score: number;
    missing_kits: string[];
    expired_documents: string[];
    risk_level: string;
    recommendations: string[];
  }> {
    const { entity_type, entity_id, condominio_id } = params;
    const response = await axiosInstance.get(
      `${this.basePath}/compliance/${entity_type}/${entity_id}`,
      { params: { condominio_id } }
    );
    return response.data;
  }

  /**
   * Prediz data de conclusão de uma atribuição
   */
  async predictCompletion(params: PredictCompletionParams): Promise<{
    assignment_id: string;
    predicted_completion_date: string;
    confidence: number;
    factors: string[];
    recommendations: string[];
  }> {
    const { assignment_id, condominio_id } = params;
    const response = await axiosInstance.get(
      `${this.basePath}/predict/${assignment_id}`,
      { params: { condominio_id } }
    );
    return response.data;
  }

  /**
   * Retorna atribuições prioritárias
   */
  async getPriorities(params: GetPrioritiesParams): Promise<
    Array<{
      assignment_id: string;
      priority_score: number;
      risk_level: string;
      reasons: string[];
      recommended_actions: string[];
    }>
  > {
    const { condominio_id, limit = 10 } = params;
    const response = await axiosInstance.get(`${this.basePath}/priorities`, {
      params: { condominio_id, limit },
    });
    return response.data;
  }

  /**
   * Analisa padrões de uso dos kits
   */
  async analyzeUsage(condominio_id: string): Promise<{
    total_kits: number;
    total_assignments: number;
    completion_rate: number;
    average_completion_time_days: number;
    most_used_kits: Array<{
      kit_id: string;
      kit_name: string;
      usage_count: number;
    }>;
    bottlenecks: string[];
    recommendations: string[];
  }> {
    const response = await axiosInstance.get(`${this.basePath}/usage`, {
      params: { condominio_id },
    });
    return response.data;
  }

  /**
   * Lista documentos próximos ao vencimento
   */
  async getExpiringDocuments(params: GetExpiringParams): Promise<
    Array<{
      assignment_id: string;
      entity_type: EntityType;
      entity_id: string;
      entity_name: string;
      item_id: string;
      item_name: string;
      expiration_date: string;
      days_until_expiration: number;
      risk_level: string;
    }>
  > {
    const { condominio_id, days_ahead = 30 } = params;
    const response = await axiosInstance.get(`${this.basePath}/expiring`, {
      params: { condominio_id, days_ahead },
    });
    return response.data;
  }
}

export const documentKitAIService = new DocumentKitAIService();
