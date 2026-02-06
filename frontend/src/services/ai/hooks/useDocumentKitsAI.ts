/**
 * React Query hooks for Document Kits AI
 */

import { useMutation, useQuery } from '@tanstack/react-query';
import { DocumentKitsAIService } from '../document-kits.service';

/**
 * Hook para verificar compliance
 */
export function useCheckCompliance(entityType: string, entityId: string, condominioId: string) {
  return useQuery({
    queryKey: ['document-kits-ai', 'compliance', entityType, entityId, condominioId],
    queryFn: () => DocumentKitsAIService.checkCompliance(entityType as any, entityId, condominioId),
    enabled: !!entityType && !!entityId && !!condominioId,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook para documentos expirando
 */
export function useExpiringDocuments(condominioId: string, daysAhead?: number) {
  return useQuery({
    queryKey: ['document-kits-ai', 'expiring', condominioId, daysAhead],
    queryFn: () => DocumentKitsAIService.getExpiringDocuments(condominioId, daysAhead),
    enabled: !!condominioId,
    staleTime: 10 * 60 * 1000,
  });
}

/**
 * Hook para prever status de documentação
 */
export function usePredictStatus(assignmentId: string, condominioId: string) {
  return useQuery({
    queryKey: ['document-kits-ai', 'predict-status', assignmentId, condominioId],
    queryFn: () => DocumentKitsAIService.predictStatus(assignmentId, condominioId),
    enabled: !!assignmentId && !!condominioId,
    staleTime: 15 * 60 * 1000,
  });
}

/**
 * Hook para prioridades de documentação
 */
export function useDocumentationPriorities(condominioId: string, limit?: number) {
  return useQuery({
    queryKey: ['document-kits-ai', 'priorities', condominioId, limit],
    queryFn: () => DocumentKitsAIService.getPriorities(condominioId, limit),
    enabled: !!condominioId,
    staleTime: 10 * 60 * 1000,
  });
}

/**
 * Hook para sugerir documentos
 */
export function useSuggestDocuments() {
  return useMutation({
    mutationFn: ({
      condominioId,
      entityType,
      cargo,
      departamento,
    }: {
      condominioId: string;
      entityType: string;
      cargo?: string;
      departamento?: string;
    }) => DocumentKitsAIService.suggestDocuments(condominioId, entityType as any, cargo, departamento),
  });
}

/**
 * Hook para analisar uso de documentação
 */
export function useDocumentUsageAnalysis(condominioId: string) {
  return useQuery({
    queryKey: ['document-kits-ai', 'usage', condominioId],
    queryFn: () => DocumentKitsAIService.analyzeUsage(condominioId),
    enabled: !!condominioId,
    staleTime: 30 * 60 * 1000,
  });
}
