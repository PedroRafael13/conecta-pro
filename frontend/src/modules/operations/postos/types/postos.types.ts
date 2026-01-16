/**
 * Tipos para o módulo de Postos de Trabalho
 * Gestão de locais de trabalho, turnos e alocação de profissionais
 */

export interface Posto {
  id: string;
  nome: string;
  endereco: string;
  cliente: string;
  cliente_id: string;
  status: PostoStatus;
  turnos: Turno[];
  coordenadas?: Coordenadas;
  contato_responsavel?: ContatoResponsavel;
  requisitos?: RequisitoPosto[];
  equipamentos?: Equipamento[];
  observacoes?: string;
  created_at: string;
  updated_at: string;
}

export type PostoStatus = 'ativo' | 'inativo' | 'em_implantacao' | 'suspenso';

export interface Coordenadas {
  lat: number;
  lng: number;
}

export interface Turno {
  id: string;
  nome: string;
  horario_inicio: string;
  horario_fim: string;
  dias_semana: number[]; // 0 = Domingo, 1 = Segunda, ..., 6 = Sábado
  profissionais_alocados: number;
  profissionais_necessarios: number;
  tipo: TipoTurno;
  adicional_noturno: boolean;
  intervalo_minutos?: number;
}

export type TipoTurno = 'diurno' | 'noturno' | 'misto' | '12x36' | '24h';

export interface ContatoResponsavel {
  nome: string;
  telefone: string;
  email?: string;
  cargo?: string;
}

export interface RequisitoPosto {
  id: string;
  descricao: string;
  obrigatorio: boolean;
  tipo: 'certificacao' | 'experiencia' | 'equipamento' | 'habilidade';
}

export interface Equipamento {
  id: string;
  nome: string;
  quantidade: number;
  status: 'disponivel' | 'em_uso' | 'manutencao';
}

export interface PostoFilters {
  status?: PostoStatus[];
  cliente_id?: string;
  cidade?: string;
  com_vagas?: boolean;
  search?: string;
}

export interface PostoStats {
  total_postos: number;
  postos_ativos: number;
  postos_inativos: number;
  total_turnos: number;
  profissionais_alocados: number;
  profissionais_necessarios: number;
  taxa_ocupacao: number;
}

export interface PostoFormData {
  nome: string;
  endereco: string;
  cliente_id: string;
  status: PostoStatus;
  coordenadas?: Coordenadas;
  contato_responsavel?: ContatoResponsavel;
  observacoes?: string;
}

export interface TurnoFormData {
  nome: string;
  horario_inicio: string;
  horario_fim: string;
  dias_semana: number[];
  profissionais_necessarios: number;
  tipo: TipoTurno;
  adicional_noturno: boolean;
  intervalo_minutos?: number;
}
