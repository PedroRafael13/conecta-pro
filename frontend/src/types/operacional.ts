/**
 * Tipos para o módulo Operacional
 */

// Enums
export type PostType =
  | 'vigilante'
  | 'porteiro'
  | 'recepcionista'
  | 'controlador_acesso'
  | 'supervisor'
  | 'lider'
  | 'rondante'
  | 'monitoramento'
  | 'manutencao'
  | 'servicos_gerais'
  | 'jardinagem'
  | 'portaria';

export type PostStatus = 'active' | 'inactive' | 'temporary' | 'suspended';

export type ShiftType =
  | 'diurno'
  | 'noturno'
  | 'manha'
  | 'tarde'
  | 'noite'
  | 'administrativo'
  | 'integral'
  | '12x36';

// Post (Posto de Trabalho)
export interface Post {
  id: string;
  code: string;
  name: string;
  description: string | null;
  post_type: PostType;
  status: PostStatus;
  shift_type: ShiftType;
  contract_id: string | null;
  client_id: string | null;
  address: string | null;
  city: string | null;
  state: string | null;
  zip_code: string | null;
  latitude: number | null;
  longitude: number | null;
  shift_start_time: string | null;
  shift_end_time: string | null;
  break_duration_minutes: number;
  night_shift_bonus_percent: number;
  hazard_pay_percent: number;
  required_certifications: Record<string, unknown> | null;
  required_headcount: number;
  current_headcount: number;
  requires_experience_months: number;
  hourly_rate: number;
  monthly_cost: number;
  requires_armed: boolean;
  requires_vehicle: boolean;
  supervisor_name: string | null;
  supervisor_phone: string | null;
  emergency_contact: string | null;
  emergency_phone: string | null;
  notes: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  // Computed properties
  is_filled: boolean;
  vacancy_count: number;
  daily_hours: number;
}

export interface PostCreate {
  name: string;
  description?: string;
  post_type: PostType;
  shift_type: ShiftType;
  contract_id?: string;
  client_id?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  latitude?: number;
  longitude?: number;
  shift_start_time?: string;
  shift_end_time?: string;
  break_duration_minutes?: number;
  night_shift_bonus_percent?: number;
  hazard_pay_percent?: number;
  required_certifications?: Record<string, unknown>;
  required_headcount?: number;
  requires_experience_months?: number;
  hourly_rate?: number;
  monthly_cost?: number;
  requires_armed?: boolean;
  requires_vehicle?: boolean;
  supervisor_name?: string;
  supervisor_phone?: string;
  emergency_contact?: string;
  emergency_phone?: string;
  notes?: string;
}

export interface PostUpdate extends Partial<PostCreate> {
  status?: PostStatus;
  is_active?: boolean;
}

export interface PostFilter {
  post_type?: PostType;
  status?: PostStatus;
  shift_type?: ShiftType;
  contract_id?: string;
  client_id?: string;
  city?: string;
  state?: string;
  requires_armed?: boolean;
  requires_vehicle?: boolean;
  has_vacancy?: boolean;
  search?: string;
}

export interface PostStats {
  total: number;
  by_status: Record<string, number>;
  by_type: Record<string, number>;
  by_shift: Record<string, number>;
  filled: number;
  with_vacancy: number;
  total_headcount: number;
  total_allocated: number;
  total_monthly_cost: number;
}

// Allocation (Alocação)
export type AllocationStatus =
  | 'active'
  | 'inactive'
  | 'pending'
  | 'suspended'
  | 'terminated';

export interface Allocation {
  id: string;
  post_id: string;
  employee_id: string;
  status: AllocationStatus;
  start_date: string;
  end_date: string | null;
  is_primary: boolean;
  is_temporary: boolean;
  hourly_rate: number;
  monthly_salary: number;
  additional_benefits: number;
  role: string | null;
  qualifications: Record<string, unknown> | null;
  notes: string | null;
  termination_reason: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  // Computed
  is_current: boolean;
  days_allocated: number;
  total_monthly_cost: number;
}

export interface AllocationCreate {
  post_id: string;
  employee_id: string;
  start_date: string;
  end_date?: string | null;
  is_primary?: boolean;
  is_temporary?: boolean;
  hourly_rate?: number;
  monthly_salary?: number;
  additional_benefits?: number;
  role?: string;
  qualifications?: Record<string, unknown>;
  notes?: string;
}

export interface AllocationUpdate {
  status?: AllocationStatus;
  end_date?: string | null;
  is_primary?: boolean;
  is_temporary?: boolean;
  hourly_rate?: number;
  monthly_salary?: number;
  additional_benefits?: number;
  role?: string;
  qualifications?: Record<string, unknown>;
  notes?: string;
  termination_reason?: string;
  is_active?: boolean;
}

export interface AllocationTerminate {
  end_date: string;
  termination_reason: string;
  notes?: string;
}

export interface AllocationFilter {
  post_id?: string;
  employee_id?: string;
  status?: AllocationStatus;
  is_primary?: boolean;
  is_temporary?: boolean;
  is_current?: boolean;
  start_date_from?: string;
  start_date_to?: string;
}

// Shift (Turnos)
export type ShiftStatus =
  | 'scheduled'
  | 'in_progress'
  | 'completed'
  | 'missed'
  | 'partial'
  | 'substituted'
  | 'cancelled'
  | 'off_day';

export interface Shift {
  id: string;
  scale_id: string;
  employee_id: string | null;
  post_id: string;
  shift_date: string;
  planned_start_time: string;
  planned_end_time: string;
  planned_break_minutes: number;
  actual_start_time: string | null;
  actual_end_time: string | null;
  actual_break_minutes: number | null;
  status: ShiftStatus;
  is_holiday: boolean;
  is_night_shift: boolean;
  is_overtime: boolean;
  is_off_day: boolean;
  needs_substitution: boolean;
  planned_hours: number;
  actual_hours: number;
  overtime_hours: number;
  night_hours: number;
  base_pay: number;
  overtime_pay: number;
  night_bonus: number;
  holiday_bonus: number;
  total_pay: number;
  notes: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  // Computed
  is_future: boolean;
  is_today: boolean;
  is_filled: boolean;
  was_worked: boolean;
}

export interface ShiftCreate {
  scale_id: string;
  employee_id?: string | null;
  post_id: string;
  shift_date: string;
  planned_start_time: string;
  planned_end_time: string;
  planned_break_minutes?: number;
  is_off_day?: boolean;
  notes?: string;
  is_holiday?: boolean;
  is_night_shift?: boolean;
  is_overtime?: boolean;
  planned_hours?: number;
}

export interface ShiftUpdate {
  employee_id?: string | null;
  planned_start_time?: string;
  planned_end_time?: string;
  planned_break_minutes?: number;
  actual_start_time?: string | null;
  actual_end_time?: string | null;
  actual_break_minutes?: number | null;
  status?: ShiftStatus;
  is_off_day?: boolean;
  is_overtime?: boolean;
  needs_substitution?: boolean;
  actual_hours?: number;
  overtime_hours?: number;
  notes?: string | null;
  is_active?: boolean;
}

export interface ShiftFilter {
  scale_id?: string;
  employee_id?: string;
  post_id?: string;
  status?: ShiftStatus;
  start_date?: string;
  end_date?: string;
  is_holiday?: boolean;
  is_night_shift?: boolean;
  is_off_day?: boolean;
  is_filled?: boolean;
  needs_substitution?: boolean;
}

export interface ShiftCheckIn {
  actual_start_time: string;
  notes?: string;
}

export interface ShiftCheckOut {
  actual_end_time: string;
  actual_break_minutes?: number;
  notes?: string;
}

// Reports (Relatorios)
export interface CoverageReportItem {
  post_id: string;
  post_name: string;
  total_allocations: number;
  active_allocations: number;
  coverage_rate: number;
}

export interface CoverageReportResponse {
  start_date: string;
  end_date: string;
  total_posts: number;
  total_allocations: number;
  active_allocations: number;
  coverage_rate: number;
  items: CoverageReportItem[];
}

export interface HoursReportItem {
  employee_id: string;
  total_shifts: number;
  total_hours: number;
  overtime_hours: number;
}

export interface HoursReportResponse {
  start_date: string;
  end_date: string;
  total_employees: number;
  total_hours: number;
  total_overtime: number;
  items: HoursReportItem[];
}

export interface CostsReportItem {
  post_id: string;
  post_name: string;
  total_shifts: number;
  total_cost: number;
}

export interface CostsReportResponse {
  start_date: string;
  end_date: string;
  total_posts: number;
  total_cost: number;
  items: CostsReportItem[];
}

// Employee (funcionário) - usado em Operacional
export interface Employee {
  id: string;
  full_name?: string | null;
  name?: string | null;
  email?: string | null;
  registration?: string | null;
  status?: string | null;
}

// Pagination
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Labels para display
export const POST_TYPE_LABELS: Record<PostType, string> = {
  vigilante: 'Vigilante',
  porteiro: 'Porteiro',
  recepcionista: 'Recepcionista',
  controlador_acesso: 'Controlador de Acesso',
  supervisor: 'Supervisor',
  lider: 'Líder',
  rondante: 'Rondante',
  monitoramento: 'Monitoramento',
  manutencao: 'Manutenção',
  servicos_gerais: 'Serviços Gerais',
  jardinagem: 'Jardinagem',
  portaria: 'Portaria',
};

export const POST_STATUS_LABELS: Record<PostStatus, string> = {
  active: 'Ativo',
  inactive: 'Inativo',
  temporary: 'Temporário',
  suspended: 'Suspenso',
};

export const SHIFT_STATUS_LABELS: Record<ShiftStatus, string> = {
  scheduled: 'Agendado',
  in_progress: 'Em andamento',
  completed: 'Concluido',
  missed: 'Falta',
  partial: 'Parcial',
  substituted: 'Substituido',
  cancelled: 'Cancelado',
  off_day: 'Folga',
};

export const ALLOCATION_STATUS_LABELS: Record<AllocationStatus, string> = {
  active: 'Ativa',
  inactive: 'Inativa',
  pending: 'Pendente',
  suspended: 'Suspensa',
  terminated: 'Encerrada',
};

export const SHIFT_TYPE_LABELS: Record<ShiftType, string> = {
  diurno: 'Diurno (07h-19h)',
  noturno: 'Noturno (19h-07h)',
  manha: 'Manhã (06h-14h)',
  tarde: 'Tarde (14h-22h)',
  noite: 'Noite (22h-06h)',
  administrativo: 'Administrativo (08h-18h)',
  integral: 'Integral (24h)',
  '12x36': '12x36',
};

// Scale Types
export type ScaleType =
  | '12x36'
  | '6x1'
  | '5x2'
  | '5x1'
  | '4x2'
  | 'turno_revezamento'
  | 'administrativo'
  | 'personalizado';

export type ScaleStatus =
  | 'draft'
  | 'pending_approval'
  | 'approved'
  | 'published'
  | 'in_progress'
  | 'completed'
  | 'cancelled';

// Scale (Escala de Trabalho)
export interface Scale {
  id: string;
  post_id: string;
  scale_type: ScaleType;
  status: ScaleStatus;
  month: number;
  year: number;
  name: string | null;
  description: string | null;
  start_date: string | null;
  end_date: string | null;
  total_shifts: number;
  filled_shifts: number;
  total_hours: number;
  overtime_hours: number;
  estimated_cost: number;
  config: Record<string, unknown> | null;
  notes: string | null;
  approved_by: string | null;
  approved_at: string | null;
  approval_notes: string | null;
  published_by: string | null;
  published_at: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  created_by: string | null;
  // Computed
  is_current_month: boolean;
  is_published: boolean;
  can_edit: boolean;
  fill_rate: number;
}

export interface ScaleCreate {
  post_id: string;
  scale_type?: ScaleType;
  month: number;
  year: number;
  notes?: string;
  config?: Record<string, unknown>;
}

export interface ScaleUpdate {
  scale_type?: ScaleType;
  status?: ScaleStatus;
  notes?: string;
  config?: Record<string, unknown>;
  is_active?: boolean;
}

export interface ScaleFilter {
  post_id?: string;
  scale_type?: ScaleType;
  status?: ScaleStatus;
  month?: number;
  year?: number;
  is_current_month?: boolean;
}

export interface ScaleGenerateRequest {
  post_id: string;
  month: number;
  year: number;
  scale_type: ScaleType;
  employee_ids: string[];
  config?: {
    consider_holidays?: boolean;
    balance_night_shifts?: boolean;
    max_consecutive_days?: number;
    min_rest_hours?: number;
  };
}

export interface ScaleStats {
  total: number;
  by_status: Record<string, number>;
  by_type: Record<string, number>;
  total_hours: number;
  total_overtime_hours: number;
  total_estimated_cost: number;
  avg_fill_rate: number;
}

export const SCALE_TYPE_LABELS: Record<ScaleType, string> = {
  '12x36': '12x36 (12h trabalho, 36h descanso)',
  '6x1': '6x1 (6 dias trabalho, 1 folga)',
  '5x2': '5x2 (Segunda a Sexta)',
  '5x1': '5x1 (5 dias trabalho, 1 folga)',
  '4x2': '4x2 (4 dias trabalho, 2 folgas)',
  turno_revezamento: 'Revezamento (Manhã/Tarde/Noite)',
  administrativo: 'Administrativo',
  personalizado: 'Personalizado',
};

export const SCALE_STATUS_LABELS: Record<ScaleStatus, string> = {
  draft: 'Rascunho',
  pending_approval: 'Aguardando Aprovação',
  approved: 'Aprovada',
  published: 'Publicada',
  in_progress: 'Em Andamento',
  completed: 'Concluída',
  cancelled: 'Cancelada',
};
