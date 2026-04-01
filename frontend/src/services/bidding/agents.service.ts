/**
 * Services para os Agentes IA de Licitações
 * Conecta PRO - 7 Agentes especializados
 */

import api from '@/lib/api';

const BASE = '/api/v1/bidding/agents';

// ===== TYPES =====

export interface AgentStatus {
  agent: string;
  status: string;
  description: string;
}

export interface AllAgentsStatus {
  total_agentes: number;
  agentes: AgentStatus[];
  pipeline_disponivel: boolean;
}

export interface ScoutRequest {
  ufs?: string[];
  dias_publicacao?: number;
  valor_minimo?: number;
  valor_maximo?: number;
}

export interface ScoutResult {
  total_encontrados: number;
  portais_consultados: number;
  oportunidades: any[];
  erros: any[];
}

export interface AnalystRequest {
  texto_edital: string;
  tender_id?: string;
}

export interface AnalystResult {
  tender_id?: string;
  analise: {
    objeto_resumido?: string;
    modalidade_identificada?: string;
    criterio_julgamento?: string;
    valor_estimado?: number;
    itens?: any[];
    requisitos_habilitacao?: Record<string, string[]>;
    prazos?: Record<string, string>;
    red_flags?: Array<{
      tipo: string;
      descricao: string;
      severidade: string;
    }>;
    documentos_necessarios?: string[];
    recomendacao_participacao?: string;
    justificativa_recomendacao?: string;
  };
  texto_tamanho: number;
  status: string;
}

export interface AssessorRequest {
  analise: Record<string, any>;
  certidoes_validas?: any[];
  capacidade_financeira?: Record<string, any>;
  equipe_disponivel?: number;
}

export interface AssessorResult {
  score: number;
  scores_detalhados: Record<string, number>;
  recomendacao: 'GO' | 'NO_GO' | 'CONDICIONAL';
  justificativa: string;
  requisitos_nao_atendidos: string[];
  acoes_necessarias: any[];
  total_acoes: number;
}

export interface PricerRequest {
  itens: any[];
  regime_tributario?: string;
  salario_base_vigilante?: number;
  margem_minima?: number;
}

export interface PricerResult {
  itens: any[];
  resumo: {
    custos_diretos: number;
    custos_indiretos: number;
    impostos: number;
    regime_tributario: string;
  };
  cenarios: Record<string, { margem: number; total: number; descricao: string }>;
  comparativo_mercado: any;
  bdi_utilizado: number;
}

export interface PipelineRequest {
  texto_edital: string;
  regime_tributario?: string;
  salario_base_vigilante?: number;
  certidoes_validas?: any[];
  capacidade_financeira?: Record<string, any>;
  equipe_disponivel?: number;
  empresa?: Record<string, any>;
}

export interface PipelineResult {
  status: string;
  recomendacao?: string;
  score?: number;
  cenarios?: Record<string, any>;
  documentos_gerados?: number;
  justificativa?: string;
  resultados?: Record<string, any>;
}

// ===== SERVICE FUNCTIONS =====

const agentsService = {
  /** Status de todos os agentes */
  getStatus: async (): Promise<AllAgentsStatus> => {
    const { data } = await api.get(`${BASE}/status`);
    return data;
  },

  /** SCOUT: Buscar oportunidades */
  scoutBuscar: async (params: ScoutRequest): Promise<ScoutResult> => {
    const { data } = await api.post(`${BASE}/scout/buscar`, params);
    return data;
  },

  /** SCOUT: Status dos portais */
  scoutPortais: async () => {
    const { data } = await api.get(`${BASE}/scout/portais`);
    return data;
  },

  /** ANALYST: Analisar edital */
  analystAnalisar: async (params: AnalystRequest): Promise<AnalystResult> => {
    const { data } = await api.post(`${BASE}/analyst/analisar`, params);
    return data;
  },

  /** ASSESSOR: Avaliar viabilidade */
  assessorAvaliar: async (params: AssessorRequest): Promise<AssessorResult> => {
    const { data } = await api.post(`${BASE}/assessor/avaliar`, params);
    return data;
  },

  /** PRICER: Calcular preço */
  pricerCalcular: async (params: PricerRequest): Promise<PricerResult> => {
    const { data } = await api.post(`${BASE}/pricer/calcular`, params);
    return data;
  },

  /** ORCHESTRATOR: Pipeline completo */
  pipeline: async (params: PipelineRequest): Promise<PipelineResult> => {
    const { data } = await api.post(`${BASE}/pipeline`, params);
    return data;
  },

  /** SENTINEL: Tipos de certidões */
  sentinelTipos: async () => {
    const { data } = await api.get(`${BASE}/sentinel/tipos`);
    return data;
  },

  /** SENTINEL: Verificar certidões */
  sentinelVerificar: async (cnpj?: string) => {
    const { data } = await api.post(`${BASE}/sentinel/verificar`, null, {
      params: { cnpj },
    });
    return data;
  },

  /** SENTINEL: Alertas */
  sentinelAlertas: async (cnpj?: string, dias?: number) => {
    const { data } = await api.post(`${BASE}/sentinel/alertas`, null, {
      params: { cnpj, dias_antecedencia: dias },
    });
    return data;
  },

  /** WARRIOR: Status disputas */
  warriorStatus: async () => {
    const { data } = await api.get(`${BASE}/warrior/status`);
    return data;
  },
};

export default agentsService;
