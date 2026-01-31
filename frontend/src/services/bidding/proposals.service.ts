/**
 * Service Layer - Proposals (Propostas de Licitação)
 *
 * Endpoints: Criação, submissão, gestão de propostas comerciais
 * Vinculação com editais, itens, valores, prazos
 */

import api from '@/lib/api';

// Tipos para propostas de licitação (não disponíveis nos schemas gerados)
export interface BiddingProposalCreate {
  tender_id: string;
  cnpj: string;
  razao_social: string;
  valor_global: number | string;
  prazo_entrega?: number;
  proposta_tecnica?: string;
  [key: string]: any;
}

export interface BiddingProposalUpdate {
  valor_global?: number | string;
  prazo_entrega?: number;
  proposta_tecnica?: string;
  status?: string;
  [key: string]: any;
}

export interface BiddingProposalResponse {
  id: string;
  tender_id: string;
  cnpj: string;
  razao_social: string;
  valor_global: number;
  status: string;
  created_at: string;
  updated_at?: string;
  [key: string]: any;
}

export interface BiddingProposalListResponse {
  items: BiddingProposalResponse[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface ProposalItemCreate {
  item_edital_id?: string;
  descricao: string;
  quantidade: number;
  valor_unitario: number;
  [key: string]: any;
}

export interface ProposalItemUpdate {
  descricao?: string;
  quantidade?: number;
  valor_unitario?: number;
  [key: string]: any;
}

export interface ProposalItemResponse {
  id: string;
  proposta_id: string;
  descricao: string;
  quantidade: number;
  valor_unitario: number;
  valor_total: number;
  created_at: string;
  [key: string]: any;
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

export interface SubmeterPropostaParams {
  proposal_id: string;
  observacoes?: string;
}

export interface AlterarStatusPropostaParams {
  proposal_id: string;
  novo_status: string;
  observacoes?: string;
}

/**
 * Lista propostas com filtros
 */
export async function listarPropostas(
  params?: ListProposalsParams
): Promise<BiddingProposalListResponse> {
  const { data } = await api.get<BiddingProposalListResponse>(
    '/api/v1/bidding/proposals/',
    { params }
  );
  return data;
}

/**
 * Busca proposta por ID
 */
export async function buscarPropostaPorId(
  proposalId: string
): Promise<BiddingProposalResponse> {
  const { data } = await api.get<BiddingProposalResponse>(
    `/api/v1/bidding/proposals/${proposalId}`
  );
  return data;
}

/**
 * Cria nova proposta
 */
export async function criarProposta(
  payload: BiddingProposalCreate
): Promise<BiddingProposalResponse> {
  const { data } = await api.post<BiddingProposalResponse>(
    '/api/v1/bidding/proposals/',
    payload
  );
  return data;
}

/**
 * Atualiza proposta existente
 */
export async function atualizarProposta(
  proposalId: string,
  payload: BiddingProposalUpdate
): Promise<BiddingProposalResponse> {
  const { data } = await api.put<BiddingProposalResponse>(
    `/api/v1/bidding/proposals/${proposalId}`,
    payload
  );
  return data;
}

/**
 * Remove proposta (soft delete)
 */
export async function removerProposta(proposalId: string): Promise<void> {
  await api.delete(`/api/v1/bidding/proposals/${proposalId}`);
}

/**
 * Lista propostas de um edital específico
 */
export async function listarPropostasPorEdital(
  tenderId: string,
  params?: { page?: number; size?: number }
): Promise<BiddingProposalListResponse> {
  const { data } = await api.get<BiddingProposalListResponse>(
    `/api/v1/bidding/proposals/tender/${tenderId}`,
    { params }
  );
  return data;
}

/**
 * Submete proposta para análise/aprovação
 */
export async function submeterProposta(
  params: SubmeterPropostaParams
): Promise<BiddingProposalResponse> {
  const { proposal_id, ...payload } = params;
  const { data } = await api.post<BiddingProposalResponse>(
    `/api/v1/bidding/proposals/${proposal_id}/submeter`,
    payload
  );
  return data;
}

/**
 * Altera status da proposta
 */
export async function alterarStatusProposta(
  params: AlterarStatusPropostaParams
): Promise<BiddingProposalResponse> {
  const { proposal_id, ...payload } = params;
  const { data } = await api.post<BiddingProposalResponse>(
    `/api/v1/bidding/proposals/${proposal_id}/status`,
    payload
  );
  return data;
}

/**
 * Lista propostas em andamento
 */
export async function listarPropostasEmAndamento(params?: {
  page?: number;
  size?: number;
}): Promise<BiddingProposalListResponse> {
  const { data } = await api.get<BiddingProposalListResponse>(
    '/api/v1/bidding/proposals/em-andamento',
    { params }
  );
  return data;
}

/**
 * Lista propostas aprovadas
 */
export async function listarPropostasAprovadas(params?: {
  page?: number;
  size?: number;
}): Promise<BiddingProposalListResponse> {
  const { data } = await api.get<BiddingProposalListResponse>(
    '/api/v1/bidding/proposals/aprovadas',
    { params }
  );
  return data;
}

/**
 * Dashboard de propostas
 */
export async function getDashboard(params?: {
  periodo_dias?: number;
}): Promise<{
  total_propostas: number;
  em_andamento: number;
  aprovadas: number;
  rejeitadas: number;
  valor_total: number;
  taxa_aprovacao: number;
}> {
  const { data } = await api.get('/api/v1/bidding/proposals/dashboard', {
    params,
  });
  return data;
}

// ========== ITENS DE PROPOSTA ==========

/**
 * Adiciona item à proposta
 */
export async function adicionarItem(
  proposalId: string,
  payload: ProposalItemCreate
): Promise<ProposalItemResponse> {
  const { data } = await api.post<ProposalItemResponse>(
    `/api/v1/bidding/proposals/${proposalId}/items`,
    payload
  );
  return data;
}

/**
 * Atualiza item da proposta
 */
export async function atualizarItem(
  proposalId: string,
  itemId: string,
  payload: ProposalItemUpdate
): Promise<ProposalItemResponse> {
  const { data } = await api.put<ProposalItemResponse>(
    `/api/v1/bidding/proposals/${proposalId}/items/${itemId}`,
    payload
  );
  return data;
}

/**
 * Remove item da proposta
 */
export async function removerItem(
  proposalId: string,
  itemId: string
): Promise<void> {
  await api.delete(
    `/api/v1/bidding/proposals/${proposalId}/items/${itemId}`
  );
}

/**
 * Lista itens de uma proposta
 */
export async function listarItens(
  proposalId: string
): Promise<ProposalItemResponse[]> {
  const { data } = await api.get<ProposalItemResponse[]>(
    `/api/v1/bidding/proposals/${proposalId}/items`
  );
  return data;
}

const proposalsService = {
  listarPropostas,
  buscarPropostaPorId,
  criarProposta,
  atualizarProposta,
  removerProposta,
  listarPropostasPorEdital,
  submeterProposta,
  alterarStatusProposta,
  listarPropostasEmAndamento,
  listarPropostasAprovadas,
  getDashboard,
  adicionarItem,
  atualizarItem,
  removerItem,
  listarItens,
};

export default proposalsService;
