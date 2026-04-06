/**
 * Document Kits AI Service
 * Análise inteligente de kits documentais: compliance, previsões, prioridades
 */

import { customInstance } from '@/lib/axios-instance';

type EntityType = 'employee' | 'condominium' | 'client' | string;

const BASE = '/api/v1/document-kits/ai';

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
  ): Promise<unknown> {
    return customInstance.get(`${BASE}/compliance/${entityType}/${entityId}`, {
      params: { condominio_id: condominioId },
    });
  }

  /**
   * Lista documentos expirando em breve
   */
  static async getExpiringDocuments(
    condominioId: string,
    daysAhead?: number
  ): Promise<unknown> {
    return customInstance.get(`${BASE}/expiring`, {
      params: { condominio_id: condominioId, days_ahead: daysAhead },
    });
  }

  /**
   * Prevê status futuro de documentação
   */
  static async predictStatus(
    assignmentId: string,
    condominioId: string
  ): Promise<unknown> {
    return customInstance.get(`${BASE}/predict/${assignmentId}`, {
      params: { condominio_id: condominioId },
    });
  }

  /**
   * Obtém prioridades de documentação
   */
  static async getPriorities(
    condominioId: string,
    limit?: number
  ): Promise<unknown> {
    return customInstance.get(`${BASE}/priorities`, {
      params: { condominio_id: condominioId, limit },
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
  ): Promise<unknown> {
    return customInstance.get(`${BASE}/suggest`, {
      params: {
        condominio_id: condominioId,
        entity_type: entityType,
        cargo,
        departamento,
      },
    });
  }

  /**
   * Analisa uso e padrões de documentação
   */
  static async analyzeUsage(condominioId: string): Promise<unknown> {
    return customInstance.get(`${BASE}/usage`, {
      params: { condominio_id: condominioId },
    });
  }
}

export default DocumentKitsAIService;
