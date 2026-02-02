/**
 * Fixtures de dados de teste para módulo de Licitações
 */

import type {
  EditalResponse,
  PropostaResponse,
  ContratoResponse,
  CertidaoResponse,
  DocumentoLicitacaoResponse,
} from '@/api/generated/bidding';

// Mock de Edital
export const mockEdital: EditalResponse = {
  id: 'edital-001',
  numero: '001/2026',
  objeto: 'Serviços de vigilância patrimonial',
  modalidade: 'pregao_eletronico',
  tipo: 'menor_preco',
  valor_estimado: 500000.0,
  data_abertura: '2026-03-15T10:00:00Z',
  data_encerramento: '2026-03-20T18:00:00Z',
  status: 'publicado',
  orgao: 'Prefeitura Municipal',
  edital_url: 'https://example.com/edital.pdf',
  created_at: '2026-02-01T10:00:00Z',
  updated_at: '2026-02-01T10:00:00Z',
};

export const mockEditais: EditalResponse[] = [
  mockEdital,
  {
    ...mockEdital,
    id: 'edital-002',
    numero: '002/2026',
    objeto: 'Serviços de limpeza',
    status: 'aberto',
    valor_estimado: 300000.0,
  },
  {
    ...mockEdital,
    id: 'edital-003',
    numero: '003/2026',
    objeto: 'Fornecimento de EPIs',
    status: 'em_analise',
    valor_estimado: 150000.0,
  },
];

// Mock de Proposta
export const mockProposta: PropostaResponse = {
  id: 'proposta-001',
  edital_id: 'edital-001',
  edital_numero: '001/2026',
  valor_proposto: 480000.0,
  prazo_execucao: 12,
  observacoes: 'Proposta técnica conforme especificações',
  status: 'em_analise',
  data_envio: '2026-03-16T14:30:00Z',
  created_at: '2026-03-16T14:30:00Z',
  updated_at: '2026-03-16T14:30:00Z',
};

export const mockPropostas: PropostaResponse[] = [
  mockProposta,
  {
    ...mockProposta,
    id: 'proposta-002',
    edital_numero: '002/2026',
    valor_proposto: 290000.0,
    status: 'classificada',
  },
  {
    ...mockProposta,
    id: 'proposta-003',
    edital_numero: '003/2026',
    valor_proposto: 145000.0,
    status: 'desclassificada',
  },
];

// Mock de Contrato
export const mockContrato: ContratoResponse = {
  id: 'contrato-001',
  numero: 'CONTRATO-001/2026',
  proposta_id: 'proposta-001',
  fornecedor: 'Empresa de Segurança LTDA',
  valor_total: 480000.0,
  valor_executado: 120000.0,
  data_inicio: '2026-04-01T00:00:00Z',
  data_fim: '2027-03-31T23:59:59Z',
  status: 'vigente',
  objeto: 'Serviços de vigilância patrimonial',
  created_at: '2026-03-25T10:00:00Z',
  updated_at: '2026-03-25T10:00:00Z',
};

export const mockContratos: ContratoResponse[] = [
  mockContrato,
  {
    ...mockContrato,
    id: 'contrato-002',
    numero: 'CONTRATO-002/2026',
    fornecedor: 'Empresa de Limpeza SA',
    valor_total: 290000.0,
    valor_executado: 0,
    status: 'assinado',
  },
];

// Mock de Certidão
export const mockCertidao: CertidaoResponse = {
  id: 'certidao-001',
  tipo: 'regularidade_fiscal',
  numero: 'CRF-123456',
  orgao_emissor: 'Receita Federal',
  data_emissao: '2026-01-15T00:00:00Z',
  data_validade: '2026-07-15T23:59:59Z',
  status: 'valida',
  arquivo_url: 'https://example.com/certidao.pdf',
  created_at: '2026-01-15T10:00:00Z',
  updated_at: '2026-01-15T10:00:00Z',
};

export const mockCertidoes: CertidaoResponse[] = [
  mockCertidao,
  {
    ...mockCertidao,
    id: 'certidao-002',
    tipo: 'trabalhista',
    numero: 'CNT-789012',
    orgao_emissor: 'TST',
    status: 'valida',
  },
  {
    ...mockCertidao,
    id: 'certidao-003',
    tipo: 'municipal',
    numero: 'CM-345678',
    orgao_emissor: 'Prefeitura',
    data_validade: '2026-02-20T23:59:59Z',
    status: 'vencida',
  },
];

// Mock de Documento
export const mockDocumento: DocumentoLicitacaoResponse = {
  id: 'doc-001',
  nome: 'Proposta Técnica.pdf',
  tipo: 'proposta_tecnica',
  categoria: 'proposta',
  tamanho: 1024000,
  arquivo_url: 'https://example.com/documento.pdf',
  created_at: '2026-03-16T14:30:00Z',
  updated_at: '2026-03-16T14:30:00Z',
};

export const mockDocumentos: DocumentoLicitacaoResponse[] = [
  mockDocumento,
  {
    ...mockDocumento,
    id: 'doc-002',
    nome: 'Proposta Comercial.pdf',
    tipo: 'proposta_comercial',
    tamanho: 512000,
  },
  {
    ...mockDocumento,
    id: 'doc-003',
    nome: 'Atestados.pdf',
    tipo: 'atestado',
    categoria: 'habilitacao',
    tamanho: 2048000,
  },
];

// Helpers para criar dados customizados
export const createMockEdital = (
  overrides?: Partial<EditalResponse>
): EditalResponse => ({
  ...mockEdital,
  ...overrides,
});

export const createMockProposta = (
  overrides?: Partial<PropostaResponse>
): PropostaResponse => ({
  ...mockProposta,
  ...overrides,
});

export const createMockContrato = (
  overrides?: Partial<ContratoResponse>
): ContratoResponse => ({
  ...mockContrato,
  ...overrides,
});

export const createMockCertidao = (
  overrides?: Partial<CertidaoResponse>
): CertidaoResponse => ({
  ...mockCertidao,
  ...overrides,
});

export const createMockDocumento = (
  overrides?: Partial<DocumentoLicitacaoResponse>
): DocumentoLicitacaoResponse => ({
  ...mockDocumento,
  ...overrides,
});
