'use client';

/**
 * Hooks React Query - Documents (Documentos de Licitação)
 *
 * Hooks para gestão de documentos exigidos em editais e documentos da empresa
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import documentsService, {
  type ListTenderDocumentsParams,
  type ListCompanyDocumentsParams,
} from '@/services/bidding/documents.service';
import type {
  CompanyDocumentCreate,
  CompanyDocumentUpdate,
} from '@/types/generated/bidding';

const QUERY_KEYS = {
  all: ['bidding', 'documents'] as const,
  tenderDocs: (tenderId: string, params?: ListTenderDocumentsParams) =>
    [...QUERY_KEYS.all, 'tender', tenderId, params] as const,
  companyDocs: {
    all: () => [...QUERY_KEYS.all, 'company'] as const,
    list: (params?: ListCompanyDocumentsParams) =>
      [...QUERY_KEYS.companyDocs.all(), 'list', params] as const,
    detail: (id: string) => [...QUERY_KEYS.companyDocs.all(), 'detail', id] as const,
    pendentes: (params?: any) =>
      [...QUERY_KEYS.companyDocs.all(), 'pendentes', params] as const,
  },
};

// ========== DOCUMENTOS DO EDITAL ==========

/**
 * Hook para listar documentos exigidos de um edital
 */
export function useListarDocumentosEdital(
  tenderId: string,
  params?: ListTenderDocumentsParams
) {
  return useQuery({
    queryKey: QUERY_KEYS.tenderDocs(tenderId, params),
    queryFn: () => documentsService.listarDocumentosEdital(tenderId, params),
    enabled: !!tenderId,
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Hook para adicionar documento exigido ao edital
 */
export function useAdicionarDocumentoEdital() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      tenderId,
      data,
    }: {
      tenderId: string;
      data: any;
    }) => documentsService.adicionarDocumentoEdital(tenderId, data),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.tenderDocs(variables.tenderId),
      });
      toast.success('Documento adicionado ao edital');
    },
    onError: (error: any) => {
      toast.error(
        error?.response?.data?.detail || 'Erro ao adicionar documento'
      );
    },
  });
}

/**
 * Hook para atualizar documento do edital
 */
export function useAtualizarDocumentoEdital() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      tenderId,
      documentId,
      data,
    }: {
      tenderId: string;
      documentId: string;
      data: any;
    }) => documentsService.atualizarDocumentoEdital(tenderId, documentId, data),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.tenderDocs(variables.tenderId),
      });
      toast.success('Documento atualizado');
    },
    onError: (error: any) => {
      toast.error(
        error?.response?.data?.detail || 'Erro ao atualizar documento'
      );
    },
  });
}

/**
 * Hook para remover documento do edital
 */
export function useRemoverDocumentoEdital() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ tenderId, documentId }: { tenderId: string; documentId: string }) =>
      documentsService.removerDocumentoEdital(tenderId, documentId),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.tenderDocs(variables.tenderId),
      });
      toast.success('Documento removido do edital');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao remover documento');
    },
  });
}

// ========== DOCUMENTOS DA EMPRESA ==========

/**
 * Hook para listar documentos da empresa
 */
export function useListarDocumentosEmpresa(params?: ListCompanyDocumentsParams) {
  return useQuery({
    queryKey: QUERY_KEYS.companyDocs.list(params),
    queryFn: () => documentsService.listarDocumentosEmpresa(params),
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Hook para buscar documento da empresa por ID
 */
export function useBuscarDocumentoEmpresa(documentId: string, enabled = true) {
  return useQuery({
    queryKey: QUERY_KEYS.companyDocs.detail(documentId),
    queryFn: () => documentsService.buscarDocumentoEmpresaPorId(documentId),
    enabled: enabled && !!documentId,
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Hook para upload de documento da empresa
 */
export function useUploadDocumentoEmpresa() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CompanyDocumentCreate) =>
      documentsService.uploadDocumentoEmpresa(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.companyDocs.all() });
      toast.success('Documento enviado com sucesso');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao enviar documento');
    },
  });
}

/**
 * Hook para atualizar documento da empresa
 */
export function useAtualizarDocumentoEmpresa() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: CompanyDocumentUpdate }) =>
      documentsService.atualizarDocumentoEmpresa(id, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.companyDocs.all() });
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.companyDocs.detail(data.id),
      });
      toast.success('Documento atualizado com sucesso');
    },
    onError: (error: any) => {
      toast.error(
        error?.response?.data?.detail || 'Erro ao atualizar documento'
      );
    },
  });
}

/**
 * Hook para remover documento da empresa
 */
export function useRemoverDocumentoEmpresa() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (documentId: string) =>
      documentsService.removerDocumentoEmpresa(documentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.companyDocs.all() });
      toast.success('Documento removido com sucesso');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao remover documento');
    },
  });
}

/**
 * Hook para listar documentos pendentes de envio
 */
export function useListarDocumentosPendentes(params?: {
  cnpj?: string;
  tender_id?: string;
}) {
  return useQuery({
    queryKey: QUERY_KEYS.companyDocs.pendentes(params),
    queryFn: () => documentsService.listarDocumentosPendentes(params),
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Hook para validar documento (Bidding)
 */
export function useValidarDocumentoBidding() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (documentId: string) =>
      documentsService.validarDocumento(documentId),
    onSuccess: (data, documentId) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.companyDocs.all() });
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.companyDocs.detail(documentId),
      });
      if (data.valido) {
        toast.success('Documento validado com sucesso');
      } else {
        toast.warning('Documento inválido');
      }
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao validar documento');
    },
  });
}

/**
 * Hook para download de documento da empresa (PDF/arquivo)
 */
export function useDownloadDocumentoEmpresa() {
  return useMutation({
    mutationFn: (documentId: string) =>
      documentsService.downloadDocumentoEmpresa(documentId),
    onSuccess: (blob, documentId) => {
      // Criar URL temporário para o blob
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `documento-${documentId}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      toast.success('Download iniciado');
    },
    onError: (error: any) => {
      toast.error(
        error?.response?.data?.detail || 'Erro ao fazer download do documento'
      );
    },
  });
}
