/**
 * Service Layer - Proposals (Propostas de Licitacao)
 *
 * Cobertura 100% dos endpoints backend:
 * GET  /proposals/                     -> listarPropostas
 * GET  /proposals/estatisticas         -> getEstatisticas
 * GET  /proposals/vencedoras           -> listarVencedoras
 * GET  /proposals/tender/{tender_id}   -> listarPropostasPorEdital
 * GET  /proposals/{id}                 -> buscarPropostaPorId
 * POST /proposals/                     -> criarProposta
 * PUT  /proposals/{id}                 -> atualizarProposta
 * DEL  /proposals/{id}                 -> removerProposta
 * POST /proposals/{id}/pronta          -> marcarPronta
 * POST /proposals/{id}/enviar          -> enviarProposta
 * POST /proposals/{id}/resultado       -> registrarResultado
 * POST /proposals/{id}/lance           -> registrarLance
 * POST /proposals/calcular-bdi         -> calcularBDI
 */

import api from '@/lib/api';

const BASE = '/api/v1/bidding/proposals';

export interface BiddingProposalCreate {
  tender_id: string;
  numero?: string;
  valor_total?: number;
  valor_unitario?: number;
  desconto_percentual?: number;
  bdi_percentual?: number;
  bdi_detalhamento?: Record<string, unknown>;
  encargos_sociais?: number;
  encargos_detalhamento?: Record<string, unknown>;
  observacoes?: string;
  justificativa_preco?: string;
  [key: string]: unknown;
}

export interface BiddingProposalUpdate {
  valor_total?: number;
  valor_unitario?: number;
  desconto_percentual?: number;
  bdi_percentual?: number;
  bdi_detalhamento?: Record<string, unknown>;
  encargos_sociais?: number;
  observacoes?: string;
  justificativa_preco?: string;
  [key: string]: unknown;
}

export interface BiddingProposalResponse {
  id: string;
  tender_id: string;
  numero: string;
  versao: number;
  valor_total: number;
  status: string;
  created_at: string;
  updated_at?: string;
  [key: string]: unknown;
}

export interface BiddingProposalListResponse {
  items: BiddingProposalResponse[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface EstatisticasResponse {
  total: number;
  por_status: Record<string, number>;
  taxa_sucesso: number;
  valor_medio: number;
  [key: string]: unknown;
}

export interface ListProposalsParams {
  tender_id?: string;
  status?: string;
  data_inicio?: string;
  data_fim?: string;
  valor_min?: number;
  valor_max?: number;
  page?: number;
  size?: number;
}

export interface RegistrarResultadoParams {
  proposal_id: string;
  venceu: boolean;
  posicao_classificacao?: number;
  valor_lance_final?: number;
  observacoes?: string;
}

export interface RegistrarLanceParams {
  proposal_id: string;
  valor: number;
  observacoes?: string;
}

export interface CalcularBDIParams {
  administracao_central: number;
  seguro_garantia: number;
  risco: number;
  despesas_financeiras: number;
  lucro: number;
  tributos: number;
}

export interface BDIResponse {
  bdi_percentual: number;
  formula: string;
  detalhamento: Record<string, number>;
}

// GET /proposals/
export async function listarPropostas(params?: ListProposalsParams): Promise<BiddingProposalListResponse> {
  const { data } = await api.get<BiddingProposalListResponse>(`${BASE}/`, { params });
  return data;
}

// GET /proposals/estatisticas
export async function getEstatisticas(): Promise<EstatisticasResponse> {
  const { data } = await api.get<EstatisticasResponse>(`${BASE}/estatisticas`);
  return data;
}

// GET /proposals/vencedoras
export async function listarVencedoras(params?: { page?: number; size?: number }): Promise<BiddingProposalResponse[]> {
  const { data } = await api.get<BiddingProposalResponse[]>(`${BASE}/vencedoras`, { params });
  return data;
}

// GET /proposals/tender/{tender_id}
export async function listarPropostasPorEdital(tenderId: string, params?: { page?: number; size?: number }): Promise<BiddingProposalListResponse> {
  const { data } = await api.get<BiddingProposalListResponse>(`${BASE}/tender/${tenderId}`, { params });
  return data;
}

// GET /proposals/{id}
export async function buscarPropostaPorId(proposalId: string): Promise<BiddingProposalResponse> {
  const { data } = await api.get<BiddingProposalResponse>(`${BASE}/${proposalId}`);
  return data;
}

// POST /proposals/
export async function criarProposta(payload: BiddingProposalCreate): Promise<BiddingProposalResponse> {
  const { data } = await api.post<BiddingProposalResponse>(`${BASE}/`, payload);
  return data;
}

// PUT /proposals/{id}
export async function atualizarProposta(proposalId: string, payload: BiddingProposalUpdate): Promise<BiddingProposalResponse> {
  const { data } = await api.put<BiddingProposalResponse>(`${BASE}/${proposalId}`, payload);
  return data;
}

// DELETE /proposals/{id}
export async function removerProposta(proposalId: string): Promise<void> {
  await api.delete(`${BASE}/${proposalId}`);
}

// POST /proposals/{id}/pronta
export async function marcarPronta(proposalId: string, observacoes?: string): Promise<BiddingProposalResponse> {
  const { data } = await api.post<BiddingProposalResponse>(`${BASE}/${proposalId}/pronta`, { observacoes });
  return data;
}

// POST /proposals/{id}/enviar
export async function enviarProposta(proposalId: string, observacoes?: string): Promise<BiddingProposalResponse> {
  const { data } = await api.post<BiddingProposalResponse>(`${BASE}/${proposalId}/enviar`, { observacoes });
  return data;
}

// POST /proposals/{id}/resultado
export async function registrarResultado(params: RegistrarResultadoParams): Promise<BiddingProposalResponse> {
  const { proposal_id, ...payload } = params;
  const { data } = await api.post<BiddingProposalResponse>(`${BASE}/${proposal_id}/resultado`, payload);
  return data;
}

// POST /proposals/{id}/lance
export async function registrarLance(params: RegistrarLanceParams): Promise<BiddingProposalResponse> {
  const { proposal_id, ...payload } = params;
  const { data } = await api.post<BiddingProposalResponse>(`${BASE}/${proposal_id}/lance`, payload);
  return data;
}

// POST /proposals/calcular-bdi
export async function calcularBDI(params: CalcularBDIParams): Promise<BDIResponse> {
  const { data } = await api.post<BDIResponse>(`${BASE}/calcular-bdi`, params);
  return data;
}

const proposalsService = {
  listarPropostas,
  getEstatisticas,
  listarVencedoras,
  listarPropostasPorEdital,
  buscarPropostaPorId,
  criarProposta,
  atualizarProposta,
  removerProposta,
  marcarPronta,
  enviarProposta,
  registrarResultado,
  registrarLance,
  calcularBDI,
};

export default proposalsService;
