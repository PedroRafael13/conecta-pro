/**
 * Fixtures de dados de teste para módulo Financial
 */

// ========== CONTAS A PAGAR ==========

export interface PayableResponse {
  id: string;
  descricao: string;
  categoria: string;
  fornecedor_id?: string;
  fornecedor_nome?: string;
  valor_original: number;
  valor_pago?: number;
  data_vencimento: string;
  data_pagamento?: string;
  data_emissao: string;
  status: 'pendente' | 'pago' | 'vencido' | 'cancelado' | 'parcelado';
  forma_pagamento?: string;
  numero_documento?: string;
  observacoes?: string;
  parcelas?: Array<{
    numero: number;
    valor: number;
    vencimento: string;
    status: string;
  }>;
  centro_custo?: string;
  updated_at: string;
}

export const mockPayable: PayableResponse = {
  id: 'payable-001',
  descricao: 'Aluguel Sede Empresarial',
  categoria: 'aluguel',
  fornecedor_id: 'forn-001',
  fornecedor_nome: 'Imobiliária Central Ltda',
  valor_original: 15000,
  data_vencimento: '2026-02-10',
  data_emissao: '2026-02-01',
  status: 'pendente',
  forma_pagamento: 'boleto',
  numero_documento: 'BOLETO-2026-0001',
  observacoes: 'Aluguel mensal sede Avenida Paulista',
  centro_custo: 'Administrativo',
  updated_at: '2026-02-01T10:00:00Z',
};

export const mockPayables: PayableResponse[] = [
  mockPayable,
  {
    ...mockPayable,
    id: 'payable-002',
    descricao: 'Energia Elétrica - Sede',
    categoria: 'utilities',
    fornecedor_nome: 'Eletropaulo',
    valor_original: 3500.5,
    valor_pago: 3500.5,
    data_vencimento: '2026-02-15',
    data_pagamento: '2026-02-14',
    status: 'pago',
  },
  {
    ...mockPayable,
    id: 'payable-003',
    descricao: 'Fornecimento de Uniformes',
    categoria: 'compras',
    fornecedor_nome: 'Uniformes Profissionais SA',
    valor_original: 8500,
    data_vencimento: '2026-01-20',
    status: 'vencido',
  },
  {
    ...mockPayable,
    id: 'payable-004',
    descricao: 'Manutenção Equipamentos',
    categoria: 'manutencao',
    fornecedor_nome: 'Tech Maintenance',
    valor_original: 2500,
    status: 'cancelado',
  },
];

// ========== CONTAS A RECEBER ==========

export interface ReceivableResponse {
  id: string;
  descricao: string;
  cliente_id: string;
  cliente_nome: string;
  contrato_id?: string;
  valor_original: number;
  valor_recebido?: number;
  data_vencimento: string;
  data_recebimento?: string;
  data_emissao: string;
  status: 'pendente' | 'recebido' | 'vencido' | 'cancelado' | 'parcelado';
  forma_recebimento?: string;
  numero_documento?: string;
  observacoes?: string;
  parcelas?: Array<{
    numero: number;
    valor: number;
    vencimento: string;
    status: string;
  }>;
  updated_at: string;
}

export const mockReceivable: ReceivableResponse = {
  id: 'receivable-001',
  descricao: 'Mensalidade Vigilância - Shopping Metropolitano',
  cliente_id: 'cliente-003',
  cliente_nome: 'Shopping Center Metropolitano',
  contrato_id: 'contrato-001',
  valor_original: 45000,
  data_vencimento: '2026-02-10',
  data_emissao: '2026-02-01',
  status: 'pendente',
  forma_recebimento: 'boleto',
  numero_documento: 'NF-2026-001',
  observacoes: 'Referência ao mês de fevereiro/2026',
  updated_at: '2026-02-01T10:00:00Z',
};

export const mockReceivables: ReceivableResponse[] = [
  mockReceivable,
  {
    ...mockReceivable,
    id: 'receivable-002',
    descricao: 'Mensalidade Segurança - Condomínio Bella Vista',
    cliente_id: 'cliente-002',
    cliente_nome: 'Condomínio Residencial Bella Vista',
    valor_original: 28000,
    valor_recebido: 28000,
    data_vencimento: '2026-02-05',
    data_recebimento: '2026-02-05',
    status: 'recebido',
  },
  {
    ...mockReceivable,
    id: 'receivable-003',
    descricao: 'Serviço Extra - Evento',
    cliente_id: 'cliente-001',
    cliente_nome: 'Empresa de Segurança LTDA',
    valor_original: 12500,
    data_vencimento: '2026-01-30',
    status: 'vencido',
  },
  {
    ...mockReceivable,
    id: 'receivable-004',
    descricao: 'Mensalidade - Indústria Nacional',
    cliente_id: 'cliente-004',
    cliente_nome: 'Indústria Nacional Ltda',
    valor_original: 55000,
    data_vencimento: '2026-02-15',
    status: 'pendente',
  },
];

// ========== FLUXO DE CAIXA ==========

export interface CashflowEntryResponse {
  id: string;
  data: string;
  tipo: 'entrada' | 'saida';
  categoria: string;
  descricao: string;
  valor: number;
  conta_bancaria_id?: string;
  conta_bancaria_nome?: string;
  documento_relacionado_id?: string;
  documento_relacionado_tipo?: 'payable' | 'receivable' | 'nfe' | 'nfse';
  centro_custo?: string;
  projeto?: string;
  observacoes?: string;
  conciliado: boolean;
  data_conciliacao?: string;
  updated_at: string;
}

export const mockCashflowEntry: CashflowEntryResponse = {
  id: 'cashflow-001',
  data: '2026-02-05',
  tipo: 'entrada',
  categoria: 'receita_operacional',
  descricao: 'Recebimento - Condomínio Bella Vista',
  valor: 28000,
  conta_bancaria_id: 'bank-001',
  conta_bancaria_nome: 'Conta Principal Itaú',
  documento_relacionado_id: 'receivable-002',
  documento_relacionado_tipo: 'receivable',
  centro_custo: 'Operacional',
  conciliado: true,
  data_conciliacao: '2026-02-05T10:30:00Z',
  updated_at: '2026-02-05T10:30:00Z',
};

export const mockCashflowEntries: CashflowEntryResponse[] = [
  mockCashflowEntry,
  {
    ...mockCashflowEntry,
    id: 'cashflow-002',
    tipo: 'saida',
    categoria: 'despesa_administrativa',
    descricao: 'Pagamento - Aluguel',
    valor: 15000,
    documento_relacionado_id: 'payable-001',
    documento_relacionado_tipo: 'payable',
    conciliado: false,
    data_conciliacao: undefined,
  },
  {
    ...mockCashflowEntry,
    id: 'cashflow-003',
    tipo: 'entrada',
    categoria: 'receita_operacional',
    descricao: 'Recebimento - Serviço Extra',
    valor: 5000,
    conciliado: true,
  },
  {
    ...mockCashflowEntry,
    id: 'cashflow-004',
    tipo: 'saida',
    categoria: 'folha_pagamento',
    descricao: 'Pagamento de Salários',
    valor: 125000,
    conciliado: true,
  },
];

export interface CashflowProjectionResponse {
  periodo: string;
  data_inicio: string;
  data_fim: string;
  saldo_inicial: number;
  total_entradas_previstas: number;
  total_saidas_previstas: number;
  saldo_final_previsto: number;
  dias: Array<{
    data: string;
    entradas_previstas: number;
    saidas_previstas: number;
    saldo_acumulado: number;
  }>;
}

export const mockCashflowProjection: CashflowProjectionResponse = {
  periodo: 'fevereiro/2026',
  data_inicio: '2026-02-01',
  data_fim: '2026-02-28',
  saldo_inicial: 150000,
  total_entradas_previstas: 180000,
  total_saidas_previstas: 165000,
  saldo_final_previsto: 165000,
  dias: [
    { data: '2026-02-01', entradas_previstas: 0, saidas_previstas: 0, saldo_acumulado: 150000 },
    { data: '2026-02-05', entradas_previstas: 28000, saidas_previstas: 0, saldo_acumulado: 178000 },
    { data: '2026-02-10', entradas_previstas: 45000, saidas_previstas: 15000, saldo_acumulado: 208000 },
  ],
};

// ========== NOTAS FISCAIS ==========

export interface NFeResponse {
  id: string;
  numero: string;
  serie: string;
  cliente_id: string;
  cliente_nome: string;
  data_emissao: string;
  data_saida?: string;
  valor_total: number;
  valor_produtos: number;
  valor_servicos: number;
  valor_impostos: number;
  status: 'rascunho' | 'emitida' | 'autorizada' | 'cancelada' | 'denegada';
  chave_acesso?: string;
  protocolo?: string;
  natureza_operacao: string;
  observacoes?: string;
  itens: Array<{
    id: string;
    produto_id: string;
    descricao: string;
    quantidade: number;
    valor_unitario: number;
    valor_total: number;
    cfop: string;
    ncm: string;
    impostos: Record<string, number>;
  }>;
  updated_at: string;
}

export const mockNFe: NFeResponse = {
  id: 'nfe-001',
  numero: '000001',
  serie: '1',
  cliente_id: 'cliente-003',
  cliente_nome: 'Shopping Center Metropolitano',
  data_emissao: '2026-02-01T10:00:00Z',
  data_saida: '2026-02-01T10:00:00Z',
  valor_total: 45000,
  valor_produtos: 0,
  valor_servicos: 45000,
  valor_impostos: 7650,
  status: 'autorizada',
  chave_acesso: '35260212345678000190550010000000011567890123',
  protocolo: '13526021234567890',
  natureza_operacao: 'Prestação de Serviços',
  observacoes: 'Nota fiscal referente à mensalidade de vigilância',
  itens: [
    {
      id: 'item-001',
      produto_id: 'serv-001',
      descricao: 'Serviço de Vigilância Patrimonial',
      quantidade: 1,
      valor_unitario: 45000,
      valor_total: 45000,
      cfop: '5933',
      ncm: '85256000',
      impostos: {
        iss: 2250,
        pis: 742.5,
        cofins: 3420,
      },
    },
  ],
  updated_at: '2026-02-01T10:05:00Z',
};

export const mockNFes: NFeResponse[] = [
  mockNFe,
  {
    ...mockNFe,
    id: 'nfe-002',
    numero: '000002',
    cliente_id: 'cliente-002',
    cliente_nome: 'Condomínio Residencial Bella Vista',
    valor_total: 28000,
    valor_servicos: 28000,
    valor_impostos: 4760,
    status: 'autorizada',
    chave_acesso: '35260212345678000190550010000000021567890124',
  },
  {
    ...mockNFe,
    id: 'nfe-003',
    numero: '000003',
    cliente_id: 'cliente-001',
    cliente_nome: 'Empresa de Segurança LTDA',
    valor_total: 12500,
    valor_servicos: 12500,
    valor_impostos: 2125,
    status: 'rascunho',
    chave_acesso: undefined,
    protocolo: undefined,
  },
  {
    ...mockNFe,
    id: 'nfe-004',
    numero: '000004',
    cliente_id: 'cliente-004',
    cliente_nome: 'Indústria Nacional Ltda',
    valor_total: 55000,
    valor_servicos: 55000,
    valor_impostos: 9350,
    status: 'cancelada',
    chave_acesso: '35260212345678000190550010000000041567890125',
  },
];

// Helpers para criar dados customizados
export const createMockPayable = (overrides?: Partial<PayableResponse>): PayableResponse => ({
  ...mockPayable,
  ...overrides,
});

export const createMockReceivable = (overrides?: Partial<ReceivableResponse>): ReceivableResponse => ({
  ...mockReceivable,
  ...overrides,
});

export const createMockCashflowEntry = (overrides?: Partial<CashflowEntryResponse>): CashflowEntryResponse => ({
  ...mockCashflowEntry,
  ...overrides,
});

export const createMockNFe = (overrides?: Partial<NFeResponse>): NFeResponse => ({
  ...mockNFe,
  ...overrides,
});
