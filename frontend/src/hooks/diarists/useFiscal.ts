/**
 * Hook: useFiscal
 *
 * Operações fiscais para diaristas:
 * - Cálculo de retenções
 * - Documentos fiscais
 * - Relatórios
 * - Tabelas
 */

import { useQuery, useMutation } from '@tanstack/react-query';
import { diaristFiscalService } from '@/services/diarists';
import type {
  TipoDocumentoFiscal,
  StatusDocumentoFiscal,
} from '@/api/diarists/generated/models';

/**
 * Hook para simular retenções
 */
export function useSimulateRetentions() {
  return useMutation({
    mutationFn: (params: {
      valorBruto: number;
      dependentes?: number;
      aliquotaIss?: number;
    }) => diaristFiscalService.simulateRetentions(params.valorBruto, params),
  });
}

/**
 * Hook para listar documentos fiscais
 */
export function useListFiscalDocuments(params?: {
  diaristId?: string;
  tipo?: TipoDocumentoFiscal;
  competencia?: string;
  status?: StatusDocumentoFiscal;
  limit?: number;
}) {
  return useQuery({
    queryKey: ['diarists', 'fiscal', 'documents', 'list', params],
    queryFn: () => diaristFiscalService.listDocuments(params),
  });
}

/**
 * Hook para buscar documento fiscal
 */
export function useFiscalDocument(documentoId: string) {
  return useQuery({
    queryKey: ['diarists', 'fiscal', 'documents', 'detail', documentoId],
    queryFn: () => diaristFiscalService.getDocument(documentoId),
    enabled: !!documentoId,
  });
}

/**
 * Hook para relatório de retenções
 */
export function useRetentionsReport(params: {
  dataInicio: string;
  dataFim: string;
  diaristId?: string;
}) {
  return useQuery({
    queryKey: ['diarists', 'fiscal', 'retentions-report', params],
    queryFn: () => diaristFiscalService.getRetentionsReport(params),
    enabled: !!params.dataInicio && !!params.dataFim,
  });
}

/**
 * Hook para relatório fiscal de diarista
 */
export function useDiaristFiscalReport(diaristId: string, ano: number) {
  return useQuery({
    queryKey: ['diarists', 'fiscal', 'diarist-report', diaristId, ano],
    queryFn: () => diaristFiscalService.getDiaristReport(diaristId, ano),
    enabled: !!diaristId && !!ano,
  });
}

/**
 * Hook para tabela INSS
 */
export function useInssTable() {
  return useQuery({
    queryKey: ['diarists', 'fiscal', 'inss-table'],
    queryFn: () => diaristFiscalService.getInssTable(),
    staleTime: 1000 * 60 * 60 * 24, // 24 horas
  });
}

/**
 * Hook para tabela IRRF
 */
export function useIrrfTable() {
  return useQuery({
    queryKey: ['diarists', 'fiscal', 'irrf-table'],
    queryFn: () => diaristFiscalService.getIrrfTable(),
    staleTime: 1000 * 60 * 60 * 24, // 24 horas
  });
}

/**
 * Hook para códigos de serviço
 */
export function useServiceCodes() {
  return useQuery({
    queryKey: ['diarists', 'fiscal', 'service-codes'],
    queryFn: () => diaristFiscalService.listServiceCodes(),
    staleTime: 1000 * 60 * 60 * 24, // 24 horas
  });
}
