/**
 * Fixtures de dados de teste para módulo de Clientes
 */

export interface ClienteResponse {
  id: string;
  nome: string;
  nome_fantasia?: string;
  documento: string;
  tipo_documento: 'cpf' | 'cnpj';
  email: string;
  telefone?: string;
  celular?: string;
  endereco?: {
    cep?: string;
    logradouro?: string;
    numero?: string;
    complemento?: string;
    bairro?: string;
    cidade?: string;
    estado?: string;
  };
  responsavel_nome?: string;
  responsavel_email?: string;
  responsavel_telefone?: string;
  status: 'ativo' | 'inativo' | 'pendente';
  data_cadastro: string;
  updated_at: string;
  observacoes?: string;
  categoria?: string;
  origem?: string;
}

export interface ClienteCreateRequest {
  nome: string;
  nome_fantasia?: string;
  documento: string;
  tipo_documento: 'cpf' | 'cnpj';
  email: string;
  telefone?: string;
  celular?: string;
  endereco?: {
    cep?: string;
    logradouro?: string;
    numero?: string;
    complemento?: string;
    bairro?: string;
    cidade?: string;
    estado?: string;
  };
  responsavel_nome?: string;
  responsavel_email?: string;
  responsavel_telefone?: string;
  observacoes?: string;
  categoria?: string;
  origem?: string;
}

// Mock de Cliente
export const mockCliente: ClienteResponse = {
  id: 'cliente-001',
  nome: 'Empresa de Segurança LTDA',
  nome_fantasia: 'Segurança Pro',
  documento: '12.345.678/0001-90',
  tipo_documento: 'cnpj',
  email: 'contato@segurancapro.com',
  telefone: '(11) 3456-7890',
  celular: '(11) 98765-4321',
  endereco: {
    cep: '01310-100',
    logradouro: 'Avenida Paulista',
    numero: '1000',
    complemento: 'Sala 1501',
    bairro: 'Bela Vista',
    cidade: 'São Paulo',
    estado: 'SP',
  },
  responsavel_nome: 'João Silva',
  responsavel_email: 'joao@segurancapro.com',
  responsavel_telefone: '(11) 98765-4321',
  status: 'ativo',
  data_cadastro: '2026-01-15T10:00:00Z',
  updated_at: '2026-02-05T14:30:00Z',
  observacoes: 'Cliente VIP',
  categoria: 'empresa',
  origem: 'indicacao',
};

export const mockClientes: ClienteResponse[] = [
  mockCliente,
  {
    ...mockCliente,
    id: 'cliente-002',
    nome: 'Condomínio Residencial Bella Vista',
    nome_fantasia: 'Condomínio Bella Vista',
    documento: '45.678.901/0001-23',
    email: 'admin@bellavista.com',
    responsavel_nome: 'Maria Santos',
    status: 'ativo',
  },
  {
    ...mockCliente,
    id: 'cliente-003',
    nome: 'Shopping Center Metropolitano',
    nome_fantasia: 'Shopping Metropolitano',
    documento: '67.890.123/0001-45',
    email: 'seguranca@shoppingmetro.com',
    responsavel_nome: 'Pedro Costa',
    status: 'inativo',
  },
  {
    ...mockCliente,
    id: 'cliente-004',
    nome: 'Indústria Nacional Ltda',
    nome_fantasia: 'Indústria Nacional',
    documento: '89.012.345/0001-67',
    email: 'contato@indnacional.com',
    status: 'pendente',
  },
];

// Mock para criação de cliente
export const mockClienteCreate: ClienteCreateRequest = {
  nome: 'Novo Cliente LTDA',
  nome_fantasia: 'Novo Cliente',
  documento: '98.765.432/0001-10',
  tipo_documento: 'cnpj',
  email: 'contato@novocliente.com',
  telefone: '(11) 3333-4444',
  celular: '(11) 98888-7777',
  endereco: {
    cep: '04538-132',
    logradouro: 'Rua Funchal',
    numero: '500',
    complemento: 'Andar 10',
    bairro: 'Vila Olímpia',
    cidade: 'São Paulo',
    estado: 'SP',
  },
  responsavel_nome: 'Ana Paula',
  responsavel_email: 'ana@novocliente.com',
  responsavel_telefone: '(11) 98888-7777',
  observacoes: 'Novo cliente potencial',
  categoria: 'empresa',
  origem: 'site',
};

// Helpers para criar dados customizados
export const createMockCliente = (overrides?: Partial<ClienteResponse>): ClienteResponse => ({
  ...mockCliente,
  ...overrides,
});

export const createMockClienteCreate = (
  overrides?: Partial<ClienteCreateRequest>
): ClienteCreateRequest => ({
  ...mockClienteCreate,
  ...overrides,
});
