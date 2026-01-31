/**
 * Service Layer - Contracts (Contratos Públicos)
 *
 * Endpoints: Gestão de contratos públicos, medições, aditivos
 * Controle de vigência, execução financeira
 */

import api from '@/lib/api';
import type {
  PublicContractCreate,
  PublicContractUpdate,
  PublicContractResponse,
} from '@/types/generated/bidding';

export interface ListContractsParams {
  status?: string;
  orgao?: string;
  tipo?: string;
  data_inicio?: string;
  data_fim?: string;
  valor_min?: number;
  valor_max?: number;
  page?: number;
  size?: number;
}

export interface AlterarStatusContratoParams {
  contract_id: string;
  novo_status: string;
  observacoes?: string;
}

export interface AditivarParams {
  contract_id: string;
  tipo_aditivo: 'PRAZO' | 'VALOR' | 'ESCOPO';
  descricao: string;
  novo_valor?: number;
  nova_data_fim?: string;
}

/**
 * Lista contratos com filtros
 */
export async function listarContratos(
  params?: ListContractsParams
): Promise<PublicContractResponse[]> {
  const { data } = await api.get<PublicContractResponse[]>(
    '/api/v1/bidding/contracts/',
    { params }
  );
  return data;
}

/**
 * Busca contrato por ID
 */
export async function buscarContratoPorId(
  contractId: string
): Promise<PublicContractResponse> {
  const { data } = await api.get<PublicContractResponse>(
    `/api/v1/bidding/contracts/${contractId}`
  );
  return data;
}

/**
 * Cria novo contrato
 */
export async function criarContrato(
  payload: PublicContractCreate
): Promise<PublicContractResponse> {
  const { data } = await api.post<PublicContractResponse>(
    '/api/v1/bidding/contracts/',
    payload
  );
  return data;
}

/**
 * Atualiza contrato existente
 */
export async function atualizarContrato(
  contractId: string,
  payload: PublicContractUpdate
): Promise<PublicContractResponse> {
  const { data } = await api.put<PublicContractResponse>(
    `/api/v1/bidding/contracts/${contractId}`,
    payload
  );
  return data;
}

/**
 * Remove contrato (soft delete)
 */
export async function removerContrato(contractId: string): Promise<void> {
  await api.delete(`/api/v1/bidding/contracts/${contractId}`);
}

/**
 * Lista contratos vigentes
 */
export async function listarContratosVigentes(params?: {
  page?: number;
  size?: number;
}): Promise<PublicContractResponse[]> {
  const { data } = await api.get<PublicContractResponse[]>(
    '/api/v1/bidding/contracts/vigentes',
    { params }
  );
  return data;
}

/**
 * Lista contratos vencendo (próximo aos 60 dias)
 */
export async function listarContratosVencendo(params?: {
  dias?: number;
  page?: number;
  size?: number;
}): Promise<PublicContractResponse[]> {
  const { data } = await api.get<PublicContractResponse[]>(
    '/api/v1/bidding/contracts/vencendo',
    { params }
  );
  return data;
}

/**
 * Altera status do contrato
 */
export async function alterarStatus(
  params: AlterarStatusContratoParams
): Promise<PublicContractResponse> {
  const { contract_id, ...payload } = params;
  const { data } = await api.post<PublicContractResponse>(
    `/api/v1/bidding/contracts/${contract_id}/status`,
    payload
  );
  return data;
}

/**
 * Cria aditivo de contrato
 */
export async function aditivar(
  params: AditivarParams
): Promise<PublicContractResponse> {
  const { contract_id, ...payload } = params;
  const { data } = await api.post<PublicContractResponse>(
    `/api/v1/bidding/contracts/${contract_id}/aditivo`,
    payload
  );
  return data;
}

/**
 * Dashboard de contratos
 */
export async function getDashboard(params?: {
  periodo_dias?: number;
}): Promise<{
  total_contratos: number;
  vigentes: number;
  vencidos: number;
  em_execucao: number;
  valor_total: number;
  [key: string]: any;
}> {
  const { data } = await api.get(
    '/api/v1/bidding/contracts/dashboard',
    { params }
  );
  return data;
}

// ========== MEDIÇÕES ==========
// Nota: Tipos Measurement não disponíveis nos schemas gerados
// Descomentar quando os tipos estiverem disponíveis

/*
export async function criarMedicao(
  contractId: string,
  payload: any
): Promise<any> {
  const { data } = await api.post(
    `/api/v1/bidding/contracts/${contractId}/measurements`,
    payload
  );
  return data;
}

export async function atualizarMedicao(
  contractId: string,
  measurementId: string,
  payload: any
): Promise<any> {
  const { data } = await api.put(
    `/api/v1/bidding/contracts/${contractId}/measurements/${measurementId}`,
    payload
  );
  return data;
}

export async function listarMedicoes(
  contractId: string,
  params?: { status?: string }
): Promise<any[]> {
  const { data } = await api.get(
    `/api/v1/bidding/contracts/${contractId}/measurements`,
    { params }
  );
  return data;
}

export async function aprovarMedicao(
  contractId: string,
  measurementId: string,
  observacoes?: string
): Promise<any> {
  const { data } = await api.post(
    `/api/v1/bidding/contracts/${contractId}/measurements/${measurementId}/aprovar`,
    { observacoes }
  );
  return data;
}

export async function rejeitarMedicao(
  contractId: string,
  measurementId: string,
  motivo: string
): Promise<any> {
  const { data } = await api.post(
    `/api/v1/bidding/contracts/${contractId}/measurements/${measurementId}/rejeitar`,
    { motivo }
  );
  return data;
}
*/

const contractsService = {
  listarContratos,
  buscarContratoPorId,
  criarContrato,
  atualizarContrato,
  removerContrato,
  listarContratosVigentes,
  listarContratosVencendo,
  alterarStatus,
  aditivar,
  getDashboard,
  // Medições comentadas até tipos estarem disponíveis
  // criarMedicao,
  // atualizarMedicao,
  // listarMedicoes,
  // aprovarMedicao,
  // rejeitarMedicao,
};

export default contractsService;
