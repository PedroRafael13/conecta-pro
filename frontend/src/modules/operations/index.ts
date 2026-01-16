/**
 * Modulo Operations - Gestao de Operacoes
 *
 * Este modulo fornece componentes e hooks para:
 * - Gestao de Postos de Trabalho
 * - Escalas e Turnos
 * - Substituicoes e Workflow de Aprovacao
 */

// === POSTOS ===
export {
  // Types
  type Posto,
  type PostoStatus,
  type Turno,
  type TipoTurno,
  type Coordenadas,
  type ContatoResponsavel,
  type RequisitoPosto,
  type Equipamento,
  type PostoFilters,
  type PostoStats,
  type PostoFormData,
  type TurnoFormData,
  // Hooks
  usePostos,
  // Components
  PostoCard,
  PostoMap,
  TurnoConfig,
} from './postos';

// === SCHEDULES ===
export {
  // Types
  type Schedule,
  type ScheduleStatus,
  type CheckInOut,
  type Conflict,
  type ConflictType,
  type ScheduleEvent,
  type ScheduleFilters,
  type ScheduleStats,
  type ScheduleFormData,
  type BulkScheduleFormData,
  type WeekDay,
  type CalendarView,
  // Hooks
  useSchedules,
  // Components
  ScheduleCalendar,
  ShiftCard,
  ConflictAlert,
  ConflictList,
} from './schedules';

// === SUBSTITUTIONS ===
export {
  // Types
  type Substitution,
  type SubstitutionStatus,
  type SubstitutionReason,
  type SubstitutionHistoryItem,
  type Documento,
  type SubstitutionFilters,
  type SubstitutionStats,
  type SubstitutionFormData,
  type ApprovalAction,
  type AvailableSubstitute,
  type WorkflowStep,
  // Hooks
  useSubstitutions,
  // Components
  SubstitutionCard,
  SubstitutionForm,
  ApprovalWorkflow,
  WorkflowSummary,
} from './substitutions';

// === DASHBOARD ===
export { OperationsDashboard } from './OperationsDashboard';
