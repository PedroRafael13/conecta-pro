// Types para Maintenance - Facilities Module
// Conecta PRO

export type MaintenanceType = 'preventiva' | 'corretiva' | 'preditiva';

export type MaintenancePriority = 'urgente' | 'alta' | 'normal' | 'baixa';

export type MaintenanceStatus = 'agendada' | 'em_execucao' | 'concluida' | 'cancelada' | 'atrasada';

export interface MaintenanceOrder {
  id: string;
  numero: string;
  equipment_id: string;
  equipment_nome: string;
  equipment_codigo?: string;
  equipment_localizacao?: string;
  tipo: MaintenanceType;
  prioridade: MaintenancePriority;
  status: MaintenanceStatus;
  descricao: string;
  tecnico_responsavel?: string;
  tecnico_id?: string;
  data_agendada: string;
  data_inicio?: string;
  data_conclusao?: string;
  tempo_estimado_horas?: number;
  tempo_real_horas?: number;
  custo_estimado?: number;
  custo_real?: number;
  pecas_utilizadas?: MaintenancePart[];
  checklist?: MaintenanceChecklistItem[];
  observacoes?: string;
  fotos?: string[];
  created_at?: string;
  updated_at?: string;
  created_by?: string;
}

export interface MaintenancePart {
  id: string;
  nome: string;
  codigo?: string;
  quantidade: number;
  valor_unitario: number;
  valor_total: number;
}

export interface MaintenanceChecklistItem {
  id: string;
  descricao: string;
  concluido: boolean;
  observacao?: string;
}

export interface PredictiveAlert {
  id: string;
  equipment_id: string;
  equipment_nome: string;
  equipment_codigo?: string;
  probabilidade_falha: number;
  dias_estimados: number;
  recomendacao: string;
  baseado_em: string[];
  severidade: 'critica' | 'alta' | 'media' | 'baixa';
  modelo_ia?: string;
  confianca?: number;
  created_at: string;
  acknowledged: boolean;
  ordem_criada?: boolean;
  ordem_id?: string;
}

export interface MaintenanceSchedule {
  id: string;
  equipment_id: string;
  equipment_nome: string;
  tipo: MaintenanceType;
  frequencia_dias: number;
  ultima_execucao?: string;
  proxima_execucao: string;
  descricao_padrao: string;
  checklist_padrao?: string[];
  ativo: boolean;
}

export interface MaintenanceFilter {
  search?: string;
  status?: MaintenanceStatus[];
  tipo?: MaintenanceType[];
  prioridade?: MaintenancePriority[];
  tecnico_id?: string;
  equipment_id?: string;
  data_inicio?: string;
  data_fim?: string;
  atrasadas?: boolean;
}

export interface MaintenanceStats {
  total: number;
  agendadas: number;
  em_execucao: number;
  concluidas: number;
  atrasadas: number;
  canceladas: number;
  preventivas: number;
  corretivas: number;
  preditivas: number;
  custo_total_mes: number;
  tempo_medio_resolucao: number;
  taxa_cumprimento: number;
}

export interface MaintenanceCalendarEvent {
  id: string;
  title: string;
  date: string;
  tipo: MaintenanceType;
  prioridade: MaintenancePriority;
  status: MaintenanceStatus;
  equipment_nome: string;
}

export interface CreateMaintenanceOrderDTO {
  equipment_id: string;
  tipo: MaintenanceType;
  prioridade: MaintenancePriority;
  descricao: string;
  data_agendada: string;
  tecnico_id?: string;
  tempo_estimado_horas?: number;
  custo_estimado?: number;
  checklist?: string[];
}

export interface UpdateMaintenanceOrderDTO extends Partial<CreateMaintenanceOrderDTO> {
  status?: MaintenanceStatus;
  data_inicio?: string;
  data_conclusao?: string;
  tempo_real_horas?: number;
  custo_real?: number;
  observacoes?: string;
}

export interface Technician {
  id: string;
  nome: string;
  email: string;
  telefone?: string;
  especialidades: string[];
  disponivel: boolean;
  ordens_ativas: number;
}
