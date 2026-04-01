/**
 * Fixtures de dados de teste para módulo de CRM
 */

// ========== LEADS ==========

export interface LeadResponse {
  id: string;
  nome: string;
  email: string;
  telefone?: string;
  empresa?: string;
  cargo?: string;
  origem: string;
  status: 'novo' | 'em_contato' | 'qualificado' | 'desqualificado' | 'convertido';
  prioridade: 'baixa' | 'media' | 'alta' | 'urgente';
  responsavel_id?: string;
  responsavel_nome?: string;
  observacoes?: string;
  data_criacao: string;
  updated_at: string;
  data_ultimo_contato?: string;
  data_conversao?: string;
  valor_estimado?: number;
  tags?: string[];
}

export const mockLead: LeadResponse = {
  id: 'lead-001',
  nome: 'Carlos Mendes',
  email: 'carlos@empresaexemplo.com',
  telefone: '(11) 99999-8888',
  empresa: 'Empresa Exemplo Ltda',
  cargo: 'Gerente de Segurança',
  origem: 'site',
  status: 'novo',
  prioridade: 'alta',
  responsavel_id: 'user-001',
  responsavel_nome: 'Administrador',
  observacoes: 'Interessado em vigilância patrimonial',
  data_criacao: '2026-02-01T10:00:00Z',
  updated_at: '2026-02-01T10:00:00Z',
  valor_estimado: 50000,
  tags: ['vigilancia', 'patrimonial', 'urgente'],
};

export const mockLeads: LeadResponse[] = [
  mockLead,
  {
    ...mockLead,
    id: 'lead-002',
    nome: 'Fernanda Lima',
    email: 'fernanda@outraempresa.com',
    empresa: 'Outra Empresa SA',
    status: 'em_contato',
    prioridade: 'media',
    valor_estimado: 30000,
  },
  {
    ...mockLead,
    id: 'lead-003',
    nome: 'Roberto Almeida',
    email: 'roberto@terceira.com',
    empresa: 'Terceira Indústria',
    status: 'convertido',
    prioridade: 'alta',
    data_conversao: '2026-02-03T15:00:00Z',
    valor_estimado: 120000,
  },
];

// ========== OPORTUNIDADES ==========

export interface OportunidadeResponse {
  id: string;
  titulo: string;
  descricao?: string;
  cliente_id: string;
  cliente_nome: string;
  contato_id?: string;
  contato_nome?: string;
  responsavel_id: string;
  responsavel_nome: string;
  etapa: 'prospeccao' | 'qualificacao' | 'proposta' | 'negociacao' | 'fechamento' | 'perdido';
  probabilidade: number;
  valor_estimado: number;
  valor_final?: number;
  data_prevista_fechamento?: string;
  data_fechamento?: string;
  motivo_perda?: string;
  origem: string;
  fonte_lead?: string;
  data_criacao: string;
  updated_at: string;
  produtos?: Array<{
    produto_id: string;
    nome: string;
    quantidade: number;
    valor_unitario: number;
    valor_total: number;
  }>;
  atividades?: Array<{
    id: string;
    tipo: string;
    descricao: string;
    data_agendada: string;
    status: string;
  }>;
}

export const mockOportunidade: OportunidadeResponse = {
  id: 'oportunidade-001',
  titulo: 'Serviço de Vigilância - Shopping',
  descricao: 'Contratação de vigilância para shopping center',
  cliente_id: 'cliente-003',
  cliente_nome: 'Shopping Center Metropolitano',
  responsavel_id: 'user-001',
  responsavel_nome: 'Administrador',
  etapa: 'proposta',
  probabilidade: 75,
  valor_estimado: 250000,
  data_prevista_fechamento: '2026-03-15T00:00:00Z',
  origem: 'indicacao',
  data_criacao: '2026-02-01T10:00:00Z',
  updated_at: '2026-02-05T14:00:00Z',
  produtos: [
    {
      produto_id: 'prod-001',
      nome: 'Vigilância Patrimonial 24h',
      quantidade: 1,
      valor_unitario: 200000,
      valor_total: 200000,
    },
    {
      produto_id: 'prod-002',
      nome: 'Monitoramento CFTV',
      quantidade: 1,
      valor_unitario: 50000,
      valor_total: 50000,
    },
  ],
  atividades: [
    {
      id: 'ativ-001',
      tipo: 'reuniao',
      descricao: 'Apresentação da proposta',
      data_agendada: '2026-02-10T14:00:00Z',
      status: 'agendada',
    },
  ],
};

export const mockOportunidades: OportunidadeResponse[] = [
  mockOportunidade,
  {
    ...mockOportunidade,
    id: 'oportunidade-002',
    titulo: 'Segurança Condominial',
    cliente_id: 'cliente-002',
    cliente_nome: 'Condomínio Residencial Bella Vista',
    etapa: 'negociacao',
    probabilidade: 90,
    valor_estimado: 180000,
  },
  {
    ...mockOportunidade,
    id: 'oportunidade-003',
    titulo: 'Portaria Remota',
    cliente_id: 'cliente-001',
    cliente_nome: 'Empresa de Segurança LTDA',
    etapa: 'fechamento',
    probabilidade: 95,
    valor_estimado: 85000,
    valor_final: 80000,
    data_fechamento: '2026-02-04T10:00:00Z',
  },
  {
    ...mockOportunidade,
    id: 'oportunidade-004',
    titulo: 'Ronda Eletrônica',
    cliente_id: 'cliente-004',
    cliente_nome: 'Indústria Nacional Ltda',
    etapa: 'perdido',
    probabilidade: 0,
    valor_estimado: 45000,
    motivo_perda: 'Preço acima do orçamento',
    data_fechamento: '2026-01-20T00:00:00Z',
  },
];

// ========== PROPOSTAS ==========

export interface PropostaResponse {
  id: string;
  numero: string;
  oportunidade_id: string;
  oportunidade_titulo: string;
  cliente_id: string;
  cliente_nome: string;
  responsavel_id: string;
  responsavel_nome: string;
  status: 'rascunho' | 'enviada' | 'em_analise' | 'aprovada' | 'rejeitada' | 'expirada';
  valor_total: number;
  desconto?: number;
  valor_final: number;
  validade_dias: number;
  data_emissao: string;
  data_validade: string;
  data_aprovacao?: string;
  data_rejeicao?: string;
  motivo_rejeicao?: string;
  condicoes_pagamento: string;
  prazo_execucao: number;
  observacoes?: string;
  itens: Array<{
    id: string;
    descricao: string;
    quantidade: number;
    valor_unitario: number;
    valor_total: number;
    observacao?: string;
  }>;
  anexos?: Array<{
    id: string;
    nome: string;
    url: string;
    tamanho: number;
  }>;
  data_criacao: string;
  updated_at: string;
}

export const mockProposta: PropostaResponse = {
  id: 'proposta-001',
  numero: 'PROP-2026-001',
  oportunidade_id: 'oportunidade-001',
  oportunidade_titulo: 'Serviço de Vigilância - Shopping',
  cliente_id: 'cliente-003',
  cliente_nome: 'Shopping Center Metropolitano',
  responsavel_id: 'user-001',
  responsavel_nome: 'Administrador',
  status: 'em_analise',
  valor_total: 250000,
  desconto: 10000,
  valor_final: 240000,
  validade_dias: 30,
  data_emissao: '2026-02-05T10:00:00Z',
  data_validade: '2026-03-07T10:00:00Z',
  condicoes_pagamento: '30/60/90 dias',
  prazo_execucao: 12,
  observacoes: 'Proposta com condições especiais para cliente VIP',
  itens: [
    {
      id: 'item-001',
      descricao: 'Serviço de Vigilância Patrimonial 24h',
      quantidade: 1,
      valor_unitario: 200000,
      valor_total: 200000,
    },
    {
      id: 'item-002',
      descricao: 'Monitoramento CFTV',
      quantidade: 1,
      valor_unitario: 50000,
      valor_total: 50000,
    },
  ],
  anexos: [
    {
      id: 'anexo-001',
      nome: 'Proposta Técnica.pdf',
      url: 'https://example.com/proposta.pdf',
      tamanho: 2048000,
    },
  ],
  data_criacao: '2026-02-05T10:00:00Z',
  updated_at: '2026-02-05T10:00:00Z',
};

export const mockPropostas: PropostaResponse[] = [
  mockProposta,
  {
    ...mockProposta,
    id: 'proposta-002',
    numero: 'PROP-2026-002',
    oportunidade_id: 'oportunidade-002',
    oportunidade_titulo: 'Segurança Condominial',
    cliente_id: 'cliente-002',
    cliente_nome: 'Condomínio Residencial Bella Vista',
    status: 'aprovada',
    valor_total: 180000,
    valor_final: 180000,
    data_aprovacao: '2026-02-03T14:00:00Z',
  },
  {
    ...mockProposta,
    id: 'proposta-003',
    numero: 'PROP-2026-003',
    oportunidade_id: 'oportunidade-004',
    oportunidade_titulo: 'Ronda Eletrônica',
    cliente_id: 'cliente-004',
    cliente_nome: 'Indústria Nacional Ltda',
    status: 'rejeitada',
    valor_total: 45000,
    valor_final: 45000,
    data_rejeicao: '2026-01-20T10:00:00Z',
    motivo_rejeicao: 'Preço acima do orçamento do cliente',
  },
  {
    ...mockProposta,
    id: 'proposta-004',
    numero: 'PROP-2026-004',
    oportunidade_id: 'oportunidade-001',
    oportunidade_titulo: 'Serviço de Vigilância - Shopping',
    status: 'rascunho',
    valor_total: 260000,
    valor_final: 250000,
  },
];

// Helpers para criar dados customizados
export const createMockLead = (overrides?: Partial<LeadResponse>): LeadResponse => ({
  ...mockLead,
  ...overrides,
});

export const createMockOportunidade = (overrides?: Partial<OportunidadeResponse>): OportunidadeResponse => ({
  ...mockOportunidade,
  ...overrides,
});

export const createMockProposta = (overrides?: Partial<PropostaResponse>): PropostaResponse => ({
  ...mockProposta,
  ...overrides,
});
