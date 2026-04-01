/**
 * Service Layer - Documents (Documentos de Licitacao)
 *
 * Cobertura 100% dos endpoints backend:
 * GET  /documents/                -> listarDocumentos
 * GET  /documents/expiring        -> listarVencendo
 * GET  /documents/status          -> getStatusGeral
 * GET  /documents/habilitacao     -> verificarHabilitacao
 * GET  /documents/tipos           -> listarTipos
 * GET  /documents/tipo/{tipo}     -> buscarPorTipo
 * GET  /documents/{id}            -> buscarDocumentoPorId
 * POST /documents/                -> criarDocumento
 * PUT  /documents/{id}            -> atualizarDocumento
 * DEL  /documents/{id}            -> removerDocumento
 * POST /documents/atualizar-status -> atualizarStatusEmLote
 */

import api from '@/lib/api';
import type {
  CompanyDocumentCreate,
  CompanyDocumentUpdate,
  CompanyDocumentResponse,
} from '@/types/generated/bidding';

const BASE = '/api/v1/bidding/documents';

export interface ListDocumentsParams {
  tipo?: string;
  status?: string;
  page?: number;
  size?: number;
}

export interface DocumentExpiringResponse {
  total: number;
  vencendo_7d: number;
  vencendo_15d: number;
  vencendo_30d: number;
  documentos: CompanyDocumentResponse[];
  [key: string]: unknown;
}

export interface StatusGeralResponse {
  total: number;
  validos: number;
  vencidos: number;
  vencendo: number;
  por_tipo: Record<string, number>;
  [key: string]: unknown;
}

export interface HabilitacaoResponse {
  habilitado: boolean;
  documentos_presentes: string[];
  documentos_faltantes: string[];
  documentos_vencidos: string[];
  [key: string]: unknown;
}

export interface DocumentTypeInfo {
  codigo: string;
  nome: string;
  descricao: string;
  obrigatorio: boolean;
}

// GET /documents/
export async function listarDocumentos(params?: ListDocumentsParams): Promise<CompanyDocumentResponse[]> {
  const { data } = await api.get<CompanyDocumentResponse[]>(`${BASE}/`, { params });
  return data;
}

// GET /documents/expiring
export async function listarVencendo(params?: { dias?: number }): Promise<DocumentExpiringResponse> {
  const { data } = await api.get<DocumentExpiringResponse>(`${BASE}/expiring`, { params });
  return data;
}

// GET /documents/status
export async function getStatusGeral(): Promise<StatusGeralResponse> {
  const { data } = await api.get<StatusGeralResponse>(`${BASE}/status`);
  return data;
}

// GET /documents/habilitacao
export async function verificarHabilitacao(): Promise<HabilitacaoResponse> {
  const { data } = await api.get<HabilitacaoResponse>(`${BASE}/habilitacao`);
  return data;
}

// GET /documents/tipos
export async function listarTipos(): Promise<DocumentTypeInfo[]> {
  const { data } = await api.get<DocumentTypeInfo[]>(`${BASE}/tipos`);
  return data;
}

// GET /documents/tipo/{tipo}
export async function buscarPorTipo(tipo: string): Promise<CompanyDocumentResponse> {
  const { data } = await api.get<CompanyDocumentResponse>(`${BASE}/tipo/${tipo}`);
  return data;
}

// GET /documents/{id}
export async function buscarDocumentoPorId(documentId: string): Promise<CompanyDocumentResponse> {
  const { data } = await api.get<CompanyDocumentResponse>(`${BASE}/${documentId}`);
  return data;
}

// POST /documents/
export async function criarDocumento(payload: CompanyDocumentCreate): Promise<CompanyDocumentResponse> {
  const { data } = await api.post<CompanyDocumentResponse>(`${BASE}/`, payload);
  return data;
}

// PUT /documents/{id}
export async function atualizarDocumento(documentId: string, payload: CompanyDocumentUpdate): Promise<CompanyDocumentResponse> {
  const { data } = await api.put<CompanyDocumentResponse>(`${BASE}/${documentId}`, payload);
  return data;
}

// DELETE /documents/{id}
export async function removerDocumento(documentId: string): Promise<void> {
  await api.delete(`${BASE}/${documentId}`);
}

// POST /documents/atualizar-status
export async function atualizarStatusEmLote(): Promise<{ total_atualizado: number; detalhes: unknown[] }> {
  const { data } = await api.post<{ total_atualizado: number; detalhes: unknown[] }>(`${BASE}/atualizar-status`);
  return data;
}

const documentsService = {
  listarDocumentos,
  listarVencendo,
  getStatusGeral,
  verificarHabilitacao,
  listarTipos,
  buscarPorTipo,
  buscarDocumentoPorId,
  criarDocumento,
  atualizarDocumento,
  removerDocumento,
  atualizarStatusEmLote,
};

export default documentsService;
