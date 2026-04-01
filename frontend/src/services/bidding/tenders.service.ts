/**
 * Service Layer - Tenders (Editais de Licitacao)
 *
 * Cobertura 100% dos endpoints backend:
 * GET  /tenders/                  -> listarEditais
 * GET  /tenders/dashboard         -> getDashboard
 * GET  /tenders/abertos           -> listarEditaisAbertos
 * GET  /tenders/participando      -> listarEditaisParticipando
 * GET  /tenders/segmento/{s}      -> listarEditaisPorSegmento
 * GET  /tenders/{id}              -> buscarEditalPorId
 * POST /tenders/                  -> criarEdital
 * PUT  /tenders/{id}              -> atualizarEdital
 * DEL  /tenders/{id}              -> removerEdital
 * POST /tenders/{id}/participar   -> marcarParticipacao
 * POST /tenders/{id}/status       -> alterarStatus
 * GET  /tenders/{id}/documentos   -> listarDocumentosEdital
 * POST /tenders/sync-pncp         -> sincronizarPNCP
 * GET  /tenders/pncp/status       -> verificarStatusPNCP
 * GET  /tenders/pncp/buscar       -> buscarPNCP
 */

import api from '@/lib/api';
import type {
  TenderCreate,
  TenderUpdate,
  TenderResponse,
  TenderListResponse,
} from '@/types/generated/bidding';

const BASE = '/api/v1/bidding/tenders';

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

export interface TenderDashboardResponse {
  total_editais: number;
  abertos: number;
  em_andamento: number;
  finalizados: number;
  valor_total: number;
  [key: string]: unknown;
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

export interface PNCPSearchResult {
  total: number;
  items: unknown[];
  [key: string]: unknown;
}

export interface PNCPStatusResponse {
  disponivel: boolean;
  url: string;
  [key: string]: unknown;
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

// GET /tenders/
export async function listarEditais(params?: ListTendersParams): Promise<TenderListResponse> {
  const { data } = await api.get<TenderListResponse>(`${BASE}/`, { params });
  return data;
}

// GET /tenders/dashboard
export async function getDashboard(params?: { uf?: string; periodo_dias?: number }): Promise<TenderDashboardResponse> {
  const { data } = await api.get<TenderDashboardResponse>(`${BASE}/dashboard`, { params });
  return data;
}

// GET /tenders/abertos
export async function listarEditaisAbertos(params?: { uf?: string; segmento?: string; page?: number; size?: number }): Promise<TenderListResponse> {
  const { data } = await api.get<TenderListResponse>(`${BASE}/abertos`, { params });
  return data;
}

// GET /tenders/participando
export async function listarEditaisParticipando(params?: { page?: number; size?: number }): Promise<TenderResponse[]> {
  const { data } = await api.get<TenderResponse[]>(`${BASE}/participando`, { params });
  return data;
}

// GET /tenders/segmento/{segmento}
export async function listarEditaisPorSegmento(segmento: string, params?: { page?: number; size?: number }): Promise<TenderResponse[]> {
  const { data } = await api.get<TenderResponse[]>(`${BASE}/segmento/${segmento}`, { params });
  return data;
}

// GET /tenders/{id}
export async function buscarEditalPorId(tenderId: string): Promise<TenderResponse> {
  const { data } = await api.get<TenderResponse>(`${BASE}/${tenderId}`);
  return data;
}

// POST /tenders/
export async function criarEdital(payload: TenderCreate): Promise<TenderResponse> {
  const { data } = await api.post<TenderResponse>(`${BASE}/`, payload);
  return data;
}

// PUT /tenders/{id}
export async function atualizarEdital(tenderId: string, payload: TenderUpdate): Promise<TenderResponse> {
  const { data } = await api.put<TenderResponse>(`${BASE}/${tenderId}`, payload);
  return data;
}

// DELETE /tenders/{id}
export async function removerEdital(tenderId: string): Promise<void> {
  await api.delete(`${BASE}/${tenderId}`);
}

// POST /tenders/{id}/participar
export async function marcarParticipacao(params: MarcarParticipacaoParams): Promise<TenderResponse> {
  const { tender_id, ...payload } = params;
  const { data } = await api.post<TenderResponse>(`${BASE}/${tender_id}/participar`, payload);
  return data;
}

// POST /tenders/{id}/status
export async function alterarStatus(params: AlterarStatusParams): Promise<TenderResponse> {
  const { tender_id, ...payload } = params;
  const { data } = await api.post<TenderResponse>(`${BASE}/${tender_id}/status`, payload);
  return data;
}

// GET /tenders/{id}/documentos
export async function listarDocumentosEdital(tenderId: string): Promise<unknown[]> {
  const { data } = await api.get<unknown[]>(`${BASE}/${tenderId}/documentos`);
  return data;
}

// POST /tenders/sync-pncp
export async function sincronizarPNCP(params?: { uf?: string; dias_retroativos?: number }): Promise<{ message: string; total_sincronizado: number }> {
  const { data } = await api.post<{ message: string; total_sincronizado: number }>(`${BASE}/sync-pncp`, params);
  return data;
}

// GET /tenders/pncp/status
export async function verificarStatusPNCP(): Promise<PNCPStatusResponse> {
  const { data } = await api.get<PNCPStatusResponse>(`${BASE}/pncp/status`);
  return data;
}

// GET /tenders/pncp/buscar
export async function buscarPNCP(params: PNCPBuscarParams): Promise<PNCPSearchResult> {
  const { data } = await api.get<PNCPSearchResult>(`${BASE}/pncp/buscar`, { params });
  return data;
}

const tendersService = {
  listarEditais,
  getDashboard,
  listarEditaisAbertos,
  listarEditaisParticipando,
  listarEditaisPorSegmento,
  buscarEditalPorId,
  criarEdital,
  atualizarEdital,
  removerEdital,
  marcarParticipacao,
  alterarStatus,
  listarDocumentosEdital,
  sincronizarPNCP,
  verificarStatusPNCP,
  buscarPNCP,
};

export default tendersService;
