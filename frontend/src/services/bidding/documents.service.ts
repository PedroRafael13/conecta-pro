/**
 * Service Layer - Documents (Documentos de Licitação)
 *
 * Endpoints: Upload, gestão de documentos exigidos em editais
 * Atestados, declarações, documentação técnica
 */

import api from '@/lib/api';
import type {
  CompanyDocumentCreate,
  CompanyDocumentUpdate,
  CompanyDocumentResponse,
} from '@/types/generated/bidding';

// Tipos para documentos de edital (não disponíveis nos schemas gerados)
interface TenderDocumentCreate {
  nome: string;
  tipo: string;
  obrigatorio?: boolean;
  descricao?: string;
  [key: string]: any;
}

interface TenderDocumentUpdate {
  nome?: string;
  tipo?: string;
  obrigatorio?: boolean;
  descricao?: string;
  [key: string]: any;
}

interface TenderDocumentResponse {
  id: string;
  nome: string;
  tipo: string;
  obrigatorio: boolean;
  descricao?: string;
  created_at: string;
  updated_at?: string;
  [key: string]: any;
}

export interface ListTenderDocumentsParams {
  tender_id?: string;
  tipo?: string;
  obrigatorio?: boolean;
}

export interface ListCompanyDocumentsParams {
  cnpj?: string;
  tipo?: string;
  status?: string;
  validade_min?: string;
  validade_max?: string;
}

// ========== DOCUMENTOS DO EDITAL ==========

/**
 * Lista documentos exigidos de um edital
 */
export async function listarDocumentosEdital(
  tenderId: string,
  params?: ListTenderDocumentsParams
): Promise<TenderDocumentResponse[]> {
  const { data } = await api.get<TenderDocumentResponse[]>(
    `/api/v1/bidding/tenders/${tenderId}/documents`,
    { params }
  );
  return data;
}

/**
 * Adiciona documento exigido ao edital
 */
export async function adicionarDocumentoEdital(
  tenderId: string,
  payload: TenderDocumentCreate
): Promise<TenderDocumentResponse> {
  const { data } = await api.post<TenderDocumentResponse>(
    `/api/v1/bidding/tenders/${tenderId}/documents`,
    payload
  );
  return data;
}

/**
 * Atualiza documento do edital
 */
export async function atualizarDocumentoEdital(
  tenderId: string,
  documentId: string,
  payload: TenderDocumentUpdate
): Promise<TenderDocumentResponse> {
  const { data } = await api.put<TenderDocumentResponse>(
    `/api/v1/bidding/tenders/${tenderId}/documents/${documentId}`,
    payload
  );
  return data;
}

/**
 * Remove documento do edital
 */
export async function removerDocumentoEdital(
  tenderId: string,
  documentId: string
): Promise<void> {
  await api.delete(
    `/api/v1/bidding/tenders/${tenderId}/documents/${documentId}`
  );
}

// ========== DOCUMENTOS DA EMPRESA ==========

/**
 * Lista documentos da empresa
 */
export async function listarDocumentosEmpresa(
  params?: ListCompanyDocumentsParams
): Promise<CompanyDocumentResponse[]> {
  const { data } = await api.get<CompanyDocumentResponse[]>(
    '/api/v1/bidding/company-documents/',
    { params }
  );
  return data;
}

/**
 * Busca documento da empresa por ID
 */
export async function buscarDocumentoEmpresaPorId(
  documentId: string
): Promise<CompanyDocumentResponse> {
  const { data } = await api.get<CompanyDocumentResponse>(
    `/api/v1/bidding/company-documents/${documentId}`
  );
  return data;
}

/**
 * Faz upload de documento da empresa
 */
export async function uploadDocumentoEmpresa(
  payload: CompanyDocumentCreate
): Promise<CompanyDocumentResponse> {
  const { data } = await api.post<CompanyDocumentResponse>(
    '/api/v1/bidding/company-documents/',
    payload
  );
  return data;
}

/**
 * Atualiza documento da empresa
 */
export async function atualizarDocumentoEmpresa(
  documentId: string,
  payload: CompanyDocumentUpdate
): Promise<CompanyDocumentResponse> {
  const { data } = await api.put<CompanyDocumentResponse>(
    `/api/v1/bidding/company-documents/${documentId}`,
    payload
  );
  return data;
}

/**
 * Remove documento da empresa
 */
export async function removerDocumentoEmpresa(
  documentId: string
): Promise<void> {
  await api.delete(`/api/v1/bidding/company-documents/${documentId}`);
}

/**
 * Download de documento da empresa (PDF/arquivo)
 */
export async function downloadDocumentoEmpresa(
  documentId: string
): Promise<Blob> {
  const { data } = await api.get<Blob>(
    `/api/v1/bidding/company-documents/${documentId}/download`,
    { responseType: 'blob' }
  );
  return data;
}

/**
 * Lista documentos pendentes de envio
 */
export async function listarDocumentosPendentes(params?: {
  cnpj?: string;
  tender_id?: string;
}): Promise<
  {
    documento_exigido: TenderDocumentResponse;
    documento_empresa?: CompanyDocumentResponse;
    status: 'PENDENTE' | 'ENVIADO' | 'VALIDO' | 'INVALIDO';
  }[]
> {
  const { data } = await api.get<
    {
      documento_exigido: TenderDocumentResponse;
      documento_empresa?: CompanyDocumentResponse;
      status: 'PENDENTE' | 'ENVIADO' | 'VALIDO' | 'INVALIDO';
    }[]
  >('/api/v1/bidding/company-documents/pendentes', { params });
  return data;
}

/**
 * Valida documento (análise automática ou manual)
 */
export async function validarDocumento(
  documentId: string
): Promise<{
  valido: boolean;
  status: string;
  mensagem: string;
  data_validacao: string;
}> {
  const { data } = await api.post<{
    valido: boolean;
    status: string;
    mensagem: string;
    data_validacao: string;
  }>(`/api/v1/bidding/company-documents/${documentId}/validar`);
  return data;
}

const documentsService = {
  listarDocumentosEdital,
  adicionarDocumentoEdital,
  atualizarDocumentoEdital,
  removerDocumentoEdital,
  listarDocumentosEmpresa,
  buscarDocumentoEmpresaPorId,
  uploadDocumentoEmpresa,
  atualizarDocumentoEmpresa,
  removerDocumentoEmpresa,
  downloadDocumentoEmpresa,
  listarDocumentosPendentes,
  validarDocumento,
};

export default documentsService;
