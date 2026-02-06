/**
 * Documents AI Service
 * Análise inteligente de documentos: OCR, classificação, extração
 */

import { getGedDocumentos } from '@/types/generated/ai/ged-documentos/ged-documentos';

const documentsApi = getGedDocumentos();

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
  ): Promise<any> {
    return documentsApi.analyzeOcrApiV1GedDocumentsDocumentIdAiAnalyzeOcrPost(
      documentId,
      { ocr_text: ocrText }
    );
  }

  /**
   * Classifica documento automaticamente
   */
  static async classifyDocument(
    text: string,
    fileName?: string
  ): Promise<any> {
    return documentsApi.classifyDocumentApiV1GedDocumentsAiClassifyPost({
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
  ): Promise<any> {
    return documentsApi.checkDuplicatesApiV1GedDocumentsAiCheckDuplicatesPost({
      checksum,
      title,
      condominium_id: condominiumId,
    });
  }

  /**
   * Extrai palavras-chave de documentos
   */
  static async extractKeywords(text: string, maxKeywords?: number): Promise<any> {
    return documentsApi.extractKeywordsApiV1GedDocumentsAiExtractKeywordsPost({
      text,
      max_keywords: maxKeywords,
    });
  }

  /**
   * Obtém insights sobre documentos
   */
  static async getInsights(condominiumId?: string): Promise<any> {
    return documentsApi.getInsightsApiV1GedDocumentsAiInsightsGet({
      condominium_id: condominiumId,
    });
  }

  /**
   * Analisa tendências de documentos
   */
  static async analyzeTrends(
    condominiumId?: string,
    days?: number
  ): Promise<any> {
    return documentsApi.getTrendsApiV1GedDocumentsAiTrendsGet({
      condominium_id: condominiumId,
      days,
    });
  }

  /**
   * Dashboard de métricas de documentos
   */
  static async getDashboard(condominiumId?: string): Promise<any> {
    return documentsApi.getAiDashboardApiV1GedDocumentsAiDashboardGet({
      condominium_id: condominiumId,
    });
  }
}

export default DocumentsAIService;
