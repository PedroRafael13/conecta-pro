/**
 * Service Layer - Contracts (Contratos Publicos)
 *
 * Cobertura 100% dos endpoints backend:
 * GET  /contracts/                              -> listarContratos
 * GET  /contracts/dashboard                     -> getDashboard
 * GET  /contracts/vigentes                      -> listarContratosVigentes
 * GET  /contracts/vencendo                      -> listarContratosVencendo
 * GET  /contracts/{id}                          -> buscarContratoPorId
 * POST /contracts/                              -> criarContrato
 * PUT  /contracts/{id}                          -> atualizarContrato
 * DEL  /contracts/{id}                          -> removerContrato
 * POST /contracts/{id}/aditivo                  -> aditivar
 * POST /contracts/{id}/reajuste/calcular        -> calcularReajuste
 * POST /contracts/{id}/reajuste/aplicar         -> aplicarReajuste
 * GET  /contracts/{id}/medicoes                 -> listarMedicoes
 * POST /contracts/{id}/medicoes                 -> criarMedicao
 * POST /medicoes/{measurement_id}/aprovar       -> aprovarMedicao
 */

import api from '@/lib/api';
import type {
  PublicContractCreate,
  PublicContractUpdate,
  PublicContractResponse,
} from '@/types/generated/bidding';

const BASE = '/api/v1/bidding/contracts';

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

export interface ContractDashboardResponse {
  total_contratos: number;
  vigentes: number;
  vencidos: number;
  em_execucao: number;
  valor_total: number;
  [key: string]: unknown;
}

export interface AditivarParams {
  contract_id: string;
  tipo_aditivo: 'PRAZO' | 'VALOR' | 'ESCOPO';
  descricao: string;
  novo_valor?: number;
  nova_data_fim?: string;
}

export interface CalcularReajusteParams {
  contract_id: string;
  indice: string;
  data_base?: string;
}

export interface ReajusteResponse {
  valor_original: number;
  valor_reajustado: number;
  percentual: number;
  indice: string;
  [key: string]: unknown;
}

export interface CriarMedicaoParams {
  contract_id: string;
  numero_medicao: number;
  competencia: string;
  tipo?: string;
  periodo_inicio?: string;
  periodo_fim?: string;
  valor_bruto: number;
  retencao_iss?: number;
  retencao_inss?: number;
  retencao_irrf?: number;
  retencao_pis_cofins_csll?: number;
  descricao_servicos?: string;
  observacoes?: string;
  [key: string]: unknown;
}

export interface MedicaoResponse {
  id: string;
  contrato_id: string;
  numero_medicao: number;
  competencia: string;
  valor_bruto: number;
  valor_liquido: number;
  status: string;
  [key: string]: unknown;
}

// GET /contracts/
export async function listarContratos(params?: ListContractsParams): Promise<PublicContractResponse[]> {
  const { data } = await api.get<PublicContractResponse[]>(`${BASE}/`, { params });
  return data;
}

// GET /contracts/dashboard
export async function getDashboard(params?: { periodo_dias?: number }): Promise<ContractDashboardResponse> {
  const { data } = await api.get<ContractDashboardResponse>(`${BASE}/dashboard`, { params });
  return data;
}

// GET /contracts/vigentes
export async function listarContratosVigentes(params?: { page?: number; size?: number }): Promise<PublicContractResponse[]> {
  const { data } = await api.get<PublicContractResponse[]>(`${BASE}/vigentes`, { params });
  return data;
}

// GET /contracts/vencendo
export async function listarContratosVencendo(params?: { dias?: number; page?: number; size?: number }): Promise<PublicContractResponse[]> {
  const { data } = await api.get<PublicContractResponse[]>(`${BASE}/vencendo`, { params });
  return data;
}

// GET /contracts/{id}
export async function buscarContratoPorId(contractId: string): Promise<PublicContractResponse> {
  const { data } = await api.get<PublicContractResponse>(`${BASE}/${contractId}`);
  return data;
}

// POST /contracts/
export async function criarContrato(payload: PublicContractCreate): Promise<PublicContractResponse> {
  const { data } = await api.post<PublicContractResponse>(`${BASE}/`, payload);
  return data;
}

// PUT /contracts/{id}
export async function atualizarContrato(contractId: string, payload: PublicContractUpdate): Promise<PublicContractResponse> {
  const { data } = await api.put<PublicContractResponse>(`${BASE}/${contractId}`, payload);
  return data;
}

// DELETE /contracts/{id}
export async function removerContrato(contractId: string): Promise<void> {
  await api.delete(`${BASE}/${contractId}`);
}

// POST /contracts/{id}/aditivo
export async function aditivar(params: AditivarParams): Promise<PublicContractResponse> {
  const { contract_id, ...payload } = params;
  const { data } = await api.post<PublicContractResponse>(`${BASE}/${contract_id}/aditivo`, payload);
  return data;
}

// POST /contracts/{id}/reajuste/calcular
export async function calcularReajuste(params: CalcularReajusteParams): Promise<ReajusteResponse> {
  const { contract_id, ...payload } = params;
  const { data } = await api.post<ReajusteResponse>(`${BASE}/${contract_id}/reajuste/calcular`, payload);
  return data;
}

// POST /contracts/{id}/reajuste/aplicar
export async function aplicarReajuste(params: CalcularReajusteParams): Promise<PublicContractResponse> {
  const { contract_id, ...payload } = params;
  const { data } = await api.post<PublicContractResponse>(`${BASE}/${contract_id}/reajuste/aplicar`, payload);
  return data;
}

// GET /contracts/{id}/medicoes
export async function listarMedicoes(contractId: string, params?: { status?: string }): Promise<MedicaoResponse[]> {
  const { data } = await api.get<MedicaoResponse[]>(`${BASE}/${contractId}/medicoes`, { params });
  return data;
}

// POST /contracts/{id}/medicoes
export async function criarMedicao(params: CriarMedicaoParams): Promise<MedicaoResponse> {
  const { contract_id, ...payload } = params;
  const { data } = await api.post<MedicaoResponse>(`${BASE}/${contract_id}/medicoes`, payload);
  return data;
}

// POST /medicoes/{measurement_id}/aprovar
export async function aprovarMedicao(measurementId: string, observacoes?: string): Promise<MedicaoResponse> {
  const { data } = await api.post<MedicaoResponse>(`${BASE}/medicoes/${measurementId}/aprovar`, { observacoes });
  return data;
}

const contractsService = {
  listarContratos,
  getDashboard,
  listarContratosVigentes,
  listarContratosVencendo,
  buscarContratoPorId,
  criarContrato,
  atualizarContrato,
  removerContrato,
  aditivar,
  calcularReajuste,
  aplicarReajuste,
  listarMedicoes,
  criarMedicao,
  aprovarMedicao,
};

export default contractsService;
