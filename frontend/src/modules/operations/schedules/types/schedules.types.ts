/**
 * Tipos para o módulo de Escalas
 * Gestão de escalas de trabalho, alocação e conflitos
 */

export interface Schedule {
  id: string;
  posto_id: string;
  posto_nome: string;
  profissional_id: string;
  profissional_nome: string;
  profissional_avatar?: string;
  profissional_funcao: string;
  data: string;
  turno_id: string;
  turno: string;
  horario_inicio: string;
  horario_fim: string;
  status: ScheduleStatus;
  check_in?: CheckInOut;
  check_out?: CheckInOut;
  observacoes?: string;
  created_at: string;
  updated_at: string;
}

export type ScheduleStatus =
  | 'confirmado'
  | 'pendente'
  | 'cancelado'
  | 'em_andamento'
  | 'concluido'
  | 'falta'
  | 'substituido';

export interface CheckInOut {
  timestamp: string;
  coordenadas?: {
    lat: number;
    lng: number;
  };
  foto_url?: string;
  metodo: 'app' | 'biometria' | 'manual' | 'qrcode';
}

export interface Conflict {
  id: string;
  tipo: ConflictType;
  severidade: 'alta' | 'media' | 'baixa';
  descricao: string;
  schedules: string[];
  profissional_id: string;
  profissional_nome: string;
  data: string;
  sugestao_resolucao?: string;
  resolvido: boolean;
  resolvido_por?: string;
  resolvido_em?: string;
}

export type ConflictType =
  | 'sobreposicao'
  | 'descanso_minimo'
  | 'limite_horas_diarias'
  | 'limite_horas_semanais'
  | 'feriado'
  | 'ferias'
  | 'atestado';

export interface ScheduleEvent {
  id: string;
  title: string;
  start: Date;
  end: Date;
  resourceId?: string;
  profissional_id: string;
  profissional_nome: string;
  posto_id: string;
  posto_nome: string;
  status: ScheduleStatus;
  color?: string;
  extendedProps?: {
    turno: string;
    funcao: string;
  };
}

export interface ScheduleFilters {
  posto_id?: string;
  profissional_id?: string;
  status?: ScheduleStatus[];
  data_inicio?: string;
  data_fim?: string;
  turno_id?: string;
  com_conflitos?: boolean;
}

export interface ScheduleStats {
  total_escalas: number;
  escalas_confirmadas: number;
  escalas_pendentes: number;
  escalas_canceladas: number;
  faltas: number;
  substituicoes: number;
  conflitos_ativos: number;
  taxa_pontualidade: number;
  horas_programadas: number;
  horas_trabalhadas: number;
}

export interface ScheduleFormData {
  posto_id: string;
  profissional_id: string;
  turno_id: string;
  data: string;
  observacoes?: string;
}

export interface BulkScheduleFormData {
  posto_id: string;
  turno_id: string;
  profissionais: string[];
  data_inicio: string;
  data_fim: string;
  dias_semana: number[];
  observacoes?: string;
}

export interface WeekDay {
  date: Date;
  dayName: string;
  dayNumber: number;
  isToday: boolean;
  isWeekend: boolean;
  schedules: Schedule[];
}

export interface CalendarView {
  type: 'day' | 'week' | 'month';
  currentDate: Date;
  startDate: Date;
  endDate: Date;
}
