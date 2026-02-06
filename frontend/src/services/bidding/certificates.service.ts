/**
 * Service Layer - Certificates (Certidões)
 *
 * Endpoints: Gestão de certidões negativas (federal, estadual, municipal, trabalhista)
 * Controle de validade, renovação automática, alertas
 */

import api from '@/lib/api';
import type {
  CertificateCreate,
  CertificateUpdate,
  CertificateResponse,
  CertificateListResponse,
  CertificateBulkStatusResponse,
  CertificateRenewResponse,
} from '@/types/generated/bidding';

export interface ListCertificatesParams {
  cnpj?: string;
  tipo?: string;
  status?: string;
  validade_min?: string;
  validade_max?: string;
  vencendo_em_dias?: number;
  page?: number;
  size?: number;
}

export interface RenovarCertidoesParams {
  cnpj: string;
  tipos?: string[];
  auto_download?: boolean;
}

export interface AtualizarStatusParams {
  cnpjs: string[];
  tipos?: string[];
}

/**
 * Lista certidões com filtros
 */
export async function listarCertidoes(
  params?: ListCertificatesParams
): Promise<CertificateListResponse> {
  const { data } = await api.get<CertificateListResponse>(
    '/api/v1/bidding/certificates/',
    { params }
  );
  return data;
}

/**
 * Busca certidão por ID
 */
export async function buscarCertidaoPorId(
  certificateId: string
): Promise<CertificateResponse> {
  const { data } = await api.get<CertificateResponse>(
    `/api/v1/bidding/certificates/${certificateId}`
  );
  return data;
}

/**
 * Cria nova certidão (upload manual)
 */
export async function criarCertidao(
  payload: CertificateCreate
): Promise<CertificateResponse> {
  const { data } = await api.post<CertificateResponse>(
    '/api/v1/bidding/certificates/',
    payload
  );
  return data;
}

/**
 * Atualiza certidão existente
 */
export async function atualizarCertidao(
  certificateId: string,
  payload: CertificateUpdate
): Promise<CertificateResponse> {
  const { data } = await api.put<CertificateResponse>(
    `/api/v1/bidding/certificates/${certificateId}`,
    payload
  );
  return data;
}

/**
 * Remove certidão (soft delete)
 */
export async function removerCertidao(certificateId: string): Promise<void> {
  await api.delete(`/api/v1/bidding/certificates/${certificateId}`);
}

/**
 * Busca certidão específica por CNPJ e tipo
 */
export async function buscarCertidaoPorCNPJeTipo(
  cnpj: string,
  tipo: string
): Promise<CertificateResponse> {
  const { data } = await api.get<CertificateResponse>(
    `/api/v1/bidding/certificates/cnpj/${cnpj}/tipo/${tipo}`
  );
  return data;
}

/**
 * Verifica status de todas as certidões de um CNPJ
 */
export async function verificarStatusPorCNPJ(
  cnpj: string
): Promise<CertificateBulkStatusResponse> {
  const { data } = await api.get<CertificateBulkStatusResponse>(
    `/api/v1/bidding/certificates/status/${cnpj}`
  );
  return data;
}

/**
 * Lista tipos de certidões disponíveis
 */
export async function listarTipos(): Promise<
  { codigo: string; nome: string; descricao: string; orgao: string }[]
> {
  const { data } = await api.get<
    { codigo: string; nome: string; descricao: string; orgao: string }[]
  >('/api/v1/bidding/certificates/tipos');
  return data;
}

/**
 * Lista certidões pendentes de renovação
 */
export async function listarPendentesRenovacao(params?: {
  dias?: number;
  page?: number;
  size?: number;
}): Promise<CertificateResponse[]> {
  const { data } = await api.get<CertificateResponse[]>(
    '/api/v1/bidding/certificates/pendentes-renovacao',
    { params }
  );
  return data;
}

/**
 * Renova certidões automaticamente (via robôs)
 */
export async function renovarCertidoes(
  params: RenovarCertidoesParams
): Promise<CertificateRenewResponse> {
  const { data } = await api.post<CertificateRenewResponse>(
    '/api/v1/bidding/certificates/renovar',
    params
  );
  return data;
}

/**
 * Atualiza status de certidões em lote
 */
export async function atualizarStatusEmLote(
  params: AtualizarStatusParams
): Promise<{
  total_processado: number;
  atualizados: number;
  erros: number;
  detalhes: { cnpj: string; tipo: string; status: string; erro?: string }[];
}> {
  const { data } = await api.post<{
    total_processado: number;
    atualizados: number;
    erros: number;
    detalhes: { cnpj: string; tipo: string; status: string; erro?: string }[];
  }>('/api/v1/bidding/certificates/atualizar-status', params);
  return data;
}

/**
 * Download de certidão (PDF)
 */
export async function downloadCertidao(
  certificateId: string
): Promise<Blob> {
  const { data } = await api.get<Blob>(
    `/api/v1/bidding/certificates/${certificateId}/download`,
    { responseType: 'blob' }
  );
  return data;
}

/**
 * Valida certidão no órgão emissor
 */
export async function validarCertidao(
  certificateId: string
): Promise<{
  valida: boolean;
  status: string;
  mensagem: string;
  data_validacao: string;
}> {
  const { data } = await api.post<{
    valida: boolean;
    status: string;
    mensagem: string;
    data_validacao: string;
  }>(`/api/v1/bidding/certificates/${certificateId}/validar`);
  return data;
}

const certificatesService = {
  listarCertidoes,
  buscarCertidaoPorId,
  criarCertidao,
  atualizarCertidao,
  removerCertidao,
  buscarCertidaoPorCNPJeTipo,
  verificarStatusPorCNPJ,
  listarTipos,
  listarPendentesRenovacao,
  renovarCertidoes,
  atualizarStatusEmLote,
  downloadCertidao,
  validarCertidao,
};

export default certificatesService;
