/**
 * GED Documents Hooks - Gestao de Documentos
 *
 * Re-exports dos hooks Orval do modulo GED documentos
 */

import {
  useListDocumentsApiV1GedDocumentsGet,
  useCreateDocumentApiV1GedDocumentsPost,
  useUploadDocumentApiV1GedDocumentsUploadPost,
  useDeleteDocumentApiV1GedDocumentsDocumentIdDelete,
  useGetViewUrlApiV1GedDocumentsDocumentIdViewUrlGet,
  useGetDocumentApiV1GedDocumentsDocumentIdGet,
  useUpdateDocumentApiV1GedDocumentsDocumentIdPut,
  useGetByFolderApiV1GedDocumentsFolderFolderIdGet,
  useSearchDocumentsApiV1GedDocumentsSearchQueryGet,
  useGetStatsApiV1GedDocumentsStatsSummaryGet,
} from '@/types/generated/ged/ged-documentos/ged-documentos';

import { customInstance } from '@/lib/api-client';

// Queries
export const useDocuments = useListDocumentsApiV1GedDocumentsGet;
export const useDocument = useGetDocumentApiV1GedDocumentsDocumentIdGet;
export const useDocumentsByFolder = useGetByFolderApiV1GedDocumentsFolderFolderIdGet;
export const useDocumentViewUrl = useGetViewUrlApiV1GedDocumentsDocumentIdViewUrlGet;
export const useSearchDocuments = useSearchDocumentsApiV1GedDocumentsSearchQueryGet;
export const useDocumentStats = useGetStatsApiV1GedDocumentsStatsSummaryGet;

// Mutations
export const useCreateDocument = useCreateDocumentApiV1GedDocumentsPost;
export const useUploadDocument = useUploadDocumentApiV1GedDocumentsUploadPost;
export const useUpdateDocument = useUpdateDocumentApiV1GedDocumentsDocumentIdPut;
export const useDeleteDocument = useDeleteDocumentApiV1GedDocumentsDocumentIdDelete;

/**
 * Download de arquivo (blob) - funcao utilitaria
 * Orval nao gera hook com responseType blob, entao usamos customInstance direto
 */
export const downloadDocumentFile = async (documentId: string, fileName: string) => {
  const blob = await customInstance<Blob>({
    url: `/api/v1/ged/documents/${documentId}/download`,
    method: 'GET',
    responseType: 'blob',
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = fileName;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

// Re-export types
export type {
  DocumentResponse,
  DocumentCreate,
  DocumentUpdate,
  DocumentListResponse,
  ListDocumentsApiV1GedDocumentsGetParams,
  BodyUploadDocumentApiV1GedDocumentsUploadPost,
} from '@/types/generated/ged/schemas';
