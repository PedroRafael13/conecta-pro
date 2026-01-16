/**
 * Field Service Types - Conecta PRO
 * Tipos para o módulo de serviços de campo
 */

// Tipos de serviço
export type TipoServico = 'instalacao' | 'manutencao' | 'reparo' | 'inspecao';
export type PrioridadeServico = 'urgente' | 'alta' | 'normal' | 'baixa';
export type StatusOrdem = 'aberta' | 'em_atendimento' | 'concluida' | 'cancelada';
export type StatusTecnico = 'disponivel' | 'ocupado' | 'offline' | 'em_deslocamento';

// Ordem de Serviço
export interface ServiceOrder {
  id: string;
  numero: string;
  cliente: string;
  endereco: string;
  tipo: TipoServico;
  prioridade: PrioridadeServico;
  status: StatusOrdem;
  tecnico_id?: string;
  tecnico_nome?: string;
  descricao: string;
  data_abertura: string;
  data_agendamento?: string;
  data_conclusao?: string;
  sla_horas: number;
  contato_cliente?: string;
  telefone_cliente?: string;
  equipamentos?: string[];
  observacoes?: string;
  fotos_antes?: string[];
  fotos_depois?: string[];
  assinatura_cliente?: string;
}

// Evento na timeline da ordem
export interface OrderTimelineEvent {
  id: string;
  ordem_id: string;
  tipo: 'abertura' | 'atribuicao' | 'deslocamento' | 'chegada' | 'inicio_atendimento' | 'conclusao' | 'cancelamento';
  descricao: string;
  data: string;
  usuario?: string;
  detalhes?: Record<string, unknown>;
}

// Técnico
export interface Technician {
  id: string;
  nome: string;
  avatar?: string;
  status: StatusTecnico;
  especialidades: string[];
  localizacao?: GeoLocation;
  ordens_hoje: number;
  rating: number;
  telefone?: string;
  email?: string;
  veiculo?: string;
  placa_veiculo?: string;
}

// Localização geográfica
export interface GeoLocation {
  lat: number;
  lng: number;
  endereco?: string;
  ultima_atualizacao?: string;
}

// Rota de atendimento
export interface Route {
  id: string;
  tecnico_id: string;
  tecnico_nome?: string;
  ordens: string[];
  ordens_detalhes?: ServiceOrder[];
  distancia_total_km: number;
  tempo_estimado_min: number;
  otimizada: boolean;
  data_criacao: string;
  data_atualizacao?: string;
}

// Ponto da rota
export interface RoutePoint {
  ordem_id: string;
  ordem_numero: string;
  endereco: string;
  localizacao: GeoLocation;
  ordem_na_rota: number;
  tempo_estimado_chegada?: string;
  tempo_estimado_atendimento_min?: number;
}

// KPIs do Field Service
export interface FieldServiceKPIs {
  ordens_abertas: number;
  ordens_em_atendimento: number;
  ordens_concluidas_hoje: number;
  sla_compliance: number;
  tempo_medio_atendimento_min: number;
  tecnicos_disponiveis: number;
  tecnicos_total: number;
}

// Filtros para busca de ordens
export interface ServiceOrderFilters {
  status?: StatusOrdem[];
  tipo?: TipoServico[];
  prioridade?: PrioridadeServico[];
  tecnico_id?: string;
  data_inicio?: string;
  data_fim?: string;
  cliente?: string;
  search?: string;
}

// Filtros para busca de técnicos
export interface TechnicianFilters {
  status?: StatusTecnico[];
  especialidade?: string;
  search?: string;
}

// Configurações de prioridade
export const PRIORIDADE_CONFIG: Record<PrioridadeServico, { label: string; color: string; bgColor: string; slaDefault: number }> = {
  urgente: { label: 'Urgente', color: 'text-red-700', bgColor: 'bg-red-100', slaDefault: 4 },
  alta: { label: 'Alta', color: 'text-orange-700', bgColor: 'bg-orange-100', slaDefault: 8 },
  normal: { label: 'Normal', color: 'text-blue-700', bgColor: 'bg-blue-100', slaDefault: 24 },
  baixa: { label: 'Baixa', color: 'text-gray-700', bgColor: 'bg-gray-100', slaDefault: 48 },
};

// Configurações de status da ordem
export const STATUS_ORDEM_CONFIG: Record<StatusOrdem, { label: string; color: string; bgColor: string }> = {
  aberta: { label: 'Aberta', color: 'text-yellow-700', bgColor: 'bg-yellow-100' },
  em_atendimento: { label: 'Em Atendimento', color: 'text-blue-700', bgColor: 'bg-blue-100' },
  concluida: { label: 'Concluída', color: 'text-green-700', bgColor: 'bg-green-100' },
  cancelada: { label: 'Cancelada', color: 'text-gray-700', bgColor: 'bg-gray-100' },
};

// Configurações de status do técnico
export const STATUS_TECNICO_CONFIG: Record<StatusTecnico, { label: string; color: string; bgColor: string; dotColor: string }> = {
  disponivel: { label: 'Disponível', color: 'text-green-700', bgColor: 'bg-green-100', dotColor: 'bg-green-500' },
  ocupado: { label: 'Ocupado', color: 'text-red-700', bgColor: 'bg-red-100', dotColor: 'bg-red-500' },
  em_deslocamento: { label: 'Em Deslocamento', color: 'text-blue-700', bgColor: 'bg-blue-100', dotColor: 'bg-blue-500' },
  offline: { label: 'Offline', color: 'text-gray-700', bgColor: 'bg-gray-100', dotColor: 'bg-gray-400' },
};

// Configurações de tipo de serviço
export const TIPO_SERVICO_CONFIG: Record<TipoServico, { label: string; icon: string }> = {
  instalacao: { label: 'Instalação', icon: 'Package' },
  manutencao: { label: 'Manutenção', icon: 'Wrench' },
  reparo: { label: 'Reparo', icon: 'AlertTriangle' },
  inspecao: { label: 'Inspeção', icon: 'ClipboardCheck' },
};
