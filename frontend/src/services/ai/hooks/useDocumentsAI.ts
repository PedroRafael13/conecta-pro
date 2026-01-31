/**
 * React Query hooks for Documents AI
 */

import { useMutation, useQuery } from '@tanstack/react-query';
import { DocumentsAIService } from '../documents.service';

/**
 * Hook para analisar documento com OCR
 */
export function useAnalyzeWithOCR() {
  return useMutation({
    mutationFn: ({ documentId, ocrText }: { documentId: string; ocrText: string }) =>
      DocumentsAIService.analyzeWithOCR(documentId, ocrText),
  });
}

/**
 * Hook para classificar documento
 */
export function useClassifyDocument() {
  return useMutation({
    mutationFn: ({ text, fileName }: { text: string; fileName?: string }) =>
      DocumentsAIService.classifyDocument(text, fileName),
  });
}

/**
 * Hook para verificar duplicatas
 */
export function useCheckDuplicates() {
  return useMutation({
    mutationFn: ({
      checksum,
      title,
      condominiumId
    }: {
      checksum: string;
      title: string;
      condominiumId?: string;
    }) => DocumentsAIService.checkDuplicates(checksum, title, condominiumId),
  });
}

/**
 * Hook para extrair palavras-chave
 */
export function useExtractKeywords() {
  return useMutation({
    mutationFn: ({ text, maxKeywords }: { text: string; maxKeywords?: number }) =>
      DocumentsAIService.extractKeywords(text, maxKeywords),
  });
}

/**
 * Hook para obter insights de documentos
 */
export function useDocumentInsights(condominiumId?: string) {
  return useQuery({
    queryKey: ['documents-ai', 'insights', condominiumId],
    queryFn: () => DocumentsAIService.getInsights(condominiumId),
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook para analisar tendências
 */
export function useDocumentTrends(condominiumId?: string, days?: number) {
  return useQuery({
    queryKey: ['documents-ai', 'trends', condominiumId, days],
    queryFn: () => DocumentsAIService.analyzeTrends(condominiumId, days),
    staleTime: 10 * 60 * 1000,
  });
}

/**
 * Hook para dashboard de documentos
 */
export function useDocumentsDashboard(condominiumId?: string) {
  return useQuery({
    queryKey: ['documents-ai', 'dashboard', condominiumId],
    queryFn: () => DocumentsAIService.getDashboard(condominiumId),
    staleTime: 2 * 60 * 1000,
  });
}
