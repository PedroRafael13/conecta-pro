/**
 * Service Layer - SST (Saude e Seguranca do Trabalho)
 * Afastamentos, CAT, Estabilidade, Ajuda Medicamento
 *
 * @module services/sst
 * @author Conecta PRO Team
 * @date 2026-03-16
 */

import api from '@/lib/api';

// =============================================================================
// TIPOS - AFASTAMENTOS
// =============================================================================

export interface Afastamento {
  id: string;
  employee_id: string;
  employee_nome: string;
  employee_cargo: string;
  tipo: string;
  motivo: string | null;
  data_inicio: string;
  data_fim_prevista: string | null;
  data_retorno: string | null;
  dias_previstos: number | null;
  atestado: boolean;
  cid: string | null;
  status: string;
  ajuda_medicamento_ativa: boolean;
  ajuda_medicamento_valor: number | null;
  gera_estabilidade: boolean;
  estabilidade_ate: string | null;
}

export interface AfastamentoList {
  total: number;
  afastamentos: Afastamento[];
}

export interface AfastamentoCreate {
  employee_id: string;
  tipo: string;
  motivo?: string;
  data_inicio: string;
  data_fim_prevista?: string;
  dias_previstos?: number;
  atestado?: boolean;
  cid?: string;
}

// =============================================================================
// TIPOS - DASHBOARD
// =============================================================================

export interface SSTDashboard {
  total_colaboradores: number;
  afastados_ativos: number;
  taxa_afastamento: string;
  risco_nr1: string;
  asos_vencendo_30d: number;
  cats_abertas: number;
  colaboradores_estabilidade: number;
  pcmso_vigente: boolean;
  ppra_vigente: boolean;
  ajuda_medicamento_ativa: number;
  custo_afastamentos_mes: number;
}

// =============================================================================
// TIPOS - CAT
// =============================================================================

export interface CATItem {
  cat_id: string;
  employee_id: string;
  tipo: string;
  data: string;
  local: string;
  gravidade: string;
  status: string;
}

export interface CATList {
  total: number;
  cats: CATItem[];
}

export interface CATCreate {
  employee_id: string;
  tipo_acidente: string;
  data_acidente: string;
  local: string;
  descricao: string;
  gravidade: string;
  testemunhas?: string[];
}

export interface TaxaAcidente {
  total_colaboradores: number;
  total_cats: number;
  taxa_acidente_percentual: number;
}

// =============================================================================
// TIPOS - ESTABILIDADE
// =============================================================================

export interface EstabilidadeItem {
  employee_id: string;
  nome: string;
  cargo: string;
  tipo_afastamento: string;
  data_retorno: string | null;
  estabilidade_ate: string;
  dias_restantes: number;
  clausula_cct: string;
}

export interface EstabilidadeList {
  total: number;
  colaboradores: EstabilidadeItem[];
}

// =============================================================================
// TIPOS - AJUDA MEDICAMENTO
// =============================================================================

export interface AjudaMedicamentoItem {
  employee_id: string;
  nome: string;
  cargo: string;
  data_inicio_afastamento: string;
  valor_mensal: number;
  clausula_cct: string;
}

export interface AjudaMedicamentoList {
  total: number;
  valor_unitario: number;
  custo_mensal_total: number;
  colaboradores: AjudaMedicamentoItem[];
}

// =============================================================================
// TIPOS - LTCAT
// =============================================================================

export interface LTCATFatorRisco {
  agente: string;
  tipo: string;
  nr_referencia: string;
}

export interface LTCATStatus {
  documento: string;
  base_legal: string;
  empresa: string;
  cnpj: string;
  vigencia: string;
  responsavel_tecnico: string;
  postos_avaliados: number;
  status: string;
  fatores_risco: LTCATFatorRisco[];
  proxima_acao: string;
}

// =============================================================================
// LABELS
// =============================================================================

export const AFASTAMENTO_STATUS_LABELS: Record<string, string> = {
  ativo: 'Ativo',
  encerrado: 'Encerrado',
  prorrogado: 'Prorrogado',
};

export const GRAVIDADE_LABELS: Record<string, string> = {
  leve: 'Leve',
  medio: 'Medio',
  grave: 'Grave',
  critico: 'Critico',
};

// =============================================================================
// SERVICE - SST
// =============================================================================

const BASE = '/api/v1/people-management/sst';

export const sstService = {
  // Dashboard
  getDashboard: () =>
    api.get<SSTDashboard>(`${BASE}/dashboard`).then((r) => r.data),

  // Afastamentos
  listAfastamentos: (status?: string) =>
    api
      .get<AfastamentoList>(`${BASE}/afastamentos`, {
        params: status ? { status } : {},
      })
      .then((r) => r.data),

  getAfastamento: (id: string) =>
    api.get<Afastamento>(`${BASE}/afastamentos/${id}`).then((r) => r.data),

  createAfastamento: (data: AfastamentoCreate) =>
    api.post(`${BASE}/afastamentos`, data).then((r) => r.data),

  registrarRetorno: (id: string, data_retorno: string) =>
    api
      .put(`${BASE}/afastamentos/${id}/retorno`, { data_retorno })
      .then((r) => r.data),

  // CAT
  listCATs: (employee_id?: string) =>
    api
      .get<CATList>(`${BASE}/cat`, {
        params: employee_id ? { employee_id } : {},
      })
      .then((r) => r.data),

  createCAT: (data: CATCreate) =>
    api.post(`${BASE}/cat`, data).then((r) => r.data),

  getTaxaAcidente: () =>
    api.get<TaxaAcidente>(`${BASE}/cat/taxa-acidente`).then((r) => r.data),

  // Estabilidade
  listEstabilidade: () =>
    api
      .get<EstabilidadeList>(`${BASE}/estabilidade/ativos`)
      .then((r) => r.data),

  // Ajuda Medicamento
  listAjudaMedicamento: () =>
    api
      .get<AjudaMedicamentoList>(`${BASE}/ajuda-medicamento/ativos`)
      .then((r) => r.data),

  // NR1 / PCMSO / PPRA
  getNR1Dashboard: () =>
    api.get(`${BASE}/nr1/dashboard`).then((r) => r.data),

  getPCMSOStatus: () =>
    api.get(`${BASE}/pcmso/status`).then((r) => r.data),

  getPPRAStatus: () =>
    api.get(`${BASE}/ppra/status`).then((r) => r.data),

  // LTCAT
  getLTCATStatus: () =>
    api.get<LTCATStatus>(`${BASE}/ltcat/status`).then((r) => r.data),
};

export default sstService;
