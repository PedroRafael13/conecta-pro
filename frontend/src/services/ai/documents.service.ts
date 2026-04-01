/**
 * Documents AI Service
 * Análise inteligente de documentos: OCR, classificação, extração
 */

import { customInstance } from '@/lib/axios-instance';

const BASE = '/api/v1/ged/documents/ai';

/**
 * Service para análise de documentos com IA
 */
export class DocumentsAIService {
  /**
   * Analisa documento com OCR e extração de dados
   */
  static async analyzeWithOCR(
    documentId: string,
    ocrText: string
  ): Promise<unknown> {
    return customInstance.post(`/api/v1/ged/documents/${documentId}/ai/analyze-ocr`, {
      ocr_text: ocrText,
    });
  }

  /**
   * Classifica documento automaticamente
   */
  static async classifyDocument(
    text: string,
    fileName?: string
  ): Promise<unknown> {
    return customInstance.post(`${BASE}/classify`, {
      text,
      file_name: fileName,
    });
  }

  /**
   * Verifica duplicatas de documentos
   */
  static async checkDuplicates(
    checksum: string,
    title: string,
    condominiumId?: string
  ): Promise<unknown> {
    return customInstance.post(`${BASE}/check-duplicates`, {
      checksum,
      title,
      condominium_id: condominiumId,
    });
  }

  /**
   * Extrai palavras-chave de documentos
   */
  static async extractKeywords(text: string, maxKeywords?: number): Promise<unknown> {
    return customInstance.post(`${BASE}/extract-keywords`, {
      text,
      max_keywords: maxKeywords,
    });
  }

  /**
   * Obtém insights sobre documentos
   */
  static async getInsights(condominiumId?: string): Promise<unknown> {
    return customInstance.get(`${BASE}/insights`, {
      params: { condominium_id: condominiumId },
    });
  }

  /**
   * Analisa tendências de documentos
   */
  static async analyzeTrends(
    condominiumId?: string,
    days?: number
  ): Promise<unknown> {
    return customInstance.get(`${BASE}/trends`, {
      params: { condominium_id: condominiumId, days },
    });
  }

  /**
   * Dashboard de métricas de documentos
   */
  static async getDashboard(condominiumId?: string): Promise<unknown> {
    return customInstance.get(`${BASE}/dashboard`, {
      params: { condominium_id: condominiumId },
    });
  }
}

export default DocumentsAIService;
