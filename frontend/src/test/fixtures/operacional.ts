/**
 * Fixtures de dados de teste para módulo Operacional
 */

// ========== POSTOS ==========

export interface PostResponse {
  id: string;
  nome: string;
  descricao?: string;
  cliente_id: string;
  cliente_nome: string;
  contrato_id?: string;
  endereco?: {
    cep?: string;
    logradouro?: string;
    numero?: string;
    complemento?: string;
    bairro?: string;
    cidade?: string;
    estado?: string;
  };
  latitude?: number;
  longitude?: number;
  status: 'ativo' | 'inativo' | 'manutencao';
  tipo: 'fixo' | 'movel' | 'evento';
  requerimentos?: {
    quantidade_funcionarios: number;
    turno?: string;
    armamento?: boolean;
    veiculo?: boolean;
    uniforme?: string;
  };
  responsavel_nome?: string;
  responsavel_telefone?: string;
  data_criacao: string;
  updated_at: string;
}

export const mockPost: PostResponse = {
  id: 'posto-001',
  nome: 'Portaria Principal - Shopping Metropolitano',
  descricao: 'Portaria principal do shopping com controle de acesso',
  cliente_id: 'cliente-003',
  cliente_nome: 'Shopping Center Metropolitano',
  contrato_id: 'contrato-001',
  endereco: {
    cep: '01310-100',
    logradouro: 'Avenida Paulista',
    numero: '1000',
    complemento: 'Entrada Principal',
    bairro: 'Bela Vista',
    cidade: 'São Paulo',
    estado: 'SP',
  },
  latitude: -23.5631,
  longitude: -46.6564,
  status: 'ativo',
  tipo: 'fixo',
  requerimentos: {
    quantidade_funcionarios: 4,
    turno: '24h',
    armamento: false,
    veiculo: false,
    uniforme: 'social',
  },
  responsavel_nome: 'Carlos Porteiro',
  responsavel_telefone: '(11) 99999-8888',
  data_criacao: '2026-01-15T10:00:00Z',
  updated_at: '2026-02-05T14:30:00Z',
};

export const mockPosts: PostResponse[] = [
  mockPost,
  {
    ...mockPost,
    id: 'posto-002',
    nome: 'Estacionamento - Shopping Metropolitano',
    descricao: 'Vigilância do estacionamento subterrâneo',
    status: 'ativo',
    tipo: 'fixo',
    requerimentos: {
      quantidade_funcionarios: 2,
      turno: '24h',
      armamento: false,
      veiculo: true,
      uniforme: 'operacional',
    },
  },
  {
    ...mockPost,
    id: 'posto-003',
    nome: 'Câmeras CFTV - Shopping Metropolitano',
    descricao: 'Central de monitoramento CFTV',
    status: 'ativo',
    tipo: 'fixo',
    requerimentos: {
      quantidade_funcionarios: 2,
      turno: '24h',
      armamento: false,
      veiculo: false,
      uniforme: 'social',
    },
  },
];

// ========== ESCALAS ==========

export interface ScaleResponse {
  id: string;
  nome: string;
  descricao?: string;
  posto_id: string;
  posto_nome: string;
  cliente_id: string;
  cliente_nome: string;
  data_inicio: string;
  data_fim: string;
  status: 'rascunho' | 'publicada' | 'em_execucao' | 'concluida' | 'cancelada';
  turno: 'diurno' | 'noturno' | '24h' | 'personalizado';
  funcionarios: Array<{
    id: string;
    funcionario_id: string;
    funcionario_nome: string;
    data: string;
    hora_inicio: string;
    hora_fim: string;
    status: 'agendado' | 'confirmado' | 'em_andamento' | 'concluido' | 'faltou';
  }>;
  data_criacao: string;
  updated_at: string;
  publicada_em?: string;
}

export const mockScale: ScaleResponse = {
  id: 'escala-001',
  nome: 'Escala Fevereiro 2026 - Portaria Principal',
  descricao: 'Escala mensal do posto de portaria',
  posto_id: 'posto-001',
  posto_nome: 'Portaria Principal - Shopping Metropolitano',
  cliente_id: 'cliente-003',
  cliente_nome: 'Shopping Center Metropolitano',
  data_inicio: '2026-02-01T00:00:00Z',
  data_fim: '2026-02-28T23:59:59Z',
  status: 'publicada',
  turno: '24h',
  funcionarios: [
    {
      id: 'escala-func-001',
      funcionario_id: 'func-001',
      funcionario_nome: 'José da Silva',
      data: '2026-02-01',
      hora_inicio: '06:00',
      hora_fim: '18:00',
      status: 'confirmado',
    },
    {
      id: 'escala-func-002',
      funcionario_id: 'func-002',
      funcionario_nome: 'Maria Oliveira',
      data: '2026-02-01',
      hora_inicio: '18:00',
      hora_fim: '06:00',
      status: 'confirmado',
    },
  ],
  data_criacao: '2026-01-25T10:00:00Z',
  updated_at: '2026-01-26T14:00:00Z',
  publicada_em: '2026-01-26T14:00:00Z',
};

export const mockScales: ScaleResponse[] = [
  mockScale,
  {
    ...mockScale,
    id: 'escala-002',
    nome: 'Escala Março 2026 - Portaria Principal',
    data_inicio: '2026-03-01T00:00:00Z',
    data_fim: '2026-03-31T23:59:59Z',
    status: 'rascunho',
    publicada_em: undefined,
  },
];

// ========== OCORRÊNCIAS ==========

export interface OccurrenceResponse {
  id: string;
  titulo: string;
  descricao: string;
  tipo: 'incidente' | 'acidente' | 'anomalia' | 'elogio' | 'sugestao' | 'outro';
  severidade: 'baixa' | 'media' | 'alta' | 'critica';
  status: 'aberta' | 'em_analise' | 'em_andamento' | 'resolvida' | 'fechada';
  posto_id: string;
  posto_nome: string;
  cliente_id: string;
  cliente_nome: string;
  funcionario_id?: string;
  funcionario_nome?: string;
  data_ocorrencia: string;
  data_registro: string;
  data_resolucao?: string;
  responsavel_id?: string;
  responsavel_nome?: string;
  acoes_tomadas?: string;
  anexos?: Array<{
    id: string;
    nome: string;
    url: string;
  }>;
  updated_at: string;
}

export const mockOccurrence: OccurrenceResponse = {
  id: 'ocorrencia-001',
  titulo: 'Tentativa de invasão no estacionamento',
  descricao: 'Indivíduo suspeito tentou acessar área restrita do estacionamento',
  tipo: 'incidente',
  severidade: 'alta',
  status: 'resolvida',
  posto_id: 'posto-002',
  posto_nome: 'Estacionamento - Shopping Metropolitano',
  cliente_id: 'cliente-003',
  cliente_nome: 'Shopping Center Metropolitano',
  funcionario_id: 'func-003',
  funcionario_nome: 'Antonio Pereira',
  data_ocorrencia: '2026-02-05T03:30:00Z',
  data_registro: '2026-02-05T03:45:00Z',
  data_resolucao: '2026-02-05T04:15:00Z',
  responsavel_id: 'user-001',
  responsavel_nome: 'Supervisor',
  acoes_tomadas: 'Indivíduo foi abordado e retirado do local. Polícia acionada.',
  anexos: [
    {
      id: 'anexo-001',
      nome: 'registro_cftv.mp4',
      url: 'https://example.com/video.mp4',
    },
  ],
  updated_at: '2026-02-05T04:15:00Z',
};

export const mockOccurrences: OccurrenceResponse[] = [
  mockOccurrence,
  {
    ...mockOccurrence,
    id: 'ocorrencia-002',
    titulo: 'Equipamento CFTV offline',
    descricao: 'Câmera 12 do estacionamento apresentou falha de conexão',
    tipo: 'anomalia',
    severidade: 'media',
    status: 'em_andamento',
    data_ocorrencia: '2026-02-06T08:00:00Z',
    data_registro: '2026-02-06T08:15:00Z',
    data_resolucao: undefined,
  },
  {
    ...mockOccurrence,
    id: 'ocorrencia-003',
    titulo: 'Elogio do cliente',
    descricao: 'Cliente elogiou atendimento do vigilante José',
    tipo: 'elogio',
    severidade: 'baixa',
    status: 'fechada',
    data_ocorrencia: '2026-02-04T14:00:00Z',
    data_registro: '2026-02-04T14:30:00Z',
    data_resolucao: '2026-02-04T15:00:00Z',
  },
];

// ========== FUNCIONÁRIOS ==========

export interface EmployeeResponse {
  id: string;
  nome: string;
  cpf: string;
  rg?: string;
  data_nascimento?: string;
  telefone?: string;
  email?: string;
  endereco?: {
    cep?: string;
    logradouro?: string;
    numero?: string;
    complemento?: string;
    bairro?: string;
    cidade?: string;
    estado?: string;
  };
  cargo: string;
  departamento?: string;
  data_admissao: string;
  data_demissao?: string;
  status: 'ativo' | 'inativo' | 'ferias' | 'afastado';
  posto_atual_id?: string;
  posto_atual_nome?: string;
  salario?: number;
  banco_horas: number;
  updated_at: string;
}

export const mockEmployee: EmployeeResponse = {
  id: 'func-001',
  nome: 'José da Silva',
  cpf: '123.456.789-00',
  rg: '12.345.678-9',
  data_nascimento: '1985-03-15',
  telefone: '(11) 98765-4321',
  email: 'jose.silva@email.com',
  endereco: {
    cep: '01001-000',
    logradouro: 'Rua das Flores',
    numero: '123',
    bairro: 'Centro',
    cidade: 'São Paulo',
    estado: 'SP',
  },
  cargo: 'Vigilante',
  departamento: 'Operações',
  data_admissao: '2025-01-10',
  status: 'ativo',
  posto_atual_id: 'posto-001',
  posto_atual_nome: 'Portaria Principal - Shopping Metropolitano',
  salario: 2500,
  banco_horas: 12.5,
  updated_at: '2026-02-05T10:00:00Z',
};

export const mockEmployees: EmployeeResponse[] = [
  mockEmployee,
  {
    ...mockEmployee,
    id: 'func-002',
    nome: 'Maria Oliveira',
    cpf: '987.654.321-00',
    cargo: 'Vigilante',
    status: 'ativo',
    posto_atual_id: 'posto-001',
    posto_atual_nome: 'Portaria Principal - Shopping Metropolitano',
    salario: 2500,
    banco_horas: -4,
  },
  {
    ...mockEmployee,
    id: 'func-003',
    nome: 'Antonio Pereira',
    cpf: '456.789.123-00',
    cargo: 'Supervisor',
    status: 'ativo',
    posto_atual_id: 'posto-002',
    posto_atual_nome: 'Estacionamento - Shopping Metropolitano',
    salario: 3500,
    banco_horas: 8,
  },
  {
    ...mockEmployee,
    id: 'func-004',
    nome: 'Ana Carolina',
    cpf: '789.123.456-00',
    cargo: 'Vigilante',
    status: 'ferias',
    posto_atual_id: undefined,
    posto_atual_nome: undefined,
    salario: 2500,
    banco_horas: 0,
  },
];

// ========== DIARISTAS ==========

export interface DiaristResponse {
  id: string;
  nome: string;
  cpf: string;
  telefone: string;
  email?: string;
  endereco?: string;
  status: 'ativo' | 'inativo' | 'bloqueado';
  avaliacao_media: number;
  total_trabalhos: number;
  especialidades: string[];
  disponibilidade: string[];
  valor_diaria_padrao: number;
  data_cadastro: string;
  updated_at: string;
}

export const mockDiarist: DiaristResponse = {
  id: 'diarista-001',
  nome: 'Cleide da Silva',
  cpf: '321.654.987-00',
  telefone: '(11) 91234-5678',
  email: 'cleide@email.com',
  endereco: 'São Paulo, SP',
  status: 'ativo',
  avaliacao_media: 4.8,
  total_trabalhos: 156,
  especialidades: ['faxina', 'passar roupa', 'lavar louça'],
  disponibilidade: ['seg', 'ter', 'qua', 'qui', 'sex'],
  valor_diaria_padrao: 120,
  data_cadastro: '2025-06-15T10:00:00Z',
  updated_at: '2026-02-01T14:00:00Z',
};

export const mockDiarists: DiaristResponse[] = [
  mockDiarist,
  {
    ...mockDiarist,
    id: 'diarista-002',
    nome: 'Maria Aparecida',
    cpf: '654.987.321-00',
    status: 'ativo',
    avaliacao_media: 4.5,
    total_trabalhos: 89,
    especialidades: ['faxina', 'organização'],
    disponibilidade: ['seg', 'qua', 'sex'],
    valor_diaria_padrao: 110,
  },
  {
    ...mockDiarist,
    id: 'diarista-003',
    nome: 'Joaquim Ferreira',
    cpf: '147.258.369-00',
    status: 'inativo',
    avaliacao_media: 3.2,
    total_trabalhos: 12,
    especialidades: ['faxina'],
    disponibilidade: ['sab', 'dom'],
    valor_diaria_padrao: 100,
  },
];

// Helpers para criar dados customizados
export const createMockPost = (overrides?: Partial<PostResponse>): PostResponse => ({
  ...mockPost,
  ...overrides,
});

export const createMockScale = (overrides?: Partial<ScaleResponse>): ScaleResponse => ({
  ...mockScale,
  ...overrides,
});

export const createMockOccurrence = (overrides?: Partial<OccurrenceResponse>): OccurrenceResponse => ({
  ...mockOccurrence,
  ...overrides,
});

export const createMockEmployee = (overrides?: Partial<EmployeeResponse>): EmployeeResponse => ({
  ...mockEmployee,
  ...overrides,
});

export const createMockDiarist = (overrides?: Partial<DiaristResponse>): DiaristResponse => ({
  ...mockDiarist,
  ...overrides,
});
