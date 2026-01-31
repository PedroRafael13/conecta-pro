/**
 * Service Layer - Tenders (Editais de Licitação)
 *
 * Endpoints: Lista, busca, criação, participação em editais
 * Integração com PNCP (Portal Nacional de Contratações Públicas)
 * Lei 14.133/2021
 */

import api from '@/lib/api';
import type {
  TenderCreate,
  TenderUpdate,
  TenderResponse,
  TenderListResponse,
} from '@/types/generated/bidding';

// Tipos adicionais não disponíveis nos schemas gerados
interface TenderSearchParams {
  termo?: string;
  uf?: string;
  municipio?: string;
  modalidade?: string;
  segmento?: string;
  [key: string]: any;
}

interface TenderDashboardResponse {
  total_editais: number;
  abertos: number;
  em_andamento: number;
  finalizados: number;
  valor_total: number;
  [key: string]: any;
}

interface PNCPSearchResult {
  total: number;
  items: any[];
  [key: string]: any;
}

export interface ListTendersParams {
  uf?: string;
  municipio?: string;
  modalidade?: string;
  segmento?: string;
  status?: string;
  participando?: boolean;
  interesse?: boolean;
  valor_min?: number;
  valor_max?: number;
  termo_busca?: string;
  page?: number;
  size?: number;
}

export interface PNCPBuscarParams {
  uf?: string;
  municipio?: string;
  modalidade?: string;
  segmento?: string;
  data_inicio?: string;
  data_fim?: string;
  valor_min?: number;
  valor_max?: number;
}

export interface MarcarParticipacaoParams {
  tender_id: string;
  participando: boolean;
  interesse?: boolean;
  observacoes?: string;
}

export interface AlterarStatusParams {
  tender_id: string;
  novo_status: string;
  observacoes?: string;
}

/**
 * Lista editais com filtros e paginação
 */
export async function listarEditais(
  params?: ListTendersParams
): Promise<TenderListResponse> {
  const { data } = await api.get<TenderListResponse>(
    '/api/v1/bidding/tenders/',
    { params }
  );
  return data;
}

/**
 * Busca edital por ID
 */
export async function buscarEditalPorId(
  tenderId: string
): Promise<TenderResponse> {
  const { data } = await api.get<TenderResponse>(
    `/api/v1/bidding/tenders/${tenderId}`
  );
  return data;
}

/**
 * Cria novo edital
 */
export async function criarEdital(
  payload: TenderCreate
): Promise<TenderResponse> {
  const { data } = await api.post<TenderResponse>(
    '/api/v1/bidding/tenders/',
    payload
  );
  return data;
}

/**
 * Atualiza edital existente
 */
export async function atualizarEdital(
  tenderId: string,
  payload: TenderUpdate
): Promise<TenderResponse> {
  const { data } = await api.put<TenderResponse>(
    `/api/v1/bidding/tenders/${tenderId}`,
    payload
  );
  return data;
}

/**
 * Remove edital (soft delete)
 */
export async function removerEdital(tenderId: string): Promise<void> {
  await api.delete(`/api/v1/bidding/tenders/${tenderId}`);
}

/**
 * Lista editais abertos (em andamento)
 */
export async function listarEditaisAbertos(params?: {
  uf?: string;
  segmento?: string;
  page?: number;
  size?: number;
}): Promise<TenderListResponse> {
  const { data } = await api.get<TenderListResponse>(
    '/api/v1/bidding/tenders/abertos',
    { params }
  );
  return data;
}

/**
 * Lista editais por segmento
 */
export async function listarEditaisPorSegmento(
  segmento: string,
  params?: { page?: number; size?: number }
): Promise<TenderListResponse> {
  const { data } = await api.get<TenderListResponse>(
    `/api/v1/bidding/tenders/segmento/${segmento}`,
    { params }
  );
  return data;
}

/**
 * Marca participação da empresa em um edital
 */
export async function marcarParticipacao(
  params: MarcarParticipacaoParams
): Promise<TenderResponse> {
  const { tender_id, ...payload } = params;
  const { data } = await api.post<TenderResponse>(
    `/api/v1/bidding/tenders/${tender_id}/participar`,
    payload
  );
  return data;
}

/**
 * Altera status de um edital
 */
export async function alterarStatus(
  params: AlterarStatusParams
): Promise<TenderResponse> {
  const { tender_id, ...payload } = params;
  const { data } = await api.post<TenderResponse>(
    `/api/v1/bidding/tenders/${tender_id}/status`,
    payload
  );
  return data;
}

/**
 * Busca editais no PNCP (Portal Nacional)
 */
export async function buscarPNCP(
  params: PNCPBuscarParams
): Promise<PNCPSearchResult> {
  const { data } = await api.get<PNCPSearchResult>(
    '/api/v1/bidding/tenders/pncp/buscar',
    { params }
  );
  return data;
}

/**
 * Sincroniza editais com o PNCP
 */
export async function sincronizarPNCP(params?: {
  uf?: string;
  dias_retroativos?: number;
}): Promise<{ message: string; total_sincronizado: number }> {
  const { data } = await api.post<{
    message: string;
    total_sincronizado: number;
  }>('/api/v1/bidding/tenders/sync-pncp', params);
  return data;
}

/**
 * Dashboard de editais
 */
export async function getDashboard(params?: {
  uf?: string;
  periodo_dias?: number;
}): Promise<TenderDashboardResponse> {
  const { data } = await api.get<TenderDashboardResponse>(
    '/api/v1/bidding/tenders/dashboard',
    { params }
  );
  return data;
}

const tendersService = {
  listarEditais,
  buscarEditalPorId,
  criarEdital,
  atualizarEdital,
  removerEdital,
  listarEditaisAbertos,
  listarEditaisPorSegmento,
  marcarParticipacao,
  alterarStatus,
  buscarPNCP,
  sincronizarPNCP,
  getDashboard,
};

export default tendersService;
